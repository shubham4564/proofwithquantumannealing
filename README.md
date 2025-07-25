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

### **1. Start Blockchain Network**
```bash
# Start 5 nodes (ports 10000-10004 for P2P, 11000-11004 for API)
./start_nodes.sh

# Expected output:
# 🚀 Starting 5 blockchain nodes...
# ✅ All 5 nodes started!
# 📡 Node ports: 10000-10004
# 🌐 API ports: 11000-11004
# 📝 Enhanced Logs: Use 'python monitor_logs.py summary' to view all logs
```

### **2. Verify Node Status**
```bash
# Check if nodes are responding
curl http://localhost:11000/api/v1/blockchain/ | jq

# Should return blockchain status with blocks array
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

### **4. Load Testing**
```bash
# Test with multiple concurrent transactions
python test_comprehensive_performance.py --transactions 50 --threads 5

# Monitor during load test (separate terminal)
python monitor_logs.py watch performance node_10000
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

### **Consensus Configuration**
Quantum consensus parameters in `blockchain/quantum_consensus/`:
- **Slot duration**: 2 seconds (configurable)
- **Leader lookahead**: 5 slots
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

#### **Poor Performance**
```bash
# Check system resources
htop

# Monitor performance logs
python monitor_logs.py watch performance node_10000

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

### **Expected Performance**
Based on testing with 5 nodes on modern hardware:

| Metric | Value | Notes |
|--------|-------|-------|
| **Transaction Submission** | 272+ TPS | API submission rate |
| **PoH Tick Rate** | 5,000/sec | Cryptographic clock |
| **Consensus Time** | 2-15 seconds | Leader selection + block creation |
| **Sealevel Threads** | 8 parallel | Configurable |
| **Block Size** | Unlimited | Removed artificial limits |
| **Network Latency** | <10ms | Localhost testing |

### **Scaling Considerations**
- **Vertical scaling**: Increase `ticks_per_second`, `thread_pool_size`
- **Horizontal scaling**: Add more nodes (tested up to 10 nodes)
- **Network optimization**: Tune Turbine fanout and shred sizes
- **Storage optimization**: Implement block pruning for long-running deployments

## �️ **Development**

### **Code Structure**
```
blockchain/
├── blockchain/           # Core implementation
│   ├── consensus/       # PoH, Sealevel, Turbine
│   ├── quantum_consensus/ # Quantum leader selection
│   ├── transaction/     # Transaction processing
│   ├── p2p/            # P2P networking
│   └── utils/          # Enhanced logging & utilities
├── api/                # FastAPI endpoints
├── tests/              # Test scripts
├── keys/               # Cryptographic keys
└── logs/               # Enhanced logging output
```

### **Adding New Features**
1. **New consensus mechanism**: Extend `blockchain/consensus/`
2. **New transaction types**: Modify `blockchain/transaction/`
3. **New APIs**: Add endpoints in `api/`
4. **New monitoring**: Extend `monitor_logs.py`

### **Contributing**
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Add tests for new functionality
4. Ensure all tests pass: `python test_solana_flow.py`
5. Submit pull request

## 📚 **Additional Resources**

### **Documentation**
- **[CLEANUP_COMPLETE.md](CLEANUP_COMPLETE.md)** - Project cleanup summary
- **[BFT_CONSENSUS_IMPLEMENTATION_PLAN.md](BFT_CONSENSUS_IMPLEMENTATION_PLAN.md)** - Consensus architecture

### **Architecture References**
- **Solana Whitepaper**: Proof of History and parallel processing concepts
- **Quantum Computing**: D-Wave quantum annealing for consensus
- **Byzantine Fault Tolerance**: Enhanced with quantum consensus

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 **Support**

- **Issues**: Report bugs and request features via GitHub Issues
- **Monitoring**: Use `python monitor_logs.py summary` for system status

---

**🚀 Ready to build the future of quantum-enhanced blockchain technology!**

⚠️ **Note**: This is a research and demonstration project. Not intended for production use.
