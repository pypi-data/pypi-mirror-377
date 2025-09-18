Packaging and Project Commands
==============================

Scaffold
--------
```
sup init myapp
```
Creates `main.sup`, `sup.json`, and `README.md`.

Build (transpile project)
------------------------
```
sup build main.sup --out dist_sup
```
Produces Python modules and a `run.py` launcher. Sourcemaps are generated with `sourceMappingURL`.

Lockfile
--------
```
sup lock main.sup
```
Writes `sup.lock` containing module paths and SHA256 hashes for reproducible builds. New projects may also use `sup.lock.json` (v2) which includes module versions and sources.

Test runner
-----------
```
sup test tests/
```
Runs all `.sup` files in a directory and reports pass count (zero exit code when all pass).

Publish (source tarball)
------------------------
```
sup publish .
```
Creates `dist_sup/<name>-<version>.tar.gz` using metadata from `sup.json`.


Install from a local registry
-----------------------------
```
sup install mathlib --registry ./registry
```
Copies `./registry/mathlib.sup` into the current project and updates `sup.lock` (or `sup.lock.json`) with integrity info.

Lockfile format (v1)
--------------------
Lines of `name:sha256hex`. Example:
```
mathlib:7b1a5f...c9
```
`sup lock` regenerates it from parsed imports.

Lockfile format (v2 JSON)
-------------------------
```
{
  "version": 2,
  "modules": {
    "mathlib": {"version": "*", "sha256": "7b1a...", "source": "local"}
  }
}
```

HTTP registry (experimental)
----------------------------
- Install: `sup install name@1.2.3 --registry https://registry.example.com`
- Publish: `sup publish . --registry https://registry.example.com`
The registry API is expected to expose `/resolve?name=&version=` and `/upload` endpoints returning/accepting JSON.

Local demo registry
-------------------
Run the built-in demo server (serves modules from `REGISTRY_DIR`, default CWD):
```
set REGISTRY_DIR=./registry  # PowerShell: $env:REGISTRY_DIR = "./registry"
python -m sup.tools.registry_server
```
Then install from it:
```
sup install mathlib --registry http://127.0.0.1:8080
```


