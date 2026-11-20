# Changelog

## 0.2.0 - 2026-11-20

- The library now lives in its own repository,
  [open-source-statistical-experimentation-library](https://github.com/tlamDson/open-source-statistical-experimentation-library),
  split out of the TravelPlan monorepo (`analytics/abkit`) with its git history.
- The public API is unchanged: the import name stays `abkit` and the PyPI distribution stays
  `abkit-experiments`.
- Releases are tagged `v<version>` (was `abkit-v<version>`) and published by
  `.github/workflows/release.yml` through PyPI Trusted Publishing.
- `[project.urls]` point at the new repository.

## 0.1.0

- First version, in the TravelPlan monorepo (`analytics/abkit`).
