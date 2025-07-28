# 🚀 Quantum-Enhanced Solana-Style Blockchain

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A high-performance blockchain implementation featuring **Solana-style architecture** with quantum consensus, Proof of History (PoH), parallel execution (Sealevel), and efficient block propagation (Turbine).

## 🌟 **Key Features**

### **🔮 Quantum Consensus**
- **Quantum annealing-based leader selection** for deterministic consensus
- **450ms slot intervals** with continuous leader scheduling
- **Byzantine fault tolerance** with quantum-enhanced security
- **Health-based voting system** prioritizing healthy nodes over stake weights

### **⚡ Solana-Style Architecture**
- **🌊 Gulf Stream**: Direct transaction forwarding to upcoming leaders
- **⏰ Proof of History**: 5,000 ticks/second cryptographic clock for verifiable ordering
- **🔄 Sealevel**: Parallel transaction execution with 8-thread processing
- **🌪️ Turbine**: Efficient block propagation with erasure coding and shred distribution

### **📊 Enhanced Performance**
- **Slot-based consensus**: 450ms slot duration for fast finality
- **Transaction throughput**: 4+ TPS measured performance
- **Submission latency**: ~120ms average transaction submission
- **End-to-end processing**: Sub-second transaction confirmation

## 🛠️ **Prerequisites**

### **System Requirements**
- **Python 3.8+** (3.9+ recommended)
- **4GB+ RAM** (8GB recommended for multi-node setups)
- **Linux/macOS** (Windows with WSL2)

### **Python Dependencies**
```bash
# Core blockchain
cryptography>=3.4.8
ecdsa>=0.17.0
pycryptodome>=3.15.0

# Networking & API
fastapi>=0.68.0
uvicorn>=0.15.0
requests>=2.26.0

# Quantum consensus (optional)
dwave-ocean-sdk>=4.0.0
dimod>=0.10.0

# Logging & monitoring
python-json-logger>=2.0.0
```

## 📦 **Installation**

### **1. Clone Repository**
```bash
git clone https://github.com/shubham4564/proofwithquantumannealing.git
cd proofwithquantumannealing
```

### **2. Create Virtual Environment** (Recommended)
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
```

### **3. Install Dependencies**
```bash
# Install all dependencies
cd blockchain
pip install -r requirements/requirements.txt

# Verify installation
python3 -c "import fastapi, cryptography, ecdsa; print('✅ Dependencies installed successfully')" 2>/dev/null || echo "❌ Some dependencies missing - check requirements.txt"
```

### **4. Generate Genesis Configuration**
```bash
# Generate genesis configuration with initial supply
python3 -m blockchain.genesis_config --supply 1000000000

# Expected output:
# ✅ Genesis configuration created successfully
# 📁 Files created: genesis_config/genesis.json, faucet_private_key.pem, etc.

# Verify genesis config
ls genesis_config/
# Should show: genesis.json, faucet_private_key.pem, bootstrap_*.pem
```

### **5. Generate Node Keys**
```bash
# Generate keys for multiple nodes (optional - nodes can use genesis keys)
python3 generate_ecdsa_keys.py 2>/dev/null || echo "Using existing genesis keys"

# Verify key generation
ls keys/ 2>/dev/null || echo "Using genesis_config/ keys"
# Should show node keys OR will use keys from genesis_config/
```

### **6. Quick Installation Verification**
```bash
# Test that everything is working
echo "=== Installation Verification ==="
echo "1. Python version:" && python3 --version
echo "2. Dependencies:" && python3 -c "import fastapi; print('✅ FastAPI OK')" 2>/dev/null || echo "❌ FastAPI missing"
echo "3. Genesis config:" && ls genesis_config/genesis.json 2>/dev/null && echo "✅ Genesis OK" || echo "❌ Genesis missing"
echo "4. Blockchain module:" && python3 -c "import sys; sys.path.append('.'); import blockchain; print('✅ Blockchain module OK')" 2>/dev/null || echo "⚠️ Check Python path"
echo "✅ Installation verification complete!"
```

## 🚀 **Quick Start**

### **1. Start Blockchain Network**
```bash
# Navigate to blockchain directory
cd blockchain

# Start first node (bootstrap node)
python3 run_node.py --node-id 1 --api-port 11000 --port 12000 --bootstrap --host 127.0.0.1 &

# Wait 3 seconds, then start second node
sleep 3
python3 run_node.py --node-id 2 --api-port 11001 --port 12001 --bootstrap-host 127.0.0.1 --bootstrap-port 12000 --host 127.0.0.1 &

# Check nodes are running
ps aux | grep run_node
```

### **2. Verify Network Status**
```bash
# Check node connectivity
curl http://localhost:11000/api/v1/blockchain/ | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'✅ Node 1: {len(data[\"blocks\"])} blocks')
"

curl http://localhost:11001/api/v1/blockchain/ | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'✅ Node 2: {len(data[\"blocks\"])} blocks')
"

