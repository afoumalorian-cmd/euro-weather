#!/bin/sh

set -e

echo "Waiting for PostgreSQL..."

while ! nc -z "${POSTGRES_HOST}" "${POSTGRES_PORT}"; do
  sleep 1
done

echo "PostgreSQL is available."

if [ -f manage.py ]; then
  python manage.py migrate --noinput
fi

exec "$@"