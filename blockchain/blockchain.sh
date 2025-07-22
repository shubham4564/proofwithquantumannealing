#!/bin/bash

# Blockchain Network Management Script
# Flexible management of blockchain nodes with automatic scaling

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Default values
DEFAULT_NODES=10
MAX_NODES=50

# Function to print colored output
print_colored() {
    echo -e "$1$2${NC}"
}

# Function to print section headers
print_header() {
    echo ""
    print_colored "$BLUE" "🔹 $1"
    echo "$(printf '%*s' "${#1}" '' | tr ' ' '=')"
}

# Function to show usage
show_usage() {
    echo "🚀 Blockchain Network Management Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start [N]     - Start N nodes (default: $DEFAULT_NODES)"
    echo "  stop          - Stop all running nodes"
    echo "  restart [N]   - Restart with N nodes"
    echo "  status        - Show network status"
    echo "  analyze       - Analyze forgers and metrics"
    echo "  test [N]      - Run transaction test with N transactions"
    echo "  keys [N]      - Generate keys for N nodes"
    echo "  watch         - Monitor network in real-time"
    echo "  clean         - Clean logs and temporary files"
    echo "  help          - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start 5    # Start 5 nodes"
    echo "  $0 test 20    # Run 20 transactions"
    echo "  $0 analyze    # Analyze current network"
    echo "  $0 watch      # Monitor network continuously"
    echo ""
}

# Function to check dependencies
check_dependencies() {
    local missing=0
    
    if ! command -v python3 &> /dev/null; then
        print_colored "$RED" "❌ python3 is required but not installed"
        missing=1
    fi
    
    if ! command -v curl &> /dev/null; then
        print_colored "$RED" "❌ curl is required but not installed"
        missing=1
    fi
    
    if ! command -v openssl &> /dev/null; then
        print_colored "$YELLOW" "⚠️  openssl not found - key generation will be limited"
    fi
    
    if [ ! -f "run_node.py" ]; then
        print_colored "$RED" "❌ run_node.py not found - are you in the correct directory?"
        missing=1
    fi
    
    return $missing
}

# Function to validate node count
validate_node_count() {
    local count=$1
    if ! [[ "$count" =~ ^[0-9]+$ ]] || [ "$count" -lt 1 ] || [ "$count" -gt $MAX_NODES ]; then
        print_colored "$RED" "❌ Invalid node count: $count (must be 1-$MAX_NODES)"
        return 1
    fi
    return 0
}

# Function to count running nodes
count_running_nodes() {
    local count=0
    for port in $(seq 11000 11099); do
        if curl -s "http://localhost:$port/api/v1/blockchain/" >/dev/null 2>&1; then
            ((count++))
        fi
    done
    echo $count
}

# Function to start nodes
start_nodes() {
    local num_nodes=${1:-$DEFAULT_NODES}
    
    if ! validate_node_count $num_nodes; then
        return 1
    fi
    
    print_header "Starting $num_nodes Blockchain Nodes"
    
    # Check if nodes are already running
    local running=$(count_running_nodes)
    if [ $running -gt 0 ]; then
        print_colored "$YELLOW" "⚠️  $running nodes are already running"
        read -p "Stop existing nodes and start fresh? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            stop_nodes
        else
            print_colored "$CYAN" "🔄 Keeping existing nodes running"
            return 0
        fi
    fi
    
    # Generate keys if needed
    if [ ! -f "keys/genesis_private_key.pem" ]; then
        print_colored "$RED" "❌ Genesis key not found. Please ensure keys exist first."
        return 1
    fi
    
    # Start nodes
    print_colored "$GREEN" "🚀 Starting $num_nodes nodes..."
    if [ -f "start_nodes.sh" ]; then
        ./start_nodes.sh $num_nodes
    else
        print_colored "$RED" "❌ start_nodes.sh not found"
        return 1
    fi
}

# Function to stop nodes
stop_nodes() {
    print_header "Stopping All Blockchain Nodes"
    
    local running=$(count_running_nodes)
    if [ $running -eq 0 ]; then
        print_colored "$CYAN" "ℹ️  No nodes are currently running"
        return 0
    fi
    
    print_colored "$YELLOW" "🛑 Stopping $running running nodes..."
    pkill -f "run_node.py" 2>/dev/null || true
    sleep 3
    
    # Verify all stopped
    local still_running=$(count_running_nodes)
    if [ $still_running -eq 0 ]; then
        print_colored "$GREEN" "✅ All nodes stopped successfully"
    else
        print_colored "$YELLOW" "⚠️  $still_running nodes still running (may take a moment to shut down)"
    fi
}

# Function to show network status
show_status() {
    print_header "Network Status"
    
    local running=$(count_running_nodes)
    print_colored "$CYAN" "📊 Running Nodes: $running"
    
    if [ $running -eq 0 ]; then
        print_colored "$YELLOW" "💤 Network is not running"
        return 0
    fi
    
    # Quick analysis
    if [ -f "analyze_forgers.py" ]; then
        print_colored "$GREEN" "🔍 Running quick analysis..."
        python3 analyze_forgers.py --nodes $running
    else
        # Manual status check
        print_colored "$BLUE" "🔍 Manual status check:"
        for port in $(seq 11000 $((11000 + 20))); do
            if curl -s "http://localhost:$port/api/v1/blockchain/" >/dev/null 2>&1; then
                node_num=$((port - 11000 + 1))
                print_colored "$GREEN" "   ✅ Node $node_num (Port $port): Running"
            fi
        done
    fi
}

# Function to analyze network
analyze_network() {
    print_header "Network Analysis"
    
    local running=$(count_running_nodes)
    if [ $running -eq 0 ]; then
        print_colored "$RED" "❌ No nodes are running. Start nodes first with: $0 start"
        return 1
    fi
    
    if [ -f "analyze_forgers.py" ]; then
        python3 analyze_forgers.py --nodes $running
    else
        print_colored "$RED" "❌ analyze_forgers.py not found"
        return 1
    fi
}

# Function to run transaction test
run_test() {
    local tx_count=${1:-10}
    
    if ! [[ "$tx_count" =~ ^[0-9]+$ ]] || [ "$tx_count" -lt 1 ]; then
        print_colored "$RED" "❌ Invalid transaction count: $tx_count"
        return 1
    fi
    
    print_header "Running Transaction Test ($tx_count transactions)"
    
    local running=$(count_running_nodes)
    if [ $running -eq 0 ]; then
        print_colored "$RED" "❌ No nodes are running. Start nodes first with: $0 start"
        return 1
    fi
    
    if [ -f "test_transactions.py" ]; then
        python3 test_transactions.py --count $tx_count
    else
        print_colored "$RED" "❌ test_transactions.py not found"
        return 1
    fi
}

# Function to generate keys
generate_keys() {
    local num_nodes=${1:-$DEFAULT_NODES}
    
    if ! validate_node_count $num_nodes; then
        return 1
    fi
    
    print_header "Generating Keys for $num_nodes Nodes"
    
    if [ -f "generate_keys.sh" ]; then
        ./generate_keys.sh $num_nodes
    else
        print_colored "$RED" "❌ generate_keys.sh not found"
        return 1
    fi
}

# Function to watch network
watch_network() {
    print_header "Real-time Network Monitoring"
    
    local running=$(count_running_nodes)
    if [ $running -eq 0 ]; then
        print_colored "$RED" "❌ No nodes are running. Start nodes first with: $0 start"
        return 1
    fi
    
    print_colored "$CYAN" "👀 Monitoring $running nodes (Press Ctrl+C to stop)"
    
    if [ -f "analyze_forgers.py" ]; then
        python3 analyze_forgers.py --watch 10 --nodes $running
    else
        print_colored "$RED" "❌ analyze_forgers.py not found"
        return 1
    fi
}

# Function to clean up
clean_up() {
    print_header "Cleaning Up"
    
    print_colored "$YELLOW" "🧹 Cleaning logs and temporary files..."
    
    # Clean log files
    if [ -d "logs" ]; then
        rm -f logs/*.log
        print_colored "$GREEN" "✅ Cleaned log files"
    fi
    
    # Clean Python cache
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    print_colored "$GREEN" "✅ Cleaned Python cache"
    
    print_colored "$GREEN" "🎉 Cleanup complete!"
}

# Main script logic
main() {
    # Check if help is requested
    if [ $# -eq 0 ] || [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        show_usage
        return 0
    fi
    
    # Check dependencies
    if ! check_dependencies; then
        print_colored "$RED" "❌ Please install missing dependencies"
        return 1
    fi
    
    # Parse command
    local command=$1
    shift || true
    
    case $command in
        "start")
            start_nodes $1
            ;;
        "stop")
            stop_nodes
            ;;
        "restart")
            stop_nodes
            sleep 2
            start_nodes $1
            ;;
        "status")
            show_status
            ;;
        "analyze")
            analyze_network
            ;;
        "test")
            run_test $1
            ;;
        "keys")
            generate_keys $1
            ;;
        "watch")
            watch_network
            ;;
        "clean")
            clean_up
            ;;
        *)
            print_colored "$RED" "❌ Unknown command: $command"
            echo ""
            show_usage
            return 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
