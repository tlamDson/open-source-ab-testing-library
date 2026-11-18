"""Every repository path comes from ``abkit.paths`` (standalone layout, ABKIT_ROOT override)."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from abkit import paths

#: This file is ``<repo>/tests/test_paths.py``.
CHECKOUT = Path(__file__).resolve().parents[1]
SRC = CHECKOUT / "src/abkit"

#: (constant, path relative to the repository root, kind) for every repository path.
LAYOUT = (
    ("GOLDEN_DIR", "golden", "dir"),
    ("GOLDEN_LATEST", "golden/v2", "dir"),
    ("DECIDE_DIR", "golden/decide/v1", "dir"),
    ("DATA_DIR", "data", "dir"),
    ("ACTIONS_PANEL_DIR", "data/actions_panel", "dir"),
    ("RUNS_DIR", "runs", "dir"),
    ("RUNS_CSV", "runs/runs.csv", "file"),
    ("FIXTURES_DIR", "fixtures", "dir"),
    ("ASSIGNMENT_VECTORS", "fixtures/assignment-vectors.json", "file"),
    ("README", "README.md", "file"),
    ("DOCS_DIR", "docs", "dir"),
)


@pytest.fixture
def no_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(paths.ROOT_ENV, raising=False)


def test_the_override_variable_is_abkit_root() -> None:
    assert paths.ROOT_ENV == "ABKIT_ROOT"


@pytest.mark.usefixtures("no_override")
def test_without_override_the_root_is_the_checkout_holding_src() -> None:
    assert paths.repo_root() == CHECKOUT
    assert paths.REPO_ROOT == CHECKOUT
    assert (paths.REPO_ROOT / "pyproject.toml").is_file()


@pytest.mark.parametrize(("name", "rel", "kind"), LAYOUT, ids=[row[0] for row in LAYOUT])
def test_each_repository_path_is_committed_at_the_standalone_location(
    name: str, rel: str, kind: str
) -> None:
    path = getattr(paths, name)
    assert path == paths.REPO_ROOT / rel
    assert path.is_dir() if kind == "dir" else path.is_file(), path


def test_package_dir_is_the_imported_package() -> None:
    import abkit

    assert Path(abkit.__file__).resolve().parent == paths.PACKAGE_DIR


def test_abkit_root_overrides_the_root(tmp_path: Path) -> None:
    assert paths.repo_root({paths.ROOT_ENV: str(tmp_path)}) == tmp_path.resolve()


def test_an_empty_override_is_ignored() -> None:
    assert paths.repo_root({paths.ROOT_ENV: ""}) == CHECKOUT
    assert paths.repo_root({}) == CHECKOUT


def test_a_relative_override_is_made_absolute(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "data-root").mkdir()
    monkeypatch.chdir(tmp_path)
    assert paths.repo_root({paths.ROOT_ENV: "data-root"}) == (tmp_path / "data-root").resolve()


def test_every_constant_follows_abkit_root_at_import(tmp_path: Path) -> None:
    names = [row[0] for row in LAYOUT]
    probe = (
        "import json, sys\n"
        "from abkit import paths\n"
        f"print(json.dumps({{n: str(getattr(paths, n)) for n in {names!r}}}))\n"
    )
    env = {**os.environ, paths.ROOT_ENV: str(tmp_path)}
    proc = subprocess.run(
        [sys.executable, "-c", probe], capture_output=True, text=True, env=env, timeout=60
    )
    assert proc.returncode == 0, proc.stderr
    got = json.loads(proc.stdout)
    for name, rel, _ in LAYOUT:
        assert Path(got[name]) == tmp_path.resolve() / rel, name


def test_module_defaults_come_from_paths() -> None:
    from abkit import assignment, cli, readme_results, runs
    from abkit.actions import cli as actions_cli
    from abkit.causal import m6
    from abkit.golden import freeze_criteo, freeze_lalonde, freeze_public, freeze_ref, mutants
    from abkit.labeling import cli as labeling_cli
    from abkit.labeling import export

    assert runs.RUNS_CSV_PATH == paths.RUNS_CSV
    assert assignment.VECTORS_PATH == paths.ASSIGNMENT_VECTORS
    assert actions_cli.ACTIONS_PANEL_DIR == paths.ACTIONS_PANEL_DIR
    assert cli.DEFAULT_GOLDEN_ROOT == paths.GOLDEN_LATEST
    assert m6.GOLDEN_ROOT == paths.GOLDEN_LATEST
    for freezer in (freeze_criteo, freeze_lalonde, freeze_public, freeze_ref):
        assert freezer.DEFAULT_ROOT == paths.GOLDEN_LATEST, freezer.__name__
    assert labeling_cli.GOLDEN_LATEST == paths.GOLDEN_LATEST
    assert export.DECIDE_ROOT == paths.DECIDE_DIR
    assert readme_results.DEFAULT_FILES == (paths.README, paths.DOCS_DIR / "results.md")
    assert mutants.PACKAGE_DIR == paths.PACKAGE_DIR


def test_only_the_paths_module_locates_files_from_its_own_location() -> None:
    offenders = [
        str(p.relative_to(SRC))
        for p in SRC.rglob("*.py")
        if p.name != "paths.py" and re.search(r"Path\(__file__\)|\.parents\[", p.read_text("utf-8"))
    ]
    assert offenders == []


def test_no_module_or_test_names_the_travelplan_layout() -> None:
    old = re.compile(r"analytics/(abkit|golden|runs|data)|packages/shared")
    offenders = [
        str(p.relative_to(CHECKOUT))
        for root in (SRC, CHECKOUT / "tests")
        for p in root.rglob("*.py")
        if p.name != "test_paths.py" and old.search(p.read_text("utf-8"))
    ]
    assert offenders == []
