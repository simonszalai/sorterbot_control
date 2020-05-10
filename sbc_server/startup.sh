#!/bin/bash
set -euo pipefail

if [ -v MIGRATE ]; then
    python3 manage.py makemigrations
    python3 manage.py migrate
fi

# exec python3 manage.py collectstatic --no-input

exec export PG_CONN=$(aws ssm get-parameter --name SorterBotCloudPostgres --with-decryption | jq -r ".Parameter.Value")

exec python3 manage.py runserver 0.0.0.0:8000