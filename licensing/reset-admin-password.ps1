[CmdletBinding()]
param([string]$Email = 'admin@evepulse.local')

$ErrorActionPreference = 'Stop'
$alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#%_-'
$bytes = New-Object byte[] 24
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
$temporaryPassword = -join ($bytes | ForEach-Object { $alphabet[$_ % $alphabet.Length] })
$envFile = Join-Path $PSScriptRoot '.env.local'
$composeFile = Join-Path $PSScriptRoot 'compose.local.yml'
docker compose --env-file $envFile -f $composeFile exec -T license-api php artisan admin:reset-password --email="$Email" --password="$temporaryPassword"
if ($LASTEXITCODE -ne 0) { throw 'Não foi possível redefinir a senha.' }
Write-Host "E-mail: $Email"
Write-Host "Senha temporária: $temporaryPassword" -ForegroundColor Yellow
Write-Host 'Copie agora. Ela será exigida apenas para definir uma nova senha.'
