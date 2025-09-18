from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from . import ast as AST


@dataclass
class TCError:
    line: Optional[int]
    code: str
    message: str


TypeName = str  # "number" | "string" | "bool" | "list" | "map" | "unknown"


def _merge(a: TypeName, b: TypeName) -> TypeName:
    if a == b:
        return a
    if a == "unknown":
        return b
    if b == "unknown":
        return a
    return "unknown"


def _type_of_literal(node: AST.Node) -> Optional[TypeName]:
    if isinstance(node, AST.Number):
        return "number"
    if isinstance(node, AST.String):
        return "string"
    if isinstance(node, AST.MakeList):
        return "list"
    if isinstance(node, AST.MakeMap):
        return "map"
    return None


def check(program: AST.Program) -> List[TCError]:
    errors: List[TCError] = []
    env: Dict[str, TypeName] = {}
    fns: Dict[str, List[str]] = {}

    def t_expr(node: AST.Node) -> TypeName:
        lit = _type_of_literal(node)
        if lit is not None:
            return lit
        if isinstance(node, AST.Identifier):
            return env.get(node.name.lower(), "unknown")
        if isinstance(node, AST.Binary):
            lt = t_expr(node.left)
            rt = t_expr(node.right)
            if node.op in {"+", "-", "*", "/"}:
                if lt != "number" or rt != "number":
                    errors.append(TCError(getattr(node, "line", None), "TC001", "Arithmetic expects numbers"))
                return "number"
            return "unknown"
        if isinstance(node, AST.Length):
            # length of list/map/string -> number
            return "number"
        if isinstance(node, AST.GetKey):
            # could be unknown; do not over-constrain
            return "unknown"
        if isinstance(node, AST.Call):
            # track arity only
            name = node.name.lower()
            if name in fns and len(node.args) != len(fns[name]):
                errors.append(TCError(getattr(node, "line", None), "TC002", f"Function '{name}' expects {len(fns[name])} args"))
            # assume returns unknown
            return "unknown"
        if isinstance(node, AST.BuiltinCall):
            # minimal builtins typing
            if node.name in {"upper", "lower", "trim", "concat", "json_stringify", "read_file"}:
                return "string"
            if node.name in {"power", "sqrt", "abs", "min", "max", "floor", "ceil", "length"}:
                return "number"
            if node.name in {"contains"}:
                return "bool"
            return "unknown"
        if isinstance(node, AST.Compare):
            # comparisons yield bool
            return "bool"
        if isinstance(node, AST.BoolBinary) or isinstance(node, AST.NotOp):
            return "bool"
        return "unknown"

    def walk_stmt(node: AST.Node) -> None:
        if isinstance(node, AST.Assignment):
            env[node.name.lower()] = t_expr(node.expr)
            return
        if isinstance(node, AST.FunctionDef):
            fns[node.name.lower()] = [p.lower() for p in node.params]
            # new scope for params
            saved = env.copy()
            for p in node.params:
                env[p.lower()] = "unknown"
            for s in node.body:
                walk_stmt(s)
            env.clear()
            env.update(saved)
            return
        if isinstance(node, AST.ExprStmt):
            _ = t_expr(node.expr)
            return
        if isinstance(node, AST.Print):
            if node.expr is not None:
                _ = t_expr(node.expr)
            return
        if isinstance(node, AST.If):
            _ = t_expr(node.cond if node.cond is not None else node.left or node.right)  # type: ignore[arg-type]
            for s in node.body or []:
                walk_stmt(s)
            for s in node.else_body or []:
                walk_stmt(s)
            return
        if isinstance(node, AST.While):
            _ = t_expr(node.cond)
            for s in node.body:
                walk_stmt(s)
            return
        if isinstance(node, AST.Repeat):
            _ = t_expr(node.count_expr)
            for s in node.body:
                walk_stmt(s)
            return
        if isinstance(node, AST.TryCatch):
            for s in node.body:
                walk_stmt(s)
            for s in node.catch_body or []:
                walk_stmt(s)
            for s in node.finally_body or []:
                walk_stmt(s)
            return
        if isinstance(node, AST.Return):
            if node.expr is not None:
                _ = t_expr(node.expr)
            return
        if isinstance(node, (AST.Import, AST.FromImport, AST.Ask, AST.Push, AST.Pop, AST.GetKey, AST.SetKey, AST.DeleteKey)):
            return

    for s in program.statements:
        walk_stmt(s)
    return errors


