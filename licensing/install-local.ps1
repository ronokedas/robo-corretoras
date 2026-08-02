[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$envFile = Join-Path $root '.env.local'
$composeFile = Join-Path $root 'compose.local.yml'

function New-RandomText([int]$Length) {
    $alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#%_-'
    $bytes = New-Object byte[] $Length
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    -join ($bytes | ForEach-Object { $alphabet[$_ % $alphabet.Length] })
}

function New-Base64Secret([int]$Length) {
    $bytes = New-Object byte[] $Length
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    [Convert]::ToBase64String($bytes)
}

docker version | Out-Null
docker compose version | Out-Null

$created = $false
$bootstrapPending = $false
$temporaryPassword = $null
if (-not (Test-Path -LiteralPath $envFile)) {
    Write-Host 'Gerando segredos exclusivos do EvePulse...'
    $phpCode = '$kp=sodium_crypto_sign_keypair(); echo sodium_bin2base64(sodium_crypto_sign_secretkey($kp), SODIUM_BASE64_VARIANT_URLSAFE_NO_PADDING), PHP_EOL, sodium_bin2base64(sodium_crypto_sign_publickey($kp), SODIUM_BASE64_VARIANT_URLSAFE_NO_PADDING), PHP_EOL;'
    $signingKeys = @(& docker run --rm php:8.3-cli php -r $phpCode)
    if ($LASTEXITCODE -ne 0 -or $signingKeys.Count -lt 2) { throw 'Não foi possível gerar o par de assinatura Ed25519.' }

    $temporaryPassword = New-RandomText 24
    $lines = @(
        "APP_KEY=base64:$(New-Base64Secret 32)",
        'MYSQL_DATABASE=evepulse_licenses',
        'MYSQL_USER=evepulse',
        "MYSQL_PASSWORD=$(New-RandomText 32)",
        "MYSQL_ROOT_PASSWORD=$(New-RandomText 36)",
        "LICENSE_PRIVATE_KEY=$($signingKeys[0].Trim())",
        "LICENSE_PUBLIC_KEY=$($signingKeys[1].Trim())",
        'ADMIN_EMAIL=admin@evepulse.local',
        "ADMIN_PASSWORD=$temporaryPassword",
        'ADMIN_NAME=Administrador',
        'APP_URL=http://127.0.0.1:8042',
        'LICENSE_LEASE_MINUTES=4320',
        'EVE_DOMAIN=licenses.example.com'
    )
    [System.IO.File]::WriteAllLines($envFile, $lines, [System.Text.UTF8Encoding]::new($false))
    $created = $true
    $bootstrapPending = $true
} else {
    $passwordLine = Get-Content -LiteralPath $envFile | Where-Object { $_ -like 'ADMIN_PASSWORD=*' }
    $temporaryPassword = ($passwordLine -split '=', 2)[1]
    $bootstrapPending = -not [string]::IsNullOrWhiteSpace($temporaryPassword)
}

Write-Host 'Construindo e iniciando o servidor de licenças...'
docker compose --env-file $envFile -f $composeFile up -d --build --wait
if ($LASTEXITCODE -ne 0) { throw 'Falha ao iniciar os containers EvePulse.' }

if ($bootstrapPending) {
    $content = [System.IO.File]::ReadAllText($envFile)
    $content = [regex]::Replace($content, '(?m)^ADMIN_PASSWORD=.*$', 'ADMIN_PASSWORD=')
    [System.IO.File]::WriteAllText($envFile, $content, [System.Text.UTF8Encoding]::new($false))
    docker compose --env-file $envFile -f $composeFile up -d --force-recreate --wait license-api
    if ($LASTEXITCODE -ne 0) { throw 'O painel iniciou, mas não foi possível remover a senha de bootstrap do container.' }
}

Write-Host ''
Write-Host 'EvePulse License Center está disponível em:' -ForegroundColor Green
Write-Host 'http://127.0.0.1:8042' -ForegroundColor Cyan
Write-Host 'E-mail: admin@evepulse.local'
if ($bootstrapPending) {
    Write-Host "Senha temporária: $temporaryPassword" -ForegroundColor Yellow
    Write-Host 'Copie a senha agora. Ela não será exibida novamente e deverá ser trocada no primeiro login.'
} else {
    Write-Host 'Instalação existente preservada; use a senha já definida.'
}
