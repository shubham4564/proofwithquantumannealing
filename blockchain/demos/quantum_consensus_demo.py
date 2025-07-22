#!/usr/bin/env python3
"""
D-Wave Quantum Annealing Consensus Demo

This script demonstrates the quantum annealing consensus mechanism
using the D-Wave Ocean SDK simulator.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
from blockchain.quantum_consensus.quantum_annealing_consensus import QuantumAnnealingConsensus

def demo_quantum_consensus():
    """Demonstrate quantum annealing consensus with multiple nodes"""
    
    print("🌌 D-WAVE QUANTUM ANNEALING CONSENSUS DEMO")
    print("=" * 80)
    print("This demo shows the quantum annealing consensus mechanism using")
    print("the D-Wave Ocean SDK simulator for realistic quantum behavior.")
    print()
    
    # Initialize quantum consensus
    print("🔧 Initializing Quantum Annealing Consensus...")
    consensus = QuantumAnnealingConsensus(initialize_genesis=False)
    
    # Add multiple nodes with different performance characteristics
    nodes_data = [
        {"id": "node_0", "pk": "pk_node_0", "uptime": 0.99, "latency": 0.05, "throughput": 150.0},
        {"id": "node_1", "pk": "pk_node_1", "uptime": 0.95, "latency": 0.08, "throughput": 120.0},
        {"id": "node_2", "pk": "pk_node_2", "uptime": 0.98, "latency": 0.03, "throughput": 180.0},
        {"id": "node_3", "pk": "pk_node_3", "uptime": 0.92, "latency": 0.12, "throughput": 100.0},
        {"id": "node_4", "pk": "pk_node_4", "uptime": 0.97, "latency": 0.06, "throughput": 140.0},
    ]
    
    print(f"🖥️  Adding {len(nodes_data)} nodes to the network...")
    for node in nodes_data:
        consensus.register_node(node["id"], node["pk"])
        # Set realistic metrics
        consensus.nodes[node["id"]].update({
            'uptime': node["uptime"],
            'latency': node["latency"],
            'throughput': node["throughput"],
            'last_seen': time.time(),
            'proposal_success_count': 0,
            'proposal_failure_count': 0
        })
        print(f"   ✅ {node['id']}: uptime={node['uptime']:.2f}, latency={node['latency']:.3f}s, throughput={node['throughput']:.1f}")
    
    print()
    
    # Simulate probe protocol to gather network metrics
    print("🔍 Executing Probe Protocol...")
    node_ids = list(consensus.nodes.keys())
    for i, source in enumerate(node_ids[:3]):  # Limit probes for demo
        for target in node_ids:
            if source != target:
                witnesses = [n for n in node_ids if n not in [source, target]][:2]
                probe_result = consensus.execute_probe_protocol(source, target, witnesses)
                print(f"   📡 {source} → {target}: latency={probe_result['latency']:.3f}s")
    
    print()
    
    # Display current suitability scores
    print("📊 SUITABILITY SCORES BEFORE QUANTUM SELECTION")
    print("-" * 50)
    for node_id in node_ids:
        score = consensus.calculate_suitability_score(node_id)
        effective_score = consensus.calculate_effective_score(node_id, "demo_vrf")
        print(f"   {node_id}: suitability={score:.4f}, effective={effective_score:.4f}")
    
    print()
    
    # Demonstrate quantum annealing selection
    print("🌌 QUANTUM ANNEALING NODE SELECTION")
    print("-" * 50)
    
    # Run multiple rounds to show quantum behavior
    for round_num in range(5):
        print(f"\n🔄 Round {round_num + 1}:")
        
        # Simulate block hash for this round
        block_hash = f"block_hash_round_{round_num}"
        
        # Show QUBO formulation
        linear_coeff, quadratic_coeff, constant = consensus.formulate_qubo_problem(block_hash)
        print(f"   📐 QUBO Problem: {len(linear_coeff)} variables, {len(quadratic_coeff)} couplings")
        
        # Perform quantum annealing selection
        start_time = time.time()
        selected_node = consensus.select_representative_node(block_hash)
        selection_time = time.time() - start_time
        
        print(f"   🎯 Selected Node: {selected_node}")
        print(f"   ⏱️  Selection Time: {selection_time:.4f}s")
        
        # Update node performance based on selection
        if selected_node:
            consensus.record_proposal_result(selected_node, True)
            print(f"   ✅ Recorded successful proposal for {selected_node}")
    
    print()
    
    # Show final metrics
    print("📈 FINAL NETWORK METRICS")
    print("-" * 50)
    metrics = consensus.get_consensus_metrics()
    
    print(f"Consensus Type: {metrics['consensus_type']}")
    print(f"Total Nodes: {metrics['total_nodes']}")
    print(f"Active Nodes: {metrics['active_nodes']}")
    print(f"Probe Count: {metrics['probe_count']}")
    
    print(f"\nQuantum Annealing Configuration:")
    qa_config = metrics['quantum_annealing_config']
    print(f"   Annealing Time: {qa_config['annealing_time_microseconds']}μs")
    print(f"   Number of Reads: {qa_config['num_reads']}")
    print(f"   Simulator Enabled: {qa_config['simulator_enabled']}")
    
    print(f"\nNode Performance Summary:")
    for node_id, scores in metrics['node_scores'].items():
        print(f"   {node_id}: score={scores['suitability_score']:.4f}, "
              f"proposals={scores['proposals_success']}")
    
    print()
    
    # Demonstrate quantum advantage
    print("🔬 QUANTUM ANNEALING ANALYSIS")
    print("-" * 50)
    print("Key advantages of quantum annealing consensus:")
    print("✅ Optimal node selection through QUBO optimization")
    print("✅ Inherent randomness prevents predictable attacks")
    print("✅ Scales efficiently with network size")
    print("✅ Considers multiple performance metrics simultaneously")
    print("✅ Natural tie-breaking through quantum fluctuations")
    
    print(f"\n🎉 Demo completed successfully!")
    print("=" * 80)


def test_quantum_vs_classical():
    """Compare quantum annealing vs classical optimization"""
    
    print("\n🔬 QUANTUM VS CLASSICAL COMPARISON")
    print("=" * 50)
    
    consensus = QuantumAnnealingConsensus(initialize_genesis=False)
    
    # Add nodes with very similar scores to test tie-breaking
    similar_nodes = [
        {"id": f"node_{i}", "pk": f"pk_{i}", "uptime": 0.95 + i*0.001, 
         "latency": 0.05 + i*0.001, "throughput": 100.0 + i}
        for i in range(10)
    ]
    
    for node in similar_nodes:
        consensus.register_node(node["id"], node["pk"])
        consensus.nodes[node["id"]].update({
            'uptime': node["uptime"],
            'latency': node["latency"],
            'throughput': node["throughput"],
            'last_seen': time.time(),
            'proposal_success_count': 0,
            'proposal_failure_count': 0
        })
    
    # Test with quantum annealing enabled
    print("🌌 With Quantum Annealing (D-Wave Simulator):")
    consensus.use_quantum_simulator = True
    quantum_selections = []
    
    for i in range(10):
        selected = consensus.select_representative_node(f"test_hash_{i}")
        quantum_selections.append(selected)
        print(f"   Round {i+1}: {selected}")
    
    # Test with classical optimization (fallback)
    print("\n🖥️  With Classical Optimization:")
    consensus.use_quantum_simulator = False
    classical_selections = []
    
    for i in range(10):
        selected = consensus.select_representative_node(f"test_hash_{i}")
        classical_selections.append(selected)
        print(f"   Round {i+1}: {selected}")
    
    # Analyze differences
    quantum_variety = len(set(quantum_selections))
    classical_variety = len(set(classical_selections))
    
    print(f"\n📊 Selection Diversity:")
    print(f"   Quantum: {quantum_variety}/10 unique selections")
    print(f"   Classical: {classical_variety}/10 unique selections")
    
    if quantum_variety > classical_variety:
        print("✅ Quantum annealing shows better selection diversity!")
    else:
        print("📝 Both methods show similar diversity for this test case")


if __name__ == "__main__":
    try:
        demo_quantum_consensus()
        test_quantum_vs_classical()
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()
