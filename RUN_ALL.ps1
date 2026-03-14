# Cardio Digital Twin - Multi-App Launcher (PowerShell)
# Starts API server + 2 dashboard apps on different ports

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   CARDIO DIGITAL TWIN - MULTI-APP SETUP" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$PYTHON_PATH = "C:\Users\sssri\.local\bin\python3.14.exe"

# Check if Python exists
if (-not (Test-Path $PYTHON_PATH)) {
    Write-Host "Error: Python not found at $PYTHON_PATH" -ForegroundColor Red
    Write-Host "Please update the path in this script" -ForegroundColor Red
    exit 1
}

# Kill any existing Python processes
Write-Host "[0/3] Cleaning up existing processes..." -ForegroundColor Yellow
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# Start API server on port 5000
Write-Host "[1/3] Starting API Server on http://localhost:5000" -ForegroundColor Green
Start-Process -FilePath $PYTHON_PATH -ArgumentList "healthkit_api_server.py" -NoNewWindow
Start-Sleep -Seconds 3

# Start main Cardio app on port 8508
Write-Host "[2/3] Starting Main Dashboard on http://localhost:8508" -ForegroundColor Green
Start-Process -FilePath $PYTHON_PATH -ArgumentList "-m streamlit run app_final.py --logger.level=error" -NoNewWindow
Start-Sleep -Seconds 3

# Start Risk Alert app on port 8509
Write-Host "[3/3] Starting Risk Alert System on http://localhost:8509" -ForegroundColor Green
Start-Process -FilePath $PYTHON_PATH -ArgumentList "-m streamlit run app_risk_alert.py --server.port=8509 --logger.level=error" -NoNewWindow

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "   ALL SERVICES STARTED!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "API Server        : http://localhost:5000" -ForegroundColor Cyan
Write-Host "Main Dashboard    : http://localhost:8508" -ForegroundColor Cyan
Write-Host "Risk Alert System : http://localhost:8509" -ForegroundColor Cyan
Write-Host ""
Write-Host "Opening apps in browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

# Open all apps in browser
Start-Process "http://localhost:8508"
Start-Process "http://localhost:8509"

Write-Host ""
Write-Host "✅ Dashboard tabs opening in browser..." -ForegroundColor Green
Write-Host ""
