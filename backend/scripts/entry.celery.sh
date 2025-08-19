#!/bin/bash

uv run celery \
    --app project \
    worker \
    --loglevel=info \
    --logfile=/shared/logfiles/celery.log
