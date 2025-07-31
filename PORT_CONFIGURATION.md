# Port Configuration Update Summary

## Updated Port Ranges

The blockchain network has been updated to use the following port ranges:

### Port Allocation by Service

| Service | Port Range | Description |
|---------|------------|-------------|
| **API** | 11000-11999 | REST API endpoints for blockchain interaction |
| **P2P** | 10000-10999 | Peer-to-peer communication between nodes |
| **Gossip** | 12000-12999 | Gossip protocol for leader schedule distribution |
| **TPU** | 13000-13999 | Transaction Processing Unit (leader transaction reception) |
| **TVU** | 14000-14999 | Transaction Validation Unit |
| **Gulf Stream** | 15000-15999 | UDP transaction forwarding |

### Node-Specific Port Assignments

#### Single Computer Network (6 Nodes)
| Node | API Port | P2P Port | Gossip | TPU | TVU |
|------|----------|----------|--------|-----|-----|
| 1    | 11000    | 10000    | 12000  | 13000 | 14000 |
| 2    | 11001    | 10001    | 12001  | 13001 | 14001 |
| 3    | 11002    | 10002    | 12002  | 13002 | 14002 |
| 4    | 11003    | 10003    | 12003  | 13003 | 14003 |
| 5    | 11004    | 10004    | 12004  | 13004 | 14004 |
| 6    | 11005    | 10005    | 12005  | 13005 | 14005 |

#### Multi-Computer Network (6 Computers)
| Computer | IP | API Port | P2P Port | Gossip | TPU | TVU |
|----------|-------|----------|----------|--------|-----|-----|
| 1 | 10.283.0.1 | 11000 | 10000 | 12000 | 13000 | 14000 |
| 2 | 10.283.0.2 | 11001 | 10001 | 12001 | 13001 | 14001 |
| 3 | 10.283.0.3 | 11002 | 10002 | 12002 | 13002 | 14002 |
| 4 | 10.283.0.4 | 11003 | 10003 | 12003 | 13003 | 14003 |
| 5 | 10.283.0.5 | 11004 | 10004 | 12004 | 13004 | 14004 |
| 6 | 10.283.0.6 | 11005 | 10005 | 12005 | 13005 | 14005 |

## Updated Endpoints

### Single Computer Network
- **Primary API**: http://127.0.0.1:11000/api/v1/blockchain/
- **Blockchain Explorer**: http://127.0.0.1:11000/api/v1/blockchain/
- **Performance Metrics**: http://127.0.0.1:11000/api/v1/blockchain/performance-metrics/
- **Network Status**: http://127.0.0.1:11000/api/v1/blockchain/network-status/
- **Transaction Submission**: http://127.0.0.1:11000/api/v1/blockchain/transaction/

### Multi-Computer Network
- **Primary API**: http://10.283.0.1:11000/api/v1/blockchain/
- **Node 2 API**: http://10.283.0.2:11001/api/v1/blockchain/
- **Node 3 API**: http://10.283.0.3:11002/api/v1/blockchain/
- **Node 4 API**: http://10.283.0.4:11003/api/v1/blockchain/
- **Node 5 API**: http://10.283.0.5:11004/api/v1/blockchain/
- **Node 6 API**: http://10.283.0.6:11005/api/v1/blockchain/

## Updated Test Commands

### Submit Transaction
```bash
# Single Computer
curl -X POST http://127.0.0.1:11000/api/v1/blockchain/transaction/ \
     -H "Content-Type: application/json" \
     -d '{"sender": "alice", "receiver": "bob", "amount": 100}'

# Multi-Computer
curl -X POST http://10.283.0.1:11000/api/v1/blockchain/transaction/ \
     -H "Content-Type: application/json" \
     -d '{"sender": "alice", "receiver": "bob", "amount": 100}'
```

### View Blockchain
```bash
# Single Computer
curl http://127.0.0.1:11000/api/v1/blockchain/

# Multi-Computer
curl http://10.283.0.1:11000/api/v1/blockchain/
```

### Check Network Status
```bash
# Single Computer
curl http://127.0.0.1:11000/api/v1/blockchain/network-status/

# Multi-Computer
curl http://10.283.0.1:11000/api/v1/blockchain/network-status/
```

## Files Updated

The following files have been updated to use the new port ranges:

1. **start_distributed_node.sh** - Multi-computer deployment script
2. **start_single_computer_network.sh** - Single computer deployment script
3. **network_health_checker.py** - Network monitoring tool
4. **stop_network.sh** - Network shutdown script
5. **validate_setup.py** - Setup validation script
6. **enhanced_node_manager.py** - Network discovery module

## Firewall Configuration

If using a firewall, ensure these ports are open:

### For Single Computer (localhost only)
No firewall changes needed for localhost communication.

### For Multi-Computer Network
```bash
# Ubuntu/Debian
sudo ufw allow 11000:11005/tcp  # API ports
sudo ufw allow 10000:10005/tcp  # P2P ports
sudo ufw allow 12000:12005/tcp  # Gossip ports
sudo ufw allow 13000:13005/tcp  # TPU ports
sudo ufw allow 14000:14005/tcp  # TVU ports
sudo ufw allow 15000:15005/udp  # Gulf Stream UDP

# CentOS/RHEL
firewall-cmd --permanent --add-port=11000-11005/tcp  # API
firewall-cmd --permanent --add-port=10000-10005/tcp  # P2P
firewall-cmd --permanent --add-port=12000-12005/tcp  # Gossip
firewall-cmd --permanent --add-port=13000-13005/tcp  # TPU
firewall-cmd --permanent --add-port=14000-14005/tcp  # TVU
firewall-cmd --permanent --add-port=15000-15005/udp  # Gulf Stream
firewall-cmd --reload
```

## Validation Commands

### Check Port Availability
```bash
# Validate setup before starting
python validate_setup.py

# Check specific port
netstat -tuln | grep 11000
```

### Monitor Network Health
```bash
# Single computer network
python network_health_checker.py --mode single --detailed

# Multi-computer network
python network_health_checker.py --mode distributed --subnet 10.283.0 --detailed
```

## Migration Notes

If you have an existing deployment using the old port ranges (8050+), you'll need to:

1. **Stop the old network**: `./stop_network.sh`
2. **Clear any port conflicts**: Check for processes using old ports
3. **Start with new configuration**: Use updated scripts
4. **Update any external integrations**: Change API endpoints to use 11000+ ports

The new port allocation provides better organization and avoids conflicts with common web development ports (8000-8999 range).
