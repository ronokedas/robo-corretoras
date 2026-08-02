#!/usr/bin/env bash
set -Eeuo pipefail
if [[ ${EUID} -ne 0 ]]; then echo "Execute com sudo." >&2; exit 1; fi
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LICENSING_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
REPO_DIR="$(cd -- "$LICENSING_DIR/.." && pwd)"
ENV_FILE="$LICENSING_DIR/.env.production"
COMPOSE_FILE="$LICENSING_DIR/compose.production.yml"
[[ -f "$ENV_FILE" ]] || { echo "Ambiente de produção ausente." >&2; exit 1; }
cd "$REPO_DIR"
git config --global --add safe.directory "$REPO_DIR"
git pull --ff-only
cd "$LICENSING_DIR"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" build --pull
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d
docker image prune -f
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps
