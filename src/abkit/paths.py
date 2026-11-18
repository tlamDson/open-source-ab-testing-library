"""Every repository path abkit reads or writes by default, in one place.

In a checkout (``pip install -e .``) the root is the directory that holds ``src/abkit``.
An installed package has no repository around it: set ``ABKIT_ROOT`` to a checkout (or to
any directory with the same ``golden``, ``data``, ``runs`` and ``fixtures`` layout).
The variable is read once, at import.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

ROOT_ENV = "ABKIT_ROOT"
#: The ``abkit`` package directory (the code itself, never overridden).
PACKAGE_DIR = Path(__file__).resolve().parent
#: ``<root>/src/abkit/paths.py`` -> ``<root>``.
_CHECKOUT_ROOT = PACKAGE_DIR.parents[1]


def repo_root(environ: Mapping[str, str] | None = None) -> Path:
    """``ABKIT_ROOT`` when set and non-empty, else the checkout that holds this package."""
    value = (os.environ if environ is None else environ).get(ROOT_ENV, "")
    return Path(value).resolve() if value else _CHECKOUT_ROOT


REPO_ROOT = repo_root()

README = REPO_ROOT / "README.md"
DOCS_DIR = REPO_ROOT / "docs"

GOLDEN_DIR = REPO_ROOT / "golden"
#: The latest golden dataset version (v1 is kept for comparison).
GOLDEN_LATEST = GOLDEN_DIR / "v2"
#: The blinded decision-labeling export.
DECIDE_DIR = GOLDEN_DIR / "decide/v1"

DATA_DIR = REPO_ROOT / "data"
ACTIONS_PANEL_DIR = DATA_DIR / "actions_panel"

RUNS_DIR = REPO_ROOT / "runs"
RUNS_CSV = RUNS_DIR / "runs.csv"

FIXTURES_DIR = REPO_ROOT / "fixtures"
#: 10,000 pinned assignment results shared with the TypeScript implementation.
ASSIGNMENT_VECTORS = FIXTURES_DIR / "assignment-vectors.json"
