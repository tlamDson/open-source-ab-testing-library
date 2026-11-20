"""The repository name is open-source-statistical-experimentation-library (renamed 2026-11-20)."""

import tomllib

from abkit import paths

NEW_SLUG = "tlamDson/open-source-statistical-experimentation-library"
#: Built from parts so this file does not contain the old slug itself.
OLD_NAME = "open-source-" + "ab-testing-library"
TEXT_SUFFIXES = {".md", ".toml", ".yml", ".yaml", ".py", ".cfg", ".txt", ".json"}
SKIP_DIRS = {".git", "golden", ".venv", "node_modules", "site", "__pycache__"}


def _text_files():
    for path in paths.REPO_ROOT.rglob("*"):
        rel = path.relative_to(paths.REPO_ROOT)
        if any(part in SKIP_DIRS or part.endswith(".egg-info") for part in rel.parts):
            continue
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            yield path


def test_readme_title_is_the_new_name_and_names_the_package_right_under_it():
    lines = [line for line in paths.README.read_text(encoding="utf-8").splitlines() if line]
    assert lines[0] == "# Open-Source Statistical Experimentation Library"
    assert "abkit" in lines[1] and "abkit-experiments" in lines[1]
    text = paths.README.read_text(encoding="utf-8")
    assert "built inside [TravelPlan]" in text and "still uses it" in text


def test_project_urls_point_at_the_new_repository():
    urls = tomllib.loads((paths.REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]["urls"]
    assert urls["Source"] == f"https://github.com/{NEW_SLUG}"
    assert urls["Issues"] == f"https://github.com/{NEW_SLUG}/issues"
    assert urls["Documentation"] == f"https://github.com/{NEW_SLUG}/tree/main/docs"


def test_trusted_publisher_names_the_new_repository():
    text = (paths.DOCS_DIR / "release.md").read_text(encoding="utf-8")
    assert "repository `open-source-statistical-experimentation-library`" in text


def test_docs_site_name_is_the_new_name():
    text = (paths.REPO_ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    assert "site_name: Open-Source Statistical Experimentation Library" in text


def test_no_file_outside_golden_names_the_old_repository():
    stale = [
        str(p.relative_to(paths.REPO_ROOT))
        for p in _text_files()
        if OLD_NAME in p.read_text(encoding="utf-8", errors="ignore")
    ]
    assert stale == []
