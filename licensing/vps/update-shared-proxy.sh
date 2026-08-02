#!/usr/bin/env bash
set -Eeuo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Execute com sudo: sudo bash licensing/vps/update-shared-proxy.sh" >&2
  exit 1
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LICENSING_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
REPO_DIR="$(cd -- "$LICENSING_DIR/.." && pwd)"
ENV_FILE="$LICENSING_DIR/.env.production"
COMPOSE_FILE="$LICENSING_DIR/compose.shared-proxy.yml"

[[ -f "$ENV_FILE" ]] || { echo "Arquivo de produção não encontrado: $ENV_FILE" >&2; exit 1; }
git config --global --add safe.directory "$REPO_DIR"
git -C "$REPO_DIR" pull --ff-only
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" build --pull
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --remove-orphans
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps
