#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

if [[ ${EUID} -ne 0 ]]; then
  echo "Execute com sudo: sudo bash licensing/vps/install.sh" >&2
  exit 1
fi

DOMAIN="${EVE_DOMAIN:-robolite.4dtech.com.br}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@robolite.4dtech.com.br}"
ACME_EMAIL="${ACME_EMAIL:-$ADMIN_EMAIL}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LICENSING_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$LICENSING_DIR/.env.production"
COMPOSE_FILE="$LICENSING_DIR/compose.production.yml"

if [[ ! -f /etc/os-release ]]; then
  echo "Distribuição Linux não reconhecida. Use Ubuntu 22.04+ ou Debian 12+." >&2
  exit 1
fi
. /etc/os-release
case "${ID:-}" in
  ubuntu|debian) ;;
  *) echo "Sistema não suportado automaticamente: ${ID:-desconhecido}." >&2; exit 1 ;;
esac

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y ca-certificates curl git gnupg openssl ufw
if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL "https://download.docker.com/linux/$ID/gpg" -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  ARCH="$(dpkg --print-architecture)"
  CODENAME="${VERSION_CODENAME:-$(. /etc/os-release && echo "$VERSION_CODENAME")}"
  echo "deb [arch=$ARCH signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/$ID $CODENAME stable" > /etc/apt/sources.list.d/docker.list
  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi
systemctl enable --now docker

ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 443/udp
ufw --force enable

if [[ -n "${SUDO_USER:-}" && "$SUDO_USER" != root ]]; then
  usermod -aG docker "$SUDO_USER"
fi

if [[ -f "$ENV_FILE" ]]; then
  echo "O arquivo $ENV_FILE já existe. Para proteger os segredos atuais, a instalação foi interrompida." >&2
  echo "Use sudo bash licensing/vps/update.sh para atualizar." >&2
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
EVE_DOMAIN=$DOMAIN
ACME_EMAIL=$ACME_EMAIL
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

# A senha inicial deixa de existir no arquivo e no ambiente do container após criar o administrador.
sed -i 's/^ADMIN_PASSWORD=.*/ADMIN_PASSWORD=/' "$ENV_FILE"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --force-recreate license-api
for _ in $(seq 1 30); do
  API_ID="$(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps -q license-api)"
  STATUS="$(docker inspect --format='{{.State.Health.Status}}' "$API_ID" 2>/dev/null || true)"
  [[ "$STATUS" == healthy ]] && break
  sleep 2
done

PUBLIC_IP="$(curl -4fsS --max-time 5 https://api.ipify.org || true)"
DNS_IP="$(getent ahostsv4 "$DOMAIN" | awk 'NR==1 {print $1}' || true)"
echo
echo "============================================================"
echo "EvePulse License Center instalado"
echo "URL: https://$DOMAIN"
echo "Administrador: $ADMIN_EMAIL"
echo "Senha temporária (aparece somente agora): $ADMIN_PASSWORD"
echo "Chave pública do cliente: $LICENSE_PUBLIC_KEY"
echo "IP público detectado: ${PUBLIC_IP:-indisponível}"
echo "DNS detectado: ${DNS_IP:-não configurado}"
echo "============================================================"
echo
if [[ -n "$PUBLIC_IP" && "$DNS_IP" != "$PUBLIC_IP" ]]; then
  echo "ATENÇÃO: crie/ajuste o registro DNS A de $DOMAIN para $PUBLIC_IP."
fi
echo "No primeiro login, troque a senha temporária."
echo "No Windows, use a chave pública acima em configure-production-client.ps1."
