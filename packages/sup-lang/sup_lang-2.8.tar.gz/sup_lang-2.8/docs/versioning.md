Versioning, Stability, and Releases
===================================

Versioning policy (v1.0 and beyond)
-----------------------------------
- Semantic Versioning (SemVer): MAJOR.MINOR.PATCH
  - Breaking language changes: MAJOR
  - Backward‑compatible features: MINOR
  - Bug fixes/perf improvements: PATCH
- Stability windows: no breaking changes within a MINOR line; deprecations are announced one MINOR ahead.
- Reserved words: additions allowed in MINOR only if they don’t collide with existing programs; otherwise MAJOR.
- Parser/AST compatibility: AST node shapes are stable within a MAJOR; new nodes are additive.

LTS releases
------------
- Designate select MINOR versions as LTS (e.g., 1.4, 2.6) supported for 12–18 months with backported fixes.
- Tooling (compiler/VM/LSP) keeps compatibility with LTS minor within its MAJOR.

Deprecations
------------
- Mark features as deprecated in docs and diagnostics; provide migration tips.
- Remove deprecations only on next MAJOR.
- Deprecation horizon: minimum one MINOR cycle, preferred two.

Migration policy
----------------
- Each deprecation entry includes: affected syntax/API, replacement, examples, and an automated lint fix if feasible.
- Provide a `--migrate` tool (future) to rewrite common patterns; changelog links to guides.
 - RFC needed for language removals; include risk & ecosystem impact.

Release cadence
---------------
- Regular MINOR releases (4–8 weeks), PATCH as needed.
- RC tags for release candidates; issue a changelog with migration notes.

Stability guarantees summary
----------------------------
- Language grammar/semantics: stable within MAJOR; see spec for details.
- Tooling (CLI/LSP/formatter): config flags may grow; defaults won’t break existing behavior within MINOR.
- Stdlib: additive within MINOR; capability requirements documented and stable.


