# Blockchain Performance Measurement Guide

This guide explains how to measure key performance metrics for your quantum annealing blockchain implementation.

## Available Performance Tools

### 1. Quick Metrics Demo (`quick_metrics_demo.py`)
**Purpose**: Simple demonstration of key performance metrics
**Best for**: Understanding basic performance characteristics

```bash
python quick_metrics_demo.py
```

**Metrics measured**:
- Transaction creation time (microseconds)
- Network submission time 
- Total transaction processing time
- Consensus timing estimation
- Transaction throughput (TPS)
- Success rates

### 2. Simple Performance Analyzer (`simple_performance.py`)
**Purpose**: Comprehensive performance analysis without external dependencies
**Best for**: Detailed performance testing and benchmarking

```bash
# Quick throughput test
python simple_performance.py --throughput-test --transactions 30

# Full benchmark
python simple_performance.py --benchmark --transactions 50 --duration 60

# Measure consensus only
python simple_performance.py --measure-consensus --duration 60

# Measure block production only
python simple_performance.py --measure-blocks --duration 60

# Sequential transaction testing
python simple_performance.py --throughput-test --transactions 20 --sequential
```

### 3. Multi-Node Test Suite (`multi_node_test.py`)
**Purpose**: Multi-node performance testing with quantum consensus analysis
**Best for**: Testing network-wide performance and consensus behavior

```bash
python multi_node_test.py --nodes 3 --transactions 50 --duration 300
```

### 4. Advanced Performance Analyzer (`performance_analyzer.py`)
**Purpose**: Enterprise-grade performance analysis with detailed metrics
**Best for**: Production performance monitoring and detailed analysis

```bash
# Run benchmark
python performance_analyzer.py --benchmark --transactions 100

# Real-time monitoring
python performance_analyzer.py --real-time --interval 10 --duration 300

# Save metrics to CSV
python performance_analyzer.py --benchmark --save-csv
```

## Key Performance Metrics Explained

### 1. Transaction Time
**Definition**: Time from transaction creation to network acceptance

**Components**:
- **Creation Time**: Time to create and sign transaction (~0.001s)
- **Submission Time**: Time to submit to network and receive response
- **Total Time**: Creation + Submission + Network processing

**Typical Values**:
- Good: < 0.5 seconds
- Acceptable: 0.5 - 2.0 seconds  
- Needs optimization: > 2.0 seconds

### 2. Consensus Time
**Definition**: Time for quantum annealing consensus to select forger and validate block

**Components**:
- **Quantum Score Calculation**: Time to compute node suitability scores
- **Forger Selection**: Time to select optimal forger using quantum annealing
- **Block Validation**: Time to validate and accept new block

**Monitoring**: Check quantum metrics API for probe counts and consensus rounds

### 3. Transaction Throughput (TPS)
**Definition**: Number of transactions processed per second

**Calculation**: `Successful Transactions / Total Time`

**Factors affecting TPS**:
- Network latency
- Consensus algorithm efficiency
- Block size and timing
- Node processing capacity

**Typical Values**:
- Small network (1-3 nodes): 5-20 TPS
- Medium network (4-10 nodes): 10-50 TPS
- Large network (10+ nodes): 20-100+ TPS

## Performance Testing Scenarios

### Scenario 1: Single Node Performance Baseline
```bash
# Start single node
python run_node.py --ip localhost --node_port 8000 --api_port 8050

# Test basic performance
python quick_metrics_demo.py
```

### Scenario 2: Multi-Node Network Performance
```bash
# Start multiple nodes
python start_nodes.py --nodes 4

# Wait for nodes to be ready (30 seconds)
sleep 30

# Run comprehensive test
python multi_node_test.py --nodes 4 --transactions 100 --duration 300
```

### Scenario 3: Load Testing
```bash
# Start nodes
python start_nodes.py --nodes 3

# Run high-load test
python simple_performance.py --benchmark --transactions 200 --duration 300

# Or concurrent load test
python simple_performance.py --throughput-test --transactions 100
```

### Scenario 4: Real-time Monitoring
```bash
# Start monitoring
python performance_analyzer.py --real-time --interval 5 --duration 600

# In another terminal, generate load
python sample_transactions.py
```

