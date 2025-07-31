#!/bin/bash

# Decentralized Blockchain Network Startup Scripts
# ================================================

# Single Computer Setup (6 Nodes)
# ===============================

echo "🚀 Starting 6-node blockchain network on single computer..."

# Kill any existing processes on our ports
echo "🧹 Cleaning up existing processes..."
pkill -f "run_node.py" 2>/dev/null || true

# Wait for cleanup
sleep 2

# Start Node 1 (Bootstrap/Genesis Node)
echo "🔄 Starting Node 1 (Bootstrap)..."
cd blockchain
python run_node.py \
    --ip 127.0.0.1 \
    --node_port 10000 \
    --api_port 11000 \
    --key_file ./keys/genesis_private_key.pem \
    --p2p_mode enhanced &

NODE1_PID=$!
echo "✅ Node 1 started (PID: $NODE1_PID) - Bootstrap node"
sleep 3

# Start Node 2
echo "🔄 Starting Node 2..."
python run_node.py \
    --ip 127.0.0.1 \
    --node_port 10001 \
    --api_port 11001 \
    --p2p_mode enhanced &

NODE2_PID=$!
echo "✅ Node 2 started (PID: $NODE2_PID)"
sleep 2

# Start Node 3
echo "🔄 Starting Node 3..."
python run_node.py \
    --ip 127.0.0.1 \
    --node_port 10002 \
    --api_port 11002 \
    --p2p_mode enhanced &

NODE3_PID=$!
echo "✅ Node 3 started (PID: $NODE3_PID)"
sleep 2

# Start Node 4
echo "🔄 Starting Node 4..."
python run_node.py \
    --ip 127.0.0.1 \
    --node_port 10003 \
    --api_port 11003 \
    --p2p_mode enhanced &

NODE4_PID=$!
echo "✅ Node 4 started (PID: $NODE4_PID)"
sleep 2

# Start Node 5
echo "🔄 Starting Node 5..."
python run_node.py \
    --ip 127.0.0.1 \
    --node_port 10004 \
    --api_port 11004 \
    --p2p_mode enhanced &

NODE5_PID=$!
echo "✅ Node 5 started (PID: $NODE5_PID)"
sleep 2

# Start Node 6
echo "🔄 Starting Node 6..."
python run_node.py \
    --ip 127.0.0.1 \
    --node_port 10005 \
    --api_port 11005 \
    --p2p_mode enhanced &

NODE6_PID=$!
echo "✅ Node 6 started (PID: $NODE6_PID)"

# Wait for all nodes to initialize
echo "⏳ Waiting for nodes to initialize..."
sleep 10

# Connect nodes to each other (P2P network formation)
echo "🔗 Connecting nodes to form P2P network..."

# Connect Node 2 to Node 1
curl -X POST "http://127.0.0.1:11001/api/v1/blockchain/connect-peer/" \
    -H "Content-Type: application/json" \
    -d '{"ip": "127.0.0.1", "port": 10000}' \
    2>/dev/null || echo "⚠️ Node 2 -> Node 1 connection may have failed"

# Connect Node 3 to Node 1 and Node 2
curl -X POST "http://127.0.0.1:11002/api/v1/blockchain/connect-peer/" \
    -H "Content-Type: application/json" \
    -d '{"ip": "127.0.0.1", "port": 10000}' \
    2>/dev/null || echo "⚠️ Node 3 -> Node 1 connection may have failed"

curl -X POST "http://127.0.0.1:11002/api/v1/blockchain/connect-peer/" \
    -H "Content-Type: application/json" \
    -d '{"ip": "127.0.0.1", "port": 10001}' \
    2>/dev/null || echo "⚠️ Node 3 -> Node 2 connection may have failed"

# Connect Node 4 to previous nodes
curl -X POST "http://127.0.0.1:11003/api/v1/blockchain/connect-peer/" \
    -H "Content-Type: application/json" \
    -d '{"ip": "127.0.0.1", "port": 10000}' \
    2>/dev/null || echo "⚠️ Node 4 -> Node 1 connection may have failed"

curl -X POST "http://127.0.0.1:11003/api/v1/blockchain/connect-peer/" \
    -H "Content-Type: application/json" \
    -d '{"ip": "127.0.0.1", "port": 10002}' \
    2>/dev/null || echo "⚠️ Node 4 -> Node 3 connection may have failed"

# Connect Node 5 to previous nodes
curl -X POST "http://127.0.0.1:11004/api/v1/blockchain/connect-peer/" \
    -H "Content-Type: application/json" \
    -d '{"ip": "127.0.0.1", "port": 10000}' \
    2>/dev/null || echo "⚠️ Node 5 -> Node 1 connection may have failed"

curl -X POST "http://127.0.0.1:11004/api/v1/blockchain/connect-peer/" \
    -H "Content-Type: application/json" \
    -d '{"ip": "127.0.0.1", "port": 10003}' \
    2>/dev/null || echo "⚠️ Node 5 -> Node 4 connection may have failed"

# Connect Node 6 to previous nodes
curl -X POST "http://127.0.0.1:11005/api/v1/blockchain/connect-peer/" \
    -H "Content-Type: application/json" \
    -d '{"ip": "127.0.0.1", "port": 10000}' \
    2>/dev/null || echo "⚠️ Node 6 -> Node 1 connection may have failed"

