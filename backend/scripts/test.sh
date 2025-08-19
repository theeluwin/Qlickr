#!/bin/bash

uv run python manage.py migrate --noinput
uv run python manage.py collectstatic --noinput
uv run python manage.py check
uv run flake8 .
uv run coverage run manage.py test
uv run coverage report -m
