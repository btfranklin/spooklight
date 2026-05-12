#!/usr/bin/env sh
set -eu

cd /app/spooklight

until pdm run python - <<'PY'
import os

import psycopg

try:
    psycopg.connect(os.environ["DATABASE_URL"]).close()
except Exception:
    raise SystemExit(1)
PY
do
  sleep 1
done

until pdm run python src/manage.py migrate --check >/dev/null 2>&1
do
  sleep 1
done

pdm run python src/manage.py recover_ai_tasks
pdm run python src/manage.py run_ai_worker
