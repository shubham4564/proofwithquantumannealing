# Complete Quantum Annealing Blockchain Operations Guide

This comprehensive guide covers everything you need to operate, monitor, and analyze your quantum annealing blockchain implementation.

## Table of Contents

1. [Quick Start Guide](#quick-start-guide)
2. [System Architecture](#system-architecture)
3. [Node Operations](#node-operations)
4. [Performance Monitoring](#performance-monitoring)
5. [Quantum Consensus Metrics](#quantum-consensus-metrics)
6. [Testing Framework](#testing-framework)
7. [API Reference](#api-reference)
8. [Troubleshooting](#troubleshooting)
9. [Production Deployment](#production-deployment)
10. [Advanced Operations](#advanced-operations)

---

## Quick Start Guide

### Prerequisites
- Python 3.13+ with virtual environment
- All dependencies installed via `requirements/dev.txt`

### Start Your First Node
```bash
# Activate virtual environment
source /Users/shubham/Documents/proofwithquantumannealing/.venv/bin/activate

# Navigate to blockchain directory
cd /Users/shubham/Documents/proofwithquantumannealing/blockchain

# Start a single node
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python run_node.py

# Or specify custom ports
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python run_node.py --ip localhost --node_port 8000 --api_port 8050
```

### Quick Performance Check
```bash
# Run basic performance measurement
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python quick_metrics_demo.py
```

---

## System Architecture

### Core Components

#### 1. Quantum Annealing Consensus (`quantum_annealing_pos.py`)
- **Purpose**: IEEE paper-based consensus mechanism
- **Key Features**: 
  - QUBO optimization for node selection
  - Probe protocol for performance measurement
  - Suitability scoring with multiple metrics
- **Location**: `blockchain/pos/quantum_annealing_pos.py`

#### 2. Blockchain Core (`blockchain.py`)
- **Purpose**: Main blockchain logic
- **Integration**: Uses quantum consensus for forger selection
- **Location**: `blockchain/blockchain.py`

#### 3. Node Runner (`run_node.py`)
- **Purpose**: Individual blockchain node process
- **Features**: P2P networking, API server, consensus participation
- **Location**: `run_node.py`

#### 4. API Layer (`api/`)
- **Purpose**: REST API for blockchain interaction
- **Endpoints**: Transaction submission, blockchain state, quantum metrics
- **Location**: `api/main.py`

### Network Architecture
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Node 1    │    │   Node 2    │    │   Node 3    │
│ Port: 8000  │◄──►│ Port: 8001  │◄──►│ Port: 8002  │
│ API:  8050  │    │ API:  8051  │    │ API:  8052  │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                          │
              ┌─────────────────────┐
              │ Quantum Consensus   │
              │ - Probe Protocol    │
              │ - QUBO Optimization │
              │ - Node Selection    │
              └─────────────────────┘
```

---

## Node Operations

### Single Node Setup
```bash
# Start with default settings
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python run_node.py

# Start with custom configuration
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python run_node.py \
  --ip localhost \
  --node_port 8000 \
  --api_port 8050
```

### Multi-Node Network Setup
```bash
# Automated startup (recommended)
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python start_nodes.py --nodes 3

# Manual startup
# Terminal 1:
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python run_node.py --node_port 8000 --api_port 8050

# Terminal 2:
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python run_node.py --node_port 8001 --api_port 8051

# Terminal 3:
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python run_node.py --node_port 8002 --api_port 8052
```

### Node Management Commands

#### Check Node Status
```bash
# 🔍 NEW: Comprehensive Node Health Checker (RECOMMENDED)
cd tools/monitoring
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python check_node_health.py

# Detailed health check with full diagnostics
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python check_node_health.py --detailed

# Quick API check (single node)
curl http://localhost:11000/api/v1/blockchain/

# Check quantum consensus health
curl http://localhost:11000/api/v1/blockchain/quantum-metrics/

# Check if processes are running
ps aux | grep "run_node.py" | grep -v grep

# Check which ports are in use
lsof -i :8050
netstat -an | grep ":80[5-6][0-9]"
```

#### Stop Nodes
```bash
# Stop automated nodes
pkill -f "run_node.py"

# Or use Ctrl+C in each terminal
```

#### Node Configuration
```bash
# View node configuration
cat setup.cfg

# Environment variables (optional)
export BLOCKCHAIN_NODE_PORT=8000
export BLOCKCHAIN_API_PORT=8050
```

---

## Performance Monitoring

### Available Monitoring Tools

#### 1. Quick Metrics Demo (`quick_metrics_demo.py`)
**Best for**: Daily health checks and basic performance overview

```bash
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python quick_metrics_demo.py
```

**Metrics Provided**:
- Transaction creation time (microseconds)
- Network submission time
- Total transaction processing time
- Consensus timing estimation
- Transaction throughput (TPS)
- Success rates

**Expected Output**:
```
🎯 QUANTUM ANNEALING BLOCKCHAIN PERFORMANCE METRICS DEMO
✅ Node available on port 8050
⏱️ MEASURING SINGLE TRANSACTION TIMING
   Transaction creation: 0.007900s
   Network submission: 0.008s
   Total transaction time: 0.016s
🔬 MEASURING CONSENSUS TIMING (30s)
   Average probe count: 90.0
🚀 MEASURING TRANSACTION THROUGHPUT
   Throughput: 211.27 TPS
   Success rate: 100.00%
```

#### 2. Simple Performance Analyzer (`simple_performance.py`)
**Best for**: Comprehensive benchmarking and detailed analysis

```bash
# Quick throughput test
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python simple_performance.py --throughput-test --transactions 30

# Full benchmark
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python simple_performance.py --benchmark --transactions 50 --duration 60

# Measure consensus only
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python simple_performance.py --measure-consensus --duration 60

# Measure block production
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python simple_performance.py --measure-blocks --duration 60

# Sequential testing (non-concurrent)
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python simple_performance.py --throughput-test --transactions 20 --sequential
```

#### 3. Multi-Node Test Suite (`multi_node_test.py`)
**Best for**: Network-wide performance and quantum consensus analysis

```bash
# Standard multi-node test
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python multi_node_test.py --nodes 3 --transactions 50 --duration 300

# Quick test
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python multi_node_test.py --nodes 3 --transactions 20 --duration 60 --wait-time 10

# High-load test
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python multi_node_test.py --nodes 4 --transactions 100 --duration 600
```

#### 4. Advanced Performance Analyzer (`performance_analyzer.py`)
**Best for**: Enterprise-grade monitoring with CSV export

```bash
# Run comprehensive benchmark
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python performance_analyzer.py --benchmark --transactions 100

# Real-time monitoring
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python performance_analyzer.py --real-time --interval 10 --duration 300

# Save metrics to CSV files
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python performance_analyzer.py --benchmark --save-csv
```

### Key Performance Metrics Explained

#### Transaction Performance Metrics

##### 1. Transaction Time
- **Creation Time**: Time to create and cryptographically sign transaction
  - Typical: 0.001-0.01 seconds
  - Good: < 0.01s
  - Concerning: > 0.1s

- **Submission Time**: Network transmission and initial validation
  - Typical: 0.01-0.1 seconds
  - Good: < 0.05s
  - Concerning: > 0.5s

- **Total Transaction Time**: Complete processing time
  - Typical: 0.02-0.5 seconds
  - Good: < 0.2s
  - Concerning: > 1.0s

##### 2. Transaction Throughput (TPS)
- **Definition**: Successful transactions processed per second
- **Calculation**: `Successful Transactions / Total Time`
- **Benchmarks**:
  - Single node: 10-50 TPS
  - 3 nodes: 20-100 TPS
  - 5+ nodes: 50-200+ TPS

##### 3. Success Rate
- **Definition**: Percentage of transactions successfully processed
- **Targets**:
  - Excellent: > 99%
  - Good: 95-99%
  - Needs attention: < 95%

#### Network Performance Metrics

##### 1. Response Time Distribution
```bash
# Example output interpretation
Average Response Time: 0.018s    # Mean processing time
Median Response Time: 0.014s     # 50th percentile (typical user experience)
Min Response Time: 0.006s        # Best case performance
Max Response Time: 0.034s        # Worst case (check for outliers)
```

##### 2. Node Synchronization
```bash
# Example from multi-node test
Node Synchronization:
node_0: 34 blocks
node_1: 34 blocks  
node_2: 33 blocks
Synchronization Difference: 1 blocks
✅ Excellent synchronization
```

**Interpretation**:
- 0-1 block difference: Excellent
- 2-3 block difference: Good
- 4+ block difference: Needs investigation

---

## Quantum Consensus Metrics

### Understanding Quantum Annealing Consensus

The quantum annealing consensus mechanism implements the IEEE paper specification with these key components:

#### 1. Probe Protocol Metrics
**Purpose**: Measure node performance for consensus decisions

```bash
# View current probe metrics
curl http://localhost:11000/api/v1/blockchain/quantum-metrics/
```

**Key Metrics**:
- **Probe Count**: Number of network probes executed
  - Typical: 50-200 probes
  - High activity: > 200 probes
  - Low activity: < 50 probes

- **Active Nodes**: Nodes currently participating in consensus
- **Node Response Times**: Latency measurements from probes

#### 2. Node Suitability Scoring
**Components** (as per IEEE paper):

##### Uptime Score (25% weight)
- Based on node availability over time
- Range: 0.0 (never available) to 1.0 (always available)

##### Latency Score (25% weight, negative)
- Lower latency = higher score
- Based on probe protocol measurements
- Typical range: 0.01-1.0 seconds

##### Throughput Score (25% weight)
- Transactions processed per unit time
- Based on historical performance

##### Past Performance Score (25% weight)
- Success/failure ratio of previous block proposals
- Includes penalty for failed proposals

#### 3. QUBO Optimization Metrics
**Quantum Annealing Process**:

```bash
# Example quantum metrics output
{
  "total_nodes": 5,
  "active_nodes": 4,
  "probe_count": 146,
  "node_scores": {
    "node_1": {
      "suitability_score": 0.7234,
      "effective_score": 0.7241,
      "uptime": 1.0,
      "latency": 0.089,
      "throughput": 23.4,
      "proposals_success": 5,
      "proposals_failed": 1
    }
  }
}
```

### Monitoring Quantum Consensus Health

#### 1. Real-time Consensus Monitoring
```bash
# Continuous monitoring script
while true; do
  echo "=== $(date) ==="
  curl -s http://localhost:11000/api/v1/blockchain/quantum-metrics/ | python -m json.tool
  echo
  sleep 10
done
```

#### 2. Consensus Performance Analysis
```bash
# Run consensus-specific analysis
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python simple_performance.py --measure-consensus --duration 120
```

**Expected Output**:
```
🔬 CONSENSUS METRICS
Measurement Duration: 120s
Samples Collected: 24
Avg Probe Count: 138.0
Avg Active Nodes: 3.8
Consensus Stability: ✅ Stable
```

#### 3. Node Score Analysis
```bash
# Analyze individual node performance
curl -s http://localhost:11000/api/v1/blockchain/quantum-metrics/ | \
  python -c "
import json, sys
data = json.load(sys.stdin)
for node_id, scores in data['node_scores'].items():
    print(f'{node_id[:20]}...: Suitability={scores['suitability_score']:.4f}, Uptime={scores['uptime']:.2f}')
"
```

---

## Testing Framework

### Unit Tests
```bash
# Run all tests
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python -m pytest tests/ -v

# Run specific test categories
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python -m pytest tests/unit/test_quantum_annealing.py -v
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python -m pytest tests/unit/test_blockchain.py -v

# Run with coverage
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python -m pytest tests/ --cov=blockchain --cov-report=html
```

### Integration Tests
```bash
# Sample transaction testing
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python sample_transactions.py

# Multi-node integration testing
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python multi_node_test.py --nodes 3 --transactions 20
```

### Load Testing Scenarios

#### Scenario 1: Single Node Stress Test
```bash
# Start single node
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python run_node.py &

# Wait for startup
sleep 10

# Run stress test
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python simple_performance.py --throughput-test --transactions 100
```

#### Scenario 2: Multi-Node Load Test
```bash
# Start 4 nodes
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python start_nodes.py --nodes 4 &

# Wait for network formation
sleep 30

# Run distributed load test
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python multi_node_test.py --nodes 4 --transactions 200 --duration 600
```

#### Scenario 3: Continuous Load Testing
```bash
# Create continuous load script
cat > continuous_load.sh << 'EOF'
#!/bin/bash
for i in {1..10}; do
  echo "=== Load Test Round $i ==="
  /Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python simple_performance.py --throughput-test --transactions 50
  sleep 60
done
EOF

chmod +x continuous_load.sh
./continuous_load.sh
```

---

## API Reference

### Blockchain State Endpoints

#### Get Blockchain State
```bash
GET http://localhost:11000/api/v1/blockchain/

# Example response:
{
  "blocks": [
    {
      "transactions": [...],
      "last_hash": "...",
      "forger": "...",
      "block_count": 5,
      "timestamp": 1674123456.789
    }
  ]
}
```

#### Get Quantum Consensus Metrics
```bash
GET http://localhost:11000/api/v1/blockchain/quantum-metrics/

# Example response:
{
  "total_nodes": 4,
  "active_nodes": 3,
  "probe_count": 125,
  "node_scores": {
    "node_id_1": {
      "suitability_score": 0.7234,
      "effective_score": 0.7241,
      "uptime": 1.0,
      "latency": 0.089,
      "throughput": 23.4
    }
  }
}
```

### Transaction Endpoints

#### Submit Transaction
```bash
POST http://localhost:11000/api/v1/transaction/create/
Content-Type: application/json

{
  "transaction": "base64_encoded_transaction"
}
```

#### Example using curl:
```bash
# Create and submit a transaction (simplified)
curl -X POST http://localhost:11000/api/v1/transaction/create/ \
  -H "Content-Type: application/json" \
  -d '{"transaction": "encoded_transaction_data"}'
```

### Network Status Endpoints

#### Get Node Information
```bash
GET http://localhost:11000/api/v1/node/info/

# Returns node configuration and status
```

#### Get Network Peers
```bash
GET http://localhost:11000/api/v1/node/peers/

# Returns connected peer information
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Node Won't Start
```bash
# Check if port is already in use
lsof -i :8050

# Kill existing processes
pkill -f "run_node.py"

# Check Python environment
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python --version

# Verify dependencies
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python -c "import requests; print('OK')"
```

#### 2. Low Transaction Throughput
```bash
# Check system resources
top -p $(pgrep -f run_node.py)

# Monitor network latency
ping localhost

# Check consensus health
curl http://localhost:11000/api/v1/blockchain/quantum-metrics/

# Analyze performance
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python quick_metrics_demo.py
```

#### 3. Node Synchronization Issues
```bash
# Check all node states
for port in 8050 8051 8052; do
  echo "=== Node on port $port ==="
  curl -s http://localhost:$port/api/v1/blockchain/ | \
    python -c "import json,sys; data=json.load(sys.stdin); print(f'Blocks: {len(data[\"blocks\"])}')"
done

# Restart nodes if needed
pkill -f "run_node.py"
sleep 5
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python start_nodes.py --nodes 3
```

#### 4. High Response Times
```bash
# Profile transaction processing
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python quick_metrics_demo.py

# Check quantum consensus metrics
curl -s http://localhost:11000/api/v1/blockchain/quantum-metrics/ | \
  python -c "import json,sys; data=json.load(sys.stdin); print(f'Probe count: {data[\"probe_count\"]}, Active: {data[\"active_nodes\"]}')"

# Monitor system resources
iostat 1 5
```

#### 5. Failed Transactions
```bash
# Check node logs (if logging enabled)
tail -f blockchain.log

# Verify wallet funding
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python sample_transactions.py

# Test basic connectivity
curl -I http://localhost:11000/api/v1/blockchain/
```

### Diagnostic Commands

#### System Health Check
```bash
# Create comprehensive health check script
cat > health_check.sh << 'EOF'
#!/bin/bash
echo "=== Blockchain Health Check ==="
echo "Date: $(date)"
echo

echo "1. Node Availability:"
for port in 8050 8051 8052; do
  if curl -s http://localhost:$port/api/v1/blockchain/ > /dev/null; then
    echo "  ✅ Node on port $port: Available"
  else
    echo "  ❌ Node on port $port: Unavailable"
  fi
done
echo

echo "2. Performance Metrics:"
/Users/shubham/Documents/proofwithquantumannealing/.venv/bin/python quick_metrics_demo.py | grep -E "(TPS|Success rate|Average)"
echo

echo "3. Quantum Consensus Status:"
curl -s http://localhost:11000/api/v1/blockchain/quantum-metrics/ | \
  python -c "import json,sys; data=json.load(sys.stdin); print(f'  Active nodes: {data[\"active_nodes\"]}/{data[\"total_nodes\"]}'); print(f'  Probe count: {data[\"probe_count\"]}')"

echo
echo "Health check complete."
EOF

chmod +x health_check.sh
./health_check.sh
```

---

## Production Deployment

### Deployment Checklist

#### 1. Environment Setup
```bash
# Create production environment
python -m venv /opt/blockchain/venv
source /opt/blockchain/venv/bin/activate

# Install dependencies
pip install -r requirements/prod.txt

# Set up systemd service (Linux)
sudo cp deployment/blockchain-node.service /etc/systemd/system/
sudo systemctl enable blockchain-node
```

#### 2. Security Configuration
```bash
# Generate production keys
openssl genpkey -algorithm RSA -out /opt/blockchain/keys/node_private.pem -aes256
openssl rsa -pubout -in /opt/blockchain/keys/node_private.pem -out /opt/blockchain/keys/node_public.pem

# Set proper permissions
chmod 600 /opt/blockchain/keys/node_private.pem
chmod 644 /opt/blockchain/keys/node_public.pem
```

#### 3. Monitoring Setup
```bash
# Set up production monitoring
crontab -e

# Add these lines:
# Health check every 5 minutes
*/5 * * * * /opt/blockchain/scripts/health_check.sh >> /var/log/blockchain/health.log 2>&1

# Performance monitoring every hour
0 * * * * /opt/blockchain/scripts/performance_check.sh >> /var/log/blockchain/performance.log 2>&1

# Daily comprehensive report
0 6 * * * /opt/blockchain/scripts/daily_report.sh
```

#### 4. Network Configuration
```bash
# Configure firewall
sudo ufw allow 8000:8010/tcp  # Node ports
sudo ufw allow 8050:8060/tcp  # API ports

# Configure reverse proxy (nginx example)
sudo nano /etc/nginx/sites-available/blockchain-api

# Add SSL/TLS configuration
sudo certbot --nginx -d blockchain-api.yourdomain.com
```

### Production Monitoring Scripts

#### Daily Performance Report
```bash
cat > daily_report.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y-%m-%d)
REPORT_DIR="/var/log/blockchain/reports"
mkdir -p $REPORT_DIR

echo "Generating daily blockchain performance report for $DATE"

# Run comprehensive benchmark
/opt/blockchain/venv/bin/python /opt/blockchain/simple_performance.py \
  --benchmark --transactions 100 --duration 300 > "$REPORT_DIR/daily_$DATE.txt"

# Generate CSV metrics
/opt/blockchain/venv/bin/python /opt/blockchain/performance_analyzer.py \
  --benchmark --save-csv

# Send report via email (optional)
mail -s "Blockchain Daily Report $DATE" admin@company.com < "$REPORT_DIR/daily_$DATE.txt"
EOF
```

#### Real-time Alerting
```bash
cat > alert_monitor.sh << 'EOF'
#!/bin/bash
# Monitor critical metrics and send alerts

# Check transaction success rate
SUCCESS_RATE=$(/opt/blockchain/venv/bin/python quick_metrics_demo.py | grep "Success rate" | cut -d: -f2 | cut -d% -f1 | tr -d ' ')

if (( $(echo "$SUCCESS_RATE < 95" | bc -l) )); then
  echo "ALERT: Transaction success rate is $SUCCESS_RATE%" | \
    mail -s "Blockchain Alert: Low Success Rate" admin@company.com
fi

# Check node availability
AVAILABLE_NODES=$(curl -s http://localhost:11000/api/v1/blockchain/quantum-metrics/ | \
  python -c "import json,sys; data=json.load(sys.stdin); print(data['active_nodes'])")

if [ "$AVAILABLE_NODES" -lt 2 ]; then
  echo "ALERT: Only $AVAILABLE_NODES nodes available" | \
    mail -s "Blockchain Alert: Low Node Count" admin@company.com
fi
EOF
```

---

## Advanced Operations

### Performance Optimization

#### 1. Quantum Consensus Tuning
Edit `quantum_annealing_pos.py`:

```python
# Adjust probe protocol parameters
self.max_delay_tolerance = 15.0  # Reduce for faster consensus
self.witness_quorum_size = 2     # Reduce for smaller networks

# Adjust scoring weights for your network
self.weight_uptime = 0.3         # Increase uptime importance
self.weight_latency = 0.3        # Increase latency importance
self.weight_throughput = 0.2     # Adjust throughput weight
self.weight_past_performance = 0.2
```

#### 2. Network Optimization
```bash
# Tune TCP parameters for better performance
echo 'net.core.rmem_max = 16777216' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 16777216' >> /etc/sysctl.conf
sysctl -p
```

#### 3. Resource Monitoring
```bash
# Monitor resource usage
cat > resource_monitor.sh << 'EOF'
#!/bin/bash
while true; do
  echo "=== $(date) ==="
  echo "CPU Usage:"
  top -b -n1 | grep "run_node.py" | awk '{print $9"%"}'
  
  echo "Memory Usage:"
  ps aux | grep "run_node.py" | awk '{sum+=$6} END {print sum/1024 " MB"}'
  
  echo "Network Connections:"
  netstat -an | grep ":80[0-9][0-9]" | wc -l
  
  echo "Transaction Rate:"
  /opt/blockchain/venv/bin/python quick_metrics_demo.py | grep "TPS" | cut -d: -f2
  
  echo "----------------------------------------"
  sleep 30
done
EOF
```

### Custom Metrics Collection

#### 1. Prometheus Integration
```python
# Add to your monitoring setup
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
TRANSACTION_COUNTER = Counter('blockchain_transactions_total', 'Total transactions')
RESPONSE_TIME_HISTOGRAM = Histogram('blockchain_response_time_seconds', 'Response time')
ACTIVE_NODES_GAUGE = Gauge('blockchain_active_nodes', 'Number of active nodes')

# Start metrics server
start_http_server(8090)
```

#### 2. Custom Dashboard
```bash
# Create dashboard data endpoint
cat > dashboard_data.py << 'EOF'
#!/usr/bin/env python3
import json
import requests
from datetime import datetime

def collect_metrics():
    metrics = {}
    
    # Collect from all nodes
    for port in [8050, 8051, 8052]:
        try:
            response = requests.get(f'http://localhost:{port}/api/v1/blockchain/quantum-metrics/')
            if response.status_code == 200:
                metrics[f'node_{port}'] = response.json()
        except:
            metrics[f'node_{port}'] = {'status': 'offline'}
    
    # Add timestamp
    metrics['timestamp'] = datetime.now().isoformat()
    
    return metrics

if __name__ == "__main__":
    print(json.dumps(collect_metrics(), indent=2))
EOF
```

### Backup and Recovery

#### 1. Blockchain State Backup
```bash
# Create backup script
cat > backup_blockchain.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/blockchain"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR/$DATE"

# Backup blockchain data
curl -s http://localhost:11000/api/v1/blockchain/ > "$BACKUP_DIR/$DATE/blockchain_state.json"

# Backup node configurations
cp -r /opt/blockchain/keys "$BACKUP_DIR/$DATE/"
cp /opt/blockchain/config.ini "$BACKUP_DIR/$DATE/"

# Create archive
tar -czf "$BACKUP_DIR/blockchain_backup_$DATE.tar.gz" -C "$BACKUP_DIR" "$DATE"
rm -rf "$BACKUP_DIR/$DATE"

echo "Backup created: blockchain_backup_$DATE.tar.gz"
EOF
```

#### 2. Recovery Procedures
```bash
# Recovery script
cat > restore_blockchain.sh << 'EOF'
#!/bin/bash
BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup_file.tar.gz>"
  exit 1
fi

# Stop nodes
systemctl stop blockchain-node

# Extract backup
tar -xzf "$BACKUP_FILE" -C /tmp/

# Restore configuration
cp /tmp/*/config.ini /opt/blockchain/
cp -r /tmp/*/keys /opt/blockchain/

# Restart nodes
systemctl start blockchain-node

echo "Recovery complete"
EOF
```

---

## Appendix

### Environment Variables
```bash
# Optional environment configuration
export BLOCKCHAIN_NODE_PORT=8000
export BLOCKCHAIN_API_PORT=8050
export BLOCKCHAIN_LOG_LEVEL=INFO
export BLOCKCHAIN_DATA_DIR=/opt/blockchain/data
export BLOCKCHAIN_KEYS_DIR=/opt/blockchain/keys
```

### Log File Locations
```bash
# Standard log locations
/var/log/blockchain/node.log          # Node operation logs
/var/log/blockchain/performance.log   # Performance monitoring
/var/log/blockchain/health.log        # Health check results
/var/log/blockchain/reports/          # Daily reports
```

### Performance Baselines
| Metric | Single Node | 3 Nodes | 5 Nodes | Target |
|--------|-------------|---------|---------|---------|
| TPS | 10-50 | 20-100 | 50-200 | >20 |
| Response Time | 0.01-0.1s | 0.02-0.2s | 0.05-0.5s | <0.2s |
| Success Rate | >99% | >95% | >90% | >95% |
| Block Time | 2-10s | 5-15s | 10-30s | 5-15s |

### Quick Reference Commands
```bash
# 🔍 CHECK NODE HEALTH
cd tools/monitoring
python check_node_health.py                    # Quick health summary
python check_node_health.py --detailed         # Full diagnostics

# 🚀 START/STOP NODES
cd tools/deployment
python start_nodes.py --nodes 3               # Start 3 nodes
pkill -f "run_node.py"                        # Stop all nodes

# 📊 PERFORMANCE TESTING
cd tools/testing
python transaction_stress_test.py              # Stress test
python quantum_consensus_demo.py               # Quantum demo

# 🔬 MONITORING
cd tools/monitoring
python monitor_quantum_consensus.py            # Real-time monitoring
python trigger_quantum_consensus.py            # Trigger consensus activity

# 📈 ANALYSIS
cd tools/analysis
python final_quantum_report.py                 # Comprehensive report
python post_test_analysis.py                   # Post-test analysis
```

---

This guide provides everything you need to operate, monitor, and optimize your quantum annealing blockchain. For additional support or questions about specific metrics, refer to the individual tool documentation or the source code in the respective Python files.
