# Decentralized Blockchain Network Deployment Guide

## Overview

This guide shows you how to set up a decentralized blockchain network that can run:

1. **Single Computer Setup**: 6 nodes on one computer (for development/testing)
2. **Multi-Computer Setup**: 6 nodes distributed across 6 computers in the same subnet

Both setups create a fully decentralized network with:
- ✅ Quantum consensus mechanism
- ✅ Automatic peer discovery and connection
- ✅ Gulf Stream transaction forwarding
- ✅ Turbine block propagation
- ✅ Performance monitoring
- ✅ Gossip protocol for leader schedules

## Prerequisites

### System Requirements
- Python 3.8+
- Network connectivity (for multi-computer setup)
- Ports 8050-8055, 10000-10005, 12000-12005, 13000-13005, 14000-14005 available
- At least 4GB RAM per computer
- Linux/macOS (Windows with WSL)

### Software Dependencies
```bash
# Install Python dependencies
cd blockchain
pip install -r requirements.txt

# Ensure all blockchain modules are available
python -c "from blockchain.blockchain import Blockchain; print('✅ Blockchain modules ready')"
```

## Setup 1: Single Computer Network (6 Nodes)

Perfect for development, testing, and demonstration purposes.

### Quick Start
```bash
# Start 6-node network on single computer
./start_single_computer_network.sh

# Stop the network
./stop_network.sh
```

### What This Creates
- **6 blockchain nodes** running on localhost
- **Automatic P2P connections** between all nodes
- **Shared genesis block** for network consistency
- **Load-balanced API access** across all nodes

### Node Configuration
| Node | API Port | P2P Port | Role |
|------|----------|----------|------|
| 1    | 8050     | 10000    | Bootstrap (Genesis) |
| 2    | 8051     | 10001    | Validator |
| 3    | 8052     | 10002    | Validator |
| 4    | 8053     | 10003    | Validator |
| 5    | 8054     | 10004    | Validator |
| 6    | 8055     | 10005    | Validator |

### Key Endpoints
- **Blockchain Explorer**: http://127.0.0.1:8050/api/v1/blockchain/
- **Performance Metrics**: http://127.0.0.1:8050/api/v1/blockchain/performance-metrics/
- **Network Status**: http://127.0.0.1:8050/api/v1/blockchain/network-status/
- **Transaction Submission**: http://127.0.0.1:8050/api/v1/blockchain/transaction/

## Setup 2: Multi-Computer Network (6 Computers)

For production deployments across multiple physical machines.

### Network Requirements
- **Same subnet**: All computers must be in the same subnet (e.g., 192.168.1.x)
- **Open ports**: Firewall must allow communication on blockchain ports
- **Static IPs**: Preferably static IP addresses or DHCP reservations

### Step-by-Step Deployment

#### Step 1: Prepare Each Computer
On each of the 6 computers:

```bash
# Clone the repository
git clone <your-repo-url>
cd proofwithquantumannealing

# Install dependencies
cd blockchain
pip install -r requirements.txt

# Verify setup
python -c "from blockchain.blockchain import Blockchain; print('✅ Ready for deployment')"
cd ..
```

#### Step 2: Configure Network Settings
Edit `start_distributed_node.sh` on each computer:

```bash
# Set your subnet prefix (modify these lines in the script)
SUBNET_PREFIX="192.168.1"  # Change to your actual subnet
TOTAL_COMPUTERS=6
```

#### Step 3: Deploy on Each Computer

**Computer 1 (192.168.1.1)** - Bootstrap Node:
```bash
./start_distributed_node.sh 1
```

**Computer 2 (192.168.1.2):**
```bash
./start_distributed_node.sh 2
```

**Computer 3 (192.168.1.3):**
```bash
./start_distributed_node.sh 3
```

**Computer 4 (192.168.1.4):**
```bash
./start_distributed_node.sh 4
```

**Computer 5 (192.168.1.5):**
```bash
./start_distributed_node.sh 5
```

**Computer 6 (192.168.1.6):**
```bash
./start_distributed_node.sh 6
```

### Multi-Computer Node Configuration
| Computer | IP | API Port | P2P Port | Role |
|----------|-------|----------|----------|------|
| 1 | 192.168.1.1 | 8050 | 10000 | Bootstrap |
| 2 | 192.168.1.2 | 8051 | 10001 | Validator |
| 3 | 192.168.1.3 | 8052 | 10002 | Validator |
| 4 | 192.168.1.4 | 8053 | 10003 | Validator |
| 5 | 192.168.1.5 | 8054 | 10004 | Validator |
| 6 | 192.168.1.6 | 8055 | 10005 | Validator |

## Network Validation

### Check Network Health
```bash
# Check individual node status
curl http://192.168.1.1:8050/api/v1/blockchain/network-status/

# Check blockchain synchronization
for i in {1..6}; do
  echo "Computer $i blockchain height:"
  curl -s http://192.168.1.$i:805$((49+$i))/api/v1/blockchain/ | jq '.blocks | length'
done
```

### Submit Test Transaction
```bash
# Submit transaction to any node
curl -X POST http://192.168.1.1:8050/api/v1/blockchain/transaction/ \
     -H "Content-Type: application/json" \
     -d '{"sender": "alice", "receiver": "bob", "amount": 100}'

# Verify transaction propagation across all nodes
for i in {1..6}; do
  echo "Node $i transaction pool:"
  curl -s http://192.168.1.$i:805$((49+$i))/api/v1/blockchain/transaction-pool/
done
```

