$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Remove-Item Env:PYTHONHOME -ErrorAction SilentlyContinue
& (Join-Path $root ".venv\Scripts\python.exe") -m evepulse_desktop
