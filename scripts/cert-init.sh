#!/bin/bash

set -e

PROJECT_ROOT=$(dirname "$(dirname "$(realpath "$0")")")
DOMAINS="-d qlickr.university.edu -d www.qlickr.university.edu"
EMAIL="theeluwin@gmail.com"

cd "$PROJECT_ROOT"

docker compose \
    --env-file "$PROJECT_ROOT/.env.prod" \
    --file "$PROJECT_ROOT/compose/certbot.yml" \
    run \
    --rm \
    certbot \
        certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        $DOMAINS