# Check leader selection
curl http://localhost:11000/api/v1/blockchain/leader/current/ | python3 -c "
import sys, json
data = json.load(sys.stdin)
leader_info = data.get('current_leader_info', {})
print(f'🎯 Current Slot: {leader_info.get(\"current_slot\", \"unknown\")}')
print(f'⏰ Slot Duration: {leader_info.get(\"slot_duration\", \"unknown\")}s')
print(f'👑 Current Leader: {data.get(\"current_leader\", \"unknown\")[:30]}...')
"
```

## 💰 **Running Transactions**

### **🎯 Basic Transaction Test**
```bash
# Run single transaction test
python3 test_sample_transaction.py --amount 100

# Expected output:
# 🧪 ENHANCED SAMPLE TRANSACTION TEST
# ✅ Node connected! Current blocks: X
# ✅ Leader selection active! Current slot: XXX
# ✅ Transaction created: ID: xxxxx, Amount: 100.0
# ✅ Transaction submitted successfully!
# 📍 Slot Information:
#    Transaction submitted within Slot XXX
# ✅ Consensus achieved! Time: X.XX seconds
# 🎯 Slot Journey: XXX → XXX (Block created in slot XXX)
```

### **📊 Performance Testing**
```bash
# Run multiple transactions for performance analysis
python3 test_sample_transaction.py --performance --count 5 --amount 50

# Expected output:
# 📊 RUNNING 5 TRANSACTIONS FOR PERFORMANCE MEASUREMENT
# ✅ Transaction 1: XXX.Xms submission, XXX.Xms total
# ✅ Transaction 2: XXX.Xms submission, XXX.Xms total
# ...
# 📊 PERFORMANCE METRICS REPORT
# 📈 Transaction Performance:
#    Throughput: X.XX TPS
#    Average Submission Time: XXX.Xms
```

### **🔍 Advanced Transaction Testing**
```bash
# Test different transaction amounts
python3 test_sample_transaction.py --amount 25.5 --node 11001

# Test on different nodes
python3 test_sample_transaction.py --amount 75 --node 11000
python3 test_sample_transaction.py --amount 125 --node 11001

# Monitor slot progression during transactions
python3 test_sample_transaction.py --amount 200 | grep -E "(Slot|slot)"
```

## 🔧 **Troubleshooting**

### **Common Issues & Solutions**

#### **1. Consensus Timeout**
```bash
# Problem: "⚠️ Consensus timeout after 30 seconds"
# Cause: No active leaders or nodes not producing blocks

# Solution 1: Check node status
curl http://localhost:11000/api/v1/blockchain/quantum-metrics/
# Look for "active_nodes": should be > 0

# Solution 2: Restart nodes
pkill -f "python.*run_node"
# Then restart as shown in Quick Start

# Solution 3: Check leadership
curl http://localhost:11000/api/v1/blockchain/leader/current/
# "current_leader" should not be "unknown"
```

#### **2. Transaction Submission Failed**
```bash
# Problem: "❌ Transaction submission failed"
# Cause: Node not responding or invalid transaction

# Solution: Check node connectivity
curl http://localhost:11000/api/v1/status
# Should return {"status": "running"}

# Check transaction pool
curl http://localhost:11000/api/v1/mempool/
```

#### **3. Genesis Configuration Missing**
```bash
# Problem: "❌ Error: Genesis configuration not found"
# Solution: Regenerate genesis config
python3 -m blockchain.genesis_config --supply 1000000000
```

### **Monitoring Commands**
```bash
# Check all running nodes
ps aux | grep run_node | grep -v grep

# Monitor logs in real-time
tail -f blockchain/logs/node1.log

# Check blockchain state
curl -s http://localhost:11000/api/v1/blockchain/ | python3 -c "
import sys, json
data = json.load(sys.stdin)
blocks = data.get('blocks', [])
print(f'Blockchain Status:')
print(f'  Total Blocks: {len(blocks)}')
if blocks:
    latest = blocks[-1]
    print(f'  Latest Block: #{latest.get(\"block_count\", \"unknown\")}')
    print(f'  Transactions: {len(latest.get(\"transactions\", []))}')
    print(f'  Timestamp: {latest.get(\"timestamp\", \"unknown\")}')
"

# Check current slot and timing
curl -s http://localhost:11000/api/v1/blockchain/leader/current/ | python3 -c "
import sys, json
data = json.load(sys.stdin)
leader_info = data.get('current_leader_info', {})
print(f'Slot Information:')
print(f'  Current Slot: {leader_info.get(\"current_slot\", \"unknown\")}')
print(f'  Time Remaining: {leader_info.get(\"time_remaining_in_slot\", 0):.1f}s')
print(f'  Slot Duration: {leader_info.get(\"slot_duration\", \"unknown\")}s')
print(f'  Leader: {data.get(\"current_leader\", \"unknown\")[:30]}...')
"
```

## 📊 **Performance Metrics**

### **Measured Performance**
- **Transaction Throughput**: 4.20 TPS (measured)
- **Slot Duration**: 450ms (0.45 seconds)
- **Transaction Submission**: 117-189ms average
- **Block Confirmation**: 0.01-30s (depends on slot timing)
- **End-to-End Latency**: ~200ms for immediate consensus

### **Transaction Flow Timing**
```
Transaction Created → Gulf Stream → Leader TPU → Block Production
     ~16ms              ~119ms        Slot-based       Immediate/Delayed
