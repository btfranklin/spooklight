# Architecture

Spooklight is a Django 6 worldbuilding application. The domain spine is:

```text
User -> World -> World artifacts
```

Implemented artifacts include `WorldCoverImage`, world truths, characters, locations, important events, image/reference items, and story concepts. Every artifact is scoped through `World`.

## App Boundaries

- `core` owns the landing page, demo login, and authenticated dashboard shell.
- `worlds` owns world data, world forms/views, world cover images, cover-generation prompts, and cover-generation tasks.
- `world_artifacts` owns editable world-scoped artifact categories under each world.
- `ai_tasks` owns the Postgres-backed AI task ledger, lifecycle events, worker heartbeats, recovery, and worker health commands.
- Cross-app access should go through explicit models, services, or views rather than hidden template/query logic.

## Data Ownership

Every `World` belongs to one user. World list, detail, and cover-generation routes must filter by `owner=request.user`.

World slugs are unique per owner, not globally unique. This allows different users to create worlds with the same name while keeping URLs stable inside each account.

## Database

Runtime database configuration is Postgres-first. Local Compose exposes the database on `localhost:5433`; the web container reaches it at `db:5432`.

The project intentionally does not include pgvector yet. Add vector fields and semantic retrieval only when embeddings for world truths or visual metadata are implemented.

## Media Storage

Generated cover images are stored under `MEDIA_ROOT/world-covers/...` and are not committed. Local Docker uses the `spooklight_media_data` volume for generated media.

## OpenAI Boundary

Cover generation uses the OpenAI Image API with `gpt-image-2`. The service boundary is `worlds.services.process_world_cover_generation_task`; tests should mock `worlds.services.request_world_cover_image` so they never call the network.

## Task Boundary

AI work is tracked in Postgres through `ai_tasks.AITask`. Redis/RQ is the execution transport, but the UI and recovery paths treat the Postgres row as the source of truth.

Request handlers create and enqueue `AITask` rows. They must not call OpenAI directly. Worker code claims tasks, records lifecycle events, updates provider metadata, and writes terminal status back to Postgres.

See [Async AI tasks](async-ai-tasks.md) for the task lifecycle and recovery contract.
