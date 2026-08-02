[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$File)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$envFile = Join-Path $root '.env.local'
$composeFile = Join-Path $root 'compose.local.yml'
$resolved = (Resolve-Path -LiteralPath $File).Path
$answer = Read-Host "A restauração substituirá os dados atuais por '$resolved'. Digite RESTAURAR"
if ($answer -ne 'RESTAURAR') { throw 'Restauração cancelada.' }
$rootPassword = ((Get-Content -LiteralPath $envFile | Where-Object { $_ -like 'MYSQL_ROOT_PASSWORD=*' }) -split '=',2)[1]
Get-Content -LiteralPath $resolved -Raw | docker compose --env-file $envFile -f $composeFile exec -T -e MYSQL_PWD="$rootPassword" mysql mysql -uroot evepulse_licenses
if ($LASTEXITCODE -ne 0) { throw 'Falha ao restaurar backup.' }
Write-Host 'Backup restaurado.' -ForegroundColor Green