### Monitor Performance
```bash
# Get performance metrics from any node
curl http://192.168.1.1:8050/api/v1/blockchain/performance-metrics/ | jq '.'

# Check consensus participation
curl http://192.168.1.1:8050/api/v1/blockchain/quantum-metrics/ | jq '.consensus_status'
```

## Decentralized Network Features

### 1. Quantum Consensus
- **Leader Selection**: Uses quantum annealing for fair leader rotation
- **Byzantine Fault Tolerance**: Tolerates up to 2 failed nodes (33% failure rate)
- **Stake-Based Voting**: Weighted consensus based on node participation

### 2. Peer-to-Peer Communication
- **Enhanced P2P Protocol**: Bitcoin-style INV/GETDATA messaging
- **Automatic Peer Discovery**: Nodes automatically find and connect to peers
- **Mesh Network Topology**: Each node connects to multiple peers for redundancy

### 3. Transaction Processing
- **Gulf Stream Forwarding**: Transactions forwarded to upcoming leaders
- **TPU Integration**: Direct transaction submission to leaders
- **Parallel Execution**: Sealevel-style parallel transaction processing

### 4. Block Propagation
- **Turbine Protocol**: Efficient block distribution via sharding
- **Gossip Network**: Leader schedule and metadata distribution
- **Proof of History**: Cryptographic transaction ordering

## Network Monitoring

### Real-Time Monitoring Dashboard
Access from any node:
```bash
# Network overview
curl http://192.168.1.1:8050/api/v1/blockchain/network-status/

# Performance metrics
curl http://192.168.1.1:8050/api/v1/blockchain/performance-metrics/

# Consensus status
curl http://192.168.1.1:8050/api/v1/blockchain/quantum-metrics/
```

### Key Metrics to Monitor
- **Block Height**: Should be consistent across all nodes
- **Peer Connections**: Each node should have 3-5 active connections
- **Transaction Throughput**: Monitor TPS across the network
- **Consensus Participation**: All nodes should participate in leader selection
- **Network Latency**: Block propagation time between nodes

## Troubleshooting

### Common Issues

#### 1. Nodes Can't Connect
```bash
# Check port availability
netstat -tuln | grep -E "(8050|10000|12000|13000|14000)"

# Check firewall
sudo ufw status
sudo iptables -L

# Test network connectivity
telnet 192.168.1.2 10001
```

#### 2. Genesis Block Mismatch
```bash
# Verify genesis configuration on all nodes
curl http://192.168.1.1:8050/api/v1/blockchain/ | jq '.blocks[0]'
curl http://192.168.1.2:8051/api/v1/blockchain/ | jq '.blocks[0]'

# If different, restart all nodes to resync
```

#### 3. Performance Issues
```bash
# Check system resources
top -p $(pgrep -f run_node.py)

# Monitor blockchain performance
curl http://192.168.1.1:8050/api/v1/blockchain/performance-metrics/ | jq '.metrics.transaction_throughput'
```

### Network Recovery
If the network becomes unstable:

1. **Stop all nodes**: Run `./stop_network.sh` on each computer
2. **Clear old data**: Remove any cached data if needed
3. **Restart in sequence**: Start Computer 1 first, then others
4. **Verify synchronization**: Check that all nodes reach consensus

## Advanced Configuration

### Custom Subnet Setup
For non-standard network configurations:

```bash
# Edit start_distributed_node.sh
SUBNET_PREFIX="10.0.0"     # For 10.0.0.x network
SUBNET_PREFIX="172.16.1"   # For 172.16.1.x network
```

### Performance Tuning
```bash
# Increase parallel processing
export SEALEVEL_MAX_WORKERS=16

# Adjust block timing
export SLOT_DURATION_SECONDS=0.4

# Modify transaction batch size
export TRANSACTION_BATCH_SIZE=200
```

### Security Hardening
```bash
# Generate unique keys for each node
cd blockchain/keys
python -c "
from blockchain.transaction.wallet import Wallet
for i in range(1, 7):
    w = Wallet()
    w.save_to_file(f'computer_{i}_private_key.pem')
    print(f'Generated key for computer {i}')
"
```

## Production Deployment Checklist

- [ ] All 6 computers have static IP addresses
- [ ] Firewall rules allow blockchain ports (8050-8055, 10000-10005, etc.)
- [ ] Network latency between computers is < 100ms
- [ ] Each computer has sufficient resources (4GB+ RAM, 2+ CPU cores)
- [ ] Genesis configuration is identical on all nodes
- [ ] Node keys are securely generated and stored
- [ ] Monitoring and alerting is configured
- [ ] Backup and recovery procedures are documented
- [ ] Network restart procedures are tested

## API Reference

### Blockchain Operations
```bash
# Get blockchain state
GET /api/v1/blockchain/

# Submit transaction
POST /api/v1/blockchain/transaction/
{
  "sender": "alice_public_key",
  "receiver": "bob_public_key", 
  "amount": 100
}

# Get network status
GET /api/v1/blockchain/network-status/
```

### Network Management
```bash
# Connect to peer
POST /api/v1/blockchain/connect-peer/
{
  "ip": "192.168.1.2",
  "port": 10001
}

# Get peer information
GET /api/v1/blockchain/peers/

# Get performance metrics
GET /api/v1/blockchain/performance-metrics/
```

## Conclusion

This setup provides a robust, decentralized blockchain network that can scale from single-computer testing to multi-computer production deployments. The network features quantum consensus, efficient P2P communication, and comprehensive monitoring capabilities.

For questions or issues, refer to the troubleshooting section or check the logs generated by each node.
