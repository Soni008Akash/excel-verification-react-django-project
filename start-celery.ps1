# Start Celery Worker for Excel Verification Project

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Celery Worker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to backend directory
Set-Location -Path "$PSScriptRoot\backend"

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Warning: Virtual environment not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "Starting Celery worker..." -ForegroundColor Green
Write-Host "Queue: RabbitMQ (localhost:5672)" -ForegroundColor Gray
Write-Host "Results: Redis (localhost:6379)" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop the worker" -ForegroundColor Yellow
Write-Host ""

# Start Celery worker
celery -A backend worker --loglevel=info --pool=solo
