#!/bin/bash

# Distributed Blockchain Network Setup
# ====================================
# Run this script on each of the 6 computers in your subnet

# Configuration - MODIFY THESE FOR YOUR NETWORK
SUBNET_PREFIX="10.283.0"  # Default - will auto-detect if possible
TOTAL_COMPUTERS=6

# Detect computer ID based on IP address or set manually
COMPUTER_ID=""

# Function to get local IP address (cross-platform)
get_local_ip() {
    # Try different methods to get the local IP
    local ip=""
    
    # Method 1: Linux style (hostname -I)
    if command -v hostname >/dev/null 2>&1; then
        ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    fi
    
    # Method 2: macOS/BSD style (ifconfig)
    if [[ -z "$ip" ]]; then
        ip=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
    fi
    
    # Method 3: Using route command
    if [[ -z "$ip" ]]; then
        ip=$(route get default 2>/dev/null | grep interface | awk '{print $2}' | xargs ifconfig 2>/dev/null | grep "inet " | awk '{print $2}' | head -1)
    fi
    
    # Method 4: Python fallback
    if [[ -z "$ip" ]]; then
        ip=$(python3 -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8', 80)); print(s.getsockname()[0]); s.close()" 2>/dev/null)
    fi
    
    echo "$ip"
}

# Function to auto-detect subnet from local IP
detect_subnet() {
    local_ip=$(get_local_ip)
    if [[ $local_ip =~ ^([0-9]+\.[0-9]+\.[0-9]+)\.[0-9]+$ ]]; then
        detected_subnet="${BASH_REMATCH[1]}"
        echo "🔍 Auto-detected subnet: ${detected_subnet}.x (from IP: $local_ip)"
        
        # Auto-update subnet if different from default
        if [[ ! $local_ip =~ ^${SUBNET_PREFIX//./\\.}\. ]]; then
            echo "⚠️ Current configuration expects subnet: ${SUBNET_PREFIX}.x"
            echo "💡 But your IP suggests subnet: ${detected_subnet}.x"
            echo "✅ Auto-updating to use detected subnet: ${detected_subnet}.x"
            SUBNET_PREFIX="$detected_subnet"
        fi
    fi
}

# Function to auto-detect computer ID from IP
detect_computer_id() {
    local_ip=$(get_local_ip)
    last_octet=$(echo "$local_ip" | cut -d'.' -f4)
    
    if [[ $last_octet =~ ^[0-9]+$ ]] && [ $last_octet -le $TOTAL_COMPUTERS ]; then
        COMPUTER_ID=$last_octet
    else
        echo "❌ Could not auto-detect computer ID from IP address"
        echo "Current IP: $local_ip"
        echo "Expected format: ${SUBNET_PREFIX}.X where X is 1-${TOTAL_COMPUTERS}"
        echo ""
        echo "Please set COMPUTER_ID manually in this script or use:"
        echo "./start_distributed_node.sh <computer_id>"
        exit 1
    fi
}

# Parse command line arguments
if [ $# -eq 1 ]; then
    COMPUTER_ID=$1
    # Still auto-detect subnet even when computer ID is provided
    detect_subnet
elif [ $# -eq 0 ]; then
    # Auto-detect subnet first, then computer ID
    detect_subnet
    detect_computer_id
else
    echo "Usage: $0 [computer_id]"
    echo "Example: $0 1  (for first computer)"
    exit 1
fi

# Validate computer ID
if ! [[ "$COMPUTER_ID" =~ ^[1-6]$ ]]; then
    echo "❌ Computer ID must be between 1 and $TOTAL_COMPUTERS"
    exit 1
fi

echo "🌐 Starting Distributed Blockchain Node"
echo "======================================="
echo "Computer ID: $COMPUTER_ID"
echo "Total Computers: $TOTAL_COMPUTERS"
echo "Subnet: ${SUBNET_PREFIX}.x"
echo ""

# Get local IP address
LOCAL_IP=$(get_local_ip)
echo "📍 Local IP Address: $LOCAL_IP"

# Validate we got a valid IP
if [[ -z "$LOCAL_IP" ]]; then
    echo "❌ Could not detect local IP address"
    echo "Please check your network connection or set LOCAL_IP manually"
    exit 1
fi

# Validate IP is in expected subnet
if [[ ! $LOCAL_IP =~ ^${SUBNET_PREFIX//./\\.}\. ]]; then
    echo "⚠️ Warning: Local IP ($LOCAL_IP) doesn't match expected subnet ($SUBNET_PREFIX.x)"
    echo "Continuing anyway..."
fi

# Kill any existing blockchain processes
echo "🧹 Cleaning up existing processes..."
pkill -f "run_node.py" 2>/dev/null || true
sleep 2

# Calculate ports based on computer ID
BASE_P2P_PORT=$((10000 + COMPUTER_ID - 1))
BASE_API_PORT=$((11000 + COMPUTER_ID - 1))
GOSSIP_PORT=$((12000 + COMPUTER_ID - 1))
TPU_PORT=$((13000 + COMPUTER_ID - 1))
TVU_PORT=$((14000 + COMPUTER_ID - 1))

echo "📊 Port Configuration:"
echo "   P2P Port: $BASE_P2P_PORT"
echo "   API Port: $BASE_API_PORT"
echo "   Gossip Port: $GOSSIP_PORT"
echo "   TPU Port: $TPU_PORT"
echo "   TVU Port: $TVU_PORT"
echo ""

# Check if ports are available
check_port() {
    local port=$1
    if netstat -tuln | grep -q ":${port} "; then
        echo "❌ Port $port is already in use"
        exit 1
    fi
}

echo "🔍 Checking port availability..."
check_port $BASE_P2P_PORT
check_port $BASE_API_PORT
check_port $GOSSIP_PORT
check_port $TPU_PORT
check_port $TVU_PORT

# Ensure we have the blockchain directory
if [ ! -d "blockchain" ]; then
    echo "❌ blockchain directory not found. Please run this script from the project root directory."
    exit 1
fi

# Create keys directory if it doesn't exist
mkdir -p blockchain/keys

# Set key file path (each computer gets its own key or uses genesis key for computer 1)
if [ $COMPUTER_ID -eq 1 ]; then
    KEY_FILE="./keys/genesis_private_key.pem"
    echo "🔑 Using genesis key for bootstrap node (Computer 1)"
else
    # Use pre-generated node keys that already exist
    KEY_FILE="./keys/node${COMPUTER_ID}_private_key.pem"
    echo "🔑 Using pre-generated key: $KEY_FILE"
    
    # Check if the key exists
    if [ ! -f "blockchain/$KEY_FILE" ]; then
        echo "❌ Key file not found: blockchain/$KEY_FILE"
        echo "Available keys in blockchain/keys/:"
        ls -la blockchain/keys/node*_private_key.pem | head -10
        echo "..."
        echo "💡 Using a fallback key instead..."
        
        # Use a generic fallback key pattern
        FALLBACK_KEY="./keys/node$((COMPUTER_ID + 1))_private_key.pem"
        if [ -f "blockchain/$FALLBACK_KEY" ]; then
            KEY_FILE="$FALLBACK_KEY"
            echo "✅ Using fallback key: $KEY_FILE"
        else
            # Last resort: use genesis key for all nodes
            KEY_FILE="./keys/genesis_private_key.pem"
            echo "⚠️ Using genesis key as fallback (not recommended for production)"
        fi
    fi
fi

# Create network discovery configuration
create_network_config() {
    cat > network_config.json << EOF
{
  "mode": "distributed",
  "computer_id": $COMPUTER_ID,
  "total_computers": $TOTAL_COMPUTERS,
  "subnet_prefix": "$SUBNET_PREFIX",
  "timestamp": $(date +%s),
  "expected_nodes": [
EOF

    for i in $(seq 1 $TOTAL_COMPUTERS); do
        comma=""
        if [ $i -lt $TOTAL_COMPUTERS ]; then
            comma=","
        fi
        
        cat >> network_config.json << EOF
    {
      "computer_id": $i,
      "expected_ip": "${SUBNET_PREFIX}.$i",
      "p2p_port": $((10000 + i - 1)),
      "api_port": $((11000 + i - 1)),
      "gossip_port": $((12000 + i - 1)),
      "tpu_port": $((13000 + i - 1)),
      "tvu_port": $((14000 + i - 1))
    }$comma
EOF
    done

    cat >> network_config.json << EOF
  ]
}
EOF

    echo "📋 Network configuration created: network_config.json"
}

create_network_config

# Function to check if other nodes are reachable
check_peer_connectivity() {
    echo "🔍 Checking connectivity to other computers..."
    
    reachable_count=0
    for i in $(seq 1 $TOTAL_COMPUTERS); do
        if [ $i -eq $COMPUTER_ID ]; then
            continue  # Skip self
        fi
        
        target_ip="${SUBNET_PREFIX}.$i"
        target_port=$((11000 + i - 1))
        
        if timeout 3 bash -c "</dev/tcp/$target_ip/$target_port" 2>/dev/null; then
            echo "✅ Computer $i ($target_ip:$target_port) is reachable"
            reachable_count=$((reachable_count + 1))
        else
            echo "⚠️ Computer $i ($target_ip:$target_port) is not reachable"
        fi
    done
    
    echo ""
    echo "📊 Connectivity: $reachable_count/$((TOTAL_COMPUTERS - 1)) other computers reachable"
    
    if [ $reachable_count -eq 0 ]; then
        echo "⚠️ No other blockchain nodes detected. This node will start in isolation."
        echo "   Make sure other computers are running their blockchain nodes."
    elif [ $reachable_count -ge 2 ]; then
        echo "🟢 Good connectivity for consensus operations"
    else
        echo "🟡 Limited connectivity - network may have reduced resilience"
    fi
    
    return $reachable_count
}

# Start the blockchain node
echo "🚀 Starting blockchain node..."

cd blockchain

# Set environment variables for enhanced features
export COMPUTER_ID
export TOTAL_COMPUTERS
export SUBNET_PREFIX
export NETWORK_CONFIG_FILE="../network_config.json"

# Start the node
python run_node.py \
    --ip $LOCAL_IP \
    --node_port $BASE_P2P_PORT \
    --api_port $BASE_API_PORT \
    --key_file $KEY_FILE \
    --p2p_mode enhanced &

NODE_PID=$!
echo "✅ Blockchain node started (PID: $NODE_PID)"

cd ..

# Wait for node to initialize
echo "⏳ Waiting for node to initialize..."
sleep 10

# Check if node started successfully
if ! kill -0 $NODE_PID 2>/dev/null; then
    echo "❌ Node failed to start. Check logs for errors."
    exit 1
fi

# Test local node API
if curl -s "http://$LOCAL_IP:$BASE_API_PORT/api/v1/blockchain/" >/dev/null; then
    echo "✅ Node API is responding"
else
    echo "⚠️ Node API is not responding yet"
fi

# Check peer connectivity
check_peer_connectivity
peer_count=$?

# Auto-connect to other nodes if they're available
if [ $peer_count -gt 0 ]; then
    echo "🔗 Attempting to connect to other nodes..."
    sleep 5  # Give a bit more time for full initialization
    
    for i in $(seq 1 $TOTAL_COMPUTERS); do
        if [ $i -eq $COMPUTER_ID ]; then
            continue  # Skip self
        fi
        
        target_ip="${SUBNET_PREFIX}.$i"
        target_p2p_port=$((10000 + i - 1))
        target_api_port=$((11000 + i - 1))
        
        # Check if target node is available
        if timeout 3 bash -c "</dev/tcp/$target_ip/$target_api_port" 2>/dev/null; then
            echo "🔄 Connecting to Computer $i ($target_ip:$target_p2p_port)..."
            
            # Attempt P2P connection
            curl -X POST "http://$LOCAL_IP:$BASE_API_PORT/api/v1/blockchain/connect-peer/" \
                -H "Content-Type: application/json" \
                -d "{\"ip\": \"$target_ip\", \"port\": $target_p2p_port}" \
                2>/dev/null && echo "✅ Connected to Computer $i" || echo "⚠️ Connection to Computer $i may have failed"
        fi
    done
fi

# Display node status
echo ""
echo "🌐 DISTRIBUTED BLOCKCHAIN NODE STATUS"
echo "====================================="
echo ""
echo "🖥️ Computer Information:"
echo "   Computer ID: $COMPUTER_ID of $TOTAL_COMPUTERS"
echo "   IP Address: $LOCAL_IP"
echo "   Subnet: ${SUBNET_PREFIX}.x"
echo ""
echo "🔗 Node Endpoints:"
echo "   Blockchain API: http://$LOCAL_IP:$BASE_API_PORT/api/v1/blockchain/"
echo "   Network Status: http://$LOCAL_IP:$BASE_API_PORT/api/v1/blockchain/network-status/"
echo "   Performance:    http://$LOCAL_IP:$BASE_API_PORT/api/v1/blockchain/performance-metrics/"
echo ""
echo "🌐 P2P Information:"
echo "   P2P Port: $BASE_P2P_PORT"
echo "   Gossip Port: $GOSSIP_PORT"
echo "   TPU Port: $TPU_PORT"
echo "   TVU Port: $TVU_PORT"
echo ""

# Function to monitor network status
monitor_network() {
    while true; do
        sleep 60  # Check every minute
        
        # Check if our node is still running
        if ! kill -0 $NODE_PID 2>/dev/null; then
            echo "❌ ERROR: Node process has died! (PID: $NODE_PID)"
            break
        fi
        
        # Check API responsiveness
        if curl -s "http://$LOCAL_IP:$BASE_API_PORT/api/v1/blockchain/" >/dev/null; then
            # Get basic status
            block_count=$(curl -s "http://$LOCAL_IP:$BASE_API_PORT/api/v1/blockchain/" | grep -o '"blocks":\[' | wc -l)
            echo "📊 $(date '+%H:%M:%S') - Node healthy, API responsive"
        else
            echo "⚠️ $(date '+%H:%M:%S') - Node API not responding"
        fi
    done
}

# Store PID for cleanup
echo $NODE_PID > /tmp/blockchain_node.pid

echo "📊 Node Startup Complete!"
echo ""
echo "🎯 Test Commands:"
echo "1. Check blockchain status:"
echo "   curl http://$LOCAL_IP:$BASE_API_PORT/api/v1/blockchain/"
echo ""
echo "2. Submit a transaction:"
echo "   curl -X POST http://$LOCAL_IP:$BASE_API_PORT/api/v1/blockchain/transaction/ \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"sender\": \"test\", \"receiver\": \"test2\", \"amount\": 10}'"
echo ""
echo "3. Check network connections:"
echo "   curl http://$LOCAL_IP:$BASE_API_PORT/api/v1/blockchain/network-status/"
echo ""

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down blockchain node..."
    
    if [ -f /tmp/blockchain_node.pid ]; then
        PID=$(cat /tmp/blockchain_node.pid)
        if kill -0 $PID 2>/dev/null; then
            echo "Stopping node process $PID..."
            kill $PID
            sleep 3
            # Force kill if still running
            if kill -0 $PID 2>/dev/null; then
                kill -9 $PID
            fi
        fi
        rm -f /tmp/blockchain_node.pid
    fi
    
    # Also kill by process name as backup
    pkill -f "run_node.py" 2>/dev/null || true
    
    echo "✅ Node stopped"
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM

echo "🌐 Node is running! Press Ctrl+C to stop."
echo "💡 Run this same script on other computers (with different computer IDs) to form the network."

# Start monitoring
monitor_network
