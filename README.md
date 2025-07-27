# 🚀 Quantum-Enhanced Solana-Style Blockchain

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A high-performance blockchain implementation featuring **Solana-style architecture** with quantum consensus, Proof of History (PoH), parallel execution (Sealevel), and efficient block propagation (Turbine).

## � **Key Features**

### **🔮 Quantum Consensus**
- **Quantum annealing-based leader selection** for deterministic consensus
- **2-second slot intervals** with continuous leader scheduling
- **Byzantine fault tolerance** with quantum-enhanced security

### **⚡ Solana-Style Architecture**
- **🌊 Gulf Stream**: Direct transaction forwarding to upcoming leaders
- **⏰ Proof of History**: 5,000 ticks/second cryptographic clock for verifiable ordering
- **🔄 Sealevel**: Parallel transaction execution with 8-thread processing
- **🌪️ Turbine**: Efficient block propagation with erasure coding and shred distribution

### **📊 Enhanced Logging & Monitoring**
- **Component-specific logs**: Separate files for PoH, Sealevel, Turbine, consensus, transactions
- **Performance metrics**: Real-time TPS monitoring and latency analysis
- **Real-time monitoring**: Live log tailing and component analysis
- **JSON-structured logs**: Machine-readable for automated analysis

## �️ **Prerequisites**

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

## � **Installation**

### **1. Clone Repository**
```bash
git clone https://github.com/shubham4564/proofwithquantumannealing.git
cd proofwithquantumannealing/blockchain
```

### **2. Install Dependencies**
```bash
# Using pip (recommended)
pip install -r requirements/requirements.txt

# Or using conda
conda create -n blockchain python=3.9
conda activate blockchain
pip install -r requirements/requirements.txt
```

### **3. Generate Cryptographic Keys**
```bash
# Generate keys for nodes (genesis + node keys)
chmod +x generate_keys.sh
./generate_keys.sh

# Verify key generation
ls keys/
# Should show: genesis_private_key.pem, genesis_public_key.pem, node*_private_key.pem, etc.
```

## 🚀 **Quick Start**

### **1. Start Blockchain Network** ⭐ **AUTO LEADER SELECTION**
```bash
# Start 5 nodes (ports 10000-10004 for P2P, 11000-11004 for API)
./start_nodes.sh

# Expected output:
# 🚀 Starting 5 blockchain nodes...
# ✅ All 5 nodes started!
# 📡 Node ports: 10000-10004
# 🌐 API ports: 11000-11004
# 📝 Enhanced Logs: Use 'python monitor_logs.py summary' to view all logs

# NEW: Leader selection now starts automatically!
# ⭐ Leaders are selected within 2-3 seconds of network startup
# ⭐ No need to wait for transactions to trigger leader selection
# ⭐ Continuous leader schedule updates every 30 seconds
```

### **2. Verify Node Status & Leader Selection** ⭐ **ENHANCED**
```bash
# Check if nodes are responding
curl http://localhost:11000/api/v1/blockchain/ | jq

# Should return blockchain status with blocks array

# Monitor leader selection (NEW!)
curl http://localhost:11000/api/v1/blockchain/leader/current/ | jq

# Expected response showing active leader:
{
  "current_leader": "node_10001",
  "current_slot": 5,
  "leader_valid": true,
  "next_leader": "node_10002",
  "next_slot": 6,
  "time_until_next_slot": 1.8
}

# Use monitoring tools for continuous tracking
python leader_monitor.py --once
```

### **3. Run Transaction Test**
```bash
# Simple transaction flow test
python simple_blockchain_test.py

# Comprehensive Solana-style flow test
python test_solana_flow.py

# Performance analysis test
python test_comprehensive_performance.py
```

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

### **1. Simple Transaction Test**
Tests basic transaction submission and blockchain interaction:
```bash
python simple_blockchain_test.py

# What it tests:
# ✅ Node connectivity
# ✅ Transaction creation and signing
# ✅ API submission
# ✅ Blockchain state changes
# ✅ Block creation monitoring
```

### **2. Solana-Style Flow Test**
Tests the complete Solana architecture pipeline:
```bash
python test_solana_flow.py

# What it tests:
# ✅ Gulf Stream transaction forwarding
# ✅ PoH transaction sequencing
# ✅ Sealevel parallel execution
# ✅ Turbine block propagation
# ✅ End-to-end transaction flow
```

### **3. Comprehensive Performance Test**
Analyzes performance metrics and throughput:
```bash
python test_comprehensive_performance.py

# What it measures:
# ✅ Transaction submission TPS
# ✅ PoH tick generation rate
# ✅ Sealevel execution parallelism
# ✅ Consensus timing
# ✅ Network latency
# ✅ End-to-end transaction processing time
```

### **4. Load Testing & Leader Monitoring** ⭐ **ENHANCED**
```bash
# Test with multiple concurrent transactions
python test_comprehensive_performance.py --transactions 50 --threads 5

# Monitor during load test (separate terminal)
python monitor_logs.py watch performance node_10000

# Monitor leader selection during high load (NEW!)
python leader_monitor.py

# Test leader APIs under load
./test_leader_apis.sh
```

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

## � **Troubleshooting**

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

### **v2.0 - Enhanced Leader Selection & Monitoring**
- ⭐ **Automatic Leader Selection**: Leaders selected immediately on network startup (2-3 seconds)
- ⭐ **Real-time Monitoring APIs**: 4 new endpoints for comprehensive leader monitoring
- ⭐ **Continuous Updates**: Leader schedules refreshed every 30 seconds automatically  
- ⭐ **Dynamic Discovery**: New nodes trigger immediate leader schedule updates
- ⭐ **Monitoring Tools**: Python and bash scripts for real-time leader tracking
- ⭐ **Complete Documentation**: `LEADER_MONITORING_GUIDE.md` with examples and integration patterns

### **Key Features Added**
1. **API Endpoints**: `/leader/current/`, `/leader/upcoming/`, `/leader/quantum-selection/`, `/leader/schedule/`
2. **Monitoring Tools**: `leader_monitor.py`, `api_test.py`, `test_leader_apis.sh`
3. **Auto-start**: No waiting for transactions - leader selection begins immediately
4. **Background Processing**: Continuous 30-second updates maintain fresh schedules
5. **Network Intelligence**: Auto-discovery triggers dynamic leader updates

⚠️ **Note**: This is a research and demonstration project. Not intended for production use.
