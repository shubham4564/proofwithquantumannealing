#!/usr/bin/env python3
"""
Timing Analysis Test for Quantum Annealing Consensus

This script analyzes the time taken by individual processes within the quantum annealing consensus mechanism.
"""

import time
import sys
import os

# Add the blockchain module to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'blockchain'))

from blockchain.quantum_consensus.quantum_annealing_consensus import QuantumAnnealingConsensus

def test_consensus_timing_4_nodes():
    """Test consensus with 4 nodes to analyze timing breakdown"""
    print("=" * 80)
    print("🚀 QUANTUM ANNEALING CONSENSUS - TIMING ANALYSIS")
    print("=" * 80)
    print(f"📊 Testing with 4 nodes (cached protocol expected)")
    print()
    
    # Initialize consensus mechanism
    consensus = QuantumAnnealingConsensus(initialize_genesis=True)
    
    # Register 4 test nodes
    test_nodes = ["node2", "node3", "node4", "node5"]
    
    print("📝 Registering test nodes...")
    registration_start = time.time()
    
    for node_id in test_nodes:
        public_key, private_key = consensus.ensure_node_keys(node_id)
        consensus.register_node(node_id, public_key)
        print(f"   ✅ Registered {node_id}")
    
    registration_time = time.time() - registration_start
    print(f"📝 Node registration completed: {registration_time * 1000:.3f}ms")
    print()
    
    # Run consensus multiple times to get average timing
    num_runs = 3
    total_times = []
    
    for run in range(num_runs):
        print(f"🔄 CONSENSUS RUN {run + 1}/{num_runs}")
        print("-" * 60)
        
        test_block_hash = f"test_block_hash_{run}_{int(time.time())}"
        
        run_start = time.time()
        selected_node = consensus.select_representative_node(test_block_hash)
        run_time = time.time() - run_start
        
        total_times.append(run_time)
        print(f"   🎯 Run {run + 1} Result: {selected_node} in {run_time * 1000:.3f}ms")
        print()
    
    # Calculate statistics
    avg_time = sum(total_times) / len(total_times)
    min_time = min(total_times)
    max_time = max(total_times)
    
    print("=" * 80)
    print("📊 TIMING ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"🔢 Number of consensus runs: {num_runs}")
    print(f"⚡ Average consensus time: {avg_time * 1000:.3f}ms")
    print(f"🚀 Fastest consensus time: {min_time * 1000:.3f}ms")
    print(f"🐌 Slowest consensus time: {max_time * 1000:.3f}ms")
    print(f"📈 Performance variance: {(max_time - min_time) * 1000:.3f}ms")
    print()
    
    # Analyze probe statistics
    probe_stats = consensus.get_all_probe_counts()
    print("📡 PROBE PROTOCOL STATISTICS")
    print("-" * 40)
    for node_id, stats in probe_stats.items():
        print(f"   {node_id}: sent={stats['probes_sent']}, received={stats['probes_received']}, witness={stats['witness_count']}")
    print()
    
    return consensus, {
        'avg_time_ms': avg_time * 1000,
        'min_time_ms': min_time * 1000,
        'max_time_ms': max_time * 1000,
        'num_nodes': len(consensus.nodes),
        'probe_stats': probe_stats
    }

def test_consensus_timing_large_network():
    """Test consensus with larger network to see full protocol timing"""
    print("=" * 80)
    print("🌐 LARGE NETWORK CONSENSUS - TIMING ANALYSIS")
    print("=" * 80)
    print(f"📊 Testing with 8 nodes (full protocol expected)")
    print()
    
    # Initialize consensus mechanism
    consensus = QuantumAnnealingConsensus(initialize_genesis=True)
    
    # Register 8 test nodes
    test_nodes = [f"node{i}" for i in range(2, 10)]
    
    print("📝 Registering test nodes...")
    registration_start = time.time()
    
    for node_id in test_nodes:
        public_key, private_key = consensus.ensure_node_keys(node_id)
        consensus.register_node(node_id, public_key)
        print(f"   ✅ Registered {node_id}")
    
    registration_time = time.time() - registration_start
    print(f"📝 Node registration completed: {registration_time * 1000:.3f}ms")
    print()
    
    # Run single consensus to analyze detailed timing
    print("🔄 DETAILED CONSENSUS ANALYSIS")
    print("-" * 60)
    
    test_block_hash = f"large_network_test_{int(time.time())}"
    
    run_start = time.time()
    selected_node = consensus.select_representative_node(test_block_hash)
    run_time = time.time() - run_start
    
    print(f"   🎯 Result: {selected_node} in {run_time * 1000:.3f}ms")
    print()
    
    return consensus, {
        'total_time_ms': run_time * 1000,
        'num_nodes': len(consensus.nodes),
        'selected_node': selected_node
    }

def main():
    """Main timing analysis function"""
    print("🔬 QUANTUM ANNEALING CONSENSUS - COMPREHENSIVE TIMING ANALYSIS")
    print("=" * 80)
    print()
    
    # Test 1: Small network (cached protocol)
    small_consensus, small_results = test_consensus_timing_4_nodes()
    
    # Test 2: Larger network (full protocol)  
    large_consensus, large_results = test_consensus_timing_large_network()
    
    # Final comparison
    print("=" * 80)
    print("🔍 PERFORMANCE COMPARISON")
    print("=" * 80)
    print(f"📊 Small Network (4 nodes): {small_results['avg_time_ms']:.3f}ms average")
    print(f"🌐 Large Network (8 nodes): {large_results['total_time_ms']:.3f}ms")
    print()
    
    if small_results['avg_time_ms'] < large_results['total_time_ms']:
        speedup = large_results['total_time_ms'] / small_results['avg_time_ms']
        print(f"⚡ Small network is {speedup:.1f}x faster (cached protocol optimization)")
    else:
        print(f"🔄 Networks show similar performance")
    
    print()
    print("🎯 BOTTLENECK IDENTIFICATION:")
    print("   - Check the detailed logs above to identify which step takes the most time")
    print("   - Probe Protocol timing should be much lower for small networks (cached)")
    print("   - QUBO Formulation and Quantum Annealing should be consistent across sizes")
    print("   - VRF Generation and Final Selection should be minimal (~0.1ms)")
    print()
    print("✅ Timing analysis complete!")

if __name__ == "__main__":
    main()
