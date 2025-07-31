# Decentralized Blockchain Network Deployment

## Quick Start Guide

This repository provides a complete solution for deploying a decentralized blockchain network with quantum consensus, either on a single computer or distributed across multiple computers in the same subnet.

## 🚀 Deployment Options

### Option 1: Single Computer (6 Nodes)
Perfect for development, testing, and demonstrations:

```bash
# 1. Validate your setup
python validate_setup.py

# 2. Start the network
./start_single_computer_network.sh

# 3. Check network health
python network_health_checker.py --mode single --detailed

# 4. Stop the network
./stop_network.sh
```

### Option 2: Multi-Computer (6 Computers)
For production deployments across a subnet network:

```bash
# On each computer (Computer 1-6):

# 1. Validate setup
python validate_setup.py

# 2. Start the node (replace X with computer number 1-6)
./start_distributed_node.sh X

# 3. Check network health from any computer
python network_health_checker.py --mode distributed --subnet 192.168.1 --detailed
```

## 🔧 Network Configuration

### Single Computer Network
- **6 nodes** on 127.0.0.1
- **API ports**: 8050-8055
- **P2P ports**: 10000-10005
- **Automatic peer discovery**
- **Shared genesis block**

### Multi-Computer Network
- **6 computers** in subnet (e.g., 192.168.1.1 - 192.168.1.6)
- **1 node per computer**
- **Automatic subnet discovery**
- **Cross-computer consensus**

## 🌐 Network Features

### ✅ Decentralized Architecture
- **Quantum Consensus**: Fair leader selection using quantum annealing
- **Byzantine Fault Tolerance**: Tolerates up to 2 node failures (33%)
- **P2P Mesh Network**: Every node connects to multiple peers
- **No Single Point of Failure**: Network continues with majority nodes

### ✅ Advanced Blockchain Features
- **Proof of History (PoH)**: Cryptographic transaction ordering
- **Gulf Stream**: Transaction forwarding to upcoming leaders
- **Turbine Protocol**: Efficient block propagation via sharding
- **Parallel Execution**: Sealevel-style parallel transaction processing
- **Gossip Protocol**: Efficient metadata distribution

### ✅ Performance & Monitoring
- **Real-time Metrics**: Comprehensive performance monitoring
- **Network Health Checks**: Automated network validation
- **Auto-Recovery**: Nodes automatically reconnect and sync
- **Load Balancing**: Transactions distributed across healthy nodes

## 📊 Testing the Network

### Submit a Test Transaction
```bash
curl -X POST http://127.0.0.1:8050/api/v1/blockchain/transaction/ \
     -H "Content-Type: application/json" \
     -d '{"sender": "alice", "receiver": "bob", "amount": 100}'
```

### View Blockchain State
```bash
curl http://127.0.0.1:8050/api/v1/blockchain/ | jq '.'
```

### Check Network Status
```bash
curl http://127.0.0.1:8050/api/v1/blockchain/network-status/ | jq '.'
```

### Monitor Performance
```bash
curl http://127.0.0.1:8050/api/v1/blockchain/performance-metrics/ | jq '.'
```

## 🔍 Health Monitoring

### Continuous Monitoring
```bash
# Monitor single computer network
python network_health_checker.py --mode single --monitor --interval 30

# Monitor distributed network
python network_health_checker.py --mode distributed --subnet 192.168.1 --monitor
```

### One-time Health Check
```bash
# Detailed health report
python network_health_checker.py --mode single --detailed

# Quick status summary
python network_health_checker.py --mode single
```

## 🌍 Multi-Computer Setup Details

### Prerequisites
- **6 computers** in the same subnet
- **Network connectivity** between all computers
- **Open firewall ports**: 8050-8055, 10000-10005, 12000-12005, 13000-13005, 14000-14005
- **Static IP addresses** (recommended)

### Subnet Configuration Examples

