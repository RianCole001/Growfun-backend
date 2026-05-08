@echo off
REM Binary Trading System Startup Script for Windows
REM This script starts all required services in separate windows

echo ========================================
echo Binary Trading System Startup
echo ========================================
echo.

REM Check if Redis is running
echo Checking Redis connection...
redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Redis is not running!
    echo Please start Redis first:
    echo   - Windows: wsl sudo service redis-server start
    echo   - Or download Redis for Windows
    pause
    exit /b 1
)
echo [OK] Redis is running
echo.

REM Start Django Server
echo Starting Django Server...
start "Django Server" cmd /k "python manage.py runserver"
timeout /t 2 >nul

REM Start Price Generator
echo Starting Price Generator...
start "Price Generator" cmd /k "python manage.py run_price_generator --interval 0.5"
timeout /t 2 >nul

REM Start Trade Closer
echo Starting Trade Closer...
start "Trade Closer" cmd /k "python manage.py close_expired_trades --interval 1"
timeout /t 2 >nul

REM Ask about Bot Simulator
echo.
set /p START_BOTS="Start Bot Simulator? (y/n): "
if /i "%START_BOTS%"=="y" (
    echo Starting Bot Simulator...
    start "Bot Simulator" cmd /k "python manage.py run_bot_simulator --trades-per-minute 3"
)

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo Services running:
echo   1. Django Server      - http://localhost:8000
echo   2. Price Generator    - Generating ticks every 0.5s
echo   3. Trade Closer       - Checking every 1s
if /i "%START_BOTS%"=="y" (
    echo   4. Bot Simulator      - 3 trades/minute
)
echo.
echo WebSocket endpoints:
echo   - ws://localhost:8000/ws/binary-trading/prices/
echo   - ws://localhost:8000/ws/binary-trading/trades/
echo   - ws://localhost:8000/ws/binary-trading/admin/monitor/
echo.
echo Press any key to stop all services...
pause >nul

REM Stop all services
echo.
echo Stopping services...
taskkill /FI "WindowTitle eq Django Server*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Price Generator*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Trade Closer*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Bot Simulator*" /T /F >nul 2>&1

echo All services stopped.
pause
