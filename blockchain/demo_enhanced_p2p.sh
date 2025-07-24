#!/bin/bash

# Enhanced P2P Demo Script
# =======================
# Demonstrates Bitcoin-style P2P transaction propagation

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

print_demo_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║                  Enhanced P2P Demo Script                           ║"
    echo "║               Bitcoin-Style Transaction Propagation                 ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_step() {
    echo -e "${GREEN}[STEP $1]${NC} $2"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

wait_for_user() {
    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read -r
}

check_api_response() {
    local port=$1
    local max_attempts=5
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s --max-time 2 "http://localhost:$port/api/v1/blockchain/" >/dev/null 2>&1; then
            return 0
        fi
        sleep 1
        ((attempt++))
    done
    return 1
}

demo_enhanced_p2p() {
    print_demo_header
    
    echo -e "${WHITE}This demo will showcase the enhanced Bitcoin-style P2P features:${NC}"
    echo ""
    echo -e "• ${CYAN}INV/GETDATA/TX message pattern${NC}"
    echo -e "• ${CYAN}Transaction mempool with peer tracking${NC}"
    echo -e "• ${CYAN}Intelligent gossip protocol${NC}"
    echo -e "• ${CYAN}Real-time P2P statistics${NC}"
    echo -e "• ${CYAN}Network performance monitoring${NC}"
    echo ""
    
    wait_for_user
    
    # Step 1: Clean start
    log_step "1" "Cleaning previous instances..."
    pkill -f "run_node.py" 2>/dev/null || true
    sleep 2
    rm -f logs/*.pid 2>/dev/null || true
    log_success "Environment cleaned"
    
    # Step 2: Start enhanced nodes
    log_step "2" "Starting 5 nodes with enhanced P2P..."
    echo ""
    
    ./start_nodes_enhanced.sh -n 5 -m enhanced -c
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to start nodes. Please check the logs.${NC}"
        exit 1
    fi
    
    wait_for_user
    
    # Step 3: Show initial network status
    log_step "3" "Checking initial network status..."
    echo ""
    
    # Wait for nodes to fully initialize
    log_info "Waiting for nodes to establish P2P connections..."
    sleep 10
    
    # Check each node's enhanced statistics
    for i in {1..5}; do
        local api_port=$((11000 + i - 1))
        echo -e "${WHITE}Node $i (port $api_port):${NC}"
        
        if check_api_response $api_port; then
            local stats=$(curl -s "http://localhost:$api_port/api/v1/blockchain/node-stats/" 2>/dev/null)
            if [ $? -eq 0 ] && [ -n "$stats" ]; then
                echo "$stats" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    mempool = data.get('mempool', {})
    p2p = data.get('p2p', {})
    print(f'  📦 Mempool: {mempool.get(\"mempool_size\", 0)} transactions')
    print(f'  🌐 P2P Connections: {p2p.get(\"connected_peers\", 0)}')
    print(f'  👥 Tracked Peers: {mempool.get(\"tracked_peers\", 0)}')
except:
    print('  ✅ Basic connectivity confirmed')
"
            else
                echo -e "  ✅ ${GREEN}Node responding${NC}"
            fi
        else
            echo -e "  ❌ ${RED}Node not responding${NC}"
        fi
        echo ""
    done
    
    wait_for_user
    
    # Step 4: Submit transactions and observe propagation
    log_step "4" "Demonstrating Bitcoin-style transaction propagation..."
    echo ""
    
    log_info "Submitting 5 test transactions..."
    python3 test_transactions.py --count 5 2>/dev/null || {
        echo -e "${YELLOW}Note: test_transactions.py not found, creating manual transaction...${NC}"
        
        # Manual transaction submission via API
        curl -s -X POST http://localhost:11000/api/v1/blockchain/transaction/ \
            -H "Content-Type: application/json" \
            -d '{
                "receiver_public_key": "demo_receiver",
                "amount": 10.5,
                "type": "TRANSFER"
            }' >/dev/null || true
    }
    
    echo ""
    log_info "Waiting 5 seconds for P2P propagation..."
    sleep 5
    
    # Step 5: Show transaction propagation results
    log_step "5" "Analyzing transaction propagation across network..."
    echo ""
    
    for i in {1..5}; do
        local api_port=$((11000 + i - 1))
        echo -e "${WHITE}Node $i mempool status:${NC}"
        
        if check_api_response $api_port; then
            local mempool_data=$(curl -s "http://localhost:$api_port/api/v1/blockchain/mempool/" 2>/dev/null)
            if [ $? -eq 0 ] && [ -n "$mempool_data" ]; then
                echo "$mempool_data" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'  📦 Mempool Size: {data.get(\"mempool_size\", 0)}')
    print(f'  👥 Tracked Peers: {data.get(\"tracked_peers\", 0)}')
    perf = data.get('performance_stats', {})
    print(f'  📨 Received: {perf.get(\"total_received\", 0)}')
    print(f'  📢 Announced: {perf.get(\"total_announced\", 0)}')
    print(f'  🤝 Served: {perf.get(\"total_served\", 0)}')
except Exception as e:
    print(f'  ⚠️ Unable to parse mempool data: {e}')
"
            else
                echo -e "  ⚠️ ${YELLOW}Enhanced stats not available${NC}"
            fi
        else
            echo -e "  ❌ ${RED}Node not responding${NC}"
        fi
        echo ""
    done
    
    wait_for_user
    
    # Step 6: Real-time monitoring demo
    log_step "6" "Starting real-time network monitor..."
    echo ""
    
    log_info "The network monitor will show live P2P statistics."
    log_info "You can submit more transactions in another terminal to see live updates."
    echo ""
    echo -e "${CYAN}Commands to try in another terminal:${NC}"
    echo -e "  ${WHITE}python3 test_transactions.py --count 10${NC}"
    echo -e "  ${WHITE}curl -X POST http://localhost:11000/api/v1/blockchain/transaction/ ...${NC}"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C in the monitor to return to this demo${NC}"
    
    wait_for_user
    
    if [ -f "./monitor_network.sh" ]; then
        ./monitor_network.sh --interval 3
    else
        log_info "Network monitor not available, showing final statistics..."
        
        # Manual final stats
        for i in {1..5}; do
            local api_port=$((11000 + i - 1))
            echo -e "${WHITE}Final stats for Node $i:${NC}"
            curl -s "http://localhost:$api_port/api/v1/blockchain/node-stats/" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'  Blockchain height: {data.get(\"blockchain\", {}).get(\"total_blocks\", 0)}')
    print(f'  Mempool size: {data.get(\"mempool\", {}).get(\"mempool_size\", 0)}')
    print(f'  P2P connections: {data.get(\"p2p\", {}).get(\"connected_peers\", 0)}')
except:
    print('  Basic node active')
" 2>/dev/null || echo "  Node statistics unavailable"
            echo ""
        done
    fi
    
    # Step 7: Cleanup option
    log_step "7" "Demo complete!"
    echo ""
    
    log_success "You've seen the enhanced Bitcoin-style P2P features in action!"
    echo ""
    echo -e "${WHITE}Key observations:${NC}"
    echo -e "• ${GREEN}Efficient transaction propagation${NC} using INV/GETDATA/TX pattern"
    echo -e "• ${GREEN}Intelligent peer tracking${NC} and selective forwarding"
    echo -e "• ${GREEN}Real-time statistics${NC} for network monitoring"
    echo -e "• ${GREEN}Backward compatibility${NC} with legacy systems"
    echo ""
    
    echo -n "Stop all demo nodes? [Y/n]: "
    read -r response
    
    if [[ ! "$response" =~ ^[Nn]$ ]]; then
        log_info "Stopping demo nodes..."
        pkill -f "run_node.py" 2>/dev/null || true
        sleep 2
        rm -f logs/*.pid 2>/dev/null || true
        log_success "Demo cleanup complete"
    else
        log_info "Demo nodes left running for your exploration"
        echo ""
        echo -e "${CYAN}Useful commands:${NC}"
        echo -e "  ${WHITE}./monitor_network.sh${NC}          # Real-time monitoring"
        echo -e "  ${WHITE}./manage_network.sh status${NC}    # Check network status"
        echo -e "  ${WHITE}pkill -f 'run_node.py'${NC}        # Stop all nodes later"
    fi
    
    echo ""
    log_success "Enhanced P2P Demo completed! 🚀"
}

# Run the demo
demo_enhanced_p2p
