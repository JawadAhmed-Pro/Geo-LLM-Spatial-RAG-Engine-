@echo off
setlocal
title Geo-LLM Spatial RAG Engine Runner

echo ============================================================
echo   GEO-LLM SPATIAL RAG ENGINE - STARTUP SEQUENCE
echo ============================================================

echo [1/3] Starting PostGIS Database (Docker)...
docker compose up -d
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not running or not installed. Please start Docker Desktop.
    pause
    exit /b %ERRORLEVEL%
)

echo [2/3] Starting FastAPI Backend AI Brain in a new window...
:: Starting in a separate window so logs are visible and it doesn't block this script
start "GeoLLM-Backend" cmd /k "python -m uvicorn backend.main:app --port 8000"

echo [3/3] Starting Next.js Command Center UI in a new window...
cd frontend
start "GeoLLM-Frontend" cmd /k "npm run dev"

echo.
echo ============================================================
echo   STACK IS INITIALIZING...
echo   Backend: http://localhost:8000
echo   Frontend: http://localhost:3000
echo ============================================================

echo Waiting 5 seconds for servers to warm up...
timeout /t 5 >nul

echo Opening browser to http://localhost:3000...
start http://localhost:3000

echo.
echo Sequence Complete. Keep the other two windows open!
pause
