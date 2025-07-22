# Quantum Annealing-Based Consensus Mechanism

This implementation follows the IEEE research paper: "Quantum Annealing based Consensus Mechanism" by Shubham Joshi et al.

## Overview

This is a **completely new consensus algorithm** (not a variant of Proof of Stake) that uses quantum annealing to select representative nodes for block proposal in blockchain networks.

## Key Components

### 1. Representative Node Selection

Unlike traditional consensus mechanisms, this approach:
- Selects a **single representative node** to propose the next block
- Uses **Quadratic Unconstrained Binary Optimization (QUBO)** formulation
- Employs **quantum annealing** to solve the optimization problem
- Based on **comprehensive suitability scores** from multiple metrics

### 2. Suitability Score Calculation

Each node receives a suitability score `Si` based on four key metrics:

```
Si = (w_uptime × norm(Ui)) + (w_perf × norm(PastPerfi)) + 
     (w_throughput × norm(Throughputi)) - (w_latency × norm(Latencyi))
```

Where:
- **Uptime (Ui)**: Node availability based on Probe Protocol responses
- **Past Performance**: Historical success/failure rate of block proposals
- **Throughput**: Node's capacity to handle requests (responses per second)
- **Network Latency**: Round-trip time for network communication

### 3. Probe Protocol

A unified measurement framework that simultaneously provides:
- **Uptime verification**: Active participation in network probes
- **Latency measurement**: Round-trip time calculation
- **Throughput calculation**: Request handling capacity

**Protocol Flow:**
1. Source node sends signed ProbeRequest with timestamp and nonce
2. Target node responds with signed TargetReceipt
3. Random witness nodes provide signed WitnessReceipts
4. Quorum of witnesses (≥k/3) required for valid measurement

### 4. QUBO Formulation

The optimization problem is formulated as:

```
H = P(∑xi - 1)² - ∑S'i×xi
```

Where:
- `xi = 1` if node i is selected, `0` otherwise
- `P` is a large penalty coefficient
- `S'i` is the effective suitability score (with tie-breaking perturbation)

**QUBO Coefficients:**
- Linear: `Qii = -(P + S'i)`
- Quadratic: `Qij = 2P` for i < j
- Constant: `C = P`

### 5. Tie-Breaking Mechanism

To ensure deterministic selection when nodes have identical scores:

```
S'i = Si + δi
```

Where `δi = Hash(VRF_output + public_key_i) × ε`

- Uses Verifiable Random Function (VRF) output from previous block
- Combines with node's unique public key
- Multiplied by small epsilon (10⁻⁵) to preserve ranking

## Security Properties

### Sybil Attack Resistance
- Selection depends on **highest single score**, not quantity of nodes
- Creating many low-score nodes doesn't improve attack success probability
- **Theorem 1**: Quantity of nodes is irrelevant to selection outcome

### Block Withholding Mitigation
- Timeout detection mechanism with on-chain penalty system
- Failed proposals significantly impact future suitability scores
- **Theorem 2**: Attack becomes irrational due to long-term reputation damage

### Collusion Attack Prevention
- Random witness selection for probe measurements
- Quorum requirement (k/3 witnesses minimum)
- **Theorem 3**: Attackers cannot reliably control witness majorities

### Probe Protocol Integrity
- Digital signatures prevent message forging
- Unique nonces and timestamps prevent replay attacks
- **Theorem 4**: Protocol secure against common network attacks

## Implementation Architecture

### Core Classes

1. **QuantumAnnealingConsensus**: Main consensus class
   - Node registration and metric tracking
   - Probe protocol execution
   - Suitability score calculation
   - QUBO formulation and solving

2. **Node Metrics Tracking**:
   ```python
   {
       'public_key': str,
       'uptime': float,
       'latency': float,
       'throughput': float,
       'last_seen': timestamp,
       'proposal_success_count': int,
       'proposal_failure_count': int
   }
   ```

3. **Probe Protocol Data Structures**:
   ```python
   ProbeProof = {
       'source_node': str,
       'target_node': str,
       'nonce': str,
       'send_time': timestamp,
       'receipt_time': timestamp,
       'witnesses': List[str],
       'witness_receipts': List[Dict],
       'latency': float,
       'valid': bool
   }
   ```

### Key Methods

- `select_representative_node()`: Main consensus entry point
- `execute_probe_protocol()`: Network measurement execution
- `calculate_suitability_score()`: Score computation with normalization
- `formulate_qubo_problem()`: QUBO coefficient generation
- `simulate_quantum_annealer()`: Optimization solver (simulated)

## API Endpoints

### Quantum Metrics
`GET /api/v1/blockchain/quantum-metrics/`

Returns:
```json
{
    "consensus_type": "Quantum Annealing",
    "total_nodes": 5,
    "active_nodes": 4,
    "probe_count": 150,
    "node_scores": {
        "node_id": {
            "suitability_score": 0.85,
            "effective_score": 0.850001,
            "uptime": 1.0,
            "latency": 0.05,
            "throughput": 25.0,
            "proposals_success": 10,
            "proposals_failed": 1
        }
    },
    "protocol_parameters": {...},
    "scoring_weights": {...}
}
```

## Usage Example

```python
# Initialize consensus mechanism
consensus = QuantumAnnealingConsensus()

# Register nodes
consensus.register_node("node1", "public_key_1")
consensus.register_node("node2", "public_key_2")

# Execute consensus round
last_block_hash = "previous_block_hash"
selected_node = consensus.select_representative_node(last_block_hash)

# Record proposal result
consensus.record_proposal_result(selected_node, success=True)
```

## Differences from Proof of Stake

| Aspect | Quantum Annealing Consensus | Proof of Stake |
|--------|----------------------------|-----------------|
| Selection Method | QUBO optimization via quantum annealing | Weighted random selection |
| Selection Criteria | Multi-metric suitability scores | Stake amount |
| Node Roles | Representative + Validators | Validators only |
| Measurement | Active probe protocol | Passive stake tracking |
| Optimization | Quantum annealer solving | Classical probability |
| Tie Breaking | Deterministic VRF perturbation | Random/stake-weighted |

## Future Enhancements

1. **Real Quantum Annealer Integration**: Replace simulation with D-Wave API
2. **Enhanced Probe Protocol**: More sophisticated network measurements
3. **Dynamic Weight Adjustment**: Adaptive scoring based on network conditions
4. **Advanced Security**: Integration with post-quantum cryptography
5. **Performance Optimization**: Batch probe processing and caching

## Testing and Validation

The implementation includes:
- Comprehensive unit tests for all core functions
- Security analysis validation
- Performance benchmarking
- Network simulation capabilities
- API endpoint testing

This quantum annealing consensus mechanism represents a significant advancement in blockchain technology, offering enhanced security, fairness, and efficiency compared to traditional approaches.
