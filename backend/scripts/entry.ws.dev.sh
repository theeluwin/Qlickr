#!/bin/bash

/app/.venv/bin/gunicorn \
    project.asgi:application \
    --worker-class=uvicorn.workers.UvicornWorker \
    --workers=1 \
    --threads=1 \
    --bind=0.0.0.0:8000 \
    --proxy-allow-from='*' \
    --forwarded-allow-ips='*' \
    --timeout=0 \
    --keep-alive=128 \
    --backlog=8192 \
    --reuse-port \
    --pid /tmp/gunicorn.ws.pid \
    1>> /shared/logfiles/gunicorn.ws.access.log \
    2>> /shared/logfiles/gunicorn.ws.error.log
