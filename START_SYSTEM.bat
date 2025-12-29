@echo off
REM ===============================================
REM  Distributed Cloud Storage System - Quick Start
REM ===============================================

echo ========================================
echo  Starting Distributed Cloud Storage
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [1/3] Starting Network Controller...
start "Network Controller" cmd /k "python network_controller.py"
timeout /t 3 /nobreak >nul

echo [2/3] Starting Web API Server...
start "Web API Server" cmd /k "python web_api.py"
timeout /t 3 /nobreak >nul

echo [3/3] Starting Demo Node (VM1)...
start "Storage Node VM1" cmd /k "python node.py --node-id VM1 --port 5001 --cpu 4 --cpu-speed 2.5 --ram 8 --storage 500 --bandwidth 1000"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo  System Started Successfully!
echo ========================================
echo.
echo Network Controller: localhost:5000
echo Web API Server:     http://localhost:8080
echo Storage Node:       VM1 on port 5001
echo.
echo Admin Dashboard:    http://localhost:8080/admin
echo User Interface:     http://localhost:8080
echo.
echo Press any key to open the web interface...
pause >nul

start http://localhost:8080

echo.
echo System is running in background windows.
echo Close those windows to stop the system.
echo.
pause
