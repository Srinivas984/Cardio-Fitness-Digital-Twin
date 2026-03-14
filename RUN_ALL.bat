@echo off
REM Cardio Digital Twin - Multi-App Launcher
REM Starts API server + 2 dashboard apps on different ports

echo.
echo ============================================
echo   CARDIO DIGITAL TWIN - MULTI-APP SETUP
echo ============================================
echo.
echo Starting services...
echo.

REM Get Python path
set PYTHON_PATH=C:\Users\sssri\.local\bin\python3.14.exe

REM Check if Python exists
if not exist "%PYTHON_PATH%" (
    echo Error: Python not found at %PYTHON_PATH%
    echo Please update the path in this script
    pause
    exit /b 1
)

REM Start API server on port 5000
echo [1/3] Starting API Server on http://localhost:5000
start "API Server" cmd /k "%PYTHON_PATH% healthkit_api_server.py"

REM Wait a bit for API to start
timeout /t 3 /nobreak

REM Start main Cardio app on port 8508
echo [2/3] Starting Main Dashboard on http://localhost:8508
start "Cardio Coach" cmd /k "%PYTHON_PATH% -m streamlit run app_final.py --logger.level=error"

REM Wait a bit for first app to start
timeout /t 3 /nobreak

REM Start Risk Alert app on port 8509
echo [3/3] Starting Risk Alert System on http://localhost:8509
start "Cardio Risk Alert" cmd /k "%PYTHON_PATH% -m streamlit run app_risk_alert.py --server.port=8509 --logger.level=error"

REM Wait for all to start
timeout /t 2 /nobreak

echo.
echo ============================================
echo   ALL SERVICES STARTED!
echo ============================================
echo.
echo API Server:         http://localhost:5000
echo Main Dashboard:     http://localhost:8508
echo Risk Alert System:  http://localhost:8509
echo.
echo All windows will remain open. Close any to stop that service.
echo.
pause
