#!/bin/bash

# Enhanced Blockchain Node Launcher with Bitcoin-Style P2P Support
# ==============================================================
# Start N blockchain nodes with Bitcoin-style P2P transaction propagation
# Supports both enhanced (INV/GETDATA/TX) and legacy (direct broadcast) modes
#
# Usage: ./start_nodes_enhanced.sh [OPTIONS]
#
# OPTIONS:
#   -n, --nodes NUMBER        Number of nodes to start (1-100, default: 10)
#   -m, --p2p-mode MODE      P2P mode: enhanced|legacy (default: enhanced)
#   -p, --port-start PORT    Starting port number (default: 10000)
#   -a, --api-start PORT     Starting API port number (default: 11000)
#   -t, --test-mode          Run in test mode with enhanced monitoring
#   -w, --watch              Start with real-time monitoring
#   -c, --clean              Clean start (kill existing nodes first)
#   -h, --help               Show this help message
#
# EXAMPLES:
#   ./start_nodes_enhanced.sh                                # 10 nodes, enhanced P2P
#   ./start_nodes_enhanced.sh -n 5 -m legacy               # 5 nodes, legacy P2P
#   ./start_nodes_enhanced.sh -n 20 -t -w                  # 20 nodes, test mode with monitoring
#   ./start_nodes_enhanced.sh -c -n 15                     # Clean start with 15 nodes

# Default configuration
NUM_NODES=10
P2P_MODE="enhanced"
PORT_START=10000
API_START=11000
TEST_MODE=false
WATCH_MODE=false
CLEAN_START=false
VERBOSE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${WHITE}          Enhanced Blockchain Node Launcher v2.0             ${CYAN}║${NC}"
    echo -e "${CYAN}║${WHITE}        Bitcoin-Style P2P Transaction Propagation            ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "OPTIONS:"
    echo "  -n, --nodes NUMBER        Number of nodes (1-100, default: 10)"
    echo "  -m, --p2p-mode MODE      P2P mode: enhanced|legacy (default: enhanced)"
    echo "  -p, --port-start PORT    Starting port (default: 10000)"
    echo "  -a, --api-start PORT     Starting API port (default: 11000)"
    echo "  -t, --test-mode          Enable test mode with enhanced monitoring"
    echo "  -w, --watch              Start real-time monitoring after launch"
    echo "  -c, --clean              Clean start (kill existing nodes)"
    echo "  -v, --verbose            Verbose output"
    echo "  -h, --help               Show this help"
    echo ""
    echo "EXAMPLES:"
    echo "  $0                           # 10 nodes, enhanced P2P"
    echo "  $0 -n 5 -m legacy          # 5 nodes, legacy P2P"
    echo "  $0 -n 20 -t -w             # 20 nodes, test + monitoring"
    echo "  $0 -c -n 15                # Clean start, 15 nodes"
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[DEBUG]${NC} $1"
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--nodes)
            NUM_NODES="$2"
            shift 2
            ;;
        -m|--p2p-mode)
            P2P_MODE="$2"
            shift 2
            ;;
        -p|--port-start)
            PORT_START="$2"
            shift 2
            ;;
        -a|--api-start)
            API_START="$2"
            shift 2
            ;;
        -t|--test-mode)
            TEST_MODE=true
            shift
            ;;
        -w|--watch)
            WATCH_MODE=true
            shift
            ;;
        -c|--clean)
            CLEAN_START=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            print_header
            print_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Validation
if ! [[ "$NUM_NODES" =~ ^[0-9]+$ ]] || [ "$NUM_NODES" -lt 1 ] || [ "$NUM_NODES" -gt 100 ]; then
    log_error "Invalid number of nodes: $NUM_NODES (must be 1-100)"
    exit 1
fi

if [[ "$P2P_MODE" != "enhanced" && "$P2P_MODE" != "legacy" ]]; then
    log_error "Invalid P2P mode: $P2P_MODE (must be 'enhanced' or 'legacy')"
    exit 1
fi

if ! [[ "$PORT_START" =~ ^[0-9]+$ ]] || [ "$PORT_START" -lt 1000 ] || [ "$PORT_START" -gt 65000 ]; then
    log_error "Invalid port start: $PORT_START (must be 1000-65000)"
    exit 1
