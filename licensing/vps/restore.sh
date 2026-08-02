#!/usr/bin/env bash
set -Eeuo pipefail
if [[ ${EUID} -ne 0 ]]; then echo "Execute com sudo." >&2; exit 1; fi
FILE="${1:-}"
[[ -f "$FILE" ]] || { echo "Uso: sudo bash licensing/vps/restore.sh /caminho/backup.sql.gz" >&2; exit 1; }
read -r -p "Digite RESTAURAR para substituir os dados atuais: " CONFIRM
[[ "$CONFIRM" == RESTAURAR ]] || { echo "Cancelado."; exit 1; }
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LICENSING_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$LICENSING_DIR/.env.production"
COMPOSE_FILE="$LICENSING_DIR/compose.production.yml"
ROOT_PASSWORD="$(sed -n 's/^MYSQL_ROOT_PASSWORD=//p' "$ENV_FILE")"
cd "$LICENSING_DIR"
gzip -dc "$FILE" | docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T -e MYSQL_PWD="$ROOT_PASSWORD" mysql mysql -uroot evepulse_licenses
echo "Restauração concluída."
