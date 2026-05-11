# Architecture

Spooklight is a Django 6 worldbuilding application. The domain spine is:

```text
User -> World -> World artifacts
```

The first implemented artifact is `WorldCoverImage`, which gives each world a visual entry point on the dashboard. Future artifacts such as world truths, references, generated images, and story concepts should also be scoped through `World`.

## App Boundaries

- `core` owns the landing page, demo login, and authenticated dashboard shell.
- `worlds` owns world data, world forms/views, world cover images, cover-generation prompts, and cover-generation tasks.
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

Cover generation uses the OpenAI Image API with `gpt-image-2`. The service boundary is `worlds.services.generate_cover_image`; tests should mock `worlds.services.request_world_cover_image` so they never call the network.

## Task Boundary

Cover generation is wrapped in a Django task, `worlds.tasks.generate_world_cover`. The current Django task backend is immediate, so local execution completes during the request. Keep the task boundary intact so a durable async backend can replace it later without changing view behavior.