fi

if ! [[ "$API_START" =~ ^[0-9]+$ ]] || [ "$API_START" -lt 1000 ] || [ "$API_START" -gt 65000 ]; then
    log_error "Invalid API start port: $API_START (must be 1000-65000)"
    exit 1
fi

# Check for port conflicts
PORT_END=$((PORT_START + NUM_NODES - 1))
API_END=$((API_START + NUM_NODES - 1))

if [ $PORT_END -gt 65535 ] || [ $API_END -gt 65535 ]; then
    log_error "Port range exceeds 65535. Reduce nodes or starting ports."
    exit 1
fi

print_header

# Display configuration
echo -e "${WHITE}Configuration:${NC}"
echo -e "  📊 Nodes:          ${GREEN}$NUM_NODES${NC}"
echo -e "  🌐 P2P Mode:       ${GREEN}$P2P_MODE${NC}"
echo -e "  📡 Node Ports:     ${GREEN}$PORT_START-$PORT_END${NC}"
echo -e "  🔌 API Ports:      ${GREEN}$API_START-$API_END${NC}"
echo -e "  🧪 Test Mode:      ${GREEN}$TEST_MODE${NC}"
echo -e "  👁️  Watch Mode:     ${GREEN}$WATCH_MODE${NC}"
echo -e "  🧹 Clean Start:    ${GREEN}$CLEAN_START${NC}"
echo ""

# Clean start if requested
if [ "$CLEAN_START" = true ]; then
    log_info "Performing clean start - killing existing nodes..."
    pkill -f "run_node.py" 2>/dev/null || true
    sleep 3
    log_info "Cleanup complete"
fi

# Check for existing processes
existing_processes=$(pgrep -f "run_node.py" | wc -l)
if [ "$existing_processes" -gt 0 ]; then
    log_warn "$existing_processes existing node processes detected"
    echo -n "Continue anyway? [y/N]: "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        log_info "Aborted by user"
        exit 0
    fi
fi

# Create necessary directories
mkdir -p logs
mkdir -p monitoring

# Enhanced node startup function
start_enhanced_node() {
    local node_num=$1
    local node_port=$((PORT_START + node_num - 1))
    local api_port=$((API_START + node_num - 1))
    local key_file="keys/node${node_num}_private_key.pem"
    local log_file="logs/node${node_num}_enhanced.log"
    
    # Key file selection logic
    if [ $node_num -eq 1 ]; then
        key_file="keys/genesis_private_key.pem"
    elif [ ! -f "$key_file" ]; then
        if [ -f "keys/staker_private_key.pem" ]; then
            key_file="keys/staker_private_key.pem"
        else
            log_warn "Key file $key_file not found, using genesis key"
            key_file="keys/genesis_private_key.pem"
        fi
    fi
    
    # Build command arguments
    local cmd_args=(
        "python" "run_node.py"
        "--ip" "localhost"
        "--node_port" "$node_port"
        "--api_port" "$api_port"
        "--key_file" "$key_file"
        "--p2p_mode" "$P2P_MODE"
    )
    
    log_verbose "Starting Node $node_num with command: ${cmd_args[*]}"
    
    echo -e "🚀 ${WHITE}Node $node_num${NC} | Port: ${GREEN}$node_port${NC} | API: ${GREEN}$api_port${NC} | Mode: ${GREEN}$P2P_MODE${NC} | Key: ${CYAN}$(basename "$key_file")${NC}"
    
    # Start the node
    "${cmd_args[@]}" > "$log_file" 2>&1 &
    local pid=$!
    
    # Store PID for monitoring
    echo "$pid" > "logs/node${node_num}.pid"
    
    log_verbose "Node $node_num started with PID $pid"
    return 0
}

