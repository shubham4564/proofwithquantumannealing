#!/bin/bash

# Enhanced Blockchain Network Monitor
# ==================================
# Real-time monitoring for Bitcoin-style P2P blockchain network
# Supports both enhanced and legacy P2P modes

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Configuration
REFRESH_INTERVAL=5
API_START=11000
MONITOR_MODE="auto"  # auto, enhanced, legacy
SHOW_DETAILS=true

print_header() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${WHITE}         Enhanced Blockchain Network Monitor              ${CYAN}║${NC}"
    echo -e "${CYAN}║${WHITE}              Real-time P2P Statistics                   ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
}

detect_nodes() {
    local nodes=()
    for port in $(seq $API_START $((API_START + 50))); do
        if curl -s --max-time 1 "http://localhost:$port/api/v1/blockchain/" >/dev/null 2>&1; then
            nodes+=($port)
        fi
    done
    echo "${nodes[@]}"
}

get_node_stats() {
    local api_port=$1
    local stats_url="http://localhost:$api_port/api/v1/blockchain/node-stats/"
    local basic_url="http://localhost:$api_port/api/v1/blockchain/"
    
    # Try enhanced stats first
    local enhanced_stats
    enhanced_stats=$(curl -s --max-time 2 "$stats_url" 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$enhanced_stats" ] && echo "$enhanced_stats" | python3 -c "import sys, json; json.load(sys.stdin)" >/dev/null 2>&1; then
        echo "enhanced:$enhanced_stats"
        return 0
    fi
    
    # Fallback to basic stats
    local basic_stats
    basic_stats=$(curl -s --max-time 2 "$basic_url" 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$basic_stats" ]; then
        echo "basic:$basic_stats"
        return 0
    fi
    
    echo "error:unreachable"
    return 1
}

parse_enhanced_stats() {
    local stats_json="$1"
    
    # Use Python to parse JSON safely
    python3 << EOF
import json, sys
try:
    data = json.loads('''$stats_json''')
    
    # Node info
    node_info = data.get('node_info', {})
    port = node_info.get('port', 'N/A')
    
    # Blockchain info
    blockchain = data.get('blockchain', {})
    blocks = blockchain.get('total_blocks', 0)
    
    # Legacy pool
    legacy_pool = data.get('legacy_transaction_pool', {})
    legacy_txs = legacy_pool.get('size', 0)
    
    # Mempool info
    mempool = data.get('mempool', {})
    mempool_size = mempool.get('mempool_size', 0)
    tracked_peers = mempool.get('tracked_peers', 0)
    
    # Performance stats
    perf_stats = mempool.get('performance_stats', {})
    received = perf_stats.get('total_received', 0)
    announced = perf_stats.get('total_announced', 0)
    served = perf_stats.get('total_served', 0)
    
    # P2P info
    p2p = data.get('p2p', {})
    connected_peers = p2p.get('connected_peers', 0)
    health_tracked = p2p.get('peer_health_tracked', 0)
    
    print(f"{port}|{blocks}|{legacy_txs}|{mempool_size}|{tracked_peers}|{connected_peers}|{received}|{announced}|{served}")
    
except Exception as e:
    print("ERROR|0|0|0|0|0|0|0|0")
EOF
}

display_network_summary() {
    local nodes_data=("$@")
    local total_nodes=${#nodes_data[@]}
    local active_nodes=0
    local total_blocks=0
    local total_mempool=0
    local total_connections=0
    local total_txs_received=0
    local enhanced_nodes=0
    
    echo -e "\n${WHITE}📊 Network Overview:${NC}"
    echo "─────────────────────────────────────────────────────────────"
    
    for node_data in "${nodes_data[@]}"; do
        if [[ "$node_data" != *"ERROR"* ]]; then
            ((active_nodes++))
            
            IFS='|' read -r port blocks legacy_txs mempool tracked_peers connected health received announced served <<< "$node_data"
            
            if [[ "$blocks" =~ ^[0-9]+$ ]]; then
                total_blocks=$(( total_blocks > blocks ? total_blocks : blocks ))
                total_mempool=$((total_mempool + mempool))
                total_connections=$((total_connections + connected))
                total_txs_received=$((total_txs_received + received))
                
                if [[ "$mempool" =~ ^[0-9]+$ ]] && [ "$mempool" -ge 0 ]; then
                    ((enhanced_nodes++))
                fi
            fi
        fi
    done
    
    local health_pct=0
    if [ $total_nodes -gt 0 ]; then
        health_pct=$(( active_nodes * 100 / total_nodes ))
    fi
    
    echo -e "   🌐 Total Nodes:       ${WHITE}$total_nodes${NC}"
    echo -e "   ✅ Active Nodes:      ${GREEN}$active_nodes${NC}"
    echo -e "   📈 Network Health:    ${GREEN}${health_pct}%${NC}"
    echo -e "   🔗 Enhanced P2P:      ${CYAN}$enhanced_nodes${NC} nodes"
    echo -e "   🧱 Blockchain Height: ${WHITE}$total_blocks${NC} blocks"
    echo -e "   📦 Total Mempool:     ${CYAN}$total_mempool${NC} transactions"
    echo -e "   🌐 Total P2P Conns:   ${CYAN}$total_connections${NC}"
    echo -e "   📨 TXs Processed:     ${CYAN}$total_txs_received${NC}"
}

display_node_details() {
    local nodes_data=("$@")
    
    echo -e "\n${WHITE}🔍 Node Details:${NC}"
    echo "─────────────────────────────────────────────────────────────"
    printf "%-6s %-8s %-7s %-8s %-8s %-6s %-6s %-6s %-6s\n" "Port" "Blocks" "Legacy" "Mempool" "Peers" "Conn" "Recv" "Ann" "Serv"
    echo "─────────────────────────────────────────────────────────────"
    
    for node_data in "${nodes_data[@]}"; do
        if [[ "$node_data" == *"ERROR"* ]]; then
            local port=$(echo "$node_data" | cut -d'|' -f1)
            printf "%-6s ${RED}%-8s${NC}\n" "$port" "DOWN"
        else
            IFS='|' read -r port blocks legacy_txs mempool tracked_peers connected received announced served <<< "$node_data"
            
            # Color coding for health
            local block_color=$GREEN
            local mempool_color=$CYAN
            local conn_color=$GREEN
            
            if [ "$connected" -eq 0 ]; then
                conn_color=$RED
            elif [ "$connected" -lt 3 ]; then
                conn_color=$YELLOW
            fi
            
            printf "%-6s ${block_color}%-8s${NC} %-7s ${mempool_color}%-8s${NC} %-8s ${conn_color}%-6s${NC} %-6s %-6s %-6s\n" \
                "$port" "$blocks" "$legacy_txs" "$mempool" "$tracked_peers" "$connected" "$received" "$announced" "$served"
        fi
    done
}

monitor_network() {
    while true; do
        clear
        print_header
        
        echo -e "${WHITE}🕐 $(date +'%Y-%m-%d %H:%M:%S')${NC} | Refresh: ${CYAN}${REFRESH_INTERVAL}s${NC} | Press Ctrl+C to exit"
        
        # Detect active nodes
        local active_ports=($(detect_nodes))
        
        if [ ${#active_ports[@]} -eq 0 ]; then
            echo -e "\n${RED}❌ No active nodes detected${NC}"
            echo -e "   Check if nodes are running on ports ${API_START}+"
            sleep $REFRESH_INTERVAL
            continue
        fi
        
        # Collect stats from all nodes
        local nodes_data=()
        for port in "${active_ports[@]}"; do
            local node_num=$((port - API_START + 1))
            echo -e "Checking node $node_num (port $port)..." >&2
            
            local stats_result
            stats_result=$(get_node_stats "$port")
            
            if [[ "$stats_result" == enhanced:* ]]; then
                local stats_json="${stats_result#enhanced:}"
                local parsed_stats
                parsed_stats=$(parse_enhanced_stats "$stats_json")
                nodes_data+=("$parsed_stats")
            elif [[ "$stats_result" == basic:* ]]; then
                # Basic stats fallback
                nodes_data+=("$port|1|0|0|0|0|0|0|0")
            else
                nodes_data+=("$port|ERROR|0|0|0|0|0|0|0")
            fi
        done
        
        # Display results
        display_network_summary "${nodes_data[@]}"
        
        if [ "$SHOW_DETAILS" = true ]; then
            display_node_details "${nodes_data[@]}"
        fi
        
        echo -e "\n${WHITE}💡 Commands:${NC}"
        echo -e "   ${CYAN}d${NC} - Toggle details view"
        echo -e "   ${CYAN}r${NC} - Refresh now"
        echo -e "   ${CYAN}q${NC} - Quit monitor"
        
        # Wait for next refresh (with ability to handle input)
        sleep $REFRESH_INTERVAL
    done
}

# Parse command line arguments
case "$1" in
    --help|-h)
        echo "Enhanced Blockchain Network Monitor"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "OPTIONS:"
        echo "  --interval N    Refresh interval in seconds (default: 5)"
        echo "  --no-details    Hide detailed node information"
        echo "  --api-start N   Starting API port (default: 11000)"
        echo "  --help         Show this help"
        echo ""
        exit 0
        ;;
    --interval)
        REFRESH_INTERVAL="$2"
        ;;
    --no-details)
        SHOW_DETAILS=false
        ;;
    --api-start)
        API_START="$2"
        ;;
esac

# Validate refresh interval
if ! [[ "$REFRESH_INTERVAL" =~ ^[0-9]+$ ]] || [ "$REFRESH_INTERVAL" -lt 1 ]; then
    echo "Invalid refresh interval: $REFRESH_INTERVAL"
    exit 1
fi

# Start monitoring
monitor_network
