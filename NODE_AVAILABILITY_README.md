# Node Availability Checker for Transaction Processing

This system provides comprehensive tools to check the availability of blockchain nodes for transaction processing. It helps you identify which nodes are ready to handle transactions and provides recommendations for optimal performance.

## Features

### 🔍 Comprehensive Node Health Checking
- **Process Status**: Checks if node processes are running
- **API Responsiveness**: Tests API endpoint availability and response times
- **Transaction Endpoints**: Verifies transaction submission endpoints
- **Leadership Status**: Identifies current and upcoming leaders
- **Quantum Consensus**: Monitors quantum consensus health
- **Network Connectivity**: Checks gossip and P2P connections

### 📊 Performance Metrics
- **Availability Scoring**: 0-100% availability score for each node
- **Response Time Analysis**: API and transaction endpoint timing
- **Network Latency**: Measures network performance
- **Transaction Readiness**: Categorizes nodes as ready/limited/not_ready

### 🚀 Automated Testing Integration
- **Auto Node Selection**: Automatically selects best nodes for testing
- **Multi-Node Testing**: Distributes transactions across multiple nodes
- **Performance Recommendations**: Suggests optimal testing configurations

## Files

### Core Components

1. **`node_availability_checker.py`** - Main availability checking system
2. **`batch_transaction_test.py`** - Enhanced with availability checking
3. **`quick_node_check.py`** - Simple one-command availability check

## Usage

### Basic Node Availability Check

```bash
# Check availability of all nodes
python node_availability_checker.py

# Detailed report for each node
python node_availability_checker.py --detailed

# Test actual transaction submission
python node_availability_checker.py --test-transactions

# Export results to JSON
python node_availability_checker.py --export-json availability_report.json
```

### Quick Check

```bash
# Quick check with recommendations
python quick_node_check.py
```

### Enhanced Batch Transaction Testing

```bash
# Check availability before testing
python batch_transaction_test.py --check-availability

# Auto-select best available node
python batch_transaction_test.py --auto-select --batch-size 100

# Multi-node distributed testing
python batch_transaction_test.py --multi-node --batch-size 300

# Traditional single-node test with availability check
python batch_transaction_test.py --node 11000 --check-availability
```

## Understanding the Output

### Node Status Categories

- **✅ Available**: Node is fully operational and ready for transactions
- **⚠️ Limited**: Node has some issues but can handle reduced load
- **🔶 Degraded**: Node is running but has significant issues
- **❌ Offline**: Node is not responding or not running

### Transaction Readiness

- **Ready**: Node can handle full transaction load
- **Limited**: Node can handle reduced transaction load
- **Not Ready**: Node cannot reliably process transactions

### Availability Score (0-100%)

The availability score is calculated based on:
- **Basic Health (40 points)**: Process running, API responsive, response time
- **Transaction Capabilities (30 points)**: Endpoint availability, acceptance rate
- **Consensus & Leadership (20 points)**: Quantum consensus, leader schedule
- **Network Connectivity (10 points)**: Gossip and P2P connections

## Example Output

```
🔍 CHECKING NODE AVAILABILITY FOR TRANSACTIONS
============================================================
Scanning 10 potential nodes...
Base API Port: 11000

📊 NODE AVAILABILITY SUMMARY
==================================================
Total Nodes Scanned: 10
✅ Available for Transactions: 5
❌ Unavailable: 5

🚀 TRANSACTION-READY NODES: 3
──────────────────────────────
  Node  1 (port 11000): 95.0% 👑
       API: 0.045s | TX: 0.052s
       Gossip: 4 peers | P2P: 3 peers
  Node  2 (port 11001): 87.5%
       API: 0.067s | TX: 0.089s
       Gossip: 3 peers | P2P: 2 peers
  Node  3 (port 11002): 82.0%
       API: 0.123s | TX: 0.156s
       Gossip: 2 peers | P2P: 2 peers

🚀 RECOMMENDATIONS FOR BATCH TRANSACTION TEST
==================================================
Best nodes for sending transactions:
  1. Node 1 (port 11000) - 95.0% (Current Leader)
  2. Node 2 (port 11001) - 87.5%
  3. Node 3 (port 11002) - 82.0%

Suggested batch_transaction_test.py commands:
  python batch_transaction_test.py --node 11000 --batch-size 100
  python batch_transaction_test.py --node 11000 --batch-size 50 --workers 25
```

## Integration with Existing Tools

### With batch_transaction_test.py

The enhanced batch transaction test now includes:

```bash
# New command line options
--check-availability    # Check node availability before testing
--auto-select          # Automatically select best node
--multi-node           # Distribute test across multiple nodes
```

### With Monitoring Tools

Works alongside existing monitoring tools:
- `check_node_health.py` - Basic health checking
- `monitoring_dashboard.py` - Real-time monitoring
- `bootstrap_network.py` - Network setup

## API Integration

You can also use the availability checker programmatically:

```python
from node_availability_checker import NodeAvailabilityChecker

# Create checker
checker = NodeAvailabilityChecker(base_port=11000, max_nodes=10)

# Check all nodes
available_nodes, unavailable_nodes = checker.check_all_nodes()

# Get best nodes for transactions
best_nodes = checker.get_best_nodes_for_transactions(count=3)

# Get detailed node information
for node in best_nodes:
    print(f"Node {node.node_id}: {node.availability_score}% available")
    print(f"  Transaction ready: {node.transaction_readiness}")
    print(f"  Is leader: {node.is_current_leader}")
```

## Troubleshooting

### No Nodes Found

```bash
# Check if nodes are running
python quick_node_check.py

# Start nodes if needed
cd blockchain && ./start_nodes.sh 5

# Check specific port ranges
python node_availability_checker.py --base-port 11000 --max-nodes 20
```

### Nodes Not Transaction-Ready

Common issues and solutions:

1. **API not responding**: Node may be starting up, wait a few seconds
2. **Transaction endpoint unavailable**: Check node configuration
3. **Low availability score**: Check network connectivity and consensus health
4. **No gossip peers**: Run network bootstrap: `python bootstrap_network.py`

### Performance Issues

1. **High response times**: Check system load and network latency
2. **Failed transactions**: Verify node has sufficient resources
3. **Low TPS**: Use nodes with higher availability scores

## Advanced Usage

### Custom Port Ranges

```bash
# Check non-standard port ranges
python node_availability_checker.py --base-port 21000 --max-nodes 5
```

### Detailed Analysis

```bash
# Export detailed data for analysis
python node_availability_checker.py --detailed --export-json full_report.json

# Test transaction submission capability
python node_availability_checker.py --test-transactions
```

### Performance Optimization

For best transaction performance:

1. Use nodes with availability scores > 80%
2. Prefer current leaders for immediate processing
3. Use multiple nodes for distributed load
4. Monitor response times and adjust batch sizes accordingly

## Integration with Your Workflow

1. **Before testing**: Run `python quick_node_check.py` to see available nodes
2. **During development**: Use `--check-availability` flag with batch tests
3. **Production monitoring**: Export JSON reports for analysis
4. **Automated testing**: Use `--auto-select` for CI/CD pipelines

This system helps ensure your transaction tests run against healthy, available nodes for more reliable and meaningful results.
