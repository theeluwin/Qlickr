#!/bin/bash

uv run celery \
    --app project \
    flower \
    --uid celery
