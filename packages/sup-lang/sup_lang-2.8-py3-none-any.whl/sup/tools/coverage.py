from __future__ import annotations

from typing import Set

from sup.parser import Parser  # type: ignore
from sup.interpreter import Interpreter


def cover_source(source: str) -> Set[int]:
    parser = Parser()
    program = parser.parse(source)
    interp = Interpreter()
    covered: Set[int] = set()

    def on_start(node):  # type: ignore[no-redef]
        ln = getattr(node, "line", None)
        if isinstance(ln, int):
            covered.add(ln)

    interp.on_node_start = on_start  # type: ignore[assignment]
    interp.run(program)
    return covered


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Report statement coverage for a SUP file")
    ap.add_argument("file", help="Path to .sup file")
    args = ap.parse_args()
    src = open(args.file, encoding="utf-8").read()
    covered = cover_source(src)
    for ln in sorted(covered):
        print(ln)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


