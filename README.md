# Quantum Annealing Consensus Blockchain

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

This is an advanced implementation of a blockchain that uses **Quantum Annealing** principles as its consensus mechanism. The project demonstrates how quantum-inspired optimization can improve fairness, security, and decentralization in blockchain networks through energy minimization approaches.

## 🌟 Features

- **Quantum Annealing-based Consensus** algorithm
- Energy minimization approach for validator selection  
- Dynamic parameter adjustment based on network conditions
- P2P communication with node discovery
- RESTful API with FastAPI
- Multi-node network support
- Comprehensive transaction testing framework
- Real-time network monitoring and analysis
- Docker support for easy deployment

⚠️ **Note**: This is a research and demonstration project. Not intended for production use.


## 📋 Prerequisites

### System Requirements
- **Python**: 3.12 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 4GB RAM (8GB recommended for multiple nodes)
- **Storage**: At least 1GB free space

### Required Software
- Git
- Python 3.12+
- pip (Python package manager)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/shubham4564/proofwithquantumannealing.git
cd proofwithquantumannealing
```

### 2. Set up Python Virtual Environment

#### On Windows (PowerShell):
```powershell
python -m venv .winvenv
.\.winvenv\Scripts\Activate.ps1
```

#### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
cd blockchain
pip install -r req.txt
```

## 🔧 Configuration

### Generate Cryptographic Keys
Before starting nodes, generate the necessary cryptographic keys:

```bash
# Navigate to blockchain directory
cd blockchain

# Generate keys (if not already present)
bash generate_keys.sh
```

This creates keys in the `keys/` directory:
- `genesis_private_key.pem` - Genesis node key
- `node[1-10]_private_key.pem` - Individual node keys

## 🏃‍♂️ Running the Blockchain

### Quick Start - Single Node
```bash
cd blockchain
python run_node.py --ip localhost --node_port 10000 --api_port 11000 --key_file keys/genesis_private_key.pem
```

### Multi-Node Network

#### Option 1: Using PowerShell Script (Windows)
```powershell
cd blockchain
.\start_nodes_clean.ps1 [NUMBER_OF_NODES]

# Examples:
.\start_nodes_clean.ps1      # Start 10 nodes (default)
.\start_nodes_clean.ps1 5    # Start 5 nodes
```

#### Option 2: Using Bash Script (Linux/macOS/WSL)
```bash
cd blockchain
./start_nodes.sh [NUMBER_OF_NODES]

# Examples:
./start_nodes.sh      # Start 10 nodes (default)  
./start_nodes.sh 5    # Start 5 nodes
```

#### Option 3: Manual Node Startup
```bash
# Terminal 1 - Node 1 (Genesis)
python run_node.py --ip localhost --node_port 10000 --api_port 11000 --key_file keys/genesis_private_key.pem

# Terminal 2 - Node 2  
python run_node.py --ip localhost --node_port 10001 --api_port 11001 --key_file keys/node2_private_key.pem

# Terminal 3 - Node 3
python run_node.py --ip localhost --node_port 10002 --api_port 11002 --key_file keys/node3_private_key.pem
```

### Network Ports
- **Node Ports**: 10000-10009 (P2P communication)
- **API Ports**: 11000-11009 (HTTP REST API)

## 📊 Testing Transactions

### Single Transaction Test
```bash
cd blockchain
python test_transactions.py --count 1 --node_port 11000
```

### Multiple Transaction Test
```bash
# Send 10 transactions
python test_transactions.py --count 10

# Send 50 transactions with specific target node
python test_transactions.py --count 50 --node_port 11001

# Stress test with 100 transactions
python test_transactions.py --count 100 --amount_range 1 100
```

### Advanced Transaction Testing
```bash
# Test with custom parameters
python test_transactions.py \
    --count 25 \
    --node_port 11000 \
    --amount_range 10 1000 \
    --delay 0.5

# Test different transaction types
python test_transactions.py --count 10 --transaction_type TRANSFER
```

