Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Set-Location $PSScriptRoot

$preferredMajor = 3
$preferredMinor = 13
$venvPath = Join-Path $PSScriptRoot 'venv'
$venvPython = Join-Path $venvPath 'Scripts\python.exe'

function Get-CommandVersionText {
    param([string]$CommandPath)
    try {
        return (& $CommandPath --version) 2>&1
    } catch {
        return $null
    }
}

function Resolve-PythonCommand {
    $candidates = @(
        'py -3.13',
        'py -3.12',
        'py',
        'python'
    )

    foreach ($candidate in $candidates) {
        try {
            $versionText = if ($candidate -like 'py*') {
                & cmd /c "$candidate --version" 2>&1
            } else {
                & $candidate --version 2>&1
            }
            if ($LASTEXITCODE -eq 0 -and $versionText) {
                return @{
                    Command = $candidate
                    Version = [string]$versionText
                }
            }
        } catch {
        }
    }

    throw 'Python nije pronadjen. Instaliraj Python 3.13 i pokusaj ponovo.'
}

$python = Resolve-PythonCommand
Write-Host "Koristim interpreter: $($python.Command) [$($python.Version)]"

if ($python.Version -notmatch "Python $preferredMajor\.$preferredMinor") {
    Write-Warning "Preporuceni Python za ovaj projekat je $preferredMajor.$preferredMinor.x. Trenutna verzija je: $($python.Version)"
    Write-Warning 'Aplikacija moze raditi i na novijem Python-u, ali produkcioni target neka ostane 3.13 dok ne zakljucamo hosting/deploy.'
}

if (-not (Test-Path $venvPath)) {
    Write-Host 'Pravim venv...'
    if ($python.Command -like 'py*') {
        & cmd /c "$($python.Command) -m venv `"$venvPath`""
    } else {
        & $python.Command -m venv $venvPath
    }
}

Write-Host 'Instaliram dependencies...'
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r (Join-Path $PSScriptRoot 'requirements.txt')

Write-Host ''
Write-Host 'Setup zavrsen.'
Write-Host "Pokretanje app: $venvPython app.py"
Write-Host "Ili: powershell -ExecutionPolicy Bypass -File `"$PSScriptRoot\RUN_KITCHEN.ps1`""
