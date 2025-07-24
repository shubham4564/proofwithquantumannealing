#!/bin/bash

# Enhanced Blockchain Network Manager
# ==================================
# Comprehensive management tool for Bitcoin-style P2P blockchain network

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║                Enhanced Blockchain Network Manager                   ║"
    echo "║                  Bitcoin-Style P2P Edition                          ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_menu() {
    echo -e "${WHITE}📋 Available Commands:${NC}"
    echo ""
    echo -e "${GREEN}🚀 Network Operations:${NC}"
    echo -e "   ${CYAN}start${NC}     - Start blockchain network"
    echo -e "   ${CYAN}stop${NC}      - Stop all nodes"
    echo -e "   ${CYAN}restart${NC}   - Restart entire network"
    echo -e "   ${CYAN}status${NC}    - Show network status"
    echo ""
    echo -e "${GREEN}📊 Monitoring:${NC}"
    echo -e "   ${CYAN}monitor${NC}   - Real-time network monitor"
    echo -e "   ${CYAN}logs${NC}      - View node logs"
    echo -e "   ${CYAN}stats${NC}     - Show network statistics"
    echo ""
    echo -e "${GREEN}🧪 Testing:${NC}"
    echo -e "   ${CYAN}test${NC}      - Run network tests"
    echo -e "   ${CYAN}tx${NC}        - Submit test transactions"
    echo -e "   ${CYAN}p2p-test${NC}  - Test enhanced P2P features"
    echo ""
    echo -e "${GREEN}🔧 Utilities:${NC}"
    echo -e "   ${CYAN}clean${NC}     - Clean all data and logs"
    echo -e "   ${CYAN}keys${NC}      - Generate/manage keys"
    echo -e "   ${CYAN}config${NC}    - Show configuration"
    echo -e "   ${CYAN}help${NC}      - Show this menu"
    echo ""
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

check_requirements() {
    local missing_deps=()
    
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        return 1
    fi
    
    # Check for required Python scripts
    local required_scripts=("run_node.py" "test_transactions.py")
    for script in "${required_scripts[@]}"; do
        if [ ! -f "$script" ]; then
            log_error "Required script not found: $script"
            return 1
        fi
    done
    
    return 0
}

detect_running_nodes() {
    pgrep -f "run_node.py" | wc -l
}

start_network() {
    local nodes=${1:-10}
    local p2p_mode=${2:-enhanced}
    local extra_args="$3"
    
    log_info "Starting blockchain network..."
    echo ""
    
    if [ ! -f "./start_nodes_enhanced.sh" ]; then
        log_error "Enhanced startup script not found"
        return 1
    fi
    
    ./start_nodes_enhanced.sh -n "$nodes" -m "$p2p_mode" $extra_args
}

