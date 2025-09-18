from __future__ import annotations

import argparse
import time
import statistics as stats

from sup.cli import run_source


CASES: dict[str, str] = {
    "arith_loop": (
        "sup\n"
        "set total to 0\n"
        "repeat 20000 times\n"
        "set total to add total and 3\n"
        "endrepeat\n"
        "print the result\n"
        "bye\n"
    ),
    "fib_recursive": (
        "sup\n"
        "define function called fib with n\n"
        "  if n is less than 2 then\n"
        "    return n\n"
        "  end if\n"
        "  return add call fib with subtract 1 from n and call fib with subtract 2 from n\n"
        "end function\n"
        "print call fib with 18\n"
        "bye\n"
    ),
    "list_map_ops": (
        "sup\n"
        "make list of 1, 2, 3, 4, 5\n"
        "repeat 1000 times\n"
        "  push 6 to list\n"
        "  pop from list\n"
        "endrepeat\n"
        "make map\n"
        "set \"k\" to 42 in map\n"
        "print get \"k\" from map\n"
        "bye\n"
    ),
    "json_stringify": (
        "sup\n"
        "set s to json stringify of make map\n"
        "print s\n"
        "bye\n"
    ),
}


def run_case(code: str, warmup: int, iters: int) -> dict[str, float]:
    for _ in range(max(0, warmup)):
        run_source(code)
    times: list[float] = []
    for _ in range(max(1, iters)):
        t0 = time.perf_counter()
        run_source(code)
        times.append(time.perf_counter() - t0)
    return {
        "min": min(times),
        "median": stats.median(times),
        "mean": stats.mean(times),
        "max": max(times),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Run SUP language benchmarks")
    ap.add_argument("--case", action="append", help="Benchmark case(s) to run", choices=sorted(CASES.keys()))
    ap.add_argument("--warmup", type=int, default=2)
    ap.add_argument("--iters", type=int, default=5)
    args = ap.parse_args()

    selected = args.case or sorted(CASES.keys())
    print("name,min,median,mean,max")
    for name in selected:
        metrics = run_case(CASES[name], args.warmup, args.iters)
        print(f"{name},{metrics['min']:.6f},{metrics['median']:.6f},{metrics['mean']:.6f},{metrics['max']:.6f}")


if __name__ == "__main__":
    main()


