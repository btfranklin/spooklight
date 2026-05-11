# Repository Guide

## Start Here
- Product direction: `VISION.md`
- Architecture map: `docs/architecture.md`
- Local operations and troubleshooting: `docs/operations.md`
- UI implementation rules: `docs/ui-implementation.md`
- Repo docs index: `docs/index.md`

## Project Shape
- Django 6 project package: `src/spooklight/`
- App-owned domain code: top-level packages under `src/`
- Current apps: `core` for landing/dashboard/auth shell, `worlds` for world data, cover generation, and world UI
- Tests: `tests/`
- Source CSS: `assets/css/app.css`; built CSS: `static/css/app.css`
- User uploads/generated media: `media/` runtime state is not versioned

## Commands
- Install Python dependencies: `pdm install --group dev`
- Start local Postgres: `docker compose up -d db`
- Migrate: `pdm run python src/manage.py migrate`
- Run app locally: `pdm run dev`
- Test: `pdm run test`
- Lint: `pdm run lint`
- Format templates: `pdm run reformat-templates`
- Build CSS: `npm install --no-package-lock && npm run build:css`

## Working Rules
- Use PDM for Python dependency management.
- Keep package constraints as `>=` unless an exact pin is required.
- Keep Django apps modular and owner-scoped; avoid cross-app domain coupling.
- Prefer Django 6 tasks for background work before adding another queue system.
- Mock OpenAI/network calls in tests; the test suite must stay offline.
- Update `docs/` when architecture, runtime, or validation rules change.