stop_network() {
    log_info "Stopping all blockchain nodes..."
    
    local running_nodes=$(detect_running_nodes)
    if [ "$running_nodes" -eq 0 ]; then
        log_warn "No running nodes detected"
        return 0
    fi
    
    pkill -f "run_node.py"
    sleep 3
    
    # Force kill if necessary
    local remaining_nodes=$(detect_running_nodes)
    if [ "$remaining_nodes" -gt 0 ]; then
        log_warn "Force killing remaining $remaining_nodes nodes"
        pkill -9 -f "run_node.py"
        sleep 1
    fi
    
    log_info "All nodes stopped"
    
    # Clean up PID files
    rm -f logs/*.pid 2>/dev/null || true
}

show_status() {
    local running_nodes=$(detect_running_nodes)
    
    echo -e "${WHITE}🔍 Network Status:${NC}"
    echo "─────────────────────────────────────"
    echo -e "   Running Nodes: ${GREEN}$running_nodes${NC}"
    
    if [ "$running_nodes" -eq 0 ]; then
        echo -e "   Status: ${RED}Network Down${NC}"
        return 0
    fi
    
    echo -e "   Status: ${GREEN}Network Active${NC}"
    echo ""
    
    # Check API endpoints
    local api_start=11000
    local active_apis=0
    
    echo -e "${WHITE}📡 API Status:${NC}"
    for i in $(seq 1 10); do
        local api_port=$((api_start + i - 1))
        if curl -s --max-time 1 "http://localhost:$api_port/api/v1/blockchain/" >/dev/null 2>&1; then
            echo -e "   Node $i (port $api_port): ${GREEN}✅ Active${NC}"
            ((active_apis++))
        else
            # Only show if we found some nodes
            if [ "$active_apis" -gt 0 ] && [ $i -le $((active_apis + 2)) ]; then
                echo -e "   Node $i (port $api_port): ${RED}❌ Down${NC}"
            fi
        fi
        
        # Stop checking after finding the gap
        if [ "$active_apis" -gt 0 ] && [ $i -gt $((active_apis + 2)) ]; then
            break
        fi
    done
    
    echo ""
    echo -e "   Active APIs: ${GREEN}$active_apis${NC}"
}

monitor_network() {
    if [ ! -f "./monitor_network.sh" ]; then
        log_error "Network monitor script not found"
        return 1
    fi
    
    log_info "Starting real-time network monitor..."
    ./monitor_network.sh "$@"
}

view_logs() {
    local node_num=${1:-1}
    local log_type=${2:-enhanced}
    local log_file="logs/node${node_num}_${log_type}.log"
    
    if [ ! -f "$log_file" ]; then
        log_file="logs/node${node_num}.log"
    fi
    
    if [ ! -f "$log_file" ]; then
        log_error "Log file not found: $log_file"
        echo ""
        echo "Available logs:"
        ls -la logs/*.log 2>/dev/null || echo "No log files found"
        return 1
    fi
    
    log_info "Viewing logs for node $node_num..."
    echo "Press Ctrl+C to stop"
    echo ""
    
    tail -f "$log_file"
}

run_tests() {
    local test_type=${1:-all}
    
    log_info "Running network tests..."
    echo ""
    
    case "$test_type" in
        p2p|enhanced)
            if [ -f "test_enhanced_p2p.py" ]; then
                log_info "Running enhanced P2P tests..."
                python3 test_enhanced_p2p.py
            else
                log_error "Enhanced P2P test script not found"
            fi
            ;;
        tx|transactions)
            if [ -f "test_transactions.py" ]; then
                log_info "Running transaction tests..."
                python3 test_transactions.py --count 10
            else
                log_error "Transaction test script not found"
            fi
            ;;
        all|*)
            if [ -f "test_enhanced_p2p.py" ]; then
                log_info "Running enhanced P2P tests..."
                python3 test_enhanced_p2p.py
                echo ""
            fi
            
            if [ -f "test_transactions.py" ]; then
                log_info "Running transaction tests..."
                python3 test_transactions.py --count 5
            fi
            ;;
    esac
}

submit_transactions() {
    local count=${1:-10}
    
    if [ ! -f "test_transactions.py" ]; then
        log_error "Transaction test script not found"
        return 1
    fi
    
    log_info "Submitting $count test transactions..."
    python3 test_transactions.py --count "$count"
}

clean_all() {
    echo -e "${YELLOW}⚠️  This will remove all blockchain data, logs, and stop running nodes.${NC}"
    echo -n "Continue? [y/N]: "
    read -r response
    
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        log_info "Cancelled by user"
        return 0
    fi
    
    log_info "Stopping all nodes..."
    stop_network
    
    log_info "Cleaning data and logs..."
    rm -rf logs/* 2>/dev/null || true
    rm -rf monitoring/* 2>/dev/null || true
    rm -f *.log 2>/dev/null || true
    
    # Clean blockchain data if exists
    if [ -d "data" ]; then
        rm -rf data/* 2>/dev/null || true
    fi
    
    log_info "Cleanup complete"
}

generate_keys() {
    local num_keys=${1:-10}
    
    if [ ! -f "generate_keys.sh" ]; then
        log_error "Key generation script not found"
        return 1
    fi
    
    log_info "Generating $num_keys node key pairs..."
    ./generate_keys.sh "$num_keys"
}

show_config() {
    echo -e "${WHITE}⚙️  Configuration:${NC}"
    echo "─────────────────────────────────────"
    echo -e "   Script Directory: ${CYAN}$SCRIPT_DIR${NC}"
    echo -e "   Python Version:   ${CYAN}$(python3 --version 2>/dev/null || echo 'Not found')${NC}"
    echo ""
    
    echo -e "${WHITE}📁 Available Scripts:${NC}"
    local scripts=("start_nodes_enhanced.sh" "monitor_network.sh" "test_enhanced_p2p.py" "test_transactions.py" "run_node.py")
    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            echo -e "   ✅ $script"
        else
            echo -e "   ❌ $script ${RED}(missing)${NC}"
        fi
    done
    
    echo ""
    echo -e "${WHITE}🔑 Keys Directory:${NC}"
    if [ -d "keys" ]; then
        local key_count=$(ls keys/*.pem 2>/dev/null | wc -l)
        echo -e "   📂 keys/ (${key_count} key files)"
    else
        echo -e "   ❌ keys/ ${RED}(missing)${NC}"
    fi
    
    echo ""
    echo -e "${WHITE}📊 Current Status:${NC}"
    local running_nodes=$(detect_running_nodes)
    echo -e "   Running Nodes: ${GREEN}$running_nodes${NC}"
}

interactive_mode() {
    while true; do
        echo ""
        echo -e "${WHITE}Enter command (or 'help' for options, 'quit' to exit):${NC}"
        echo -n "> "
        read -r command args
        
        case "$command" in
            start)
                start_network $args
                ;;
            stop)
                stop_network
                ;;
            restart)
                stop_network
                sleep 2
                start_network $args
                ;;
            status)
                show_status
                ;;
            monitor)
                monitor_network $args
                ;;
            logs)
                view_logs $args
                ;;
            test)
                run_tests $args
                ;;
            tx)
                submit_transactions $args
                ;;
            p2p-test)
                run_tests "p2p"
                ;;
            clean)
                clean_all
                ;;
            keys)
                generate_keys $args
                ;;
            config)
                show_config
                ;;
            stats)
                if [ -f "analyze_forgers.py" ]; then
                    python3 analyze_forgers.py
                else
                    show_status
                fi
                ;;
            help)
                print_menu
                ;;
            quit|exit|q)
                log_info "Goodbye!"
                exit 0
                ;;
            "")
                # Empty command, continue
                ;;
            *)
                log_error "Unknown command: $command"
                echo "Type 'help' for available commands"
                ;;
        esac
    done
}

# Main script execution
case "${1:-interactive}" in
    start)
        shift
        start_network "$@"
        ;;
    stop)
        stop_network
        ;;
    restart)
        stop_network
        sleep 2
        shift
        start_network "$@"
        ;;
    status)
        show_status
        ;;
    monitor)
        shift
        monitor_network "$@"
        ;;
    logs)
        shift
        view_logs "$@"
        ;;
    test)
        shift
        run_tests "$@"
        ;;
    tx)
        shift
        submit_transactions "$@"
        ;;
    p2p-test)
        run_tests "p2p"
        ;;
    clean)
        clean_all
        ;;
    keys)
        shift
        generate_keys "$@"
        ;;
    config)
        show_config
        ;;
    stats)
        if [ -f "analyze_forgers.py" ]; then
            python3 analyze_forgers.py
        else
            show_status
        fi
        ;;
    help|--help|-h)
        print_banner
        print_menu
        echo ""
        echo -e "${WHITE}Usage Examples:${NC}"
        echo -e "   ${CYAN}$0${NC}                    # Interactive mode"
        echo -e "   ${CYAN}$0 start 5 enhanced${NC}   # Start 5 nodes with enhanced P2P"
        echo -e "   ${CYAN}$0 monitor${NC}            # Real-time monitoring"
        echo -e "   ${CYAN}$0 test p2p${NC}           # Test enhanced P2P features"
        echo -e "   ${CYAN}$0 tx 20${NC}              # Submit 20 test transactions"
        echo ""
        ;;
    interactive|*)
        if ! check_requirements; then
            log_error "Requirements check failed"
            exit 1
        fi
        
        print_banner
        echo -e "${WHITE}Welcome to the Enhanced Blockchain Network Manager!${NC}"
        echo ""
        show_status
        print_menu
        interactive_mode
        ;;
esac