# Health check function
check_node_health() {
    local node_num=$1
    local api_port=$((API_START + node_num - 1))
    local timeout=5
    
    # Check if process is running
    if [ -f "logs/node${node_num}.pid" ]; then
        local pid=$(cat "logs/node${node_num}.pid")
        if ! kill -0 "$pid" 2>/dev/null; then
            return 1
        fi
    fi
    
    # Check API responsiveness
    if curl -s --max-time $timeout "http://localhost:$api_port/api/v1/blockchain/" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Enhanced health check with P2P metrics
check_enhanced_health() {
    local node_num=$1
    local api_port=$((API_START + node_num - 1))
    
    if check_node_health "$node_num"; then
        if [ "$P2P_MODE" = "enhanced" ]; then
            # Get enhanced statistics
            local stats
            stats=$(curl -s --max-time 3 "http://localhost:$api_port/api/v1/blockchain/node-stats/" 2>/dev/null)
            if [ $? -eq 0 ] && [ -n "$stats" ]; then
                echo "$stats"
                return 0
            fi
        fi
        echo "basic_health_ok"
        return 0
    else
        return 1
    fi
}

# Start all nodes
log_info "Launching $NUM_NODES nodes with $P2P_MODE P2P mode..."
echo ""

startup_pids=()
for i in $(seq 1 $NUM_NODES); do
    start_enhanced_node $i
    startup_pids+=($!)
    
    # Staggered startup to prevent resource conflicts
    if [ $i -lt $NUM_NODES ]; then
        sleep 1.5
    fi
done

echo ""
log_info "All nodes launched. Waiting for initialization..."

# Progressive health checking
echo ""
log_info "Performing initial health checks..."
sleep 5

# Quick initial check
active_nodes=0
echo -e "${WHITE}Initial Status:${NC}"
for i in $(seq 1 $NUM_NODES); do
    echo -n "  Node $i: "
    if check_node_health $i; then
        echo -e "${GREEN}✅ Starting${NC}"
        ((active_nodes++))
    else
        echo -e "${RED}❌ Failed${NC}"
    fi
done

if [ $active_nodes -eq 0 ]; then
    log_error "No nodes started successfully. Check configuration and logs."
    exit 1
fi

# Detailed health check after more time
echo ""
log_info "Waiting for P2P connections to establish..."
sleep 10

echo ""
log_info "Detailed health assessment..."
echo ""

detailed_active=0
network_stats=()

for i in $(seq 1 $NUM_NODES); do
    api_port=$((API_START + i - 1))
    echo -n "🔍 Node $i (API $api_port): "
    
    health_result=$(check_enhanced_health $i)
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Running${NC}"
        ((detailed_active++))
        
        if [ "$P2P_MODE" = "enhanced" ] && [ "$health_result" != "basic_health_ok" ]; then
            # Parse enhanced stats
            mempool_size=$(echo "$health_result" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('mempool', {}).get('mempool_size', 0))" 2>/dev/null || echo "0")
            connected_peers=$(echo "$health_result" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('p2p', {}).get('connected_peers', 0))" 2>/dev/null || echo "0")
            
            echo -e "    📦 Mempool: ${CYAN}$mempool_size${NC} | 🌐 Peers: ${CYAN}$connected_peers${NC}"
            network_stats+=("$i:$mempool_size:$connected_peers")
        fi
    else
        echo -e "${RED}❌ Not responding${NC}"
        
        # Check logs for errors
        if [ -f "logs/node${i}_enhanced.log" ]; then
            error_count=$(tail -20 "logs/node${i}_enhanced.log" | grep -i error | wc -l)
            if [ "$error_count" -gt 0 ]; then
                echo -e "    ${RED}📄 $error_count errors in recent logs${NC}"
            fi
        fi
    fi
done

# Network summary
echo ""
echo -e "${WHITE}📊 Network Summary:${NC}"
echo -e "   🌐 Mode:              ${GREEN}$P2P_MODE${NC}"
echo -e "   📊 Total Configured:  ${WHITE}$NUM_NODES${NC}"
echo -e "   ✅ Active Nodes:      ${GREEN}$detailed_active${NC}"

if command -v bc >/dev/null 2>&1; then
    health_pct=$(echo "scale=1; $detailed_active * 100 / $NUM_NODES" | bc -l 2>/dev/null || echo "0")
    echo -e "   📈 Network Health:    ${GREEN}${health_pct}%${NC}"
else
    echo -e "   📈 Network Health:    ${GREEN}$detailed_active/$NUM_NODES${NC}"
fi

# Enhanced network statistics for enhanced mode
if [ "$P2P_MODE" = "enhanced" ] && [ ${#network_stats[@]} -gt 0 ]; then
    echo ""
    echo -e "${WHITE}🔗 Enhanced P2P Statistics:${NC}"
    
    total_mempool=0
    total_connections=0
    for stat in "${network_stats[@]}"; do
        IFS=':' read -r node_id mempool_size peer_count <<< "$stat"
        total_mempool=$((total_mempool + mempool_size))
        total_connections=$((total_connections + peer_count))
    done
    
    avg_connections=$((total_connections / detailed_active))
    echo -e "   📦 Total Mempool TXs: ${CYAN}$total_mempool${NC}"
    echo -e "   🌐 Total P2P Conns:   ${CYAN}$total_connections${NC}"
    echo -e "   📊 Avg Conns/Node:    ${CYAN}$avg_connections${NC}"
fi

# Status summary
echo ""
if [ $detailed_active -eq $NUM_NODES ]; then
    echo -e "${GREEN}🎉 Perfect! All nodes are running successfully.${NC}"
elif [ $detailed_active -gt $((NUM_NODES / 2)) ]; then
    echo -e "${YELLOW}⚠️  Most nodes started successfully. Network is functional.${NC}"
elif [ $detailed_active -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Some nodes failed. Check logs for details.${NC}"
else
    echo -e "${RED}❌ Critical: No nodes responding. Check configuration.${NC}"
fi

# Useful commands section
echo ""
echo -e "${WHITE}💡 Useful Commands:${NC}"
if [ "$P2P_MODE" = "enhanced" ]; then
    echo -e "   🧪 Test enhanced P2P:   ${CYAN}python test_enhanced_p2p.py${NC}"
    echo -e "   📊 Node statistics:     ${CYAN}curl http://localhost:$API_START/api/v1/blockchain/node-stats/${NC}"
    echo -e "   📦 Mempool status:      ${CYAN}curl http://localhost:$API_START/api/v1/blockchain/mempool/${NC}"
fi
echo -e "   🔄 Submit transactions: ${CYAN}python test_transactions.py --count 10${NC}"
echo -e "   📈 Network analysis:    ${CYAN}python analyze_forgers.py${NC}"
echo -e "   📝 View node logs:      ${CYAN}tail -f logs/node1_enhanced.log${NC}"
echo -e "   🛑 Stop all nodes:      ${CYAN}pkill -f 'run_node.py'${NC}"

# Test mode features
if [ "$TEST_MODE" = true ]; then
    echo ""
    log_info "Test mode enabled - running automated tests..."
    
    if [ -f "test_enhanced_p2p.py" ] && [ "$P2P_MODE" = "enhanced" ]; then
        echo ""
        log_info "Running enhanced P2P tests..."
        python test_enhanced_p2p.py
    fi
    
    if [ -f "test_transactions.py" ]; then
        echo ""
        log_info "Running transaction tests..."
        python test_transactions.py --count 5
    fi
fi

# Watch mode
if [ "$WATCH_MODE" = true ]; then
    echo ""
    log_info "Watch mode enabled - starting real-time monitoring..."
    
    if [ -f "analyze_forgers.py" ]; then
        log_info "Starting network analyzer..."
        python analyze_forgers.py --watch 30
    else
        log_info "Network analyzer not found, showing basic monitoring..."
        while true; do
            clear
            echo -e "${WHITE}Real-time Network Monitor${NC}"
            echo "Press Ctrl+C to exit"
            echo ""
            
            for i in $(seq 1 $detailed_active); do
                api_port=$((API_START + i - 1))
                if curl -s "http://localhost:$api_port/api/v1/blockchain/" >/dev/null 2>&1; then
                    echo -e "Node $i: ${GREEN}✅ Active${NC}"
                else
                    echo -e "Node $i: ${RED}❌ Down${NC}"
                fi
            done
            
            sleep 5
        done
    fi
fi

echo ""
log_info "Enhanced node launcher completed!"
echo -e "${GREEN}🚀 Your blockchain network is ready!${NC}"
