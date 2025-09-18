from __future__ import annotations

import os
import pytest


@pytest.fixture(autouse=True, scope="session")
def enable_sup_caps_for_tests() -> None:
    """Ensure capabilities required by tests are enabled.

    Tests exercise filesystem writes, archiving, sqlite, subprocess, and
    networking. The interpreter is safe-by-default now, so enable these
    capabilities for the duration of the test session unless the user has
    explicitly set their own SUP_CAPS.
    """
    prev_caps = os.environ.get("SUP_CAPS")
    prev_unsafe = os.environ.get("SUP_UNSAFE")
    required = {"fs_write", "archive", "sql", "process", "net"}
    if prev_unsafe not in {"1", "true", "yes"}:
        existing = {c.strip() for c in (prev_caps or "").split(",") if c.strip()}
        combined = sorted(existing.union(required)) if existing else sorted(required)
        os.environ["SUP_CAPS"] = ",".join(combined)
    try:
        yield
    finally:
        if prev_caps is None:
            os.environ.pop("SUP_CAPS", None)
        else:
            os.environ["SUP_CAPS"] = prev_caps
        if prev_unsafe is None:
            os.environ.pop("SUP_UNSAFE", None)
        else:
            os.environ["SUP_UNSAFE"] = prev_unsafe


