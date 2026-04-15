# CVScope Frontend - Start Script
# ==================================
# Run this from the cv-scope-frontend directory.

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

if (-not (Test-Path (Join-Path $scriptDir "node_modules"))) {
    Write-Host "node_modules not found. Running npm install..." -ForegroundColor Yellow
    npm install
}

Write-Host ""
Write-Host "Starting CVScope frontend at http://localhost:3000" -ForegroundColor Green
Write-Host "Make sure the backend is running first (start_backend.ps1)." -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

npm start