#!/bin/bash

# Stop all blockchain network nodes
# ================================

echo "🛑 Stopping blockchain network..."

# Method 1: Use stored PIDs
if [ -f /tmp/blockchain_nodes.pids ]; then
    echo "📋 Found PID file for single computer network"
    PIDS=$(cat /tmp/blockchain_nodes.pids)
    for pid in $PIDS; do
        if kill -0 $pid 2>/dev/null; then
            echo "Stopping process $pid..."
            kill $pid
        fi
    done
    rm -f /tmp/blockchain_nodes.pids
    echo "✅ Single computer network nodes stopped"
fi

# Method 2: Stop distributed node
if [ -f /tmp/blockchain_node.pid ]; then
    echo "📋 Found PID file for distributed node"
    PID=$(cat /tmp/blockchain_node.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "Stopping distributed node process $PID..."
        kill $PID
    fi
    rm -f /tmp/blockchain_node.pid
    echo "✅ Distributed node stopped"
fi

# Method 3: Kill all blockchain processes by name (fallback)
echo "🧹 Cleaning up any remaining blockchain processes..."
pkill -f "run_node.py" 2>/dev/null && echo "✅ Additional processes stopped" || echo "ℹ️ No additional processes found"

# Wait for processes to terminate
sleep 2

# Check if any processes are still running
remaining=$(pgrep -f "run_node.py" | wc -l)
if [ $remaining -gt 0 ]; then
    echo "⚠️ $remaining processes still running, force killing..."
    pkill -9 -f "run_node.py"
    sleep 1
fi

# Clean up any remaining port bindings
echo "🔍 Checking for remaining port usage..."
for port in 11000 11001 11002 11003 11004 11005 10000 10001 10002 10003 10004 10005; do
    pid=$(lsof -t -i:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "Killing process $pid using port $port"
        kill -9 $pid 2>/dev/null || true
    fi
done

echo "✅ All blockchain nodes stopped successfully"
echo "🌐 Network is now offline"
