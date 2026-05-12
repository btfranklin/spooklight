# Spooklight Docs

This directory is the repo-local system of record for product, architecture, and operations knowledge.

## Core References

- [Product vision](../VISION.md)
- [Architecture](architecture.md)
- [Async AI tasks](async-ai-tasks.md)
- [Operations](operations.md)
- [UI implementation guidance](ui-implementation.md)

## Validation

Use these checks before committing behavior changes:

```sh
docker compose up -d db
docker compose up -d redis
pdm run python src/manage.py migrate
pdm run test
pdm run python src/manage.py check
pdm run lint
npm install --no-package-lock
npm run build:css
```
