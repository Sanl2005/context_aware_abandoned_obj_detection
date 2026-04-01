@echo off
echo ===================================================
echo Starting Context-Aware Abandonment Detection System
echo ===================================================

echo 1. Starting Redis...
if exist "C:\Program Files\Redis\redis-server.exe" (
    start "Redis Server" "C:\Program Files\Redis\redis-server.exe"
) else (
    echo Redis executable not found at C:\Program Files\Redis\redis-server.exe
    echo Attempting to rely on PATH...
    start "Redis Server" redis-server
)

timeout /t 2 /nobreak >nul

echo 2. Starting Rails Backend (Port 3000)...
cd rails_backend
start "Rails Backend" cmd /k "bundle exec rails s"
cd ..

timeout /t 5 /nobreak >nul

echo 3. Starting ML Service (Port 5000)...
cd ml_service
start "ML Service" cmd /k "..\.venv\Scripts\python.exe app.py"
cd ..

echo 4. Starting Frontend Dashboard (Port 3001)...
cd frontend_dashboard
start "Frontend Dashboard" cmd /k "npm start"
cd ..

echo ===================================================
echo All services launched in separate windows.
echo - Rails API: http://localhost:3000
echo - ML Service: http://localhost:5000
echo - Frontend: http://localhost:3001
echo ===================================================
pause
