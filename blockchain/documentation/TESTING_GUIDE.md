# 🚀 Multi-Node Quantum Annealing Consensus Testing Guide

This guide will help you set up and test multiple blockchain nodes with the quantum annealing consensus mechanism.

## 📋 Prerequisites

1. **Python Environment**: Ensure you have the virtual environment activated
2. **Required Packages**: All dependencies should be installed via requirements
3. **Project Structure**: You should be in the blockchain directory

## 🏗️ Step 1: Start Multiple Nodes

### Option A: Use the Node Starter Script (Recommended)
```bash
# Start 3 nodes (default)
python start_nodes.py

# Start 4 nodes
python start_nodes.py --nodes 4

# Start nodes on different ports
python start_nodes.py --nodes 3 --base-node-port 9000 --base-api-port 9050
```

### Option B: Start Nodes Manually
Open separate terminal windows and run:

```bash
# Terminal 1 - Node 0 (Genesis node)
python run_node.py --ip localhost --node_port 8000 --api_port 8050 --key_file ./keys/genesis_private_key.pem

# Terminal 2 - Node 1
python run_node.py --ip localhost --node_port 8001 --api_port 8051

# Terminal 3 - Node 2
python run_node.py --ip localhost --node_port 8002 --api_port 8052

# Terminal 4 - Node 3 (optional)
python run_node.py --ip localhost --node_port 8003 --api_port 8053
```

## 📊 Step 2: Run Sample Transactions

Wait about 30 seconds for nodes to initialize, then:

```bash
# Run the enhanced sample transactions
python sample_transactions.py
```

This will:
- Create test wallets
- Send exchange transactions
- Set up staking for quantum consensus
- Execute transfer transactions
- Display performance metrics
- Show blockchain and quantum consensus state

## 🧪 Step 3: Run Comprehensive Multi-Node Tests

```bash
# Run full test suite with 3 nodes, 30 transactions over 60 seconds
python multi_node_test.py

# Custom test configuration
python multi_node_test.py --nodes 4 --transactions 50 --duration 120
```

This will:
- Test transaction processing across all nodes
- Measure consensus performance
- Analyze block timing and throughput
- Check node synchronization
- Generate detailed performance reports

## 📈 Step 4: Monitor and Analyze

### API Endpoints
With 3 nodes running, you can access:

- **Node 0**: http://localhost:8050/api/v1/blockchain/
- **Node 1**: http://localhost:8051/api/v1/blockchain/
- **Node 2**: http://localhost:8052/api/v1/blockchain/

### Quantum Metrics
- **Node 0**: http://localhost:8050/api/v1/blockchain/quantum-metrics/
- **Node 1**: http://localhost:8051/api/v1/blockchain/quantum-metrics/
- **Node 2**: http://localhost:8052/api/v1/blockchain/quantum-metrics/

### Real-time Monitoring
```bash
# Monitor blockchain growth
watch -n 5 'curl -s http://localhost:8050/api/v1/blockchain/ | jq ".blocks | length"'

# Monitor quantum metrics
watch -n 5 'curl -s http://localhost:8050/api/v1/blockchain/quantum-metrics/ | jq'
```

## 🔬 Step 5: Run Quantum Demo

```bash
# Interactive quantum consensus demonstration
python quantum_demo.py
```

## 📊 Understanding the Metrics

### Transaction Performance
- **Response Time**: Time from transaction submission to API response
- **Success Rate**: Percentage of successful transactions
- **Throughput**: Transactions per second

### Block Performance
- **Block Time**: Time between consecutive blocks
- **Consensus Time**: Time for quantum annealing consensus to select forger
- **Synchronization**: How well nodes stay in sync

### Quantum Consensus Metrics
- **Total Nodes**: Number of registered nodes in consensus
- **Active Nodes**: Nodes actively participating
- **Probe Count**: Number of network measurements performed
- **Node Scores**: Suitability scores for each node
- **Selection Distribution**: How often each node is selected as forger

## 🔧 Troubleshooting

### Nodes Not Starting
```bash
# Check if ports are available
netstat -an | grep -E ':(8050|8051|8052)'

# Kill existing processes if needed
pkill -f run_node.py
```

### API Connection Issues
```bash
# Test API connectivity
curl http://localhost:8050/api/v1/blockchain/

# Check node logs
# Look at terminal output where nodes are running
```

### Transaction Failures
- Ensure nodes have had time to initialize (30+ seconds)
- Check that staking transactions have been processed
- Verify wallet balances are sufficient

## 📋 Test Scenarios

### 1. Basic Functionality Test
```bash
python start_nodes.py --nodes 3
# Wait 30 seconds
python sample_transactions.py
```

### 2. Load Testing
```bash
python start_nodes.py --nodes 4
# Wait 30 seconds
python multi_node_test.py --nodes 4 --transactions 100 --duration 300
```

### 3. Consensus Fairness Test
```bash
python start_nodes.py --nodes 5
# Wait 30 seconds
python multi_node_test.py --nodes 5 --transactions 200 --duration 600
```

## 📈 Expected Results

### Good Performance Indicators
- **Transaction Success Rate**: >95%
- **Average Response Time**: <1 second
- **Block Time**: 10-30 seconds
- **Node Synchronization**: ≤1 block difference

### Quantum Consensus Health
- **Active Nodes**: Should match total registered nodes
- **Probe Count**: Should be increasing over time
- **Fair Selection**: No single node should dominate (>80%) forger selection
- **Score Distribution**: Nodes with better performance should have higher scores

## 🛑 Stopping Nodes

### If using start_nodes.py
Press `Ctrl+C` in the terminal where start_nodes.py is running

### If starting manually
Press `Ctrl+C` in each terminal, or run:
```bash
pkill -f run_node.py
```

## 📊 Sample Output Analysis

Look for these key indicators in the output:

```
📈 TRANSACTION PERFORMANCE SUMMARY
Total Transactions: 30
Successful: 29 (96.7%)
Failed: 1 (3.3%)
Average Response Time: 0.245s

⛓️ BLOCK PERFORMANCE
Average Block Time: 15.3s
Transaction Throughput: 1.89 tx/s

🔄 NODE SYNCHRONIZATION
node_0: 5 blocks
node_1: 5 blocks
node_2: 5 blocks
✅ Excellent synchronization

🔬 QUANTUM CONSENSUS METRICS
Total Nodes: 4
Active Nodes: 4
Probe Count: 156
Fair Selection Distribution: ✅
```

This indicates a healthy, well-performing quantum annealing consensus network!

## 🎯 Next Steps

1. **Experiment with different node counts** (3-6 nodes work well)
2. **Test various transaction loads** (10-200 transactions)
3. **Monitor long-running tests** (30+ minutes)
4. **Analyze consensus fairness** over extended periods
5. **Compare with traditional PoS** if available

The quantum annealing consensus should demonstrate:
- **Better fairness** than pure stake-based selection
- **Performance-aware** forger selection
- **Network adaptability** through probe protocols
- **Robust consensus** even with varying node performance
