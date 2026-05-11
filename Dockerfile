FROM node:20-bookworm-slim AS assets

WORKDIR /app

COPY package.json tailwind.config.js /app/
COPY assets/ /app/assets/
COPY src/ /app/src/

RUN npm install
RUN npm run build:css

FROM python:3.14-slim

WORKDIR /app

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install --no-cache-dir pdm

COPY . /app/spooklight

WORKDIR /app/spooklight

COPY --from=assets /app/static/css/app.css /app/spooklight/static/css/app.css

RUN pdm install --group dev

ENV DJANGO_SECRET_KEY="build-secret-key" \
    DJANGO_DEBUG="0" \
    DJANGO_ALLOWED_HOSTS="*"

RUN pdm run python src/manage.py collectstatic --noinput

CMD ["pdm", "run", "python", "src/manage.py", "runserver", "0.0.0.0:8000"]
