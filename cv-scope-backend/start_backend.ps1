# CVScope Backend - Start Script
# ================================
# Fixes the PowerShell execution policy issue AND activates the venv.
# Run this from the cv-scope-backend directory.
#
# If you get "cannot be loaded because running scripts is disabled", run ONCE:
#   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then you can always just double-click this file.

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$venvPython = Join-Path $scriptDir ".venv\Scripts\python.exe"
$venvActivate = Join-Path $scriptDir ".venv\Scripts\Activate.ps1"

if (-not (Test-Path $venvPython)) {
    Write-Host "Virtual environment not found. Creating one now..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "venv created." -ForegroundColor Green
}

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& $venvActivate

Write-Host "Installing / verifying dependencies from requirements.txt..." -ForegroundColor Cyan
pip install -r requirements.txt --quiet

# Check if spaCy model is installed
$modelCheck = & $venvPython -c "import spacy; spacy.load('en_core_web_sm')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Downloading spaCy model en_core_web_sm..." -ForegroundColor Yellow
    python -m spacy download en_core_web_sm
}

Write-Host ""
Write-Host "Starting CVScope backend at http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

uvicorn main:app --reload --host 127.0.0.1 --port 8000 --log-level info