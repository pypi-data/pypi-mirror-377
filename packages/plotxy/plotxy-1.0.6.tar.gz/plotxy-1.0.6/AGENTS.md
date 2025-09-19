# Repository Guidelines

This guide summarizes how to contribute effectively to the PlotX codebase.

## Project Structure & Module Organization
Library code lives in `src/plotx/`, grouped by domain: `core/` for computation, `viz/` for rendering, `io/` for data adapters, and shared helpers in `utils/`. CLI entry points and notebooks stay in `apps/` and `notebooks/` to keep the library reusable. Mirror the source tree under `tests/` (for example, `src/plotx/core/loader.py` maps to `tests/core/test_loader.py`). Lightweight configuration belongs in `config/`; large assets should stay out of the repo.

## Build, Test, and Development Commands
Create a virtual environment with `python -m venv .venv && source .venv/bin/activate`, then install runtime deps via `pip install -r requirements.txt` and tooling using `pip install -r requirements-dev.txt`. Run `ruff check src tests` and `black --check src tests` before committing. Execute targeted tests with `pytest tests/core -k <pattern>` and the full suite via `pytest --maxfail=1 --disable-warnings`. Launch the CLI for manual verification using `python -m plotx.apps.cli`.

## Coding Style & Naming Conventions
Write Python 3.11+ with type hints and prefer `pathlib.Path` for filesystem paths. Follow Black formatting and keep lines ≤88 characters. Ruff enforces import ordering and lint rules—address warnings rather than ignoring them. Name packages with lowercase underscores, classes in PascalCase, and functions or variables in snake_case. Export only intended public APIs through module-level `__all__` lists.

## Testing Guidelines
Use Pytest with files named `test_*.py` and descriptive test names such as `test_loader_handles_missing_files`. Maintain ≥90% coverage across `src/plotx/` by running `pytest --cov=plotx --cov-report=term-missing`. Place reusable fixtures in `tests/fixtures/` and mark time-consuming cases with `@pytest.mark.slow` so default runs stay fast.

## Commit & Pull Request Guidelines
Adopt Conventional Commit prefixes (e.g., `feat:`, `fix:`) with concise, imperative summaries. Keep each commit focused on a single concern and note migrations or breaking changes in the body. Pull requests should state the problem, the solution, and validation evidence; link related issues and include screenshots or logs when plot output changes. Ensure CI passes lint and test checks before requesting review.

## Configuration & Security Tips
Document required environment variables in `.env.example` with safe defaults. Never commit real credentials or large datasets—use `.gitignore` to keep secrets out of version control and reference secure storage options in `docs/security.md` when needed.
