$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "Ambiente .venv ausente. Crie-o e instale as dependências primeiro."
}

Remove-Item Env:PYTHONHOME -ErrorAction SilentlyContinue
$venvConfig = Get-Content (Join-Path $root ".venv\pyvenv.cfg")
$runtimeHomeLine = $venvConfig | Where-Object { $_ -match '^home\s*=' } | Select-Object -First 1
if ($runtimeHomeLine) {
    $runtimeHome = ($runtimeHomeLine -split '=', 2)[1].Trim()
    $env:PATH = "$runtimeHome;$runtimeHome\DLLs;$env:PATH"
}
& $python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Os testes falharam." }

& $python -m PyInstaller --noconfirm --clean (Join-Path $root "evepulse.spec")
if ($LASTEXITCODE -ne 0) { throw "A geração do executável falhou." }

$makensis = Get-Command makensis.exe -ErrorAction SilentlyContinue
if (-not $makensis) {
    $candidate = "${env:ProgramFiles(x86)}\NSIS\makensis.exe"
    if (Test-Path $candidate) { $makensis = Get-Item $candidate }
}
if (-not $makensis) {
    $candidate = Join-Path $root ".tools\nsis-msys2\mingw64\bin\makensis.exe"
    if (Test-Path $candidate) { $makensis = Get-Item $candidate }
}
if ($makensis) {
    New-Item -ItemType Directory -Force (Join-Path $root "release") | Out-Null
    $makensisPath = if ($makensis -is [System.IO.FileInfo]) { $makensis.FullName } else { $makensis.Source }
    Push-Location (Join-Path $root "installer")
    try {
        & $makensisPath (Join-Path $root "installer\EvePulseTrader.nsi")
        if ($LASTEXITCODE -ne 0) { throw "A geração do instalador falhou." }
    } finally {
        Pop-Location
    }
    Write-Host "Instalador criado em release\EvePulseTrader-Setup-1.0.2.exe"
} else {
    Write-Warning "NSIS não encontrado. O aplicativo portátil foi criado em dist\EvePulseTrader."
}
