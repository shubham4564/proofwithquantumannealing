#!/usr/bin/env python3
"""
Scalability Testing Script for Quantum Annealing Consensus
Tests the system with 1000+ nodes to verify performance optimizations.
"""

import sys
import os
import time
import random
import statistics
from typing import List, Dict

# Add the parent directory to Python path to find blockchain modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from blockchain.quantum_consensus.quantum_annealing_consensus import QuantumAnnealingConsensus


class ScalabilityTester:
    """Test quantum consensus mechanism scalability with large node counts"""
    
    def __init__(self):
        self.consensus = QuantumAnnealingConsensus(initialize_genesis=True)
        self.test_results = {}
        
    def generate_mock_nodes(self, count: int) -> List[str]:
        """Generate mock nodes with realistic performance characteristics"""
        nodes = []
        
        print(f"Generating {count} mock nodes...")
        
        for i in range(count):
            node_id = f"node_{i:04d}_{random.randint(1000, 9999)}"
            public_key = f"pk_{node_id}"
            
            # Register node
            self.consensus.register_node(node_id, public_key)
            
            # Assign realistic performance metrics
            self.consensus.nodes[node_id].update({
                'uptime': random.uniform(0.8, 1.0),  # 80-100% uptime
                'latency': random.uniform(0.01, 0.5),  # 10ms to 500ms
                'throughput': random.uniform(10, 200),  # 10-200 TPS
                'proposal_success_count': random.randint(0, 50),
                'proposal_failure_count': random.randint(0, 10),
                'trust_score': random.uniform(0.3, 1.0),
                'cluster_id': random.randint(0, 9)  # 10 geographic clusters
            })
            
            nodes.append(node_id)
            
            # Progress indicator
            if (i + 1) % 100 == 0:
                print(f"  Generated {i + 1}/{count} nodes...")
                
        print(f"✅ Successfully generated {count} nodes")
        return nodes
    
    def test_node_selection_performance(self, node_counts: List[int]):
        """Test node selection performance at various scales"""
        print("\n=== Testing Node Selection Performance ===")
        
        results = {}
        
        for count in node_counts:
            print(f"\nTesting with {count} nodes:")
            
            # Clear existing nodes except genesis
            genesis_node = list(self.consensus.nodes.keys())[0]
            self.consensus.nodes = {genesis_node: self.consensus.nodes[genesis_node]}
            self.consensus.node_performance_cache.clear()
            
            # Generate nodes for this test
            nodes = self.generate_mock_nodes(count - 1)  # -1 for genesis
            
            # Measure selection performance
            selection_times = []
            selections = []
            
            print(f"  Running 10 selection rounds...")
            
            for round_num in range(10):
                # Cleanup performance data to simulate real conditions
                if round_num % 3 == 0:
                    self.consensus.cleanup_performance_data()
                
                # Measure selection time
                start_time = time.time()
                
                last_block_hash = f"test_hash_{round_num}_{random.randint(1000, 9999)}"
                selected_node = self.consensus.select_representative_node(last_block_hash)
                
                end_time = time.time()
                selection_time = end_time - start_time
                
                selection_times.append(selection_time)
                selections.append(selected_node)
                
                print(f"    Round {round_num + 1}: {selection_time:.3f}s - Selected: {selected_node[:20]}...")
            
            # Calculate statistics
            avg_time = statistics.mean(selection_times)
            max_time = max(selection_times)
            min_time = min(selection_times)
            
            results[count] = {
                'avg_selection_time': avg_time,
                'max_selection_time': max_time,
                'min_selection_time': min_time,
                'total_nodes': len(self.consensus.nodes),
                'unique_selections': len(set(selections))
            }
            
            print(f"  Results:")
            print(f"    Average selection time: {avg_time:.3f}s")
            print(f"    Max selection time: {max_time:.3f}s")
            print(f"    Min selection time: {min_time:.3f}s")
            print(f"    Total registered nodes: {len(self.consensus.nodes)}")
            print(f"    Unique nodes selected: {len(set(selections))}/10")
            
        self.test_results['node_selection_performance'] = results
        return results
    
    def test_probe_protocol_scaling(self, node_counts: List[int]):
        """Test probe protocol efficiency at scale"""
        print("\n=== Testing Probe Protocol Scaling ===")
        
        results = {}
        
        for count in node_counts:
            print(f"\nTesting probe protocol with {count} nodes:")
            
            # Clear existing nodes except genesis
            genesis_node = list(self.consensus.nodes.keys())[0]
            self.consensus.nodes = {genesis_node: self.consensus.nodes[genesis_node]}
            
            # Generate nodes
            nodes = self.generate_mock_nodes(count - 1)
            
            # Get candidate nodes
            candidates = self.consensus.get_top_candidate_nodes("test_vrf_output")
            
            print(f"  Candidate nodes for probing: {len(candidates)}")
            
            # Measure probe execution time
            start_time = time.time()
            self.consensus.execute_scalable_probe_protocol(candidates)
            end_time = time.time()
            
            probe_time = end_time - start_time
            probe_count = len(self.consensus.probe_history)
            
            results[count] = {
                'probe_execution_time': probe_time,
                'total_probes_executed': probe_count,
                'candidate_nodes': len(candidates),
                'probes_per_second': probe_count / probe_time if probe_time > 0 else 0
            }
            
            print(f"  Results:")
            print(f"    Probe execution time: {probe_time:.3f}s")
            print(f"    Total probes executed: {probe_count}")
            print(f"    Probes per second: {probe_count / probe_time:.1f}" if probe_time > 0 else "    Probes per second: ∞")
        
        self.test_results['probe_protocol_scaling'] = results
        return results
    
    def test_memory_efficiency(self, node_count: int = 1000):
        """Test memory usage and cleanup efficiency"""
        print(f"\n=== Testing Memory Efficiency with {node_count} nodes ===")
        
        # Generate large number of nodes
        nodes = self.generate_mock_nodes(node_count - 1)
        
        # Fill performance cache
        print("Filling performance cache...")
        for node_id in list(self.consensus.nodes.keys())[:100]:
            self.consensus.calculate_suitability_score(node_id)
        
        cache_size_before = len(self.consensus.node_performance_cache)
        total_nodes_before = len(self.consensus.nodes)
        
        print(f"Before cleanup:")
        print(f"  Cached performance scores: {cache_size_before}")
        print(f"  Total nodes: {total_nodes_before}")
        
        # Test cleanup
        print("Running cleanup...")
        self.consensus.cleanup_performance_data()
        
        cache_size_after = len(self.consensus.node_performance_cache)
        total_nodes_after = len(self.consensus.nodes)
        
        print(f"After cleanup:")
        print(f"  Cached performance scores: {cache_size_after}")
        print(f"  Total nodes: {total_nodes_after}")
        
        results = {
            'cache_size_before': cache_size_before,
            'cache_size_after': cache_size_after,
            'nodes_before': total_nodes_before,
            'nodes_after': total_nodes_after,
            'cache_cleanup_ratio': (cache_size_before - cache_size_after) / cache_size_before if cache_size_before > 0 else 0
        }
        
        self.test_results['memory_efficiency'] = results
        return results
    
    def run_full_scalability_test(self):
        """Run comprehensive scalability test suite"""
        print("🚀 Starting Quantum Consensus Scalability Testing")
        print("=" * 60)
        
        # Test node counts
        test_scales = [10, 50, 100, 250, 500, 1000]
        
        # Run tests
        start_time = time.time()
        
        try:
            # Test 1: Node selection performance
            self.test_node_selection_performance(test_scales)
            
            # Test 2: Probe protocol scaling
            self.test_probe_protocol_scaling(test_scales[:4])  # Limit for probe tests
            
            # Test 3: Memory efficiency
            self.test_memory_efficiency(1000)
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        total_time = time.time() - start_time
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎉 SCALABILITY TEST RESULTS SUMMARY")
        print("=" * 60)
        
        if 'node_selection_performance' in self.test_results:
            print("\n📊 Node Selection Performance:")
            for count, results in self.test_results['node_selection_performance'].items():
                print(f"  {count:4d} nodes: {results['avg_selection_time']:.3f}s avg, "
                      f"{results['max_selection_time']:.3f}s max")
        
        if 'probe_protocol_scaling' in self.test_results:
            print("\n🔍 Probe Protocol Scaling:")
            for count, results in self.test_results['probe_protocol_scaling'].items():
                print(f"  {count:4d} nodes: {results['probe_execution_time']:.3f}s, "
                      f"{results['total_probes_executed']} probes")
        
        if 'memory_efficiency' in self.test_results:
            print("\n💾 Memory Efficiency:")
            mem_results = self.test_results['memory_efficiency']
            print(f"  Cache cleanup: {mem_results['cache_cleanup_ratio']:.1%}")
            print(f"  Node management: {mem_results['nodes_before']} → {mem_results['nodes_after']} nodes")
        
        print(f"\n⏱️  Total test time: {total_time:.2f} seconds")
        
        # Determine if scaling is successful
        max_selection_time = max(
            results['max_selection_time'] 
            for results in self.test_results.get('node_selection_performance', {}).values()
        ) if 'node_selection_performance' in self.test_results else float('inf')
        
        success = max_selection_time < 5.0  # Selection should complete within 5 seconds
        
        if success:
            print("\n✅ SCALABILITY TEST PASSED")
            print("   System successfully handles 1000+ nodes with good performance!")
        else:
            print("\n⚠️  SCALABILITY TEST NEEDS IMPROVEMENT")
            print(f"   Maximum selection time ({max_selection_time:.3f}s) exceeds threshold (5.0s)")
        
        return success


def main():
    """Run scalability tests"""
    print("Quantum Annealing Consensus - Scalability Testing")
    print("Testing capability to handle 1000+ nodes efficiently")
    print()
    
    tester = ScalabilityTester()
    success = tester.run_full_scalability_test()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
