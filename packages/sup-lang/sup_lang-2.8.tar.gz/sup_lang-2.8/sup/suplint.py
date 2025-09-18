from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Iterable


@dataclass
class Diagnostic:
    path: str
    line: int
    column: int
    code: str
    message: str


def _iter_lines(source: str) -> Iterable[tuple[int, str]]:
    for idx, line in enumerate(source.splitlines(), start=1):
        yield idx, line


def lint_text(path: str, source: str) -> list[Diagnostic]:
    diags: list[Diagnostic] = []
    # Rule SUP001: tabs are not allowed (use spaces)
    for ln, text in _iter_lines(source):
        if "\t" in text:
            diags.append(Diagnostic(path, ln, text.find("\t") + 1, "SUP001", "Tab character found; use spaces"))
    # Rule SUP002: Windows CRLF discouraged inside repo (normalize)
    if "\r\n" in source:
        # report at first line
        diags.append(Diagnostic(path, 1, 1, "SUP002", "Use LF line endings"))
    # Rule SUP003: ensure program starts with 'sup' and ends with 'bye'
    stripped = [line.strip() for line in source.splitlines() if line.strip() and not line.strip().lower().startswith("note")]
    if stripped:
        if stripped[0].lower() != "sup":
            diags.append(Diagnostic(path, 1, 1, "SUP003", "Program should start with 'sup'"))
        if stripped[-1].lower() != "bye":
            diags.append(Diagnostic(path, max(1, source.count("\n")), 1, "SUP003", "Program should end with 'bye'"))
    return diags


def main() -> int:
    parser = argparse.ArgumentParser(prog="suplint", description="Lint SUP source files")
    parser.add_argument("paths", nargs="+", help=".sup files to lint")
    args = parser.parse_args()

    had_errors = False
    for p in args.paths:
        with open(p, "r", encoding="utf-8") as f:
            src = f.read()
        diags = lint_text(p, src)
        for d in diags:
            print(f"{d.path}:{d.line}:{d.column}: {d.code} {d.message}")
        had_errors = had_errors or bool(diags)
    return 1 if had_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())


