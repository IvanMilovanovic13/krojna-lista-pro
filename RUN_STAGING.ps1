Set-Location C:\Users\Korisnik\krojna_lista_pro

$venvPython = Join-Path $PSScriptRoot "venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Error "Project venv nije pronadjen. Pokreni .\\SETUP_VENV.ps1 pa zatim ponovo probaj."
    exit 1
}

$env:APP_ENV = "staging"

& $venvPython app.py
