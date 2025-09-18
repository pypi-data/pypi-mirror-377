from __future__ import annotations

from . import ast as AST
from time import perf_counter
from typing import Dict, Iterable, Optional, Tuple, TextIO, cast

from copy import deepcopy


def optimize_ex(
    program: AST.Program,
    *,
    enabled_passes: Optional[Iterable[str]] = None,
    collect_timings: bool = False,
    dump_stream: Optional[TextIO] = None,
) -> Tuple[AST.Program, Dict[str, float]]:
    """Apply AST optimizations with optional pass selection, timings, and dump.

    Pass names: 'const_fold', 'dead_branch', 'copy_prop', 'cse', 'inline', 'dce_pure', 'jump_thread'
    Returns (program, timings_ms)
    """

    INLINE_EXPR_NODE_LIMIT = 12
    COPY_PROP_NODE_LIMIT = 6
    CSE_EXPR_NODE_LIMIT = 8
    enabled: set[str] = set(enabled_passes or {
        "const_fold",
        "dead_branch",
        "copy_prop",
        "cse",
        "licm",
        "dce_assign",
        "inline",
        "dce_pure",
        "jump_thread",
        "tree_shake",
    })
    timings: Dict[str, float] = {}

    def _tick(name: str, t0: float) -> None:
        if collect_timings:
            timings[name] = (perf_counter() - t0) * 1000.0

    # Collect inline-eligible functions: single Return body; expression over params
    inlineable: dict[str, AST.FunctionDef] = {}

    def node_size(n: AST.Node) -> int:
        # Structural size estimate for heuristics
        if isinstance(n, (AST.Number, AST.String, AST.Identifier)):
            return 1
        if isinstance(n, AST.Binary) or isinstance(n, AST.Compare) or isinstance(n, AST.BoolBinary):
            return 1 + node_size(n.left) + node_size(n.right)
        if isinstance(n, AST.NotOp):
            return 1 + node_size(n.expr)
        if isinstance(n, AST.BuiltinCall):
            return 1 + sum(node_size(a) for a in n.args)
        if isinstance(n, AST.Length):
            return 1 + node_size(n.target)
        if isinstance(n, AST.GetKey):
            return 1 + node_size(n.target) + node_size(n.key)
        if isinstance(n, AST.MakeList):
            return 1 + sum(node_size(it) for it in n.items)
        return 3  # coarse default for other node kinds

    def is_pure_expr(node: AST.Node, allowed_names: set[str]) -> bool:
        if isinstance(node, (AST.Number, AST.String)):
            return True
        if isinstance(node, AST.Identifier):
            return node.name in allowed_names
        if isinstance(node, AST.Binary):
            return is_pure_expr(node.left, allowed_names) and is_pure_expr(
                node.right, allowed_names
            )
        if isinstance(node, AST.Compare):
            return is_pure_expr(node.left, allowed_names) and is_pure_expr(
                node.right, allowed_names
            )
        if isinstance(node, AST.BoolBinary):
            return is_pure_expr(node.left, allowed_names) and is_pure_expr(
                node.right, allowed_names
            )
        if isinstance(node, AST.NotOp):
            return is_pure_expr(node.expr, allowed_names)
        if isinstance(node, AST.BuiltinCall):
            # Consider builtins pure for optimizer if arguments are pure.
            # Only evaluate once; inlining/cse will not duplicate evaluation.
            return all(is_pure_expr(a, allowed_names) for a in node.args)
        if isinstance(node, AST.Length):
            return is_pure_expr(node.target, allowed_names)
        if isinstance(node, AST.GetKey):
            return is_pure_expr(node.target, allowed_names) and is_pure_expr(node.key, allowed_names)
        if isinstance(node, AST.MakeList):
            return all(is_pure_expr(it, allowed_names) for it in node.items)
        return False

    def is_inline_safe_expr(node: AST.Node, allowed_names: set[str]) -> bool:
        # Broader than purity: allow builtin calls (single evaluation) and pure ops over params
        if not is_pure_expr(node, allowed_names):
            # Allow BuiltinCall with pure args
            if isinstance(node, AST.BuiltinCall):
                return all(is_pure_expr(a, allowed_names) for a in node.args)
            return False
        return True

    for s in program.statements:
        if isinstance(s, AST.FunctionDef):
            if len(s.body) == 1 and isinstance(s.body[0], AST.Return) and s.body[0].expr is not None:
                expr = s.body[0].expr
                if node_size(expr) <= INLINE_EXPR_NODE_LIMIT and is_inline_safe_expr(expr, set(s.params)):
                    inlineable[s.name] = s

    def substitute(expr: AST.Node, mapping: dict[str, AST.Node]) -> AST.Node:
        # Deep substitute identifiers by param mapping; clone others
        if isinstance(expr, AST.Identifier) and expr.name in mapping:
            return deepcopy(mapping[expr.name])
        if isinstance(expr, AST.Binary):
            return AST.Binary(op=expr.op, left=substitute(expr.left, mapping), right=substitute(expr.right, mapping))
        if isinstance(expr, AST.Compare):
            return AST.Compare(op=expr.op, left=substitute(expr.left, mapping), right=substitute(expr.right, mapping))
        if isinstance(expr, AST.BoolBinary):
            return AST.BoolBinary(op=expr.op, left=substitute(expr.left, mapping), right=substitute(expr.right, mapping))
        if isinstance(expr, AST.NotOp):
            return AST.NotOp(expr=substitute(expr.expr, mapping))
        if isinstance(expr, AST.BuiltinCall):
            return AST.BuiltinCall(name=expr.name, args=[substitute(a, mapping) for a in expr.args])
        if isinstance(expr, AST.Length):
            return AST.Length(target=substitute(expr.target, mapping))
        if isinstance(expr, AST.GetKey):
            return AST.GetKey(key=substitute(expr.key, mapping), target=substitute(expr.target, mapping))
        if isinstance(expr, AST.MakeList):
            return AST.MakeList(items=[substitute(it, mapping) for it in expr.items])
        # Base cases
        if isinstance(expr, (AST.Number, AST.String, AST.Identifier)):
            return deepcopy(expr)
        return deepcopy(expr)

    def truthy_of(node: AST.Node) -> bool | None:
        # Determine constant truthiness if possible
        if isinstance(node, AST.Number):
            try:
                return float(node.value) != 0.0
            except Exception:
                return None
        return None

    def expr_key(n: AST.Node) -> tuple:
        # Structural key for CSE (pure expressions only)
        if isinstance(n, AST.Number):
            return ("num", n.value)
        if isinstance(n, AST.String):
            return ("str", n.value)
        if isinstance(n, AST.Identifier):
            return ("id", n.name)
        if isinstance(n, AST.Binary):
            return ("bin", n.op, expr_key(n.left), expr_key(n.right))
        if isinstance(n, AST.Compare):
            return ("cmp", n.op, expr_key(n.left), expr_key(n.right))
        if isinstance(n, AST.BoolBinary):
            return ("bool", n.op, expr_key(n.left), expr_key(n.right))
        if isinstance(n, AST.NotOp):
            return ("not", expr_key(n.expr))
        if isinstance(n, AST.BuiltinCall):
            return ("builtin", n.name, tuple(expr_key(a) for a in n.args))
        if isinstance(n, AST.Length):
            return ("len", expr_key(n.target))
        if isinstance(n, AST.GetKey):
            return ("getkey", expr_key(n.target), expr_key(n.key))
        if isinstance(n, AST.MakeList):
            return ("list", tuple(expr_key(it) for it in n.items))
        return ("other", type(n).__name__)

    def replace_idents(node: AST.Node, env: dict[str, AST.Node]) -> AST.Node:
        # Replace identifiers using env mapping; recurse
        if isinstance(node, AST.Identifier):
            repl = env.get(node.name)
            return deepcopy(repl) if repl is not None else node
        if isinstance(node, AST.Binary):
            return AST.Binary(op=node.op, left=replace_idents(node.left, env), right=replace_idents(node.right, env))
        if isinstance(node, AST.Compare):
            return AST.Compare(op=node.op, left=replace_idents(node.left, env), right=replace_idents(node.right, env))
        if isinstance(node, AST.BoolBinary):
            return AST.BoolBinary(op=node.op, left=replace_idents(node.left, env), right=replace_idents(node.right, env))
        if isinstance(node, AST.NotOp):
            return AST.NotOp(expr=replace_idents(node.expr, env))
        if isinstance(node, AST.BuiltinCall):
            return AST.BuiltinCall(name=node.name, args=[replace_idents(a, env) for a in node.args])
        if isinstance(node, AST.Length):
            return AST.Length(target=replace_idents(node.target, env))
        if isinstance(node, AST.GetKey):
            return AST.GetKey(key=replace_idents(node.key, env), target=replace_idents(node.target, env))
        if isinstance(node, AST.MakeList):
            return AST.MakeList(items=[replace_idents(it, env) for it in node.items])
        return node

    def collect_assigned_names(stmts: list[AST.Node]) -> set[str]:
        names: set[str] = set()
        def walk(n: AST.Node) -> None:
            if isinstance(n, AST.Assignment):
                names.add(n.name)
                return
            if isinstance(n, AST.FunctionDef):
                names.add(n.name)
                for s in n.body:
                    walk(s)
                return
            # walk bodies to catch nested assignments
            for attr in ("body", "else_body"):
                seq = getattr(n, attr, None)
                if isinstance(seq, list):
                    for s in seq:
                        walk(s)
        for s in stmts:
            walk(s)
        return names

    def cse_block(stmts: list[AST.Node]) -> list[AST.Node]:
        # 1) collect candidate pure expression frequencies
        freq: dict[tuple, int] = {}
        def bump_expr(n: AST.Node) -> None:
            # Only count pure expressions
            if is_pure_expr(n, allowed_names=set() | set()):
                k = expr_key(n)
                freq[k] = freq.get(k, 0) + 1
        def scan(n: AST.Node) -> None:
            if isinstance(n, AST.ExprStmt):
                scan(n.expr)
                return
            if isinstance(n, AST.Assignment):
                scan(n.expr)
                return
            if isinstance(n, AST.Print) and n.expr is not None:
                scan(n.expr)
                return
            if isinstance(n, (AST.If, AST.While)):
                c = n.cond if isinstance(n, AST.If) else n.cond
                if c is not None:
                    scan(c)
                for s in getattr(n, "body", []) or []:
                    scan(s)
                for s in getattr(n, "else_body", []) or []:
                    scan(s)
                return
            if isinstance(n, AST.Repeat):
                scan(n.count_expr)
                for s in n.body:
                    scan(s)
                return
            if isinstance(n, AST.Binary) or isinstance(n, AST.Compare) or isinstance(n, AST.BoolBinary) or isinstance(n, AST.NotOp) or isinstance(n, AST.BuiltinCall) or isinstance(n, AST.Length) or isinstance(n, AST.GetKey) or isinstance(n, AST.MakeList):
                # post-order bump
                for ch in [getattr(n, 'left', None), getattr(n, 'right', None), getattr(n, 'expr', None), getattr(n, 'target', None), getattr(n, 'key', None)]:
                    if isinstance(ch, AST.Node):
                        scan(ch)
                if isinstance(n, AST.BuiltinCall):
                    for a in n.args:
                        scan(a)
                if isinstance(n, AST.MakeList):
                    for it in n.items:
                        scan(it)
                bump_expr(n)
                return
        for s in stmts:
            scan(s)

        # 2) pick winners
        winners = {k for k, c in freq.items() if c >= 2}
        if not winners:
            return stmts

        # 3) materialize temps at block start
        existing_names = collect_assigned_names(stmts)
        temps: dict[tuple, str] = {}
        counter = 1
        prologue: list[AST.Node] = []

        def rebuild_by_key(k: tuple) -> AST.Node:
            # Not ideal: cannot rebuild from key alone for all cases.
            # Instead, find a representative occurrence from original stmts.
            rep: AST.Node | None = None
            def find(n: AST.Node) -> None:
                nonlocal rep
                if rep is not None:
                    return
                if is_pure_expr(n, set()) and expr_key(n) == k:
                    rep = n
                    return
                # descend
                for child in [getattr(n, 'left', None), getattr(n, 'right', None), getattr(n, 'expr', None), getattr(n, 'target', None), getattr(n, 'key', None)]:
                    if isinstance(child, AST.Node):
                        find(child)
                if isinstance(n, AST.BuiltinCall):
                    for a in n.args:
                        find(a)
                if isinstance(n, AST.MakeList):
                    for it in n.items:
                        find(it)
            for s in stmts:
                find(s)
                if rep is not None:
                    break
            return deepcopy(rep) if rep is not None else AST.Number(0)

        for k in winners:
            # size gate and purity gate
            # use a representative node to measure size
            expr_rep = rebuild_by_key(k)
            if not is_pure_expr(expr_rep, set()):
                continue
            if node_size(expr_rep) < CSE_EXPR_NODE_LIMIT:
                continue
            name = f"_cse{counter}"
            while name in existing_names:
                counter += 1
                name = f"_cse{counter}"
            existing_names.add(name)
            temps[k] = name
            prologue.append(AST.Assignment(name=name, expr=expr_rep))
            counter += 1

        if not temps:
            return stmts

        def replace_cse(n: AST.Node) -> AST.Node:
            if is_pure_expr(n, set()):
                k = expr_key(n)
                t = temps.get(k)
                if t is not None:
                    return AST.Identifier(name=t)
            # Recurse
            if isinstance(n, AST.Binary):
                return AST.Binary(op=n.op, left=replace_cse(n.left), right=replace_cse(n.right))
            if isinstance(n, AST.Compare):
                return AST.Compare(op=n.op, left=replace_cse(n.left), right=replace_cse(n.right))
            if isinstance(n, AST.BoolBinary):
                return AST.BoolBinary(op=n.op, left=replace_cse(n.left), right=replace_cse(n.right))
            if isinstance(n, AST.NotOp):
                return AST.NotOp(expr=replace_cse(n.expr))
            if isinstance(n, AST.BuiltinCall):
                return AST.BuiltinCall(name=n.name, args=[replace_cse(a) for a in n.args])
            if isinstance(n, AST.Length):
                return AST.Length(target=replace_cse(n.target))
            if isinstance(n, AST.GetKey):
                return AST.GetKey(key=replace_cse(n.key), target=replace_cse(n.target))
            if isinstance(n, AST.MakeList):
                return AST.MakeList(items=[replace_cse(it) for it in n.items])
            return n

        new_stmts: list[AST.Node] = []
        for s in stmts:
            if isinstance(s, AST.Assignment):
                new_stmts.append(AST.Assignment(name=s.name, expr=replace_cse(s.expr)))
            elif isinstance(s, AST.ExprStmt):
                new_stmts.append(AST.ExprStmt(expr=replace_cse(s.expr)))
            elif isinstance(s, AST.Print):
                new_stmts.append(AST.Print(expr=None if s.expr is None else replace_cse(s.expr)))
            elif isinstance(s, AST.If):
                cond = s.cond if s.cond is not None else s.left  # type: ignore[assignment]
                cond2 = None if cond is None else replace_cse(cond)
                body2 = [replace_cse(b) if isinstance(b, AST.ExprStmt) else b for b in s.body or []]  # shallow in blocks
                else2 = [replace_cse(b) if isinstance(b, AST.ExprStmt) else b for b in s.else_body or []]
                ns = AST.If(left=None, op=None, right=None, cond=cond2, body=body2, else_body=else2)
                new_stmts.append(ns)
            else:
                new_stmts.append(s)

        return prologue + new_stmts

    def copy_propagate_block(stmts: list[AST.Node]) -> list[AST.Node]:
        env: dict[str, AST.Node] = {}

        def consider_binding(name: str, expr: AST.Node) -> None:
            # Kill on self reference
            if isinstance(expr, AST.Identifier) and expr.name == name:
                env.pop(name, None)
                return
            # Add only small, pure expressions
            if is_pure_expr(expr, set()) and node_size(expr) <= COPY_PROP_NODE_LIMIT:
                env[name] = deepcopy(expr)
            else:
                env.pop(name, None)

        new_stmts: list[AST.Node] = []
        for s in stmts:
            if isinstance(s, AST.Assignment):
                rhs = replace_idents(s.expr, env)
                new_stmts.append(AST.Assignment(name=s.name, expr=rhs))
                consider_binding(s.name, rhs)
                continue
            if isinstance(s, AST.ExprStmt):
                new_stmts.append(AST.ExprStmt(expr=replace_idents(s.expr, env)))
                continue
            if isinstance(s, AST.Print):
                new_stmts.append(AST.Print(expr=None if s.expr is None else replace_idents(s.expr, env)))
                continue
            if isinstance(s, AST.If):
                cond = s.cond if s.cond is not None else s.left  # type: ignore[assignment]
                cond2 = None if cond is None else replace_idents(cond, env)
                body2 = copy_propagate_block(s.body or [])
                else2 = copy_propagate_block(s.else_body or []) if s.else_body is not None else None
                new_stmts.append(AST.If(left=None, op=None, right=None, cond=cond2, body=body2, else_body=else2))
                continue
            if isinstance(s, AST.While):
                cond2 = replace_idents(s.cond, env)
                body2 = copy_propagate_block(s.body)
                new_stmts.append(AST.While(cond=cond2, body=body2))
                continue
            if isinstance(s, AST.Repeat):
                cnt2 = replace_idents(s.count_expr, env)
                body2 = copy_propagate_block(s.body)
                new_stmts.append(AST.Repeat(count_expr=cnt2, body=body2))
                continue
            # Unknown or side-effecting statements: conservatively drop env
            env.clear()
            new_stmts.append(s)
        return new_stmts

    def dce_assign_block(stmts: list[AST.Node]) -> list[AST.Node]:
        # Remove assignments whose value is never used before being reassigned
        live: set[str] = set()
        # Backward pass to collect used names
        def collect_used(n: AST.Node) -> None:
            if isinstance(n, AST.Identifier):
                live.add(n.name)
            for attr in ("left", "right", "expr", "target", "key"):
                v = getattr(n, attr, None)
                if isinstance(v, AST.Node):
                    collect_used(v)
            for attr in ("args", "items", "body", "else_body"):
                vs = getattr(n, attr, None)
                if isinstance(vs, list):
                    for ch in vs:
                        if isinstance(ch, AST.Node):
                            collect_used(ch)
        for s in reversed(stmts):
            if isinstance(s, AST.Assignment):
                collect_used(s.expr)
        # Forward pass: drop dead simple assignments to identifiers not live
        out: list[AST.Node] = []
        for s in stmts:
            if isinstance(s, AST.Assignment) and s.name not in live:
                # keep side-effecting expr conservatively
                if is_pure_expr(s.expr, set()):
                    continue
            out.append(s)
        return out

    def licm_block(stmts: list[AST.Node]) -> list[AST.Node]:
        # Hoist loop-invariant pure expressions assigned to temps out of while/repeat bodies
        prologue: list[AST.Node] = []
        def hoist_in_while(n: AST.While) -> AST.While:
            body = []
            for s in n.body:
                if isinstance(s, AST.Assignment) and is_pure_expr(s.expr, set()):
                    prologue.append(s)
                else:
                    body.append(s)
            n.body = body
            return n
        def hoist_in_repeat(n: AST.Repeat) -> AST.Repeat:
            body = []
            for s in n.body:
                if isinstance(s, AST.Assignment) and is_pure_expr(s.expr, set()):
                    prologue.append(s)
                else:
                    body.append(s)
            n.body = body
            return n
        out: list[AST.Node] = []
        for s in stmts:
            if isinstance(s, AST.While):
                out.append(hoist_in_while(s))
            elif isinstance(s, AST.Repeat):
                out.append(hoist_in_repeat(s))
            else:
                out.append(s)
        return prologue + out

    def fold(node: AST.Node) -> AST.Node:
        # Recurse into child nodes and apply constant folding/inlining
        if isinstance(node, AST.Program):
            # 1) const fold children
            t0 = perf_counter()
            folded = [fold(s) for s in node.statements]
            _tick("const_fold", t0)

            # 2) dead-branch elimination and simple jump threading
            if "dead_branch" in enabled or "jump_thread" in enabled:
                t1 = perf_counter()
                flat: list[AST.Node] = []
                for s in folded:
                    if isinstance(s, AST.If):
                        cond = s.cond
                        if cond is not None:
                            t = truthy_of(cond)
                            if t is True:
                                flat.extend(s.body or [])
                                continue
                            if t is False:
                                flat.extend(s.else_body or [])
                                continue
                        # Jump threading: if body is single If with same cond, collapse
                        if (
                            "jump_thread" in enabled
                            and s.body
                            and len(s.body) == 1
                            and isinstance(s.body[0], AST.If)
                            and s.body[0].cond is not None
                            and cond is not None
                            and expr_key(s.body[0].cond) == expr_key(cond)
                        ):
                            inner: AST.If = s.body[0]  # type: ignore[assignment]
                            # Replace outer with inner (thread)
                            flat.append(AST.If(left=None, op=None, right=None, cond=inner.cond, body=inner.body, else_body=inner.else_body))
                            continue
                    if isinstance(s, AST.While):
                        t = truthy_of(s.cond)
                        if t is False:
                            continue  # remove unreachable loop
                    if isinstance(s, AST.Repeat):
                        if isinstance(s.count_expr, AST.Number) and float(s.count_expr.value) == 0.0:
                            continue
                    # DCE: drop pure expression statements
                    if "dce_pure" in enabled and isinstance(s, AST.ExprStmt) and is_pure_expr(s.expr, set()):
                        continue
                    flat.append(s)
                folded = flat
                _tick("dead_branch", t1)

            # 3) copy-prop, CSE
            if "copy_prop" in enabled:
                t2 = perf_counter()
                folded = copy_propagate_block(folded)
                _tick("copy_prop", t2)
            if "cse" in enabled:
                t3 = perf_counter()
                folded = cse_block(folded)
                _tick("cse", t3)
            if "dce_assign" in enabled:
                t4 = perf_counter()
                folded = dce_assign_block(folded)
                _tick("dce_assign", t4)
            if "licm" in enabled:
                t5 = perf_counter()
                folded = licm_block(folded)
                _tick("licm", t5)
            # 4) optional tree-shake: remove unused function defs
            if "tree_shake" in enabled:
                t6 = perf_counter()

                def collect_calls(sts: list[AST.Node]) -> set[str]:
                    used: set[str] = set()

                    def walk(n: AST.Node) -> None:
                        if isinstance(n, AST.Call):
                            used.add(n.name)
                            for a in n.args:
                                walk(a)
                            return
                        # descend into common containers
                        for attr in ("expr", "left", "right", "cond", "count_expr", "iterable", "target", "key"):
                            v = getattr(n, attr, None)
                            if isinstance(v, AST.Node):
                                walk(v)
                        for attr in ("args", "items", "body", "else_body"):
                            vs = getattr(n, attr, None)
                            if isinstance(vs, list):
                                for ch in vs:
                                    if isinstance(ch, AST.Node):
                                        walk(ch)

                    for st in sts:
                        walk(st)
                    return used

                called = collect_calls(folded)
                # Keep function defs that are called or whose names start with '_'? We keep all starting without '_' too risky? We'll keep only called; others removed.
                new_folded: list[AST.Node] = []
                for st in folded:
                    if isinstance(st, AST.FunctionDef) and st.name not in called:
                        # drop unused def
                        continue
                    new_folded.append(st)
                folded = new_folded
                _tick("tree_shake", t6)

            node.statements = folded
            return node
        if isinstance(node, AST.FunctionDef):
            t0 = perf_counter()
            node.body = [fold(s) for s in node.body]
            _tick("const_fold.fn", t0)
            # Then local block-level passes
            if "copy_prop" in enabled:
                t2 = perf_counter()
                node.body = copy_propagate_block(node.body)
                _tick("copy_prop.fn", t2)
            if "cse" in enabled:
                t3 = perf_counter()
                node.body = cse_block(node.body)
                _tick("cse.fn", t3)
            return node
        if isinstance(node, AST.ExprStmt):
            node.expr = fold(node.expr)
            return node
        if isinstance(node, AST.Assignment):
            node.expr = fold(node.expr)
            return node
        if isinstance(node, AST.Print):
            if node.expr is not None:
                node.expr = fold(node.expr)
            return node
        if isinstance(node, AST.If):
            if node.cond is not None:
                node.cond = fold(node.cond)
            node.body = [fold(s) for s in (node.body or [])]
            if node.else_body is not None:
                node.else_body = [fold(s) for s in node.else_body]
            return node
        if isinstance(node, AST.While):
            node.cond = fold(node.cond)
            node.body = [fold(s) for s in node.body]
            return node
        if isinstance(node, AST.ForEach):
            node.iterable = fold(node.iterable)
            node.body = [fold(s) for s in node.body]
            return node
        if isinstance(node, AST.Repeat):
            node.count_expr = fold(node.count_expr)
            node.body = [fold(s) for s in node.body]
            return node
        if isinstance(node, AST.Call):
            node.args = [fold(a) for a in node.args]
            if "inline" in enabled:
                fn = inlineable.get(node.name)
                if fn and len(fn.params) == len(node.args):
                    mapping = {p: a for p, a in zip(fn.params, node.args)}
                    inlined = substitute(cast_return_expr(fn), mapping)
                    return fold(inlined)
            return node
        if isinstance(node, AST.MakeList):
            node.items = [fold(it) for it in node.items]
            return node
        if isinstance(node, AST.MakeMap):
            return node
        if isinstance(node, AST.Push):
            node.item = fold(node.item)
            node.target = fold(node.target)
            return node
        if isinstance(node, AST.Pop):
            node.target = fold(node.target)
            return node
        if isinstance(node, AST.GetKey):
            node.key = fold(node.key)
            node.target = fold(node.target)
            return node
        if isinstance(node, AST.SetKey):
            node.key = fold(node.key)
            node.value = fold(node.value)
            node.target = fold(node.target)
            return node
        if isinstance(node, AST.DeleteKey):
            node.key = fold(node.key)
            node.target = fold(node.target)
            return node
        if isinstance(node, AST.Length):
            node.target = fold(node.target)
            return node
        if isinstance(node, AST.BoolBinary):
            node.left = fold(node.left)
            node.right = fold(node.right)
            return node
        if isinstance(node, AST.NotOp):
            node.expr = fold(node.expr)
            return node
        if isinstance(node, AST.Compare):
            node.left = fold(node.left)
            node.right = fold(node.right)
            if isinstance(node.left, AST.Number) and isinstance(node.right, AST.Number):
                lval = node.left.value
                r = node.right.value
                if node.op == ">":
                    return AST.Number(1.0 if lval > r else 0.0)
                if node.op == "<":
                    return AST.Number(1.0 if lval < r else 0.0)
                if node.op == "==":
                    return AST.Number(1.0 if lval == r else 0.0)
                if node.op == "!=":
                    return AST.Number(1.0 if lval != r else 0.0)
                if node.op == ">=":
                    return AST.Number(1.0 if lval >= r else 0.0)
                if node.op == "<=":
                    return AST.Number(1.0 if lval <= r else 0.0)
            return node
        if isinstance(node, AST.Binary):
            node.left = fold(node.left)
            node.right = fold(node.right)
            if isinstance(node.left, AST.Number) and isinstance(node.right, AST.Number):
                lval = node.left.value
                r = node.right.value
                if node.op == "+":
                    return AST.Number(lval + r)
                if node.op == "-":
                    return AST.Number(lval - r)
                if node.op == "*":
                    return AST.Number(lval * r)
                if node.op == "/":
                    return AST.Number(float(lval) / float(r))
            return node
        return node

    def cast_return_expr(fn: AST.FunctionDef) -> AST.Node:
        ret = fn.body[0]
        assert isinstance(ret, AST.Return) and ret.expr is not None
        return ret.expr

    prog_node = fold(program)
    prog = cast(AST.Program, prog_node)
    if dump_stream is not None:
        try:
            dump_stream.write(format_ast(prog) + "\n")
        except Exception:
            pass
    return prog, timings


