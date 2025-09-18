from __future__ import annotations

"""
Minimal WASM prototype emitter for a tiny SUP subset.

Emits a .wat (WASM text) module with one exported function `main` that returns a constant
or simple arithmetic on two constants. This is a scaffold to be expanded.
"""

from typing import Tuple


def emit_constant_module(value: int | float) -> str:
    if isinstance(value, int):
        return f"""(module
  (func $main (result i32)
    i32.const {int(value)}
  )
  (export "main" (func $main))
)"""
    else:
        return f"""(module
  (func $main (result f64)
    f64.const {float(value)}
  )
  (export "main" (func $main))
)"""


def emit_add_module(a: int | float, b: int | float) -> Tuple[str, str]:
    if isinstance(a, float) or isinstance(b, float):
        wat = f"""(module
  (func $main (result f64)
    f64.const {float(a)}
    f64.const {float(b)}
    f64.add
  )
  (export \"main\" (func $main))
)"""
        result_type = "f64"
    else:
        wat = f"""(module
  (func $main (result i32)
    i32.const {int(a)}
    i32.const {int(b)}
    i32.add
  )
  (export \"main\" (func $main))
)"""
        result_type = "i32"
    return wat, result_type


