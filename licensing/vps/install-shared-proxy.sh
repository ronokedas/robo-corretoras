#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

if [[ ${EUID} -ne 0 ]]; then
  echo "Execute com sudo: sudo bash licensing/vps/install-shared-proxy.sh" >&2
  exit 1
fi

APP_URL="${EVE_APP_URL:-https://www.4dtech.com.br/robo}"
BASE_PATH="${EVE_BASE_PATH:-/robo}"
SESSION_DOMAIN="${SESSION_DOMAIN:-www.4dtech.com.br}"
PROXY_NETWORK="${PROXY_NETWORK:-html-em-pdf_default}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@4dtech.com.br}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LICENSING_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$LICENSING_DIR/.env.production"
COMPOSE_FILE="$LICENSING_DIR/compose.shared-proxy.yml"

command -v docker >/dev/null 2>&1 || { echo "Docker não encontrado." >&2; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "Docker Compose não encontrado." >&2; exit 1; }
docker network inspect "$PROXY_NETWORK" >/dev/null 2>&1 || {
  echo "A rede Docker do proxy não existe: $PROXY_NETWORK" >&2
  exit 1
}

if [[ -f "$ENV_FILE" ]]; then
  echo "O arquivo $ENV_FILE já existe. Use licensing/vps/update-shared-proxy.sh." >&2
  exit 1
fi

APP_KEY="base64:$(openssl rand -base64 32 | tr -d '\n')"
MYSQL_PASSWORD="$(openssl rand -hex 32)"
MYSQL_ROOT_PASSWORD="$(openssl rand -hex 32)"
ADMIN_PASSWORD="EvP-$(openssl rand -hex 10)-Aa9"
mapfile -t SIGNING_KEYS < <(docker run --rm php:8.3-cli-alpine php -r '$kp=sodium_crypto_sign_keypair(); echo sodium_bin2base64(sodium_crypto_sign_secretkey($kp), SODIUM_BASE64_VARIANT_URLSAFE_NO_PADDING), PHP_EOL, sodium_bin2base64(sodium_crypto_sign_publickey($kp), SODIUM_BASE64_VARIANT_URLSAFE_NO_PADDING), PHP_EOL;')
LICENSE_PRIVATE_KEY="${SIGNING_KEYS[0]:-}"
LICENSE_PUBLIC_KEY="${SIGNING_KEYS[1]:-}"
if [[ ${#LICENSE_PRIVATE_KEY} -lt 80 || ${#LICENSE_PUBLIC_KEY} -ne 43 ]]; then
  echo "Falha ao gerar o par Ed25519." >&2
  exit 1
fi

cat > "$ENV_FILE" <<EOF
APP_KEY=$APP_KEY
MYSQL_DATABASE=evepulse_licenses
MYSQL_USER=evepulse
MYSQL_PASSWORD=$MYSQL_PASSWORD
MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD
LICENSE_PRIVATE_KEY=$LICENSE_PRIVATE_KEY
LICENSE_PUBLIC_KEY=$LICENSE_PUBLIC_KEY
LICENSE_LEASE_MINUTES=4320
ADMIN_EMAIL=$ADMIN_EMAIL
ADMIN_PASSWORD=$ADMIN_PASSWORD
ADMIN_NAME=Administrador
EVE_APP_URL=$APP_URL
EVE_BASE_PATH=$BASE_PATH
SESSION_DOMAIN=$SESSION_DOMAIN
PROXY_NETWORK=$PROXY_NETWORK
EOF
chmod 600 "$ENV_FILE"

cd "$LICENSING_DIR"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" build --pull
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d

echo "Aguardando API e banco..."
for _ in $(seq 1 60); do
  API_ID="$(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps -q license-api)"
  STATUS="$(docker inspect --format='{{.State.Health.Status}}' "$API_ID" 2>/dev/null || true)"
  [[ "$STATUS" == healthy ]] && break
  sleep 3
done
API_ID="$(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps -q license-api)"
STATUS="$(docker inspect --format='{{.State.Health.Status}}' "$API_ID" 2>/dev/null || true)"
if [[ "$STATUS" != healthy ]]; then
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs --tail=100 license-api mysql
  echo "A API não ficou saudável." >&2
  exit 1
fi

sed -i 's/^ADMIN_PASSWORD=.*/ADMIN_PASSWORD=/' "$ENV_FILE"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --force-recreate license-api

echo
echo "============================================================"
echo "EvePulse License Center preparado no proxy compartilhado"
echo "URL: $APP_URL"
echo "Administrador: $ADMIN_EMAIL"
echo "Senha temporária (aparece somente agora): $ADMIN_PASSWORD"
echo "Chave pública do cliente: $LICENSE_PUBLIC_KEY"
echo "Rede compartilhada: $PROXY_NETWORK"
echo "============================================================"
echo
echo "Ainda é necessário incluir licensing/caddy-robo-snippet.txt no Caddyfile principal e recarregar o Caddy."