def optimize(program: AST.Program) -> AST.Program:
    # Back-compat wrapper used by existing code paths
    prog, _ = optimize_ex(program)
    return prog


def format_ast(node: AST.Node, indent: int = 0) -> str:
    pad = "  " * indent
    def fmt(n: AST.Node, d: int) -> list[str]:
        lines: list[str] = []
        T = type(n).__name__
        loc = f"@{getattr(n, 'line', None)}:{getattr(n, 'column', None)}"
        if isinstance(n, AST.Program):
            lines.append(f"{pad}{T}{loc}")
            for s in n.statements:
                lines.extend(format_ast(s, indent + 1).splitlines())
            return lines
        if isinstance(n, AST.Assignment):
            lines.append(f"{pad}{T}{loc} {n.name} =")
            lines.extend(format_ast(n.expr, indent + 1).splitlines())
            return lines
        if isinstance(n, AST.ExprStmt):
            lines.append(f"{pad}{T}{loc}")
            lines.extend(format_ast(n.expr, indent + 1).splitlines())
            return lines
        if isinstance(n, AST.Print):
            lines.append(f"{pad}{T}{loc}")
            if n.expr is not None:
                lines.extend(format_ast(n.expr, indent + 1).splitlines())
            return lines
        if isinstance(n, AST.If):
            lines.append(f"{pad}{T}{loc} cond:")
            c = n.cond if n.cond is not None else AST.Compare(op=n.op, left=n.left, right=n.right)  # type: ignore[arg-type]
            lines.extend(format_ast(c, indent + 1).splitlines())
            lines.append(f"{pad}  then:")
            for s in n.body or []:
                lines.extend(format_ast(s, indent + 2).splitlines())
            if n.else_body:
                lines.append(f"{pad}  else:")
                for s in n.else_body:
                    lines.extend(format_ast(s, indent + 2).splitlines())
            return lines
        if isinstance(n, AST.While):
            lines.append(f"{pad}{T}{loc} while:")
            lines.extend(format_ast(n.cond, indent + 1).splitlines())
            for s in n.body:
                lines.extend(format_ast(s, indent + 1).splitlines())
            return lines
        if isinstance(n, AST.Repeat):
            lines.append(f"{pad}{T}{loc} repeat:")
            lines.extend(format_ast(n.count_expr, indent + 1).splitlines())
            for s in n.body:
                lines.extend(format_ast(s, indent + 1).splitlines())
            return lines
        if isinstance(n, AST.FunctionDef):
            lines.append(f"{pad}{T}{loc} {n.name}({', '.join(n.params)})")
            for s in n.body:
                lines.extend(format_ast(s, indent + 1).splitlines())
            return lines
        if isinstance(n, AST.Return):
            lines.append(f"{pad}{T}{loc}")
            if n.expr is not None:
                lines.extend(format_ast(n.expr, indent + 1).splitlines())
            return lines
        if isinstance(n, (AST.Number, AST.String, AST.Identifier)):
            val = getattr(n, 'value', getattr(n, 'name', None))
            lines.append(f"{pad}{T}{loc} {val}")
            return lines
        # Generic fallback
        lines.append(f"{pad}{T}{loc}")
        for attr in ("left", "right", "expr", "target", "key"):
            if hasattr(n, attr):
                v = getattr(n, attr)
                if isinstance(v, AST.Node):
                    lines.extend(format_ast(v, indent + 1).splitlines())
        for attr in ("args", "items", "body", "else_body"):
            v = getattr(n, attr, None)
            if isinstance(v, list):
                for ch in v:
                    if isinstance(ch, AST.Node):
                        lines.extend(format_ast(ch, indent + 1).splitlines())
        return lines

    return "\n".join(fmt(node, indent))


