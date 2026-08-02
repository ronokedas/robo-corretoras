[CmdletBinding()]
param(
    [string]$LicenseUrl = 'https://robolite.4dtech.com.br',
    [Parameter(Mandatory = $true)][string]$PublicKey
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$LicenseUrl = $LicenseUrl.TrimEnd('/')
if ($LicenseUrl -notmatch '^https://[A-Za-z0-9.-]+$') {
    throw 'LicenseUrl deve ser uma URL HTTPS sem caminho.'
}
if ($PublicKey -notmatch '^[A-Za-z0-9_-]{43}$') {
    throw 'A chave pública Ed25519 deve ter 43 caracteres em base64url.'
}
$target = Join-Path $root 'evepulse_desktop\production_config.py'
$content = @"
# Gerado localmente; não versionar.
LICENSE_URL = "$LicenseUrl"
LICENSE_PUBLIC_KEY = "$PublicKey"
"@
[System.IO.File]::WriteAllText($target, $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "Configuração de produção criada para $LicenseUrl" -ForegroundColor Green
Write-Host 'Execute .\build-desktop.ps1 para gerar o instalador Windows.' -ForegroundColor Cyan