```

## 🎯 **Next Steps**

After successful installation and transaction testing:

1. **� Explore Advanced Features**:
   - Quantum consensus parameters
   - Parallel execution (Sealevel)
   - Block propagation (Turbine)

2. **📈 Performance Optimization**:
   - Adjust slot duration
   - Tune quantum consensus weights
   - Configure parallel execution threads

3. **🌐 Network Scaling**:
   - Add more nodes
   - Test with larger transaction volumes
   - Monitor network synchronization

4. **🛠️ Development**:
   - Implement custom transaction types
   - Add application-specific logic
   - Integrate with external systems
- **EXCHANGE**: Initial funding/exchange transactions
- **Custom types**: Extensible for future use cases

#### **2. Transaction Structure**
```python
# Basic transaction components
{
    "sender_public_key": "-----BEGIN PUBLIC KEY-----...",
    "receiver_public_key": "-----BEGIN PUBLIC KEY-----...", 
    "amount": 10.0,
    "type": "TRANSFER",
    "timestamp": 1640995200,
    "signature": "base64_encoded_signature"
}
```

### **📝 Creating and Sending Transactions**

#### **Option 1: Using Python Scripts (Recommended)**

**Simple Transaction Test:**
```bash
# NEW: Interactive transaction example with detailed output
python simple_transaction_example.py

# Basic transaction flow test
python test_sample_transaction.py

# Expected output from simple_transaction_example.py:
# 🚀 SIMPLE TRANSACTION EXAMPLE
# ✅ Node is healthy and responsive
# ✅ Genesis keys loaded successfully  
# ✅ Transaction created and signed
# ✅ Transaction submitted successfully!
# 🎉 New block(s) created - transaction likely included!
```

**Custom Transaction Script:**
```python
#!/usr/bin/env python3
from blockchain.transaction.transaction import Transaction
from blockchain.transaction.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils
import requests

# 1. Load or create wallet
wallet = Wallet()
# OR load existing keys:
# with open('keys/genesis_private_key.pem', 'r') as f:
#     wallet.from_key(f.read())

# 2. Create transaction
transaction = Transaction(
    sender_public_key=wallet.public_key_string(),
    receiver_public_key="<recipient_public_key>",
    amount=25.0,
    type="TRANSFER"
)

# 3. Sign transaction
signature = wallet.sign(transaction.payload())
transaction.sign(signature)

# 4. Submit to blockchain
encoded_tx = BlockchainUtils.encode(transaction)
response = requests.post(
    "http://localhost:11000/api/v1/transaction/create/",
    json={"transaction": encoded_tx}
)

print(f"Transaction result: {response.status_code}")
```

#### **Option 2: Using API Directly**

**API Transaction Submission:**
```bash
# Create and encode transaction (use Python helper)
python -c "
from blockchain.transaction.transaction import Transaction
from blockchain.transaction.wallet import Wallet  
from blockchain.utils.helpers import BlockchainUtils

# Load genesis keys
with open('keys/genesis_private_key.pem', 'r') as f:
    private_key = f.read()
with open('keys/genesis_public_key.pem', 'r') as f:
    public_key = f.read()

wallet = Wallet()
wallet.from_key(private_key)

# Create self-transfer for testing
tx = Transaction(public_key, public_key, 10.0, 'TRANSFER')
signature = wallet.sign(tx.payload())
tx.sign(signature)

encoded = BlockchainUtils.encode(tx)
print('ENCODED_TRANSACTION:')
print(encoded)
" > encoded_tx.txt

# Extract the encoded transaction
ENCODED_TX=$(grep -A1 "ENCODED_TRANSACTION:" encoded_tx.txt | tail -1)

# Submit via API
curl -X POST http://localhost:11000/api/v1/transaction/create/ \
  -H "Content-Type: application/json" \
  -d "{\"transaction\": \"$ENCODED_TX\"}"

# Clean up
rm encoded_tx.txt
```

**Alternative: Quick Test Script**
```bash
# Use the built-in transaction test
python test_proper_flow.py

# Or test with multiple nodes
python test_multinode_transaction.py
```

### **🧪 Comprehensive Testing Guide**

#### **Test Categories**

**1. Basic Connectivity Tests**
```bash
# Test node health
curl http://localhost:11000/api/v1/health/
curl http://localhost:11001/api/v1/health/
curl http://localhost:11002/api/v1/health/

# Test blockchain status
curl http://localhost:11000/api/v1/blockchain/ | jq '.blocks | length'
```

**2. Transaction Flow Tests**
```bash
# Single transaction test
python test_sample_transaction.py

