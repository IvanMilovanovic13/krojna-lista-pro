Set-Location C:\Users\Korisnik\krojna_lista_pro

$venvPython = Join-Path $PSScriptRoot "venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Error "Project venv nije pronadjen. Pokreni .\\SETUP_VENV.ps1 pa zatim ponovo probaj."
    exit 1
}

$target = if ($args.Count -gt 0 -and $args[0]) { $args[0] } else { "staging" }

$env:APP_ENV = $target

& $venvPython ops_diagnostics_cli.py --readiness --target $target
