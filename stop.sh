#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo ""
echo "  ========================================"
echo "    SIGS - Stop All Services"
echo "  ========================================"
echo ""

kill_port() {
    local port=$1
    local label=$2
    local pids
    pids=$(lsof -ti :"$port" 2>/dev/null)
    if [ -n "$pids" ]; then
        for pid in $pids; do
            echo -e "    ${YELLOW}[KILL]${NC} $label port $port - PID $pid"
            kill -9 "$pid" 2>/dev/null
        done
    else
        echo -e "    ${GREEN}[OK]${NC}  $label port $port (not running)"
    fi
}

kill_port 8888 "Backend"
kill_port 3111 "Frontend"

echo ""
echo "  All services stopped."
echo ""
