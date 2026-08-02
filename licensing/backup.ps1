[CmdletBinding()]
param([string]$Destination)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$envFile = Join-Path $root '.env.local'
$composeFile = Join-Path $root 'compose.local.yml'
if (-not (Test-Path -LiteralPath $envFile)) { throw 'Execute install-local.ps1 primeiro.' }
if (-not $Destination) {
    $backupDir = Join-Path $root 'backups'
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    $Destination = Join-Path $backupDir ("evepulse-{0}.sql" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
}
$resolvedParent = [System.IO.Path]::GetFullPath((Split-Path -Parent $Destination))
New-Item -ItemType Directory -Path $resolvedParent -Force | Out-Null
$rootPassword = ((Get-Content -LiteralPath $envFile | Where-Object { $_ -like 'MYSQL_ROOT_PASSWORD=*' }) -split '=',2)[1]
docker compose --env-file $envFile -f $composeFile exec -T -e MYSQL_PWD="$rootPassword" mysql mysqldump -uroot --single-transaction --routines evepulse_licenses | Set-Content -LiteralPath $Destination -Encoding utf8
if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar backup.' }
Write-Host "Backup criado em $Destination" -ForegroundColor Green
