#!/bin/bash
# Binary Trading System Startup Script for Linux/Mac
# This script starts all required services in separate terminals

echo "========================================"
echo "Binary Trading System Startup"
echo "========================================"
echo ""

# Check if Redis is running
echo "Checking Redis connection..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "[ERROR] Redis is not running!"
    echo "Please start Redis first:"
    echo "  - Linux: sudo service redis-server start"
    echo "  - macOS: brew services start redis"
    exit 1
fi
echo "[OK] Redis is running"
echo ""

# Detect terminal emulator
if command -v gnome-terminal > /dev/null 2>&1; then
    TERM_CMD="gnome-terminal --"
elif command -v xterm > /dev/null 2>&1; then
    TERM_CMD="xterm -e"
elif command -v konsole > /dev/null 2>&1; then
    TERM_CMD="konsole -e"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    TERM_CMD="osascript -e 'tell app \"Terminal\" to do script"
else
    echo "[WARNING] Could not detect terminal emulator"
    echo "Please run these commands manually in separate terminals:"
    echo "  1. python manage.py runserver"
    echo "  2. python manage.py run_price_generator"
    echo "  3. python manage.py close_expired_trades"
    echo "  4. python manage.py run_bot_simulator --trades-per-minute 3"
    exit 1
fi

# Start Django Server
echo "Starting Django Server..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e 'tell app "Terminal" to do script "cd '"$(pwd)"' && python manage.py runserver"'
else
    $TERM_CMD "bash -c 'python manage.py runserver; exec bash'" &
fi
sleep 2

# Start Price Generator
echo "Starting Price Generator..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e 'tell app "Terminal" to do script "cd '"$(pwd)"' && python manage.py run_price_generator --interval 0.5"'
else
    $TERM_CMD "bash -c 'python manage.py run_price_generator --interval 0.5; exec bash'" &
fi
sleep 2

# Start Trade Closer
echo "Starting Trade Closer..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e 'tell app "Terminal" to do script "cd '"$(pwd)"' && python manage.py close_expired_trades --interval 1"'
else
    $TERM_CMD "bash -c 'python manage.py close_expired_trades --interval 1; exec bash'" &
fi
sleep 2

# Ask about Bot Simulator
echo ""
read -p "Start Bot Simulator? (y/n): " START_BOTS
if [[ "$START_BOTS" == "y" || "$START_BOTS" == "Y" ]]; then
    echo "Starting Bot Simulator..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        osascript -e 'tell app "Terminal" to do script "cd '"$(pwd)"' && python manage.py run_bot_simulator --trades-per-minute 3"'
    else
        $TERM_CMD "bash -c 'python manage.py run_bot_simulator --trades-per-minute 3; exec bash'" &
    fi
fi

echo ""
echo "========================================"
echo "All services started!"
echo "========================================"
echo ""
echo "Services running:"
echo "  1. Django Server      - http://localhost:8000"
echo "  2. Price Generator    - Generating ticks every 0.5s"
echo "  3. Trade Closer       - Checking every 1s"
if [[ "$START_BOTS" == "y" || "$START_BOTS" == "Y" ]]; then
    echo "  4. Bot Simulator      - 3 trades/minute"
fi
echo ""
echo "WebSocket endpoints:"
echo "  - ws://localhost:8000/ws/binary-trading/prices/"
echo "  - ws://localhost:8000/ws/binary-trading/trades/"
echo "  - ws://localhost:8000/ws/binary-trading/admin/monitor/"
echo ""
echo "To stop all services, close the terminal windows or press Ctrl+C in each."
echo ""
