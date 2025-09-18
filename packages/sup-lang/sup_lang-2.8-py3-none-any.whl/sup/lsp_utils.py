from __future__ import annotations

import re
from typing import Dict, List, Tuple

from .parser import Parser, AST  # type: ignore


def compute_line_starts(text: str) -> List[int]:
    starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            starts.append(i + 1)
    return starts


def position_to_offset(text: str, line: int, character: int) -> int:
    starts = compute_line_starts(text)
    if line < 0:
        return 0
    if line >= len(starts):
        return len(text)
    line_start = starts[line]
    return min(len(text), line_start + max(0, character))


def offset_to_position(text: str, offset: int) -> Tuple[int, int]:
    starts = compute_line_starts(text)
    if offset < 0:
        offset = 0
    if offset > len(text):
        offset = len(text)
    # binary search line
    lo, hi = 0, len(starts) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if starts[mid] <= offset:
            lo = mid + 1
        else:
            hi = mid - 1
    line = hi
    col = offset - starts[line]
    return line, col


def word_at(text: str, line: int, character: int) -> str:
    # Return alnum/underscore token under position
    offset = position_to_offset(text, line, character)
    if not text:
        return ""
    if offset >= len(text):
        offset = len(text) - 1
    # Expand to word boundaries
    left = offset
    while left > 0 and re.match(r"[A-Za-z0-9_.]", text[left - 1]):
        left -= 1
    right = offset
    while right < len(text) and re.match(r"[A-Za-z0-9_.]", text[right]):
        right += 1
    return text[left:right]


def build_index(uri: str, text: str) -> Dict[str, dict]:
    # Build a minimal index: function definitions map, positions
    index: Dict[str, dict] = {"functions": {}}
    parser = Parser()
    try:
        program = parser.parse(text)
    except Exception:
        return index
    lines = text.splitlines()
    for node in program.statements:
        if isinstance(node, AST.FunctionDef):
            name = node.name.lower()
            def_line = max(0, (node.line or 1) - 1)
            # best-effort column by searching function header line
            col = 0
            if 0 <= def_line < len(lines):
                header = lines[def_line]
                pos = header.lower().find(name)
                if pos >= 0:
                    col = pos
            index["functions"][name] = {
                "params": [p.lower() for p in node.params],
                "def": {
                    "uri": uri,
                    "line": def_line,
                    "character": col,
                },
            }
    return index


BUILTIN_DOCS: Dict[str, str] = {
    "add": "add A and B",
    "subtract": "subtract A and B | subtract A from B",
    "multiply": "multiply A and B",
    "divide": "divide A by B",
    "upper": "upper of S",
    "lower": "lower of S",
    "concat": "concat of A and B",
    "power": "power of A and B",
    "sqrt": "sqrt of A",
    "abs": "absolute of A",
    "min": "min of A and B",
    "max": "max of A and B",
    "floor": "floor of A",
    "ceil": "ceil of A",
    "trim": "trim of S",
    "contains": "contains of A and B",
    "join": "join of SEP and LIST",
    "read_file": "read file of PATH",
    "write_file": "write file of PATH and DATA",
    "json_parse": "json parse of S",
    "json_stringify": "json stringify of V",
}


KEYWORDS: List[str] = [
    "sup",
    "bye",
    "define",
    "function",
    "called",
    "with",
    "return",
    "end function",
    "print",
    "if",
    "then",
    "else",
    "end if",
    "repeat",
    "times",
    "end repeat",
    "while",
    "end while",
    "for each",
    "in",
    "end for",
    "make list",
    "make map",
    "call",
]


