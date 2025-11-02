@echo off
REM Quick Start Script for Local Development
REM This script helps you start all services with one command

echo ========================================
echo AI Outbound Meeting Scheduler - Local
echo ========================================
echo.

REM Check if Docker services are running
echo [1/3] Checking Docker services...
docker ps | findstr homework-postgres >nul 2>&1
if errorlevel 1 (
    echo   - PostgreSQL: Not running. Start with: docker start homework-postgres
) else (
    echo   - PostgreSQL: Running
)

docker ps | findstr homework-redis >nul 2>&1
if errorlevel 1 (
    echo   - Redis: Not running. Start with: docker start homework-redis
) else (
    echo   - Redis: Running
)

echo.
echo [2/3] Checking environment...
if not exist .env (
    echo   WARNING: .env file not found!
    echo   Copy .env.example to .env and configure it first.
    pause
    exit /b 1
)

if not exist backend\service-account.json (
    echo   WARNING: backend\service-account.json not found!
    echo   You need Google Calendar credentials.
    pause
    exit /b 1
)

echo   - Environment configured
echo.

echo [3/3] Ready to start services!
echo.
echo You need to open 3 separate terminals:
echo.
echo   Terminal 1 (Backend API):
echo   cd c:\Users\A\Desktop\HomeWork
echo   py -3.13 -m uvicorn backend.main:app --reload
echo.
echo   Terminal 2 (Celery Worker):
echo   cd c:\Users\A\Desktop\HomeWork
echo   py -3.13 -m celery -A backend.workers.celery_app worker --loglevel=info --pool=solo
echo.
echo   Terminal 3 (Frontend):
echo   cd c:\Users\A\Desktop\HomeWork\frontend
echo   npm run dev
echo.
echo ========================================
echo After starting all services, visit:
echo http://localhost:5173
echo ========================================
echo.
pause
