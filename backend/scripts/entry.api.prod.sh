#!/bin/bash

uv run python manage.py migrate --noinput
uv run python manage.py collectstatic --noinput
uv run python manage.py check
uv run gunicorn \
    project.wsgi:application \
    --workers=9 \
    --threads=4 \
    --bind=0.0.0.0:8000 \
    --proxy-allow-from='*' \
    --forwarded-allow-ips='*' \
    --keep-alive=128 \
    --backlog=8192 \
    --reuse-port \
    1>> /shared/logfiles/gunicorn.api.access.log \
    2>> /shared/logfiles/gunicorn.api.error.log
