FROM python:3.14-slim

WORKDIR /app

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install --no-cache-dir pdm

COPY . /app/spooklight

WORKDIR /app/spooklight

RUN rm -f pdm.lock && pdm install --group dev

CMD ["pdm", "run", "python", "src/manage.py", "runserver", "0.0.0.0:8000"]