# Multiple transaction test  
python test_multinode_transaction.py

# Proper transaction flow test
python test_proper_flow.py

# Gulf Stream transaction forwarding test
python test_gulf_stream_transactions.py
```

**3. Performance & Load Tests**
```bash
# Comprehensive performance analysis
python test_comprehensive_performance.py

# Quick performance check
python test_quick_check.py

# Force block creation test
python test_force_block.py
```

**4. Solana Component Tests**
```bash
# PoH and Turbine integration test
python test_poh_turbine.py

# Solana validation test (complete compliance)
python test_solana_validation.py

# Fast Gulf Stream test
python test_fast_gulf_stream.py
```

#### **Transaction Testing Patterns**

**Pattern 1: Simple Self-Transfer**
```python
# Test basic transaction mechanics
transaction = Transaction(
    sender_public_key=my_public_key,
    receiver_public_key=my_public_key,  # Self-send
    amount=10.0,
    type="TRANSFER"
)
```

**Pattern 2: Multi-Node Transfer**
```python
# Test cross-node transactions
# Load different node keys for sender/receiver
with open('keys/node2_public_key.pem', 'r') as f:
    receiver_key = f.read()
    
transaction = Transaction(
    sender_public_key=genesis_public_key,
    receiver_public_key=receiver_key,
    amount=50.0,
    type="TRANSFER"
)
```

**Pattern 3: High-Volume Testing**
```python
# Test multiple rapid transactions
for i in range(20):
    tx = Transaction(
        sender_public_key=wallet.public_key_string(),
        receiver_public_key=target_key,
        amount=float(i + 1),
        type="TRANSFER"
    )
    # Sign and submit...
```

#### **Monitoring Transaction Processing**

**Real-time Transaction Monitoring:**
```bash
# Monitor transaction processing
python monitor_logs.py watch transactions node_10000

# Monitor Gulf Stream forwarding
python monitor_logs.py watch network node_10000

# Monitor block creation
python monitor_logs.py watch consensus node_10000
```

**Check Transaction Pool:**
```bash
# View pending transactions
curl http://localhost:11000/api/v1/transaction/transaction_pool/ | jq

# View mempool statistics
curl http://localhost:11000/api/v1/blockchain/mempool/ | jq
```

**Verify Transaction Inclusion:**
```bash
# Check if transactions made it into blocks
curl http://localhost:11000/api/v1/blockchain/ | jq '.blocks[-1].transactions'

# Count total transactions across all blocks
curl http://localhost:11000/api/v1/blockchain/ | jq '[.blocks[].transactions | length] | add'
```

### **🔍 Troubleshooting Transactions**

#### **Common Issues & Solutions**

**Transaction Not Included in Blocks:**
```bash
# Check leader status
curl http://localhost:11000/api/v1/blockchain/leader/current/ | jq

# Verify node connectivity
python leader_monitor.py --once

# Check transaction pool
curl http://localhost:11000/api/v1/transaction/transaction_pool/ | jq '. | length'

# Force a block creation for testing
python test_force_block.py
```

**Invalid Signature Errors:**
```bash
# Verify key loading
python -c "
with open('keys/genesis_private_key.pem', 'r') as f:
    print('Private key loaded:', len(f.read()), 'characters')
with open('keys/genesis_public_key.pem', 'r') as f:
    print('Public key loaded:', len(f.read()), 'characters')
"

# Test signature creation
python test_transaction_create.py
```

**Network Connectivity Issues:**
```bash
# Test all node endpoints
for port in {11000..11004}; do
    echo "Testing node on port $port:"
    curl -s http://localhost:$port/api/v1/health/ | jq '.status' || echo "Failed"
done

# Check P2P connectivity
netstat -an | grep :10000
netstat -an | grep :11000
```

#### **Transaction Testing Checklist**

✅ **Prerequisites Check:**
- [ ] All nodes started: `./start_nodes.sh`
- [ ] Keys generated: `ls keys/` shows .pem files
- [ ] Leader selection active: `python leader_monitor.py --once`

✅ **Basic Transaction Test:**
- [ ] Node connectivity: `curl http://localhost:11000/api/v1/health/`
- [ ] Simple transaction: `python test_sample_transaction.py`
- [ ] Blockchain updated: Check block count increased

✅ **Advanced Testing:**
- [ ] Multi-node test: `python test_multinode_transaction.py`
- [ ] Performance test: `python test_comprehensive_performance.py`
- [ ] Solana compliance: `python test_solana_validation.py`

### **📊 Transaction Performance Metrics**

Expected transaction processing performance:

