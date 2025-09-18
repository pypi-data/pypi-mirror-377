from __future__ import annotations

import json
import os
from typing import Dict, Tuple, Optional


_VLQ_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
_VLQ_VALUES = {c: i for i, c in enumerate(_VLQ_CHARS)}


def _from_vlq_signed(v: int) -> int:
    is_neg = v & 1
    v >>= 1
    return -v if is_neg else v


def _decode_vlq(segment: str, pos: int) -> Tuple[int, int]:
    result = 0
    shift = 0
    while pos < len(segment):
        c = segment[pos]
        pos += 1
        val = _VLQ_VALUES.get(c, 0)
        continuation = val & 32
        digit = val & 31
        result += digit << shift
        shift += 5
        if not continuation:
            break
    return _from_vlq_signed(result), pos


def load_line_map(map_path: str) -> Optional[Dict[int, Tuple[str, int]]]:
    if not os.path.exists(map_path):
        return None
    try:
        data = json.load(open(map_path, encoding="utf-8"))
    except Exception:
        return None
    sources = data.get("sources") or []
    src_name = sources[0] if sources else ""
    mappings = data.get("mappings", "")
    lines = mappings.split(";")
    last_gen_col = 0
    last_src_idx = 0
    last_orig_line = 0
    last_orig_col = 0
    result: Dict[int, Tuple[str, int]] = {}
    for i, segs in enumerate(lines, start=1):
        if not segs:
            last_gen_col = 0
            continue
        # take first segment only (first mapping in the line)
        pos = 0
        try:
            gen_col_delta, pos = _decode_vlq(segs, pos)
            src_idx_delta, pos = _decode_vlq(segs, pos)
            orig_line_delta, pos = _decode_vlq(segs, pos)
            orig_col_delta, pos = _decode_vlq(segs, pos)
        except Exception:
            last_gen_col = 0
            continue
        last_gen_col += gen_col_delta
        last_src_idx += src_idx_delta
        last_orig_line += orig_line_delta
        last_orig_col += orig_col_delta
        result[i] = (src_name, last_orig_line + 1)
        last_gen_col = 0
        last_src_idx = 0
    return result


def map_frame(py_file: str, py_line: int) -> Optional[Tuple[str, int]]:
    map_path = py_file + ".map"
    if not os.path.exists(map_path):
        # also try same dir with basename.map
        base = os.path.basename(py_file)
        alt = os.path.join(os.path.dirname(py_file), base + ".map")
        map_path = alt
    line_map = load_line_map(map_path)
    if not line_map:
        return None
    entry = line_map.get(py_line)
    return entry


def remap_exception(e: BaseException) -> str:
    tb = e.__traceback__
    frames = []
    while tb is not None:
        frame = tb.tb_frame
        lineno = tb.tb_lineno
        filename = frame.f_code.co_filename
        frames.append((filename, lineno))
        tb = tb.tb_next
    # Map deepest-first frame with an available map; try all frames for best effort.
    # If multiple frames map, prefer the one whose source file ends with .sup
    best: Optional[Tuple[str, int]] = None
    for filename, lineno in reversed(frames):
        m = map_frame(filename, lineno)
        if m:
            if best is None:
                best = m
            else:
                # prefer .sup sources
                if (not best[0].endswith('.sup')) and m[0].endswith('.sup'):
                    best = m
    if best is not None:
        src_name, src_line = best
        if not src_name.endswith(".sup"):
            src_name = src_name + ".sup"
        return f"{type(e).__name__}: {e} (at {src_name}:{src_line})"
    return f"{type(e).__name__}: {e}"


