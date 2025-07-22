# Timing Calculation Guide for Quantum Annealing Blockchain

This guide explains how to calculate consensus time, transaction time with signature verification, and communication time through direct code analysis.

## Overview of Timing Components

The quantum annealing blockchain has several key timing components that can be measured directly:

### 1. Consensus Time (Quantum Annealing)
### 2. Transaction Processing Time with Signature Verification  
### 3. Communication Time (P2P Network)
### 4. Block Creation and Propagation Time

---

## 1. Consensus Time Calculation

The consensus time includes several sub-components:

### A. Node Eligibility Check Time
```python
start_time = time.perf_counter()
eligible_nodes = []
for node_id in all_nodes:
    if consensus.is_node_eligible_for_consensus(node_id):
        eligible_nodes.append(node_id)
eligibility_time = (time.perf_counter() - start_time) * 1000  # ms
```

### B. Suitability Score Calculation Time
```python
start_time = time.perf_counter()
node_scores = {}
for node_id in eligible_nodes:
    node_scores[node_id] = consensus.calculate_node_suitability_score(node_id)
scoring_time = (time.perf_counter() - start_time) * 1000  # ms
```

### C. Quantum Annealing Execution Time
```python
start_time = time.perf_counter()
selected_forger = consensus.select_representative_node(last_block_hash)
quantum_execution_time = (time.perf_counter() - start_time) * 1000  # ms
```

### D. Total Consensus Time
```python
total_consensus_time = eligibility_time + scoring_time + quantum_execution_time
```

### Quantum Annealing Specifics:
- **Annealing Time**: ~20 microseconds (typical D-Wave quantum annealer)
- **Number of Reads**: 50-150 (scales with network size)
- **Problem Formulation**: QUBO (Quadratic Unconstrained Binary Optimization)

---

## 2. Transaction Time with Signature Verification

### A. Transaction Creation Time
```python
start_time = time.perf_counter()
transaction = wallet.create_transaction(receiver_key, amount, tx_type)
creation_time = (time.perf_counter() - start_time) * 1000  # ms
```

### B. Digital Signature Generation Time
```python
start_time = time.perf_counter()
signature = wallet.sign(transaction_data)
signature_generation_time = (time.perf_counter() - start_time) * 1000  # ms
```

### C. Signature Verification Time
```python
start_time = time.perf_counter()
is_valid = wallet.verify_signature(message, signature, public_key)
verification_time = (time.perf_counter() - start_time) * 1000  # ms
```

### D. Transaction Encoding Time
```python
start_time = time.perf_counter()
encoded_transaction = BlockchainUtils.encode(transaction)
encoding_time = (time.perf_counter() - start_time) * 1000  # ms
```

### E. Total Transaction Processing Time
```python
total_tx_time = creation_time + signature_generation_time + verification_time + encoding_time
```

### Signature Verification Breakdown:
- **RSA 2048-bit Key Generation**: ~100-500ms (one-time)
- **RSA Signature Generation**: ~5-15ms per signature
- **RSA Signature Verification**: ~1-3ms per verification
- **Hash Calculation (SHA-256)**: ~0.1-0.5ms per hash

---

## 3. Communication Time (P2P Network)

### A. API Request Time
```python
start_time = time.perf_counter()
response = requests.get(f'http://localhost:{port}/api/v1/blockchain/', timeout=5)
api_response_time = (time.perf_counter() - start_time) * 1000  # ms
```

### B. Network Latency Estimation
```python
# Round-trip time measurement
round_trip_time = api_response_time
network_latency = round_trip_time / 2  # One-way latency estimate
```

### C. P2P Message Propagation Time
```python
start_time = time.perf_counter()
# Send message to all peers
for peer_port in peer_ports:
    send_message_to_peer(peer_port, message)
    
# Wait for all confirmations
wait_for_all_confirmations()
propagation_time = (time.perf_counter() - start_time) * 1000  # ms
```

### D. Communication Matrix Analysis
```python
communication_matrix = {}
for source_port in api_ports:
    for target_port in api_ports:
        if source_port != target_port:
            latency = measure_latency(source_port, target_port)
            communication_matrix[(source_port, target_port)] = latency
```

---

## 4. Block Creation and Propagation Time

### A. Block Creation Time
```python
start_time = time.perf_counter()
new_block = blockchain.create_new_block(transactions, selected_forger)
block_creation_time = (time.perf_counter() - start_time) * 1000  # ms
```

### B. Block Validation Time
```python
start_time = time.perf_counter()
is_valid = blockchain.validate_block(new_block)
validation_time = (time.perf_counter() - start_time) * 1000  # ms
```

### C. Block Propagation Time
```python
propagation_start = time.perf_counter()
initial_block_count = get_blockchain_length_all_nodes()

# Wait for block to propagate to all nodes
while True:
    current_block_counts = get_blockchain_length_all_nodes()
    if all(count > initial_count for count, initial_count in zip(current_block_counts, initial_block_count)):
        break
    time.sleep(0.1)

propagation_time = (time.perf_counter() - propagation_start) * 1000  # ms
```

---

## 5. End-to-End Transaction Time

