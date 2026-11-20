"""The golden gate is wired into CI: required job (fast) and nightly (full), B2 plan PR 15a."""

import re

from conftest import REPO_ROOT

WORKFLOWS = REPO_ROOT / ".github/workflows"
CI = WORKFLOWS / "ci.yml"
NIGHTLY = WORKFLOWS / "golden-nightly.yml"
REQUIRED_JOB = "Lint + Test"
BADGE = (
    "[![CI](https://github.com/tlamDson/open-source-statistical-experimentation-library"
    "/actions/workflows/ci.yml/badge.svg?branch=develop)]"
)


def _job_block(text: str, name: str) -> str:
    """Lines of the job whose ``name:`` is ``name``, up to the next top-level job."""
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == f"name: {name}")
    end = next(
        (j for j in range(start + 1, len(lines)) if re.match(r"^  [A-Za-z0-9_-]+:\s*$", lines[j])),
        len(lines),
    )
    return "\n".join(lines[start:end])


def _run_lines(block: str) -> list[str]:
    return [line.split("run:", 1)[1].strip() for line in block.splitlines() if "run:" in line]


def test_required_job_runs_the_fast_golden_gate_and_the_mutants() -> None:
    job = _job_block(CI.read_text(encoding="utf-8"), REQUIRED_JOB)
    runs = _run_lines(job)
    assert "python -m pytest -q" in runs
    assert "python -m abkit golden --subset ci-fast --strict" in runs  # G-ref + G-sim subset
    assert "python -m abkit gate" in runs  # 10 mutants must be blocked (M10)
    assert "|| " not in job and "continue-on-error" not in job
    assert "analytics/" not in job  # standalone layout: the package is the repository root


def test_nightly_workflow_runs_the_full_golden_dataset() -> None:
    text = NIGHTLY.read_text(encoding="utf-8")
    assert re.search(r"^\s+schedule:\s*$", text, re.M)
    assert re.search(r"^\s+- cron: \"[^\"]+\"", text, re.M)
    assert "workflow_dispatch:" in text
    runs = _run_lines(text)
    assert "python -m abkit golden --strict" in runs
    assert "python -m abkit gate --full" in runs
    assert "|| " not in text and "continue-on-error" not in text
    assert "analytics/" not in text
    # Not a required check: it must never borrow the required job's name.
    assert f"name: {REQUIRED_JOB}\n" not in text


def test_readme_shows_the_ci_badge() -> None:
    assert BADGE in (REPO_ROOT / "README.md").read_text(encoding="utf-8")