## Understanding Results

### Transaction Response Times
```
Avg Response Time: 0.234s    # Good - under 0.5s
Median Response Time: 0.198s # Most transactions processed quickly
Min Response Time: 0.089s    # Best case performance
Max Response Time: 1.234s    # Worst case (check for outliers)
```

### Throughput Analysis
```
TPS: 15.67                   # Transactions per second
Success Rate: 98.5%          # Should be > 95%
Total Duration: 45.2s        # Test execution time
```

### Consensus Metrics
```
Avg Probe Count: 78.3        # Quantum annealing iterations
Avg Active Nodes: 3.8        # Participating nodes
Consensus Stability: ✅ Stable # Consistent node participation
```

### Block Production
```
Blocks Produced: 12          # New blocks during test
Avg Block Time: 3.45s        # Time between blocks
Blocks per Minute: 17.4      # Block production rate
```

## Performance Optimization Tips

### 1. Transaction Performance
- **Batch transactions** when possible
- **Use concurrent submission** for load testing
- **Monitor network latency** between nodes
- **Optimize transaction size** (smaller = faster)

### 2. Consensus Performance  
- **Monitor probe counts** - high counts may indicate network issues
- **Check node synchronization** - ensure all nodes stay in sync
- **Verify quantum algorithm parameters** for optimal performance

### 3. Network Performance
- **Use local networks** for testing (lower latency)
- **Monitor node availability** and connection health
- **Balance load across nodes** for multi-node tests

## Troubleshooting Performance Issues

### Low TPS (< 5 transactions/second)
```bash
# Check node health
python simple_performance.py --measure-consensus --duration 30

# Verify network connectivity
curl http://localhost:8050/api/v1/blockchain/

# Check system resources
top -p $(pgrep -f run_node.py)
```

### High Response Times (> 1 second)
```bash
# Test individual components
python quick_metrics_demo.py

# Check for network issues
ping localhost

# Monitor consensus behavior
python simple_performance.py --measure-consensus --duration 60
```

### Failed Transactions
```bash
# Check node logs
python run_node.py --ip localhost --node_port 8000 --api_port 8050

# Verify wallet funding
python sample_transactions.py

# Test basic connectivity
curl -X GET http://localhost:8050/api/v1/blockchain/
```

## Automated Performance Testing

### Daily Performance Check
```bash
#!/bin/bash
# daily_performance_check.sh

echo "Starting daily performance check..."

# Start nodes
python start_nodes.py --nodes 3 &
sleep 30

# Run benchmark
python simple_performance.py --benchmark --transactions 50 --duration 120

# Save results with timestamp
timestamp=$(date +%Y%m%d_%H%M%S)
mv performance_report_*.txt "daily_report_${timestamp}.txt"

# Cleanup
pkill -f run_node.py

echo "Performance check complete"
```

### Continuous Monitoring
```bash
#!/bin/bash
# continuous_monitor.sh

while true; do
    python performance_analyzer.py --real-time --interval 30 --duration 300
    sleep 300
done
```

## Performance Benchmarks

### Expected Performance Baselines

| Metric | Single Node | 3 Nodes | 5 Nodes |
|--------|-------------|---------|---------|
| TPS | 10-25 | 15-35 | 20-50 |
| Avg Response Time | 0.1-0.3s | 0.2-0.5s | 0.3-0.8s |
| Block Time | 2-5s | 3-8s | 5-12s |
| Success Rate | >99% | >95% | >90% |

### Performance Goals
- **Transaction Time**: < 0.5 seconds average
- **Consensus Time**: < 10 seconds per round
- **Throughput**: > 20 TPS for 3+ nodes
- **Success Rate**: > 95% under normal load
- **Block Time**: 5-15 seconds (configurable)

## Next Steps

1. **Run baseline tests** with single node using `quick_metrics_demo.py`
2. **Scale to multi-node** testing with `multi_node_test.py`
3. **Perform load testing** with `simple_performance.py --benchmark`
4. **Set up monitoring** with `performance_analyzer.py --real-time`
5. **Analyze results** and optimize configuration based on findings

For production deployments, establish regular performance monitoring and set up alerts for metrics that fall outside acceptable ranges.