### Transaction Test Parameters
- `--count`: Number of transactions to send (default: 10)
- `--node_port`: Target node API port (default: 11000)
- `--amount_range`: Min and max transaction amounts (default: 1 100)
- `--delay`: Delay between transactions in seconds (default: 1.0)
- `--transaction_type`: Transaction type (TRANSFER, STAKE, etc.)

## 📈 Network Monitoring

### Analyze Network Performance
```bash
cd blockchain

# Basic network analysis
python analyze_forgers.py

# Real-time monitoring (30-second intervals)
python analyze_forgers.py --watch 30

# Generate detailed reports
python analyze_forgers.py --detailed --export
```

### Check Node Status
```bash
# Check if nodes are responding
curl http://localhost:11000/api/v1/blockchain/
curl http://localhost:11001/api/v1/blockchain/
curl http://localhost:11002/api/v1/blockchain/
```

### Performance Testing
```bash
# Quick performance test
python quick_performance_test.py

# Comprehensive performance analysis
python flexible_performance_test.py --nodes 5 --transactions 100

# Batch performance testing
python batch_performance_test.py
```

## 🔍 API Endpoints

### Blockchain Information
- `GET /api/v1/blockchain/` - Get blockchain state

### Quantum Consensus Metrics
- `GET /api/v1/blockchain/quantum-metrics/` - Get quantum consensus data

### Example API Calls
```bash
# Get blockchain info
curl http://localhost:11000/api/v1/blockchain/

# Get quantum metrics
curl http://localhost:11000/api/v1/blockchain/quantum-metrics/
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Import Errors / Module Not Found
```bash
# Ensure you're in the correct directory and virtual environment is activated
cd blockchain
pip install -r req.txt
```

#### 2. Port Already in Use
```bash
# Kill existing processes
# Windows:
taskkill /f /im python.exe

# Linux/macOS:
pkill -f "run_node.py"
```

#### 3. Nodes Not Responding
Check the log files:
```bash
# View node logs
cat logs/node1.log
cat logs/node1_error.log

# Real-time log monitoring
tail -f logs/node1.log
```

#### 4. Key File Not Found
```bash
# Generate missing keys
bash generate_keys.sh

# Or manually create specific key
python -c "
from blockchain.transaction.wallet import Wallet
wallet = Wallet()
wallet.save_keys('keys/node1_private_key.pem', 'keys/node1_public_key.pem')
"
```

### Performance Optimization

#### For Multiple Nodes:
- Increase delay between node startups if experiencing connection issues
- Monitor system resources (CPU, memory) during high transaction loads
- Use SSD storage for better I/O performance

#### For High Transaction Volumes:
- Adjust transaction pool size in configuration
- Modify consensus parameters for faster block generation
- Consider running nodes on separate machines for true distributed testing

## 📁 Project Structure

```
proofwithquantumannealing/
├── blockchain/
│   ├── api/                    # REST API implementation
│   ├── blockchain/             # Core blockchain logic
│   │   ├── quantum_consensus/  # Quantum annealing consensus
│   │   ├── transaction/        # Transaction handling
│   │   └── utils/             # Utility functions
│   ├── keys/                  # Cryptographic keys
│   ├── logs/                  # Node operation logs
│   ├── documentation/         # Technical documentation
│   ├── tests/                 # Unit and integration tests
│   ├── req.txt               # Python dependencies
│   ├── run_node.py           # Node startup script
│   ├── test_transactions.py  # Transaction testing
│   ├── analyze_forgers.py    # Network analysis
│   └── start_nodes_clean.ps1 # Multi-node startup (Windows)
└── README.md                 # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check existing documentation in the `blockchain/documentation/` directory
- Review the troubleshooting section above

---

**Disclaimer**: This is a research project for educational and demonstration purposes. Do not use in production environments or with real financial assets.
