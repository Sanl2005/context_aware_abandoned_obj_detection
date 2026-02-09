@echo off
REM Quick Start Script for Object Detection Dashboard (Windows)
REM This starts all required services in the correct order

echo ========================================
echo  SentinelEye Object Detection System
echo ========================================
echo.

REM Step 1: Start ML Service (Flask)
echo [1/3] Starting ML Service (Video Feed + Object Detection)...
cd ml_service
start "ML Service" cmd /k "python app.py"
echo       ML Service starting on http://127.0.0.1:5000
timeout /t 3 /nobreak >nul
cd ..

REM Step 2: Start Rails Backend (Optional)
echo.
echo [2/3] Starting Rails Backend (API)...
cd rails_backend
start "Rails Backend" cmd /k "rails server -p 3000"
echo       Rails Backend starting on http://127.0.0.1:3000
timeout /t 5 /nobreak >nul
cd ..

REM Step 3: Start Frontend Dashboard
echo.
echo [3/3] Starting Frontend Dashboard...
cd frontend_dashboard
start "Frontend Dashboard" cmd /k "npm start"
echo       Frontend will open at http://localhost:3001
cd ..

echo.
echo ========================================
echo  All services started successfully!
echo ========================================
echo.
echo  Open your browser to: http://localhost:3001
echo.
echo  Services are running in separate windows.
echo  Close each window to stop the services.
echo.
echo  Press any key to exit this launcher...
pause >nul
