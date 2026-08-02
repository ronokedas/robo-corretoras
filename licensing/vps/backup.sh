#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
if [[ ${EUID} -ne 0 ]]; then echo "Execute com sudo." >&2; exit 1; fi
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LICENSING_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$LICENSING_DIR/.env.production"
COMPOSE_FILE="$LICENSING_DIR/compose.production.yml"
BACKUP_DIR="${1:-/var/backups/evepulse}"
mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"
ROOT_PASSWORD="$(sed -n 's/^MYSQL_ROOT_PASSWORD=//p' "$ENV_FILE")"
FILE="$BACKUP_DIR/evepulse-$(date -u +%Y%m%d-%H%M%S).sql.gz"
cd "$LICENSING_DIR"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T -e MYSQL_PWD="$ROOT_PASSWORD" mysql \
  mysqldump -uroot --single-transaction --routines evepulse_licenses | gzip -9 > "$FILE"
chmod 600 "$FILE"
find "$BACKUP_DIR" -type f -name 'evepulse-*.sql.gz' -mtime +30 -delete
echo "Backup criado: $FILE"