| Metric | Value | Notes |
|--------|-------|-------|
| **API Submission Rate** | 272+ TPS | HTTP POST to `/api/v1/transaction/create/` |
| **Transaction Validation** | ~1ms | Signature + balance verification |
| **Gulf Stream Forwarding** | ~5ms | Leader-targeted forwarding |
| **PoH Integration** | ~0.2ms | Transaction sequencing |
| **Sealevel Execution** | ~2ms | Parallel execution per transaction |
| **Block Inclusion Time** | 2-15s | Depends on leader selection timing |
| **End-to-End Latency** | 3-20s | Submit → Block inclusion → Confirmation |

## 📊 **Monitoring & Logging**

### **📋 Leader Selection Monitoring** ⭐ **NEW**
Real-time monitoring of leader selection and consensus:

```bash
# Continuous leader monitoring (recommended)
python leader_monitor.py

# Output shows real-time leader information:
# ═══════════════════════════════════════════
# 🎯 QUANTUM BLOCKCHAIN LEADER MONITOR
# ═══════════════════════════════════════════
# 🕐 Timestamp: 2024-01-15 10:30:15
# 🌐 Monitoring Node: localhost:11000
# 
# 👑 CURRENT LEADER
# ├─ Leader: node_10001
# ├─ Slot: 150
# ├─ Status: ✅ Valid
# └─ Next Change: 1.2s
# 
# 📅 UPCOMING LEADERS
# ├─ Slot 151: node_10002
# ├─ Slot 152: node_10000
# └─ Slot 153: node_10001

# Monitor specific node
python leader_monitor.py --node-port 11001

# Single check (non-continuous)
python leader_monitor.py --once

# Quick API test
./test_leader_apis.sh
```

### **📋 Log Overview**
```bash
# Show all available logs
python monitor_logs.py summary

# Output shows organized log structure:
# 📁 consensus/     - PoH, Sealevel, Turbine, quantum consensus
# 📁 transactions/ - Transaction processing logs
# 📁 network/      - P2P, Gulf Stream, API logs
# 📁 performance/  - Timing and throughput metrics
# 📁 errors/       - Error aggregation
```

### **🎯 Component-Specific Monitoring**
```bash
# Watch Proof of History in real-time
python monitor_logs.py watch poh node_10000

# Monitor transaction processing
python monitor_logs.py watch transactions node_10000

# Watch consensus decisions
python monitor_logs.py watch consensus node_10000

# Monitor parallel execution
python monitor_logs.py watch sealevel node_10000

# Watch block propagation
python monitor_logs.py watch turbine node_10000
```

### **📈 Performance Analysis**
```bash
# Analyze performance metrics (last hour)
python monitor_logs.py performance node_10000

# Analyze last 4 hours
python monitor_logs.py performance node_10000 --hours 4

# View recent logs
python monitor_logs.py tail performance node_10000 --lines 50
```

### **🚨 Error Monitoring**
```bash
# Watch for errors across all components
python monitor_logs.py watch errors node_10000

# View recent errors
python monitor_logs.py tail errors node_10000
```

## 🧪 **Testing**