### Complete Transaction Processing Pipeline:
```python
def measure_end_to_end_transaction_time():
    total_start = time.perf_counter()
    
    # 1. Transaction creation and signing
    tx_start = time.perf_counter()
    transaction = create_and_sign_transaction()
    tx_creation_time = (time.perf_counter() - tx_start) * 1000
    
    # 2. Network submission
    submit_start = time.perf_counter()
    submit_transaction(transaction)
    submission_time = (time.perf_counter() - submit_start) * 1000
    
    # 3. Wait for consensus and block inclusion
    consensus_start = time.perf_counter()
    wait_for_consensus_and_block_creation()
    consensus_time = (time.perf_counter() - consensus_start) * 1000
    
    # 4. Wait for network propagation
    propagation_start = time.perf_counter()
    wait_for_full_network_propagation()
    propagation_time = (time.perf_counter() - propagation_start) * 1000
    
    total_time = (time.perf_counter() - total_start) * 1000
    
    return {
        'transaction_creation_time_ms': tx_creation_time,
        'network_submission_time_ms': submission_time,
        'consensus_and_block_time_ms': consensus_time,
        'propagation_time_ms': propagation_time,
        'total_end_to_end_time_ms': total_time
    }
```

---

## 6. Performance Metrics and Calculations

### A. Throughput Calculations
```python
# Consensus throughput (decisions per second)
consensus_throughput = 1000 / average_consensus_time_ms

# Signature verification throughput (verifications per second)  
verification_throughput = 1000 / average_verification_time_ms

# Transaction throughput (transactions per second)
transaction_throughput = 1000 / average_transaction_processing_time_ms

# Network communication throughput (requests per second)
communication_throughput = 1000 / average_response_time_ms
```

### B. Overhead Analysis
```python
def calculate_overhead_percentages(consensus_time, signature_time, 
                                 communication_time, total_time):
    return {
        'consensus_overhead_percent': (consensus_time / total_time) * 100,
        'signature_overhead_percent': (signature_time / total_time) * 100,
        'communication_overhead_percent': (communication_time / total_time) * 100
    }
```

### C. Scalability Analysis
```python
def analyze_scalability(node_counts, timing_measurements):
    """Analyze how timing scales with network size"""
    scaling_factors = {}
    
    for component in ['consensus', 'communication', 'propagation']:
        # Calculate scaling factor (linear, quadratic, etc.)
        scaling_factors[component] = calculate_scaling_factor(
            node_counts, 
            timing_measurements[component]
        )
    
    return scaling_factors
```

---

## 7. Code Implementation Examples

### A. Using the Comprehensive Timing Analyzer
```bash
# Run comprehensive analysis
python comprehensive_timing_analyzer.py --nodes 3 --transactions 10

# Save results to specific file
python comprehensive_timing_analyzer.py --output my_timing_results.json
```

### B. Using Direct Timing Measurements
```python
from direct_timing_measurements import DirectTimingMeasurements

# Measure consensus time directly
consensus_results = DirectTimingMeasurements.measure_consensus_time_direct(
    node_ids=['node1', 'node2', 'node3']
)

# Measure signature verification
signature_results = DirectTimingMeasurements.measure_signature_verification_time_direct(
    num_iterations=100
)

# Measure communication
communication_results = DirectTimingMeasurements.measure_communication_time_direct(
    source_port=11000,
    target_ports=[11001, 11002]
)
```

### C. Quick Timing Demo
```bash
# Run quick demonstration
python quick_timing_demo.py
```

---

## 8. Expected Performance Ranges

### Typical Timing Ranges (for reference):

- **Consensus Time**: 10-100ms (depends on network size and quantum reads)
- **Signature Generation**: 5-15ms (RSA-2048)
- **Signature Verification**: 1-3ms (RSA-2048)  
- **Network Latency**: 1-50ms (localhost: ~0.1ms, LAN: 1-5ms, WAN: 10-100ms)
- **Transaction Creation**: 3-10ms
- **Block Creation**: 5-50ms (depends on transaction count)
- **Block Propagation**: 50-500ms (depends on network size and topology)

### Performance Optimization Tips:

1. **Consensus Optimization**: Reduce quantum reads for smaller networks
2. **Signature Optimization**: Use ECDSA for faster verification (vs RSA)
3. **Communication Optimization**: Implement connection pooling and compression
4. **Propagation Optimization**: Use efficient gossip protocols

---

## 9. Monitoring and Analysis Tools

### Real-time Monitoring:
```python
# Monitor live performance
python monitoring/performance_monitor.py --live --interval 1

# Analyze historical performance  
python analysis/performance_analyzer.py --log-file performance.log
```

### Statistical Analysis:
```python
import statistics

def analyze_timing_statistics(timing_data):
    return {
        'mean': statistics.mean(timing_data),
        'median': statistics.median(timing_data),
        'std_dev': statistics.stdev(timing_data),
        'percentile_95': statistics.quantiles(timing_data, n=20)[18],  # 95th percentile
        'min': min(timing_data),
        'max': max(timing_data)
    }
```

This guide provides the foundation for measuring and analyzing all timing components in the quantum annealing blockchain system.
