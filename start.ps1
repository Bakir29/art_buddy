# Art Buddy - Unified Startup Script
# This script ensures clean startup of both backend and frontend servers

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🎨 Art Buddy - Starting Application" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Kill any existing processes
Write-Host "🧹 Cleaning up existing processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -eq "node" -or $_.ProcessName -eq "python"} | Where-Object {$_.Path -like "*art_buddy*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Check if ports are free
$backendPort = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$frontendPort = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue

if ($backendPort) {
    Write-Host "⚠️  Port 8000 is still in use. Waiting..." -ForegroundColor Red
    Start-Sleep -Seconds 3
}

if ($frontendPort) {
    Write-Host "⚠️  Port 3000 is still in use. Waiting..." -ForegroundColor Red
    Start-Sleep -Seconds 3
}

# Start Backend
Write-Host ""
Write-Host "🚀 Starting Backend Server (Port 8000)..." -ForegroundColor Green
$backend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; .\.venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload --port 8000" -PassThru -WindowStyle Normal
Start-Sleep -Seconds 5

# Verify backend
$backendCheck = curl http://localhost:8000 -UseBasicParsing -ErrorAction SilentlyContinue
if ($backendCheck) {
    Write-Host "✅ Backend is running successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Backend failed to start!" -ForegroundColor Red
}

# Start Frontend
Write-Host ""
Write-Host "🚀 Starting Frontend Server (Port 3000)..." -ForegroundColor Green
$frontend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev" -PassThru -WindowStyle Normal
Start-Sleep -Seconds 8

# Verify frontend
$frontendCheck = curl http://localhost:3000 -UseBasicParsing -ErrorAction SilentlyContinue
if ($frontendCheck) {
    Write-Host "✅ Frontend is running successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend failed to start!" -ForegroundColor Red
}

# Final Status
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✨ Art Buddy is Ready!" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "📍 Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "📍 API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "🔑 Test Login:" -ForegroundColor Yellow
Write-Host "   Email: test@example.com" -ForegroundColor White
Write-Host "   Pass:  testpass123" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to open the app in your browser..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Start-Process "http://localhost:3000"