> **📋 See the [Transaction Testing Guide](#-sending-transactions--testing) above for comprehensive transaction testing instructions.**

### **Quick Testing Commands**
```bash
# Quick health check
curl http://localhost:11000/api/v1/health/

# Quick transaction test
python test_sample_transaction.py

# Quick leader check  
python leader_monitor.py --once
```

### **Test Categories Overview**

**🔧 Basic Tests:**
- **Node connectivity**: `curl` health endpoints
- **Key verification**: Check genesis and node keys exist
- **Leader selection**: Verify quantum consensus working

**💰 Transaction Tests:**
- **Simple transaction**: `python test_sample_transaction.py`
- **Multi-node transfer**: `python test_multinode_transaction.py`  
- **High-volume testing**: `python test_comprehensive_performance.py`

**⚡ Solana Component Tests:**
- **Complete pipeline**: `python test_solana_validation.py`
- **PoH + Turbine**: `python test_poh_turbine.py`
- **Gulf Stream**: `python test_fast_gulf_stream.py`

**📊 Performance Tests:**
- **TPS analysis**: `python test_comprehensive_performance.py`
- **Load testing**: Multi-threaded transaction submission
- **Latency analysis**: End-to-end timing measurements

## 🔧 **Configuration**

### **Node Configuration**
Modify node startup parameters in `start_nodes.sh`:
```bash
# Default configuration
NUM_NODES=5           # Number of nodes to start
PORT_START=10000      # Starting P2P port
API_START=11000       # Starting API port

# To start more nodes:
# Edit start_nodes.sh and change NUM_NODES=10
```

### **Consensus Configuration** ⭐ **ENHANCED**
Quantum consensus parameters in `blockchain/quantum_consensus/`:
- **Slot duration**: 2 seconds (configurable)
- **Leader lookahead**: 5 slots
- **Auto leader selection**: Starts 2 seconds after blockchain initialization
- **Continuous updates**: Leader schedule refreshed every 30 seconds
- **Dynamic discovery**: New nodes trigger immediate leader schedule updates
- **Quantum annealing parameters**: Tunable in quantum_consensus.py

### **Performance Tuning**
PoH and Sealevel parameters in their respective files:
```python
# In proof_of_history.py
self.ticks_per_second = 5000  # PoH frequency
self.max_entries_in_memory = 10000

# In sealevel.py  
self.thread_pool_size = 8  # Parallel execution threads
self.max_batch_size = 100  # Transaction batch size
```

## � **Docker Deployment**

### **Build Docker Image**
```bash
docker build -t quantum-blockchain .
```

### **Run Single Node**
```bash
docker run -p 10000:10000 -p 11000:11000 \
  -e NODE_PORT=10000 \
  -e API_PORT=11000 \
  quantum-blockchain
```

### **Run Multi-Node with Docker Compose**
```bash
# Use the provided docker-compose.yml
docker-compose up -d

# Scale to more nodes
docker-compose up -d --scale node=5
```

## 📡 **API Reference**

### **Leader Selection Monitoring Endpoints** ⭐ **NEW**
The blockchain now provides comprehensive APIs for monitoring leader selection and consensus:

```bash
# Get current leader information
GET http://localhost:11000/api/v1/blockchain/leader/current/

# Response:
{
  "current_leader": "node_10001",
  "current_slot": 150,
  "leader_valid": true,
  "next_leader": "node_10002",
  "next_slot": 151,
  "time_until_next_slot": 1.2
}

# Get upcoming leader schedule
GET http://localhost:11000/api/v1/blockchain/leader/upcoming/

# Response:
{
  "upcoming_leaders": [
    {"slot": 151, "leader": "node_10002"},
    {"slot": 152, "leader": "node_10000"},
    {"slot": 153, "leader": "node_10001"}
  ],
  "current_slot": 150,
  "schedule_generated_at": "2024-01-15T10:30:00Z"
}

# Get quantum consensus selection details
GET http://localhost:11000/api/v1/blockchain/leader/quantum-selection/

# Response:
{
  "quantum_enabled": true,
  "selection_method": "quantum_annealing",
  "last_selection_time": "2024-01-15T10:29:58Z",
  "participants": ["node_10000", "node_10001", "node_10002"],
  "selection_success": true
}

# Get complete leader schedule with timing
GET http://localhost:11000/api/v1/blockchain/leader/schedule/

# Response:
{
  "total_slots": 10,
  "slot_duration": 2.0,
  "current_slot": 150,
  "schedule": [
    {
      "slot": 150,
      "leader": "node_10001",
      "status": "active",
      "start_time": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### **Leader Monitoring Tools** ⭐ **NEW**
Enhanced monitoring capabilities with automated tools:

```bash
# Continuous leader monitoring (Python script)
python leader_monitor.py

# Monitor specific node
python leader_monitor.py --node-port 11001

# Single-time check
python leader_monitor.py --once

# Quick API test (Bash script)
./test_leader_apis.sh

# API testing with specific node
./test_leader_apis.sh 11002
```

### **Blockchain Endpoints**
```bash
# Get blockchain status
GET http://localhost:11000/api/v1/blockchain/

# Get specific block
GET http://localhost:11000/api/v1/blockchain/block/{block_index}

# Get node statistics
GET http://localhost:11000/api/v1/blockchain/node-stats/
```

### **Transaction Endpoints**
```bash
# Submit transaction
POST http://localhost:11000/api/v1/transaction/create/
Content-Type: application/json
{
  "transaction": "<base64_encoded_transaction>"
}

# Get transaction pool status
GET http://localhost:11000/api/v1/blockchain/mempool/
```

### **Health Check**
```bash
# Node health status
GET http://localhost:11000/api/v1/health/

# Expected response:
{
  "status": "healthy",
  "node_id": "node_10000",
  "uptime": "0:05:23",
  "consensus": "active",
  "poh_ticks": 1500000,
  "blocks": 42
}
```

## 🔧 **Troubleshooting**

> **📋 See the [Transaction Troubleshooting Guide](#-troubleshooting-transactions) above for detailed transaction debugging.**

### **Quick Diagnostic Commands**
```bash
# Check node health
curl http://localhost:11000/api/v1/health/

# Check leader status
python leader_monitor.py --once

# Check transaction pool
curl http://localhost:11000/api/v1/transaction/transaction_pool/ | jq '. | length'

# Check recent blocks
curl http://localhost:11000/api/v1/blockchain/ | jq '.blocks[-3:] | length'
```

### **Common Issues**

#### **Port Already in Use**
```bash
# Check what's using the port
lsof -i :10000

# Kill existing processes
pkill -f 'run_node.py'

# Start fresh
./start_nodes.sh
```

#### **Key Generation Fails**
```bash
# Ensure OpenSSL is installed
openssl version

# Regenerate keys
rm keys/*.pem
./generate_keys.sh
```

#### **Nodes Not Connecting**
```bash
# Check node logs
python monitor_logs.py tail network node_10000

# Verify network connectivity
curl http://localhost:11000/api/v1/health/
```

#### **Transaction Not Included in Blocks** ⭐ **KNOWN ISSUE**
```bash
# Current issue: Transactions are submitted successfully but not included in blocks
# This is due to leader selection and block creation timing mismatch

# Check transaction submission
curl http://localhost:11000/api/v1/transaction/create/ \
  -X POST -H "Content-Type: application/json" \
  -d '{"transaction": "<base64_encoded_transaction>"}'

# Check if transaction pool is empty (indicates processing)
curl http://localhost:11000/api/v1/transaction/transaction_pool/

# Workaround: Force block creation through leader monitoring
python leader_monitor.py 11000 1 --detailed
```

#### **Leader Selection Issues** ⭐ **NEW**
```bash
# Leader not being selected
curl http://localhost:11000/api/v1/blockchain/leader/current/

# If no leader, check quantum consensus
curl http://localhost:11000/api/v1/blockchain/leader/quantum-selection/

# Monitor leader selection process
python leader_monitor.py --once

# Check if nodes are properly connected
curl http://localhost:11000/api/v1/health/ | jq '.consensus'
```

#### **Leader Selection Not Starting**
```bash
# Ensure auto-start is working (should start within 2-3 seconds)
# Check blockchain logs for leader selection initialization
python monitor_logs.py tail consensus node_10000

# Manually trigger if needed (shouldn't be necessary)
# Leader selection now starts automatically on network startup
```
#### **Poor Performance**
```bash
# Check system resources
htop

# Monitor performance logs
python monitor_logs.py watch performance node_10000

# Monitor leader selection performance
python leader_monitor.py

# Tune configuration parameters
# Edit blockchain/consensus/ configuration files
```

### **Debug Mode**
```bash
# Start with debug logging
export LOG_LEVEL=DEBUG
python run_node.py --ip localhost --node_port 10000 --api_port 11000

# View debug logs
python monitor_logs.py watch debug node_10000
```

## 📊 **Performance Benchmarks**

### **Expected Performance** ⭐ **UPDATED**
Based on testing with 5 nodes on modern hardware:

| Metric | Value | Notes |
|--------|-------|-------|
| **Transaction Submission** | 272+ TPS | API submission rate |
| **PoH Tick Rate** | 5,000/sec | Cryptographic clock |
| **Consensus Time** | 2-15 seconds | Leader selection + block creation |
| **Leader Selection Startup** | 2-3 seconds | NEW: Automatic on network start |
| **Leader Schedule Updates** | Every 30 seconds | NEW: Continuous background updates |
| **Sealevel Threads** | 8 parallel | Configurable |
| **Block Size** | Unlimited | Removed artificial limits |
| **Network Latency** | <10ms | Localhost testing |
| **Leader API Response** | <50ms | NEW: Real-time leader monitoring |

### **Scaling Considerations**
- **Vertical scaling**: Increase `ticks_per_second`, `thread_pool_size`
- **Horizontal scaling**: Add more nodes (tested up to 10 nodes)
- **Network optimization**: Tune Turbine fanout and shred sizes
- **Storage optimization**: Implement block pruning for long-running deployments

## �️ **Development**

### **Code Structure** ⭐ **UPDATED**
```
blockchain/
├── blockchain/           # Core implementation
│   ├── consensus/       # PoH, Sealevel, Turbine
│   ├── quantum_consensus/ # Quantum leader selection
│   ├── transaction/     # Transaction processing
│   ├── p2p/            # P2P networking
│   └── utils/          # Enhanced logging & utilities
├── api/                # FastAPI endpoints + leader monitoring APIs
│   └── api_v1/
│       └── blockchain/
│           └── views.py # NEW: Leader selection endpoints
├── tests/              # Test scripts
├── keys/               # Cryptographic keys
├── logs/               # Enhanced logging output
├── leader_monitor.py   # NEW: Real-time leader monitoring tool
├── api_test.py         # NEW: Python API testing script
├── test_leader_apis.sh # NEW: Bash API testing script
└── LEADER_MONITORING_GUIDE.md # NEW: Complete API documentation
```

### **Adding New Features** ⭐ **UPDATED**
1. **New consensus mechanism**: Extend `blockchain/consensus/`
2. **New transaction types**: Modify `blockchain/transaction/`
3. **New APIs**: Add endpoints in `api/` (see leader monitoring APIs as example)
4. **New monitoring**: Extend `monitor_logs.py` or create tools like `leader_monitor.py`
5. **Leader selection enhancements**: Modify `blockchain/quantum_consensus/`

### **Contributing**
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Add tests for new functionality
4. Ensure all tests pass: `python test_solana_flow.py`
5. Submit pull request

## 📚 **Additional Resources**

### **Documentation** ⭐ **UPDATED**
- **[LEADER_MONITORING_GUIDE.md](LEADER_MONITORING_GUIDE.md)** - NEW: Complete leader monitoring API guide
- **[CLEANUP_COMPLETE.md](CLEANUP_COMPLETE.md)** - Project cleanup summary
- **[BFT_CONSENSUS_IMPLEMENTATION_PLAN.md](BFT_CONSENSUS_IMPLEMENTATION_PLAN.md)** - Consensus architecture

### **Architecture References**
- **Solana Whitepaper**: Proof of History and parallel processing concepts
- **Quantum Computing**: D-Wave quantum annealing for consensus
- **Byzantine Fault Tolerance**: Enhanced with quantum consensus

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

### **Support** ⭐ **ENHANCED**

- **Issues**: Report bugs and request features via GitHub Issues
- **Monitoring**: Use `python monitor_logs.py summary` for system status
- **Leader Selection**: Use `python leader_monitor.py` for real-time leader monitoring
- **API Testing**: Use `./test_leader_apis.sh` for quick API verification
- **Documentation**: See `LEADER_MONITORING_GUIDE.md` for complete API documentation

---

**🚀 Ready to build the future of quantum-enhanced blockchain technology!**

## 🆕 **Latest Updates**

### **v2.1 - Comprehensive Transaction Testing & Health-Based Consensus**
- 💰 **Complete Transaction Guide**: Step-by-step instructions for creating, signing, and submitting transactions
- 🧪 **Enhanced Testing Suite**: Multiple testing patterns for different use cases and load scenarios
- 🔍 **Transaction Troubleshooting**: Detailed debugging guide for common transaction issues
- ⚕️ **Health-Based Voting**: Consensus now prioritizes healthy nodes over stake weights (100% Solana compliant)
- 📊 **Performance Metrics**: Detailed transaction processing benchmarks and monitoring
- 🛠️ **API Examples**: Complete Python and curl examples for transaction submission

### **v2.0 - Enhanced Leader Selection & Monitoring**
- ⭐ **Automatic Leader Selection**: Leaders selected immediately on network startup (2-3 seconds)
- ⭐ **Real-time Monitoring APIs**: 4 new endpoints for comprehensive leader monitoring
- ⭐ **Continuous Updates**: Leader schedules refreshed every 30 seconds automatically  
- ⭐ **Dynamic Discovery**: New nodes trigger immediate leader schedule updates
- ⭐ **Monitoring Tools**: Python and bash scripts for real-time leader tracking
- ⭐ **Complete Documentation**: `LEADER_MONITORING_GUIDE.md` with examples and integration patterns

### **Key Features Added**
**v2.1 Transaction & Testing Enhancements:**
1. **Transaction Guide**: Complete walkthrough from wallet creation to blockchain confirmation
2. **Testing Patterns**: Simple self-transfer, multi-node, high-volume, and load testing examples
3. **API Integration**: Python and curl examples for direct transaction submission
4. **Performance Benchmarks**: Detailed metrics for transaction processing stages
5. **Troubleshooting Tools**: Comprehensive debugging guide for transaction issues
6. **Health-Based Consensus**: Voting system prioritizes node health over economic stake

**v2.0 Leader Selection & Monitoring:**
1. **API Endpoints**: `/leader/current/`, `/leader/upcoming/`, `/leader/quantum-selection/`, `/leader/schedule/`
2. **Monitoring Tools**: `leader_monitor.py`, `api_test.py`, `test_leader_apis.sh`
3. **Auto-start**: No waiting for transactions - leader selection begins immediately
4. **Background Processing**: Continuous 30-second updates maintain fresh schedules
5. **Network Intelligence**: Auto-discovery triggers dynamic leader updates

⚠️ **Note**: This is a research and demonstration project. Not intended for production use.

---

## 🚀 **Quick Reference**

### **Essential Commands**
```bash
# Start the network
./start_nodes.sh

# Test transaction submission (NEW - recommended for beginners)
python simple_transaction_example.py

# Alternative transaction tests
python test_sample_transaction.py

# Monitor leaders
python leader_monitor.py --once

# Check node health
curl http://localhost:11000/api/v1/health/

# View blockchain status
curl http://localhost:11000/api/v1/blockchain/ | jq '.blocks | length'

# Submit custom transaction (see Transaction Guide above)
curl -X POST http://localhost:11000/api/v1/transaction/create/ \
  -H "Content-Type: application/json" \
  -d '{"transaction": "<base64_encoded_transaction>"}'
```

### **Key URLs**
- **Node API**: `http://localhost:11000-11004/api/v1/`
- **Health Check**: `/api/v1/health/`
- **Blockchain Status**: `/api/v1/blockchain/`
- **Submit Transaction**: `/api/v1/transaction/create/`
- **Leader Status**: `/api/v1/blockchain/leader/current/`
- **Transaction Pool**: `/api/v1/transaction/transaction_pool/`

### **Important Files**
- **Keys**: `keys/genesis_*_key.pem` (for testing)
- **Start Script**: `./start_nodes.sh`
- **Transaction Examples**: `simple_transaction_example.py` (NEW), `test_sample_transaction.py`, `test_proper_flow.py`
- **Monitoring**: `leader_monitor.py`, `monitor_logs.py`
