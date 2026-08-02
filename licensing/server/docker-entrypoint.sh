#!/bin/sh
set -eu
php artisan migrate --force
if [ -n "${ADMIN_EMAIL:-}" ] && [ -n "${ADMIN_PASSWORD:-}" ]; then
  php artisan admin:create --email="$ADMIN_EMAIL" --password="$ADMIN_PASSWORD" --name="${ADMIN_NAME:-Administrador}"
fi
exec php artisan serve --host=0.0.0.0 --port=8000
