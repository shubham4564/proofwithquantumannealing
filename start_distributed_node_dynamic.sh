#!/bin/bash

# Distributed Blockchain Network Setup with Dynamic Discovery
# ===========================================================
# Run this script on each computer in your subnet
# It will automatically discover other blockchain nodes

# Configuration
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

# Function to discover other blockchain nodes in subnet
discover_network_nodes() {
    echo "🔍 Discovering other blockchain nodes in the subnet..."
    
    # Run subnet discovery
    if python3 subnet_discovery.py $COMPUTER_ID; then
        if [ -f "dynamic_network_config.json" ]; then
            echo "✅ Dynamic network discovery completed"
            # Use the dynamic config instead of static one
            export NETWORK_CONFIG_FILE="dynamic_network_config.json"
            return 0
        else
            echo "⚠️ Dynamic discovery failed, using static configuration"
            return 1
        fi
    else
        echo "⚠️ Could not run subnet discovery, using static configuration"
        return 1
    fi
}

# Function to auto-detect computer ID from IP
detect_computer_id() {
    local_ip=$(get_local_ip)
    last_octet=$(echo "$local_ip" | cut -d'.' -f4)
    
    # For auto-assignment, use a simple mapping
    if [[ $last_octet =~ ^[0-9]+$ ]]; then
        # Use last octet mod 6, plus 1 to get 1-6 range
        COMPUTER_ID=$(( (last_octet % 6) + 1 ))
        echo "🔍 Auto-assigned Computer ID: $COMPUTER_ID (based on IP: $local_ip)"
    else
        echo "❌ Could not auto-detect computer ID from IP address"
        echo "Current IP: $local_ip"
        echo "Please provide computer ID manually:"
        echo "./start_distributed_node.sh <computer_id>"
        exit 1
    fi
}

# Parse command line arguments
if [ $# -eq 1 ]; then
    COMPUTER_ID=$1
    echo "💻 Using provided Computer ID: $COMPUTER_ID"
elif [ $# -eq 0 ]; then
    detect_computer_id
else
    echo "Usage: $0 [computer_id]"
    echo "Example: $0 1  (for first computer)"
    echo "Note: If no computer_id provided, it will be auto-detected"
    exit 1
fi

# Validate computer ID
if ! [[ "$COMPUTER_ID" =~ ^[1-6]$ ]]; then
    echo "❌ Computer ID must be between 1 and $TOTAL_COMPUTERS"
    exit 1
fi

echo "🌐 Starting Distributed Blockchain Node with Dynamic Discovery"
echo "============================================================="
echo "Computer ID: $COMPUTER_ID"
echo "Total Computers: $TOTAL_COMPUTERS"
echo ""

# Get local IP address
LOCAL_IP=$(get_local_ip)
echo "📍 Local IP Address: $LOCAL_IP"

# Validate we got a valid IP
if [[ -z "$LOCAL_IP" ]]; then
    echo "❌ Could not detect local IP address"
    echo "Please check your network connection"
    exit 1
fi

# Get subnet info
SUBNET_PREFIX=$(echo "$LOCAL_IP" | cut -d'.' -f1-3)
echo "🌐 Subnet: ${SUBNET_PREFIX}.x"
echo ""

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

# Discover other nodes in the network
echo ""
discover_network_nodes
echo ""

# Function to check if other nodes are reachable (now reads from dynamic config)
check_peer_connectivity() {
    echo "🔍 Checking connectivity to discovered nodes..."
    
    if [ -f "dynamic_network_config.json" ]; then
        # Read discovered nodes from dynamic config
        node_count=$(python3 -c "
import json
with open('dynamic_network_config.json', 'r') as f:
    config = json.load(f)
    discovered = config.get('discovered_nodes', [])
    print(len(discovered))
")
        
        if [ "$node_count" -gt 0 ]; then
            echo "✅ Found $node_count other blockchain nodes in the network"
            return $node_count
        else
            echo "⚠️ No other blockchain nodes detected. This node will start in isolation."
            echo "   Other nodes can join the network dynamically."
            return 0
        fi
    else
        echo "⚠️ No dynamic network configuration found."
        return 0
    fi
}

# Start the blockchain node
echo "🚀 Starting blockchain node..."

cd blockchain

# Set environment variables for enhanced features
export COMPUTER_ID
export TOTAL_COMPUTERS
export SUBNET_PREFIX
export NETWORK_CONFIG_FILE="../dynamic_network_config.json"

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

# Auto-connect to discovered nodes
if [ $peer_count -gt 0 ] && [ -f "dynamic_network_config.json" ]; then
    echo "🔗 Attempting to connect to discovered nodes..."
    sleep 5  # Give a bit more time for full initialization
    
    # Connect to nodes using dynamic config
    python3 -c "
import json
import requests
import time

try:
    with open('dynamic_network_config.json', 'r') as f:
        config = json.load(f)
    
    local_ip = '$LOCAL_IP'
    local_api_port = $BASE_API_PORT
    
    for node in config.get('discovered_nodes', []):
        target_ip = node['ip']
        target_p2p_port = node['p2p_port']
        
        print(f'🔄 Connecting to {target_ip}:{target_p2p_port}...')
        
        try:
            response = requests.post(
                f'http://{local_ip}:{local_api_port}/api/v1/blockchain/connect-peer/',
                json={'ip': target_ip, 'port': target_p2p_port},
                timeout=5
            )
            if response.status_code == 200:
                print(f'✅ Connected to {target_ip}')
            else:
                print(f'⚠️ Connection to {target_ip} may have failed')
        except Exception as e:
            print(f'⚠️ Could not connect to {target_ip}: {str(e)[:50]}...')
        
        time.sleep(1)
except Exception as e:
    print(f'Error connecting to peers: {e}')
"
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
            
            # Periodically rediscover peers (every 10 minutes)
            current_minute=$(date '+%M')
            if [ $(( current_minute % 10 )) -eq 0 ]; then
                echo "🔍 Performing periodic peer discovery..."
                discover_network_nodes >/dev/null 2>&1 &
            fi
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
echo "4. Rediscover network nodes:"
echo "   python3 subnet_discovery.py $COMPUTER_ID"
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

echo "🌐 Node is running with dynamic peer discovery!"
echo "💡 New nodes can join by running this script on other computers in the subnet."
echo "🔄 Press Ctrl+C to stop."

# Start monitoring
monitor_network
