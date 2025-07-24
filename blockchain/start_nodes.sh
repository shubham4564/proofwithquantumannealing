#!/bin/bash

# Start N blockchain nodes with different ports and keys
# Usage: ./start_10_nodes.sh [NUMBER_OF_NODES]
# Default: 10 nodes if no parameter provided
# Node ports: 10000-1000N
# API ports: 11000-1100N

# Get number of nodes from command line argument, default to 10
NUM_NODES=${1:-10}

# Validate input
if ! [[ "$NUM_NODES" =~ ^[0-9]+$ ]] || [ "$NUM_NODES" -lt 1 ] || [ "$NUM_NODES" -gt 100 ]; then
    echo "❌ Error: Please provide a valid number of nodes (1-100)"
    echo "Usage: $0 [NUMBER_OF_NODES]"
    echo "Example: $0 5    # Start 5 nodes"
    echo "Example: $0      # Start 10 nodes (default)"
    exit 1
fi

echo "Starting $NUM_NODES blockchain nodes..."

# Kill any existing python processes for clean start
pkill -f "run_node.py" 2>/dev/null || true
sleep 2

# Function to start a node
start_node() {
    local node_num=$1
    local node_port=$((10000 + node_num - 1))
    local api_port=$((11000 + node_num - 1))
    local key_file="keys/node${node_num}_private_key.pem"
    
    # Use genesis key for node 1, or generate/use existing keys for other nodes
    if [ $node_num -eq 1 ]; then
        key_file="keys/genesis_private_key.pem"
    elif [ ! -f "$key_file" ]; then
        # If node key doesn't exist, use staker key as fallback
        if [ -f "keys/staker_private_key.pem" ]; then
            key_file="keys/staker_private_key.pem"
        else
            echo "⚠️  Warning: Key file $key_file not found, using genesis key as fallback"
            key_file="keys/genesis_private_key.pem"
        fi
    fi
    
    echo "Starting Node $node_num - Port: $node_port, API: $api_port, Key: $key_file"
    
    python run_node.py \
        --ip localhost \
        --node_port $node_port \
        --api_port $api_port \
        --key_file $key_file \
        > logs/node${node_num}.log 2>&1 &
    
    echo "Node $node_num started with PID $!"
}

# Create logs directory if it doesn't exist
mkdir -p logs

# Start all nodes
echo "🚀 Launching $NUM_NODES nodes..."
for i in $(seq 1 $NUM_NODES); do
    start_node $i
    sleep 1  # Small delay between node starts
done

echo ""
echo "✅ All $NUM_NODES nodes started!"
echo "📡 Node ports: 10000-$((10000 + NUM_NODES - 1))"
echo "🌐 API ports: 11000-$((11000 + NUM_NODES - 1))"
echo "📝 Logs: logs/node1.log - logs/node${NUM_NODES}.log"
echo ""
echo "⏳ Wait 10 seconds for nodes to initialize and connect..."
sleep 10

echo "🔍 Checking node status..."
active_nodes=0
for i in $(seq 1 $NUM_NODES); do
    api_port=$((11000 + i - 1))
    echo -n "Node $i (API $api_port): "
    if curl -s "http://localhost:$api_port/api/v1/blockchain/" >/dev/null 2>&1; then
        echo "✅ Running"
        ((active_nodes++))
    else
        echo "❌ Not responding"
    fi
done

echo ""
echo "📊 Network Summary:"
echo "   🌐 Total Nodes Configured: $NUM_NODES"
echo "   ✅ Active Nodes: $active_nodes"
if command -v bc >/dev/null 2>&1; then
    health_pct=$(echo "scale=1; $active_nodes * 100 / $NUM_NODES" | bc -l 2>/dev/null || echo "0")
    echo "   📈 Network Health: ${health_pct}%"
else
    echo "   📈 Network Health: $active_nodes/$NUM_NODES nodes"
fi

if [ $active_nodes -eq $NUM_NODES ]; then
    echo "   🎉 Perfect! All nodes are running successfully."
elif [ $active_nodes -gt 0 ]; then
    echo "   ⚠️  Some nodes failed to start. Check logs for details."
else
    echo "   ❌ No nodes are responding. Check configuration and logs."
fi

echo ""
echo "💡 Useful commands:"
echo "   📊 Network analysis: python3 analyze_forgers.py"
echo "   🧪 Run transactions: python3 test_transactions.py --count 10"
echo "   📈 Monitor network: python3 analyze_forgers.py --watch 30"
echo "   🛑 Stop all nodes: pkill -f 'run_node.py'"
