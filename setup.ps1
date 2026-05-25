# Quick Setup Script for Excel Verify Project
# Run this script to set up both backend and frontend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Excel Verify Project - Quick Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = $PSScriptRoot

# Backend Setup
Write-Host "1. Setting up Django Backend..." -ForegroundColor Yellow
Set-Location "$projectRoot\backend"

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "   Creating virtual environment..." -ForegroundColor Green
    python -m venv venv
}

Write-Host "   Activating virtual environment..." -ForegroundColor Green
& ".\venv\Scripts\Activate.ps1"

Write-Host "   Installing Python dependencies..." -ForegroundColor Green
pip install -r requirements.txt --quiet

Write-Host "   Running migrations..." -ForegroundColor Green
python manage.py makemigrations
python manage.py migrate

Write-Host "   Creating media directories..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path "media\uploads" | Out-Null

Write-Host "   ✓ Backend setup complete!" -ForegroundColor Green
Write-Host ""

# Frontend Setup
Write-Host "2. Setting up React Frontend..." -ForegroundColor Yellow
Set-Location "$projectRoot\frontend"

Write-Host "   Installing Node dependencies..." -ForegroundColor Green
npm install

Write-Host "   ✓ Frontend setup complete!" -ForegroundColor Green
Write-Host ""

# Summary
Set-Location $projectRoot
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Start Django backend:"
Write-Host "   cd backend"
Write-Host "   .\venv\Scripts\Activate.ps1"
Write-Host "   python manage.py runserver 8000"
Write-Host ""
Write-Host "2. Start React frontend (new terminal):"
Write-Host "   cd frontend"
Write-Host "   npm run dev"
Write-Host ""
Write-Host "3. Access application at: http://localhost:5173"
Write-Host ""
