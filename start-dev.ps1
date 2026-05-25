# Start Development Servers Script
# This script starts both backend and frontend in development mode

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Excel Verify - Start Development Servers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = $PSScriptRoot

# Start Django backend in new window
Write-Host "Starting Django backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\backend'; .\venv\Scripts\Activate.ps1; Write-Host 'Django Backend Server' -ForegroundColor Green; python manage.py runserver 8000"

Start-Sleep -Seconds 2

# Start React frontend in new window
Write-Host "Starting React frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\frontend'; Write-Host 'React Frontend Server' -ForegroundColor Green; npm run dev"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Servers Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend (Django): http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend (React): http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "Check the new terminal windows for server output" -ForegroundColor Yellow
Write-Host "Press Ctrl+C in each window to stop the servers" -ForegroundColor Yellow
Write-Host ""
