@echo off
REM Setup Docker containers for PostgreSQL and Redis
REM Run this once to create the containers

echo ========================================
echo Docker Setup for Local Development
echo ========================================
echo.

REM Check if Docker is running
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running!
    echo.
    echo Please install Docker Desktop from:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo Docker is installed and running!
echo.

REM Setup PostgreSQL
echo [1/2] Setting up PostgreSQL...
docker ps -a | findstr homework-postgres >nul 2>&1
if errorlevel 1 (
    echo   Creating PostgreSQL container...
    docker run -d --name homework-postgres -e POSTGRES_USER=ai_user -e POSTGRES_PASSWORD=ai_password -e POSTGRES_DB=ai_scheduler -p 5432:5432 postgres:15-alpine
    echo   PostgreSQL created!
) else (
    docker ps | findstr homework-postgres >nul 2>&1
    if errorlevel 1 (
        echo   PostgreSQL exists but not running. Starting...
        docker start homework-postgres
    ) else (
        echo   PostgreSQL already running!
    )
)

echo.

REM Setup Redis
echo [2/2] Setting up Redis...
docker ps -a | findstr homework-redis >nul 2>&1
if errorlevel 1 (
    echo   Creating Redis container...
    docker run -d --name homework-redis -p 6379:6379 redis:alpine
    echo   Redis created!
) else (
    docker ps | findstr homework-redis >nul 2>&1
    if errorlevel 1 (
        echo   Redis exists but not running. Starting...
        docker start homework-redis
    ) else (
        echo   Redis already running!
    )
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Your database connection strings:
echo   DATABASE_URL=postgresql://ai_user:ai_password@localhost:5432/ai_scheduler
echo   REDIS_URL=redis://localhost:6379/0
echo.
echo Add these to your .env file!
echo.
echo To stop containers:
echo   docker stop homework-postgres homework-redis
echo.
echo To start containers later:
echo   docker start homework-postgres homework-redis
echo.
pause