**Home Network (192.168.1.x):**
```bash
# Computer 1: 192.168.1.1
./start_distributed_node.sh 1

# Computer 2: 192.168.1.2  
./start_distributed_node.sh 2

# ... and so on for computers 3-6
```

**Office Network (10.0.0.x):**
```bash
# Edit start_distributed_node.sh:
SUBNET_PREFIX="10.0.0"

# Then run on each computer:
./start_distributed_node.sh 1  # on 10.0.0.1
./start_distributed_node.sh 2  # on 10.0.0.2
# ... etc
```

## 🔧 Troubleshooting

### Common Issues

**Port conflicts:**
```bash
# Stop any existing blockchain processes
./stop_network.sh

# Check for processes using our ports
netstat -tuln | grep -E "(8050|10000)"

# Kill specific processes if needed
sudo lsof -ti:8050 | xargs kill -9
```

**Nodes can't connect:**
```bash
# Check firewall
sudo ufw status
sudo iptables -L

# Test network connectivity
telnet 192.168.1.2 10001

# Verify node is listening
netstat -tuln | grep 10001
```

**Genesis block mismatch:**
```bash
# Check genesis hash on all nodes
curl http://192.168.1.1:8050/api/v1/blockchain/ | jq '.blocks[0].hash'
curl http://192.168.1.2:8051/api/v1/blockchain/ | jq '.blocks[0].hash'

# If different, restart all nodes to resync
```

### Network Recovery
If the network becomes unstable:

1. **Stop all nodes**: `./stop_network.sh` on each computer
2. **Wait 30 seconds** for cleanup
3. **Restart Computer 1 first** (bootstrap node)
4. **Wait for initialization** (30 seconds)
5. **Start other computers** in sequence
6. **Verify synchronization** with health checker

## 📁 File Structure

```
proofwithquantumannealing/
├── start_single_computer_network.sh    # Single computer deployment
├── start_distributed_node.sh           # Multi-computer deployment  
├── stop_network.sh                     # Stop all nodes
├── network_health_checker.py           # Network monitoring
├── validate_setup.py                   # Setup validation
├── DEPLOYMENT_GUIDE.md                 # Detailed documentation
├── blockchain/                         # Core blockchain code
│   ├── run_node.py                     # Node startup script
│   ├── enhanced_node_manager.py        # Network discovery
│   └── blockchain/                     # Blockchain modules
└── genesis_config/                     # Genesis configuration
```

## 🎯 Next Steps

1. **Validate Setup**: Run `python validate_setup.py`
2. **Choose Deployment**: Single computer or multi-computer
3. **Start Network**: Use appropriate startup script
4. **Monitor Health**: Use network health checker
5. **Test Functionality**: Submit transactions and verify propagation
6. **Scale as Needed**: Add more computers to the network

## 📚 Additional Documentation

- **[Detailed Deployment Guide](DEPLOYMENT_GUIDE.md)**: Comprehensive setup instructions
- **[API Documentation](blockchain/api/)**: REST API reference
- **[Network Architecture](docs/)**: Technical architecture details

## 🔐 Security Considerations

- **Private Keys**: Each node generates unique private keys
- **Network Security**: Use VPN for distributed deployments over internet
- **Firewall Rules**: Only open required ports
- **Access Control**: Restrict API access to trusted networks
- **Monitoring**: Set up alerts for network health issues

## ✅ Success Indicators

Your decentralized blockchain network is working correctly when:

- ✅ All nodes show "healthy" status in health checker
- ✅ Blockchain height is consistent across all nodes
- ✅ Transactions propagate to all nodes within 10 seconds
- ✅ New blocks are created and distributed automatically
- ✅ Network survives individual node failures
- ✅ Consensus mechanisms select leaders fairly

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Run the network health checker for diagnostics
3. Review node logs for specific error messages
4. Ensure network connectivity and port availability

---

**🌐 Congratulations!** You now have a fully decentralized blockchain network with quantum consensus, ready for development, testing, or production use.
