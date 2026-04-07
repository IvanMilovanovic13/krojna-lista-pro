Set-Location C:\Users\Korisnik\krojna_lista_pro

$venvPython = Join-Path $PSScriptRoot "venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    & $venvPython app.py
} else {
    python app.py
}
