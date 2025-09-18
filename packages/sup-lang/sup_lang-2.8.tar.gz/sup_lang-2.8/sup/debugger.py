from __future__ import annotations

from typing import Optional, Set

from . import ast as AST
from .interpreter import Interpreter


class Debugger:
    def __init__(self, program: AST.Program, source: str) -> None:
        self.program = program
        self.source_lines = source.splitlines()
        self.breakpoints: Set[int] = set()
        self.cond_breaks: dict[int, str] = {}
        self.watch: dict[str, object] = {}
        self.current_node: Optional[AST.Node] = None
        self.current_depth: int = 0
        self.pause: bool = False
        self.step_mode: str = "continue"  # continue | step | next
        self.next_base_depth: int = 0
        self.interp = Interpreter()
        self.snapshots: list[tuple[int | None, dict[str, object], object | None]] = []

        # Attach hooks
        # Attach hooks if interpreter supports them (optional)
        try:
            setattr(self.interp, "on_node_start", self._on_node_start)
            setattr(self.interp, "on_node_end", self._on_node_end)
        except Exception:
            pass

    # Hooks
    def _on_node_start(self, node: AST.Node) -> None:
        self.current_depth += 1
        self.current_node = node
        line = getattr(node, "line", None)
        # take lightweight snapshot (line, env copy, last_result)
        try:
            self.snapshots.append((line, dict(self.interp.env), self.interp.last_result))
        except Exception:
            pass
        should_break = False
        if isinstance(line, int) and line in self.breakpoints:
            expr = self.cond_breaks.get(line)
            if expr:
                try:
                    val = self.interp.env.get(expr.lower())
                    should_break = bool(val)
                except Exception:
                    should_break = True
            else:
                should_break = True
        if self.step_mode == "step":
            should_break = True
        elif self.step_mode == "next" and self.current_depth <= self.next_base_depth:
            should_break = True
        if should_break:
            self.pause = True
            self._interactive()

    def _on_node_end(self, node: AST.Node) -> None:
        # Balance depth
        if self.current_depth > 0:
            self.current_depth -= 1

    # REPL
    def _interactive(self) -> None:
        while self.pause:
            where = self._format_where()
            print(where)
            try:
                cmd = input("dbg> ").strip()
            except EOFError:
                cmd = "c"
            if not cmd:
                continue
            op, *rest = cmd.split()
            if op in {"c", "cont", "continue"}:
                self.step_mode = "continue"
                self.pause = False
            elif op in {"s", "step"}:
                self.step_mode = "step"
                self.pause = False
            elif op in {"n", "next"}:
                self.step_mode = "next"
                self.next_base_depth = self.current_depth
                self.pause = False
            elif op in {"b", "break"}:
                if rest and rest[0].isdigit():
                    ln = int(rest[0])
                    self.breakpoints.add(ln)
                    print(f"Breakpoint set at {ln}")
                else:
                    print("Usage: b <line>")
            elif op in {"p", "print"}:
                if not rest:
                    print("Usage: p <name>")
                    continue
                name = rest[0].lower()
                val = None
                if name == "result":
                    val = self.interp.last_result
                else:
                    val = self.interp.env.get(name)
                print(val)
            elif op in {"w", "watch"}:
                if not rest:
                    print("Usage: watch <name>")
                    continue
                self.watch[rest[0].lower()] = None
                print(f"Watching {rest[0]}")
            elif op in {"bw", "breakif"}:
                if len(rest) >= 2 and rest[0].isdigit():
                    ln = int(rest[0])
                    self.breakpoints.add(ln)
                    self.cond_breaks[ln] = rest[1]
                    print(f"Conditional breakpoint set at {ln} if {rest[1]}")
                else:
                    print("Usage: breakif <line> <name>")
            elif op in {"l", "list"}:
                # list current line context
                self._list_context()
            elif op in {"t", "time"}:
                # time travel: show snapshots and jump
                print(f"{len(self.snapshots)} snapshots recorded. Use 'jump <index>' to restore.")
            elif op in {"j", "jump"}:
                if not rest or not rest[0].isdigit():
                    print("Usage: jump <index>")
                else:
                    idx = int(rest[0])
                    if 0 <= idx < len(self.snapshots):
                        _, env, last = self.snapshots[idx]
                        try:
                            self.interp.env = dict(env)
                            self.interp.last_result = last
                            print(f"Restored snapshot {idx}.")
                        except Exception as e:
                            print(f"Failed to restore: {e}")
                    else:
                        print("Invalid snapshot index")
            elif op in {"q", "quit"}:
                raise SystemExit(0)
            else:
                print("Commands: c(continue), s(step), n(next), b <line>, breakif <line> <name>, p <name>, w <name>, l(list), t(time), j(jump) <i>, q(quit)")

    def _format_where(self) -> str:
        line = getattr(self.current_node, "line", None)
        if isinstance(line, int) and 1 <= line <= len(self.source_lines):
            base = f"Line {line}: {self.source_lines[line - 1]}"
            if self.watch:
                pairs = []
                for k in list(self.watch.keys()):
                    pairs.append(f"{k}={self.interp.env.get(k)}")
                return base + "\nwatch: " + ", ".join(pairs)
            return base
        return "Line ?"

    def _list_context(self, span: int = 3) -> None:
        line = getattr(self.current_node, "line", None)
        if not isinstance(line, int):
            print("<no location>")
            return
        start = max(1, line - span)
        end = min(len(self.source_lines), line + span)
        for ln in range(start, end + 1):
            prefix = "=>" if ln == line else "  "
            print(f"{prefix} {ln:4d}  {self.source_lines[ln - 1]}")

    def run(self) -> None:
        # Start with step mode to stop on first statement
        self.step_mode = "step"
        self.pause = False
        self.interp.run(self.program)


