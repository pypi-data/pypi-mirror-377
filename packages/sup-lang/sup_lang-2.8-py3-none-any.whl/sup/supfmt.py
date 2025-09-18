from __future__ import annotations

import argparse
from typing import Iterable


def _trim_trailing_whitespace(lines: Iterable[str]) -> list[str]:
    return [line.rstrip() for line in lines]


def _collapse_consecutive_blank_lines(lines: Iterable[str]) -> list[str]:
    formatted: list[str] = []
    blank_streak = 0
    for line in lines:
        if line == "":
            blank_streak += 1
            if blank_streak <= 1:
                formatted.append(line)
        else:
            blank_streak = 0
            formatted.append(line)
    return formatted


def format_text(source: str) -> str:
    # Keep original line endings normalization to "\n" and ensure trailing newline
    raw_lines = source.splitlines()
    lines = _trim_trailing_whitespace(raw_lines)
    lines = _collapse_consecutive_blank_lines(lines)
    text = "\n".join(lines)
    if not text.endswith("\n"):
        text += "\n"
    return text


def main() -> int:
    parser = argparse.ArgumentParser(prog="supfmt", description="Format SUP source files")
    parser.add_argument("paths", nargs="+", help=".sup files to format")
    parser.add_argument("--check", action="store_true", help="Only check if files would change")
    parser.add_argument("--write", action="store_true", help="Write changes to files in place")
    args = parser.parse_args()

    changed = False
    for p in args.paths:
        with open(p, "r", encoding="utf-8") as f:
            src = f.read()
        out = format_text(src)
        if out != src:
            changed = True
            if args.write:
                with open(p, "w", encoding="utf-8", newline="\n") as f:
                    f.write(out)
    if args.check and changed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