curl -X POST "http://127.0.0.1:11005/api/v1/blockchain/connect-peer/" \
    -H "Content-Type: application/json" \
    -d '{"ip": "127.0.0.1", "port": 10004}' \
    2>/dev/null || echo "⚠️ Node 6 -> Node 5 connection may have failed"

# Wait for P2P connections to establish
echo "⏳ Allowing P2P connections to establish..."
sleep 5

# Display network status
echo ""
echo "🌐 DECENTRALIZED BLOCKCHAIN NETWORK STATUS"
echo "========================================="
echo ""
echo "📊 Node Information:"
echo "Node 1 (Bootstrap): http://127.0.0.1:11000 (P2P: 10000) - PID: $NODE1_PID"
echo "Node 2:             http://127.0.0.1:11001 (P2P: 10001) - PID: $NODE2_PID"
echo "Node 3:             http://127.0.0.1:11002 (P2P: 10002) - PID: $NODE3_PID"
echo "Node 4:             http://127.0.0.1:11003 (P2P: 10003) - PID: $NODE4_PID"
echo "Node 5:             http://127.0.0.1:11004 (P2P: 10004) - PID: $NODE5_PID"
echo "Node 6:             http://127.0.0.1:11005 (P2P: 10005) - PID: $NODE6_PID"
echo ""
echo "🔗 Key Endpoints:"
echo "Blockchain Explorer:     http://127.0.0.1:11000/api/v1/blockchain/"
echo "Performance Metrics:     http://127.0.0.1:11000/api/v1/blockchain/performance-metrics/"
echo "Network Status:          http://127.0.0.1:11000/api/v1/blockchain/network-status/"
echo "Transaction Submission:  http://127.0.0.1:11000/api/v1/blockchain/transaction/"
echo ""
echo "📈 Additional Node APIs:"
echo "Node 2 API: http://127.0.0.1:11001/api/v1/blockchain/"
echo "Node 3 API: http://127.0.0.1:11002/api/v1/blockchain/"
echo "Node 4 API: http://127.0.0.1:11003/api/v1/blockchain/"
echo "Node 5 API: http://127.0.0.1:11004/api/v1/blockchain/"
echo "Node 6 API: http://127.0.0.1:11005/api/v1/blockchain/"
echo ""

# Function to check network health
check_network_health() {
    echo "🏥 Checking Network Health..."
    
    active_nodes=0
    total_nodes=6
    
    for port in 11000 11001 11002 11003 11004 11005; do
        if curl -s "http://127.0.0.1:$port/api/v1/blockchain/" >/dev/null 2>&1; then
            active_nodes=$((active_nodes + 1))
            echo "✅ Node on port $port is responsive"
        else
            echo "❌ Node on port $port is not responsive"
        fi
    done
    
    echo ""
    echo "📊 Network Health: $active_nodes/$total_nodes nodes active ($(( active_nodes * 100 / total_nodes ))%)"
    
    if [ $active_nodes -ge 4 ]; then
        echo "🟢 Network is healthy (majority consensus possible)"
    elif [ $active_nodes -ge 2 ]; then
        echo "🟡 Network is partially healthy (limited consensus)"
    else
        echo "🔴 Network is unhealthy (insufficient nodes for consensus)"
    fi
}

# Initial health check
echo "⏳ Performing initial network health check..."
sleep 3
check_network_health

echo ""
echo "🎯 Test the Network:"
echo "1. Submit a transaction:"
echo "   curl -X POST http://127.0.0.1:11000/api/v1/blockchain/transaction/ \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"sender\": \"test_sender\", \"receiver\": \"test_receiver\", \"amount\": 10}'"
echo ""
echo "2. View blockchain:"
echo "   curl http://127.0.0.1:11000/api/v1/blockchain/"
echo ""
echo "3. Check node connections:"
echo "   curl http://127.0.0.1:11000/api/v1/blockchain/network-status/"
echo ""

# Store process IDs for cleanup
echo "Process IDs stored in /tmp/blockchain_nodes.pids"
echo "$NODE1_PID $NODE2_PID $NODE3_PID $NODE4_PID $NODE5_PID $NODE6_PID" > /tmp/blockchain_nodes.pids

echo "🌐 Network is running! Press Ctrl+C to stop all nodes or run './stop_network.sh'"

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down blockchain network..."
    
    if [ -f /tmp/blockchain_nodes.pids ]; then
        PIDS=$(cat /tmp/blockchain_nodes.pids)
        for pid in $PIDS; do
            if kill -0 $pid 2>/dev/null; then
                echo "Stopping process $pid..."
                kill $pid
            fi
        done
        rm -f /tmp/blockchain_nodes.pids
    fi
    
    # Also kill by process name as backup
    pkill -f "run_node.py" 2>/dev/null || true
    
    echo "✅ All nodes stopped"
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM

# Keep script running and periodically check health
while true; do
    sleep 30
    
    # Check if any processes have died
    if [ -f /tmp/blockchain_nodes.pids ]; then
        PIDS=$(cat /tmp/blockchain_nodes.pids)
        dead_count=0
        for pid in $PIDS; do
            if ! kill -0 $pid 2>/dev/null; then
                dead_count=$((dead_count + 1))
            fi
        done
        
        if [ $dead_count -gt 0 ]; then
            echo "⚠️ Warning: $dead_count nodes have stopped"
            check_network_health
        fi
    fi
done
