from __future__ import annotations

from typing import Dict

from sup.tools.benchmarks import CASES, run_case


def main() -> int:
    budgets: Dict[str, float] = {
        "arith_loop": 0.20,
        "fib_recursive": 0.80,
        "list_map_ops": 0.15,
        "json_stringify": 0.05,
    }
    failures: Dict[str, float] = {}
    for name, code in CASES.items():
        res = run_case(code, warmup=1, iters=5)
        if name in budgets and res.get("median", 0.0) > budgets[name]:
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


