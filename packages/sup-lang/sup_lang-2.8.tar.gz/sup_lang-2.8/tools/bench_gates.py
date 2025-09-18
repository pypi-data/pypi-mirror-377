from __future__ import annotations

import json
import sys
from typing import Dict

from sup.tools.benchmarks import run_case, CASES


def main() -> int:
    # Define budgets (in seconds) per case median
    budgets: Dict[str, float] = {
        "arith_loop": 0.05,
        "json_io": 0.05,
    }
    failures: Dict[str, float] = {}
    for name, code in CASES:
        res = run_case(name, code, warmup=1, iters=5)
        if name in budgets and res["median"] > budgets[name]:
            failures[name] = res["median"]
    if failures:
        print("Performance regressions detected:")
        for n, v in failures.items():
            print(f"  {n}: median {v:.6f}s > budget {budgets[n]:.6f}s")
        return 1
    print("Performance within budgets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


