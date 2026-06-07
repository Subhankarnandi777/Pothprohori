# PowerShell Script to run FastAPI backend
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
cd "$ScriptDir\..\backend"

Write-Host "Installing backend dependencies from requirements.txt..." -ForegroundColor Cyan
pip install -r requirements.txt -q

Write-Host "Starting FastAPI Development Server..." -ForegroundColor Green
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
