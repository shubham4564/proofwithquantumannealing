# Health Monitoring Enhancement for start_nodes.py

## Overview

The `start_nodes.py` script has been enhanced with comprehensive health monitoring capabilities that continuously monitor the status of all running blockchain nodes and provide real-time alerts when nodes go down.

## New Features

### 1. Periodic Health Checks
- **Automatic Monitoring**: Checks all nodes every 30 seconds (configurable)
- **API Endpoint Testing**: Verifies that each node's API is responding correctly
- **Process Status Verification**: Ensures node processes are still running
- **Response Time Tracking**: Measures API response times for performance monitoring

### 2. Real-Time Alerts
- **Node Down Alerts**: Immediate notifications when a healthy node goes down
- **Node Recovery Alerts**: Notifications when a down node comes back online
- **Status Change Detection**: Tracks transitions between healthy/unhealthy states
- **Timestamped Messages**: All alerts include precise timestamps

### 3. Health Status Categories
- **Healthy**: Node process running and API responding correctly
- **Unhealthy**: Node process running but API returning errors
- **Unreachable**: Node process running but API not accessible
- **Timeout**: Node process running but API requests timing out
- **Dead**: Node process has exited/crashed
- **Error**: Unexpected errors during health checks

### 4. Periodic Status Summaries
- **5-Minute Summaries**: Detailed health reports every 5 minutes
- **Node Count**: Shows healthy vs. total nodes ratio
- **Individual Status**: Lists each node's current health state
- **Port Information**: Displays P2P and API ports for each node

## Usage

### Basic Usage
```bash
cd blockchain
python demos/start_nodes.py --nodes 3
```

### With Custom Health Check Interval
```bash
python demos/start_nodes.py --nodes 4 --health-interval 15
```

### Start Without Waiting (Background Mode)
```bash
python demos/start_nodes.py --nodes 3 --no-wait
```

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--nodes` | 3 | Number of nodes to start |
| `--base-node-port` | 10000 | Base port for P2P communication |
| `--base-api-port` | 11000 | Base port for API endpoints |
| `--health-interval` | 30 | Health check interval in seconds |
| `--no-wait` | False | Don't wait for interrupt, just start and exit |

## Sample Output

### Node Startup
```
🌟 QUANTUM ANNEALING MULTI-NODE STARTER
==================================================
Starting 3 nodes
P2P ports: 10000-10002
API ports: 11000-11002

🚀 Starting 3 blockchain nodes...
============================================================
🔍 Checking port availability and allocating ports...
✅ All ports allocated successfully

Starting Node 0:
  Command: python run_node.py --ip localhost --node_port 10000 --api_port 11000 --key_file ./keys/genesis_private_key.pem
  Node Port: 10000
  API Port: 11000
  API URL: http://localhost:11000/api/v1/blockchain/
  ✅ Node 0 started (PID: 12345)

[... similar output for other nodes ...]

🎯 All nodes started!
🔍 Health monitoring will start in 30 seconds...
```

### Health Check Alerts
```
⚠️  HEALTH CHECK ALERT [14:32:15]
============================================================
  🚨 Node 1 (API:11001) went DOWN: Connection refused
  ✅ Node 2 (API:11002) is back UP
============================================================
```

### Periodic Health Summary
```
💊 Health Check Summary [14:35:00]
   Healthy Nodes: 2/3
   Node 0 (API:11000): ✅ healthy
   Node 1 (API:11001): ❌ unreachable - Connection refused
   Node 2 (API:11002): ✅ healthy
```

## Benefits

1. **Early Problem Detection**: Identify node failures immediately rather than discovering them during testing
2. **System Reliability**: Monitor the overall health of your blockchain network
3. **Debugging Support**: Detailed error messages help diagnose node issues
4. **Operational Awareness**: Understand which nodes are performing well
5. **Automated Monitoring**: No manual intervention required for basic health checks

## Integration with Existing Tools

The health monitoring works seamlessly with:
- **sample_transactions.py**: Automatically uses healthy nodes for transactions
- **multi_node_test.py**: Validates network health before running tests
- **quantum_demo.py**: Ensures all demonstration nodes are operational
- **check_node_health.py**: Provides complementary detailed health analysis

## Demo Script

A demonstration script is available at `demos/health_monitoring_demo.py` that shows the health monitoring features in action:

```bash
cd blockchain
python demos/health_monitoring_demo.py
```

This demo will:
1. Start 2 blockchain nodes
2. Monitor their health every 10 seconds
3. Simulate node failure by stopping one node
4. Show health alerts in real-time
5. Clean up all processes

## Technical Implementation

### Health Check Method
The health monitoring uses a multi-layered approach:

1. **Process Check**: Verify the node process is still running
2. **API Check**: Send HTTP request to `/api/v1/blockchain/info/` endpoint
3. **Response Validation**: Ensure HTTP 200 status and valid response
4. **Timeout Handling**: 5-second timeout for API requests
5. **Error Categorization**: Classify different types of failures

### Dependencies
- **requests**: For HTTP API health checks
- **datetime**: For timestamping alerts and summaries
- **subprocess**: For process management and monitoring

### Performance Impact
- **Minimal Overhead**: Health checks run in the main monitoring loop
- **Efficient Requests**: Uses connection pooling and short timeouts
- **Configurable Interval**: Adjust frequency based on your needs
- **Background Operation**: Doesn't interfere with node operations

## Troubleshooting

### Common Issues

1. **High False Positives**: Increase health check interval if nodes are slow to respond
2. **Missing Alerts**: Check that nodes have proper API endpoints configured
3. **Performance Impact**: Reduce check frequency for resource-constrained systems

### Debug Information
When nodes fail, the system provides detailed debug information including:
- Exit codes
- Process IDs
- Port allocations
- STDOUT/STDERR output
- Error timestamps

## Future Enhancements

Potential improvements for future versions:
- **Webhook Notifications**: Send alerts to external monitoring systems
- **Health History**: Track node uptime and failure patterns
- **Automatic Recovery**: Restart failed nodes automatically
- **Metrics Export**: Export health data for analysis
- **Load Balancing**: Route traffic away from unhealthy nodes
