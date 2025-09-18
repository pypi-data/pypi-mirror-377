from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict, Tuple

from sup.parser import Parser  # type: ignore
from sup.interpreter import Interpreter


def profile_source(source: str) -> Dict[int, Tuple[int, float]]:
    parser = Parser()
    program = parser.parse(source)
    interp = Interpreter()

    counts: Dict[int, int] = defaultdict(int)
    times: Dict[int, float] = defaultdict(float)
    t0 = 0.0
    current_line = None

    def on_start(node):  # type: ignore[no-redef]
        nonlocal t0, current_line
        current_line = getattr(node, "line", None)
        t0 = time.perf_counter()

    def on_end(node):  # type: ignore[no-redef]
        nonlocal t0, current_line
        if isinstance(current_line, int):
            counts[current_line] += 1
            times[current_line] += time.perf_counter() - t0
        current_line = None

    interp.on_node_start = on_start  # type: ignore[assignment]
    interp.on_node_end = on_end  # type: ignore[assignment]
    interp.run(program)
    return {ln: (counts[ln], times[ln]) for ln in sorted(counts)}


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Profile a SUP file")
    ap.add_argument("file", help="Path to .sup file")
    args = ap.parse_args()
    src = open(args.file, encoding="utf-8").read()
    stats = profile_source(src)
    for ln, (cnt, tm) in stats.items():
        print(f"{ln:5d}  count={cnt:6d}  time={tm*1000:.3f}ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


