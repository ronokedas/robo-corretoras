$ErrorActionPreference = 'Stop'
docker compose --env-file (Join-Path $PSScriptRoot '.env.local') -f (Join-Path $PSScriptRoot 'compose.local.yml') stop
