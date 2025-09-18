## Contributing

Thank you for contributing to SUP! Please:

- Use `pre-commit` hooks (Black, Ruff, Isort, Pyupgrade, MyPy where applicable)
- Write tests (pytest + Hypothesis) and keep coverage healthy
- Include clear commit messages and small focused PRs
- Discuss larger changes via an RFC (see RFCs section)

### Deprecation policy and RFCs

- Follow the Versioning and Stability policy in `versioning.md`.
- Any language removal or breaking change requires an RFC with:
  - Problem statement, alternatives considered, migration path
  - Deprecation horizon (≥1 MINOR), lint hint or auto-fix if feasible
  - Impact on tooling (LSP/formatter/transpiler) and ecosystem
- Deprecations must be surfaced in diagnostics and docs; removals only in next MAJOR.

Setup:

```bash
pip install -r requirements-dev.txt  # or use pipx/venv
pre-commit install
pytest -q
```


