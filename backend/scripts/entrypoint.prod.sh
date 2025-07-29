#!/bin/bash

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py check
daphne \
    --bind 0.0.0.0 \
    --port 8000 \
    --http-timeout 600 \
    project.asgi:application \
    1>> /shared/logfiles/daphne.access.log \
    2>> /shared/logfiles/daphne.error.log
