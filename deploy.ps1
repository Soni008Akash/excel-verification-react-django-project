# Deploy to nginx Script
# This script builds the frontend and deploys to nginx

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Excel Verify - Deploy to nginx" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = $PSScriptRoot
$nginxPath = "C:\nginx"
$nginxHtmlPath = "$nginxPath\html\excel-verify"

# Build React frontend
Write-Host "1. Building React frontend..." -ForegroundColor Yellow
Set-Location "$projectRoot\frontend"
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ✗ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "   ✓ Build complete!" -ForegroundColor Green
Write-Host ""

# Copy build to nginx
Write-Host "2. Deploying to nginx..." -ForegroundColor Yellow

if (-not (Test-Path $nginxPath)) {
    Write-Host "   ✗ nginx not found at $nginxPath" -ForegroundColor Red
    Write-Host "   Please update the script with correct nginx path" -ForegroundColor Yellow
    exit 1
}

Write-Host "   Creating nginx html directory..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path $nginxHtmlPath | Out-Null

Write-Host "   Copying build files..." -ForegroundColor Green
Copy-Item -Path "dist\*" -Destination $nginxHtmlPath -Recurse -Force

Write-Host "   ✓ Files deployed!" -ForegroundColor Green
Write-Host ""

# Copy nginx config
Write-Host "3. Updating nginx configuration..." -ForegroundColor Yellow
$nginxConfPath = "$nginxPath\conf\nginx.conf"
$backupConfPath = "$nginxPath\conf\nginx.conf.backup"

# Backup existing config
if (Test-Path $nginxConfPath) {
    Write-Host "   Backing up existing config..." -ForegroundColor Green
    Copy-Item -Path $nginxConfPath -Destination $backupConfPath -Force
}

Write-Host "   Copying new configuration..." -ForegroundColor Green
Copy-Item -Path "$projectRoot\nginx.conf" -Destination $nginxConfPath -Force

Write-Host "   ✓ Configuration updated!" -ForegroundColor Green
Write-Host ""

# Test nginx config
Write-Host "4. Testing nginx configuration..." -ForegroundColor Yellow
Set-Location $nginxPath
& ".\nginx.exe" -t

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ✗ nginx configuration test failed!" -ForegroundColor Red
    Write-Host "   Restoring backup..." -ForegroundColor Yellow
    Copy-Item -Path $backupConfPath -Destination $nginxConfPath -Force
    exit 1
}

Write-Host "   ✓ Configuration valid!" -ForegroundColor Green
Write-Host ""

# Reload nginx
Write-Host "5. Reloading nginx..." -ForegroundColor Yellow

# Check if nginx is running
$nginxProcess = Get-Process nginx -ErrorAction SilentlyContinue

if ($nginxProcess) {
    Write-Host "   Reloading nginx..." -ForegroundColor Green
    & ".\nginx.exe" -s reload
    Write-Host "   ✓ nginx reloaded!" -ForegroundColor Green
} else {
    Write-Host "   Starting nginx..." -ForegroundColor Green
    Start-Process -FilePath ".\nginx.exe" -WindowStyle Hidden
    Start-Sleep -Seconds 2
    Write-Host "   ✓ nginx started!" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Important:" -ForegroundColor Yellow
Write-Host "1. Make sure Django backend is running:"
Write-Host "   cd backend"
Write-Host "   .\venv\Scripts\Activate.ps1"
Write-Host "   python manage.py runserver 8000"
Write-Host ""
Write-Host "2. Access application at: http://localhost"
Write-Host ""
Write-Host "To stop nginx:" -ForegroundColor Yellow
Write-Host "   cd C:\nginx"
Write-Host "   .\nginx.exe -s stop"
Write-Host ""

Set-Location $projectRoot
