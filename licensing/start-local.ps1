$ErrorActionPreference = 'Stop'
docker compose --env-file (Join-Path $PSScriptRoot '.env.local') -f (Join-Path $PSScriptRoot 'compose.local.yml') up -d --wait
Write-Host 'Painel: http://127.0.0.1:8042' -ForegroundColor Cyan
