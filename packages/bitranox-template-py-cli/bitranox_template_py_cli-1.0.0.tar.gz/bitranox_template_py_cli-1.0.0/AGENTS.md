# Repository Guidelines

## On session start

- Connect to the `systemprompts` MCP filesystem.
- Read following files and keep their guidance in working memory:
  - core_programming_solid.md
  - bash_clean_architecture.md
  - bash_clean_code.md
  - bash_small_functions.md
  - python_solid_architecture_enforcer.md
  - python_clean_architecture.md
  - python_clean_code.md
  - python_small_functions_style.md
  - python_libraries_to_use.md
  - python_structure_template.md
  - self_documenting.md


always apply those Rules :

- core_programming_solid.md

when writing or refracturing Bash scripts, apply those Rules :

- core_programming_solid.md
- bash_clean_architecture.md
- bash_clean_code.md
- bash_small_functions.md

when writing or refracturing Python scripts, apply those Rules :
- core_programming_solid.md
- python_solid_architecture_enforcer.md
- python_clean_architecture.md
- python_clean_code.md
- python_small_functions_style.md
- python_libraries_to_use.md
- python_lib_structure_template.md

## Project Structure & Module Organization

- `src/bitranox_template_py_cli/`: Python package exposing placeholders for Rich logging helpers.
- `scripts/`: shared automation (build/test/release) reused from scaffold.
- `packaging/`: Conda, Homebrew, and Nix specs kept in sync via scripts.
- `tests/`: placeholder suite skipping until logging features exist.

## Build, Test, and Development Commands

- `make help` — list all targets with one‑line docs.
- `make test` — run ruff (lint + format check), pyright, pytest with coverage (enabled by default), and upload to Codecov (if configured via `.env`).
  - Auto‑bootstrap: `make test` installs dev tools (`pip install -e .[dev]`) if linters/test deps are missing. Use `SKIP_BOOTSTRAP=1 make test` to disable.
  - Coverage control: `COVERAGE=on|auto|off` (default `on` locally). Uses a unique `COVERAGE_FILE` each run to avoid DB locks.
  - Before uploading to Codecov the harness creates an allow-empty commit (`test: auto commit before Codecov upload`) so the report attaches to a revision. Reset or amend if you do not want to keep it.
- `make build` — build Python wheel/sdist and attempt Conda/Homebrew/Nix builds (auto‑installs missing tools when needed).
- `make push` — runs the full `scripts/test.py` flow, prompts for/accepts a commit message (or `COMMIT_MESSAGE`), creates an allow-empty commit if needed, then pushes to the selected remote.
- `make clean` — remove caches, coverage, and build artifacts (includes `dist/` and `build/`).

### Versioning & Releases

- Single source of truth for the package version is `pyproject.toml` (`[project].version`).
- Runtime code reads metadata via `importlib.metadata`; do not duplicate the version in code files.
- On a version bump, update only `pyproject.toml` and the `CHANGELOG.md` entry; do not edit `src/bitranox_template_py_cli/__init__conf__.py` for versioning.
- Tag releases `vX.Y.Z` and push tags; CI will build artifacts and publish when configured.

### Common Make Targets (Alphabetical)


| Target            | One-line description                                                           |
|-------------------|--------------------------------------------------------------------------------|
| `build`           | Build wheel/sdist and attempt Conda/Brew/Nix builds (auto-installs tools).     |
| `bump`            | Bump version (VERSION=X.Y.Z or PART=major\|minor\|patch) and update changelog. |
| `bump-major`      | Increment major version ((X+1).0.0).                                           |
| `bump-minor`      | Increment minor version (X.Y.Z → X.(Y+1).0).                                   |
| `bump-patch`      | Increment patch version (X.Y.Z → X.Y.(Z+1)).                                   |
| `clean`           | Remove caches, coverage, and build artifacts (includes `dist/` and `build/`).  |
| `dev`             | Install package with dev extras.                                               |
| `help`            | Show this table.                                                               |
| `install`         | Editable install.                                                              |
| `menu`            | Interactive TUI menu (make menu).                                              |
| `push`            | Commit changes once and push to GitHub (no CI monitoring).                     |
| `release`         | Tag vX.Y.Z, push, sync packaging, run gh release if available.                 |
| `run`             | Run module entry (`python -m ... --help`).                                     |
| `test`            | Lint, format, type-check, run tests with coverage, upload to Codecov.          |
| `version-current` | Print current version from `pyproject.toml`.                                   |

## Coding Style & Naming Conventions

- Keep modules and functions snake_case.
- Prefer dataclasses for configuration objects (see `Config` in `bitranox_template_py_cli`).
- Rich renderables will live in dedicated helper modules once implemented.

## Testing Guidelines

- Unit and integration-style tests live under `tests/`; keep them up to date when adding features.
- Extend coverage for new CLI or library behaviour (the suite exercises CLI commands, package metadata, and automation scripts).
- When adding functionality, replace or remove placeholders and ensure `make test` remains green.

## Commit & Pull Request Guidelines

## Architecture Overview

Placeholder: logging pipeline will organize around Rich renderables managed by a configurable core module and optional CLI utilities.

## Security & Configuration Tips

- `.env` is only for local tooling (CodeCov tokens, etc.); do not commit secrets.
- Rich logging should sanitize payloads before rendering once implemented.

## Translations (Docs)

## Translations (App UI Strings)

## Changes in WEB Documentation

- when asked to update documentation - only do that in the english docs under /website/docs because other languages will be translated automatically,
  unless stated otherwise by the user. In doubt - ask the user

## Changes in APP Strings

- when i18 strings are changed, only to that in sources/\_locales/en because other languages will be translated automatically,
  unless stated otherwise by the user. In doubt - ask the user

## commit/push/GitHub policy

- run "make test" before any push to avoid lint/test breakage.
- after push, monitor errors in the github actions and try to correct the errors

## documentation
whenever a new feature, function, configuration, dataclass field, etc. is introduced: 
  - check first if it aligns with docs/systemdesign/*  
  - document it in docs/systemdesign/module_reference.md, using the template from self_documenting.md and save it in docs/systemdesign/module_reference.md 
