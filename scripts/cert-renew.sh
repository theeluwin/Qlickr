#!/bin/bash

set -e

export PROJECT_ROOT="$(cd "$(dirname "$(dirname "$(realpath "$0")")")" && pwd)"
cd "$PROJECT_ROOT"
export COMPOSE_FILE="$PROJECT_ROOT/compose/prod.yml"

export RENEW_OUTPUT=$(docker compose \
    --env-file "$PROJECT_ROOT/.env.prod" \
    --file "$COMPOSE_FILE" \
    run \
    --rm \
    certbot \
        renew \
        --webroot \
        --webroot-path=/var/www/certbot)

if echo "$RENEW_OUTPUT" | grep -q "successfully renewed"; then
    docker compose \
        --env-file "$PROJECT_ROOT/.env.prod" \
        --file "$COMPOSE_FILE" \
        exec \
        nginx \
            nginx \
            -s \
            reload
else
    echo "nothing to renew"
fi
