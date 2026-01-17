# Repository Guidelines

## Project Structure & Module Organization
- This repository is the Spooklight Django project, using a `src/` layout with the Django project package in `src/spooklight/`.
- Add new Django apps as top-level packages under `src/` (for example, `src/stories/`), and keep app logic self-contained.
- Keep tests in `tests/` and follow pytest discovery conventions.
- Keep Django apps as owners of their data and logic; avoid cross-app coupling between example apps.
- Store uncompiled front-end assets in `assets/` and deposit build outputs into `static/`. Keep runtime collections such as `staticfiles/` and user uploads (`media/`) outside of version control.
- Consolidate architecture notes, runbooks, and decision records in `docs/`. Before major refactors, review and extend these documents to keep system knowledge current.

## Build, Test, and Development Commands
- Use PDM to capture application and dev-only dependencies. Document the canonical install command (e.g., `pdm install --group dev`).
- Target runtimes: Python 3.14+ always; use Django 6.x for Django services unless explicitly scoped otherwise.
- Enforce version policy in `pyproject.toml`: set `requires-python = ">=3.13"` and pin Django to `>=6.0.1` (or the project’s chosen minor track).
- Ensure database migrations run before the app starts by standardizing on `python manage.py migrate` (wrap with your packaging tool as needed: `pdm run python manage.py migrate`).
- Expose a single test runner command (`pdm run test`) in this example project.
- Expose a lint command (`pdm run lint`) in this example project.
- Maintain an `npm` script for CSS/JS tooling (`npm run build:css`) so front-end assets rebuild predictably across machines and CI.

## Coding Style & Naming Conventions
- Use 4-space indentation, type-annotate every function, and prefer built-in generics (`list[str]`, `dict[str, Any]`) with `| None` for optionals on Python 3.14+.
- Keep Django apps modular: new views, forms, services, and tasks should live under the app that owns the corresponding data or workflow.
- Prefer Django 6’s built-in tasks framework for background work; introduce Celery only when its operational guarantees/features are required.
- Follow a predictable template hierarchy (`<app>/templates/<app>/**`) and colocate HTMX or partial templates alongside the features that render them.
- Prefer Django 6 template partials (`{% partialdef %}` / `{% partial %}`) before splitting markup into many tiny `{% include %}` files.
- Enable Django 6’s built-in Content Security Policy support by default where feasible; tighten policies and selectively open `script-src`/`connect-src` per feature.
- Avoid relying on undocumented Django email internals; Django 6 modernizes the email API implementation, so keep custom backends/subclasses conservative.
- Explicitly set `DEFAULT_AUTO_FIELD` (or accept the BigAutoField default) to keep migrations deterministic across apps.
- Treat the linter as non-optional. Run it locally before committing; unresolved linting errors should block CI.
- Write docstrings and comments in American English; focus on clarifying intent rather than restating code.

## Testing Guidelines
- Keep tests adjacent to their code in `apps/<app>/tests/`. Name modules `test_*.py`, classes `Test*`, and functions `test_*` for automatic discovery.
- Cover asynchronous tasks, external service adapters, and LLM helpers with deterministic fixtures. Mock network-bound APIs so the suite stays offline and fast.
- When adding migrations or long-running flows, include regression tests that exercise both success and failure paths.
- Make `pdm run test` (or the equivalent) the default validation step before pushing changes.

## Commit & Pull Request Guidelines
- Favor concise, sentence-case commit messages that describe both the change and its intent (e.g., `Add credit balance tracking to user profiles`).
- Keep commits scoped to a single concern. Mention the affected app or feature area when useful for reviewers.
- Pull requests should summarize the change set, call out new migrations, list manual or automated test results, and attach UI screenshots or logs for behavioral updates.
