WASM and C-ABI Plan
====================

Scope
-----
- Define a minimal portable C-ABI for SUP runtime embedding
- Provide a WASM host functions surface for stdlib (fs/net disabled by default)
- Prototype a transpiler path from a strict SUP subset to WASM via Python (wasmtime/wasmer)

C-ABI (embedding)
-----------------
- Entry points:
  - sup_init(const sup_config* cfg)
  - sup_eval(const char* source, sup_result* out)
  - sup_free(sup_result*)
- Callbacks for IO and clock provided via function pointers in sup_config
- Memory: host-allocated; results returned as (ptr,len) with ownership flags

WASM host functions
-------------------
- env.now() -> string
- env.random_bytes(n) -> bytes
- json.parse/stringify
- string ops (upper/lower/length)
- Disabled by default: fs, net, process; enable via capabilities map at instantiation

Prototype plan
--------------
1) Define a tiny SSA-like intermediate (expressions, variables, blocks)
2) Lower SUP subset (numbers/strings, arithmetic, conditionals, while, functions) to SSA
3) Emit WASM text (wat) or use wasm module builder
4) Execute via wasmtime and map host functions

Security model
--------------
- No syscalls by default; only explicitly injected host funcs
- Deterministic mode toggles time/random providers

Timeline
--------
- Week 1: design + minimal host surface + run a constant function
- Week 2: arithmetic + if/while + functions + return
- Week 3: variables and simple closures (env capture via structs)
- Week 4: MVP docs and example


