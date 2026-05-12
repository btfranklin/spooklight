# Operations

## Local Setup

Install Python and Node dependencies:

```sh
pdm install --group dev
npm install --no-package-lock
```

Create local environment configuration:

```sh
cp .env.example .env
```

`.env` is where local API keys and local process settings live. Docker Compose
loads it into the web container with `env_file`, matching the Syncretic Mind
runtime pattern.

Start Postgres and Redis:

```sh
docker compose up -d db redis
```

Run migrations:

```sh
pdm run python src/manage.py migrate
```

Run the app:

```sh
pdm run dev
```

The app reads `DATABASE_URL` when it is present and otherwise falls back to
`127.0.0.1:5433`. Docker web overrides `DATABASE_URL` to `db:5432` inside the
Compose network.

`REDIS_URL` defaults to `redis://127.0.0.1:6379/0` locally. Docker web and
worker services override it to `redis://redis:6379/0`.

## Docker Preview

Run the full stack:

```sh
docker compose up -d --build
```

The web app is exposed at [http://127.0.0.1:8001/](http://127.0.0.1:8001/).

Postgres data lives in the Docker `spooklight_postgres_data` named volume.
Redis data lives in the Docker `spooklight_redis_data` named volume.
Generated media lives in the Docker `spooklight_media_data` named volume.

## Cover Generation

Set `OPENAI_API_KEY` in `.env` before using the Generate cover button:

```sh
OPENAI_API_KEY=...
```

If the key is missing, cover generation should fail gracefully and show an error message on the world detail page. The world itself remains usable.

Generated cover files are stored in `media/world-covers/` locally or in the
Docker `spooklight_media_data` volume.

Cover generation is asynchronous. The request creates a `WorldCoverImage` and
`AITask`, enqueues it, and returns immediately. The worker handles the OpenAI
request and the world detail page polls a small status fragment while the task
is active.

Useful task commands:

```sh
pdm run python src/manage.py recover_ai_tasks
pdm run python src/manage.py check_ai_worker_health
pdm run python src/manage.py run_ai_worker
```

## Validation

Run:

```sh
pdm run test
pdm run python src/manage.py check
pdm run lint
npm run build:css
```

The test suite expects Postgres to be reachable. Start it with `docker compose up -d db`.
