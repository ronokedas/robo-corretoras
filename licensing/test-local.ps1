$ErrorActionPreference = 'Stop'
$envFile = Join-Path $PSScriptRoot '.env.local'
$composeFile = Join-Path $PSScriptRoot 'compose.local.yml'
docker compose --env-file $envFile -f $composeFile exec -T `
    -e APP_ENV=testing `
    -e DB_CONNECTION=sqlite `
    -e DB_DATABASE=:memory: `
    -e SESSION_DRIVER=array `
    -e CACHE_STORE=array `
    license-api php artisan test
if ($LASTEXITCODE -ne 0) { throw 'Testes do servidor de licenças falharam.' }
