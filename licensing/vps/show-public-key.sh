#!/usr/bin/env bash
set -Eeuo pipefail
if [[ ${EUID} -ne 0 ]]; then echo "Execute com sudo." >&2; exit 1; fi
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$(cd -- "$SCRIPT_DIR/.." && pwd)/.env.production"
[[ -f "$ENV_FILE" ]] || { echo "Ambiente de produção ausente." >&2; exit 1; }
KEY="$(sed -n 's/^LICENSE_PUBLIC_KEY=//p' "$ENV_FILE")"
[[ ${#KEY} -eq 43 ]] || { echo "Chave pública inválida." >&2; exit 1; }
echo "$KEY"
