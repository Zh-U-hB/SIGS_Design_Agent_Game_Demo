#!/bin/bash

BACKEND_PORT=8888
FRONTEND_PORT=3111
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo "  ========================================"
echo "    SIGS - Start Script (macOS)"
echo "  ========================================"
echo ""

# ---------- helper: kill process on a port ----------
kill_port() {
    local port=$1
    local pids
    pids=$(lsof -ti :"$port" 2>/dev/null)
    if [ -n "$pids" ]; then
        for pid in $pids; do
            echo -e "    ${YELLOW}[KILL]${NC} Port $port occupied by PID $pid, killing..."
            kill -9 "$pid" 2>/dev/null
        done
        sleep 1
    fi
    echo -e "    ${GREEN}[OK]${NC}  Port $port free"
}

# ---------- 1/4 Check & clean ports ----------
echo "  [1/4] Checking ports..."
kill_port "$BACKEND_PORT"
kill_port "$FRONTEND_PORT"
echo ""

# ---------- 2/4 Check environment ----------
echo "  [2/4] Checking environment..."

if ! command -v uv &>/dev/null; then
    echo -e "    ${RED}[ERROR]${NC} uv not found. Install: pip install uv"
    exit 1
fi
echo -e "    ${GREEN}[OK]${NC}  uv"

if ! command -v node &>/dev/null; then
    echo -e "    ${RED}[ERROR]${NC} node not found. Install: https://nodejs.org/"
    exit 1
fi
echo -e "    ${GREEN}[OK]${NC}  node"
echo ""

# ---------- 3/4 Install dependencies ----------
echo "  [3/4] Installing dependencies..."

if [ ! -d "$BACKEND_DIR/.venv" ]; then
    echo "     Installing backend deps..."
    (cd "$BACKEND_DIR" && uv sync)
    if [ $? -ne 0 ]; then
        echo -e "    ${RED}[ERROR]${NC} Backend install failed"
        exit 1
    fi
    echo -e "    ${GREEN}[OK]${NC}  Backend deps installed"
else
    echo -e "    ${GREEN}[OK]${NC}  Backend deps ready"
fi

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "     Installing frontend deps..."
    (cd "$FRONTEND_DIR" && npm install)
    if [ $? -ne 0 ]; then
        echo -e "    ${RED}[ERROR]${NC} Frontend install failed"
        exit 1
    fi
    echo -e "    ${GREEN}[OK]${NC}  Frontend deps installed"
else
    echo -e "    ${GREEN}[OK]${NC}  Frontend deps ready"
fi
echo ""

# ---------- 4/4 Start services ----------
echo "  [4/4] Starting services..."

osascript -e "tell application \"Terminal\" to do script \"cd '$BACKEND_DIR' && uv run uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload; exec bash\"" \
    > /dev/null 2>&1
echo -e "    ${CYAN}[START]${NC} Backend  - http://localhost:$BACKEND_PORT"

sleep 2

osascript -e "tell application \"Terminal\" to do script \"cd '$FRONTEND_DIR' && npx live-server --port=$FRONTEND_PORT --open=/pages/landing.html; exec bash\"" \
    > /dev/null 2>&1
echo -e "    ${CYAN}[START]${NC} Frontend - http://localhost:$FRONTEND_PORT"
echo ""

echo "  ========================================"
echo "    Started!"
echo "  ----------------------------------------"
echo "    Frontend : http://localhost:$FRONTEND_PORT"
echo "    Backend  : http://localhost:$BACKEND_PORT"
echo "    API Docs : http://localhost:$BACKEND_PORT/docs"
echo "  ----------------------------------------"
echo "    Close this window will NOT stop services."
echo "    Close the Terminal windows to stop,"
echo "    or run: ./stop.sh"
echo "  ========================================"
echo ""
