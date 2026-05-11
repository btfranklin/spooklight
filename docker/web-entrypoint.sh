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

pdm run python src/manage.py migrate
pdm run python src/manage.py runserver 0.0.0.0:8000
