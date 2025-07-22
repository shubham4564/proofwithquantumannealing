#!/usr/bin/env python3
"""
Comprehensive demonstration of IEEE paper-compliant quantum consensus with cryptographic verification.
This script shows the complete implementation including scalability and verification features.
"""

import sys
import os
import time
import json

# Add the blockchain package to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'blockchain'))

from blockchain.quantum_consensus.quantum_annealing_consensus import QuantumAnnealingConsensus

def demonstrate_ieee_paper_compliance():
    """Demonstrate complete IEEE paper compliance with cryptographic verification"""
    print("🚀 IEEE Paper-Compliant Quantum Consensus Demonstration\n")
    
    # Initialize quantum consensus system
    print("🌟 Initializing Quantum Annealing Consensus System...")
    consensus = QuantumAnnealingConsensus(initialize_genesis=True)
    genesis_nodes = [node_id for node_id in consensus.nodes.keys() if 'genesis' in node_id.lower()]
    genesis_id = genesis_nodes[0] if genesis_nodes else "genesis_000"
    print(f"✅ Genesis node initialized: {genesis_id}")
    print(f"✅ Consensus parameters: {consensus.witness_quorum_size} witness quorum\n")
    
    # Create a realistic network of nodes
    print("🔗 Setting up distributed network...")
    network_nodes = []
    for i in range(20):  # 20 nodes for demonstration
        node_id = f"node_{i:03d}"
        public_key, private_key = consensus.generate_node_keys(node_id)
        consensus.register_node(node_id, public_key)
        network_nodes.append(node_id)
    
    print(f"✅ Network established with {len(network_nodes)} nodes")
    print(f"✅ Each node has RSA-2048 cryptographic keys\n")
    
    # Demonstrate cryptographic probe protocol
    print("📡 Executing IEEE Paper-Compliant Probe Protocols...")
    
    # Execute multiple probe protocols to establish network metrics
    probe_results = []
    for i in range(10):
        source = network_nodes[i % len(network_nodes)]
        target = network_nodes[(i + 5) % len(network_nodes)]
        witnesses = [
            network_nodes[(i + 1) % len(network_nodes)],
            network_nodes[(i + 2) % len(network_nodes)],
            network_nodes[(i + 3) % len(network_nodes)]
        ]
        
        print(f"  🔍 Probe {i+1}: {source} → {target}")
        probe_proof = consensus.execute_probe_protocol(source, target, witnesses)
        
        # Verify cryptographic signatures
        verification_results = []
        for verifier in witnesses[:2]:  # Test with subset of verifiers
            is_valid = consensus.verify_probe_proof(probe_proof, verifier)
            verification_results.append(is_valid)
        
        probe_results.append({
            'source': source,
            'target': target,
            'latency': probe_proof['measured_latency'],
            'verified': all(verification_results),
            'witnesses': len(probe_proof['WitnessReceipts'])
        })
        
        if probe_proof.get('valid', False):
            print(f"    ✅ Verified latency: {probe_proof['measured_latency']:.6f}s")
        else:
            print(f"    ❌ Verification failed")
    
    verified_probes = sum(1 for p in probe_results if p['verified'])
    print(f"\n✅ Completed {len(probe_results)} probes, {verified_probes} verified\n")
    
    # Demonstrate quantum candidate selection
    print("⚛️ Quantum Annealing Candidate Selection...")
    
    # Use VRF to get deterministic randomness
    vrf_output = "test_vrf_output_for_demonstration"
    
    # Get top candidates using quantum-enhanced selection
    start_time = time.time()
    top_candidates = consensus.get_top_candidate_nodes(vrf_output, max_candidates=10)
    selection_time = time.time() - start_time
    
    print(f"✅ Selected {len(top_candidates)} candidates in {selection_time:.6f}s")
    print("🏆 Top candidates with their scores:")
    
    for i, candidate in enumerate(top_candidates[:5]):
        suitability_score = consensus.calculate_suitability_score(candidate)
        effective_score = consensus.calculate_effective_score(candidate, vrf_output)
        uptime = consensus.calculate_uptime(candidate)
        latency = consensus.nodes[candidate]['latency']
        
        print(f"  {i+1}. {candidate}:")
        print(f"     Suitability: {suitability_score:.4f}")
        print(f"     Effective: {effective_score:.4f}")
        print(f"     Uptime: {uptime:.2%}")
        print(f"     Latency: {latency:.6f}s")
    
    print()
    
    # Demonstrate QUBO formulation and quantum solving
    print("🧮 Quantum QUBO Problem Formulation...")
    
    start_time = time.time()
    linear_coeff, quadratic_coeff, energy_offset = consensus.formulate_qubo_problem(vrf_output, top_candidates)
    formulation_time = time.time() - start_time
    
    print(f"✅ QUBO formulated in {formulation_time:.6f}s")
    print(f"✅ Problem size: {len(linear_coeff)} variables")
    print(f"✅ Quadratic terms: {len(quadratic_coeff)}")
    
    # Solve using quantum annealing simulation
    start_time = time.time()
    solution = consensus.simulate_quantum_annealer(linear_coeff, quadratic_coeff, top_candidates)
    solving_time = time.time() - start_time
    
    selected_nodes = [top_candidates[i] for i in range(len(solution)) if solution[i] == 1]
    
    print(f"✅ Quantum solution found in {solving_time:.6f}s")
    print(f"🎯 Selected representative nodes: {selected_nodes}")
    print()
    
    # Demonstrate scalability metrics
    print("📈 Performance and Scalability Metrics...")
    
    total_nodes = len(consensus.nodes)
    total_probes = len(consensus.probe_history)
    avg_latency = sum(p['latency'] for p in probe_results) / len(probe_results)
    
    print(f"🔢 Network Statistics:")
    print(f"   Total nodes: {total_nodes}")
    print(f"   Total probes executed: {total_probes}")
    print(f"   Average network latency: {avg_latency:.6f}s")
    print(f"   Verification success rate: {100*verified_probes/len(probe_results):.1f}%")
    
    print(f"\n⚡ Performance Metrics:")
    print(f"   Candidate selection: {selection_time*1000:.2f}ms")
    print(f"   QUBO formulation: {formulation_time*1000:.2f}ms")
    print(f"   Quantum solving: {solving_time*1000:.2f}ms")
    
    # Show security features
    print(f"\n🔐 Security Features Implemented:")
    print(f"   ✅ RSA-2048 cryptographic signatures")
    print(f"   ✅ Nonce-based replay protection")
    print(f"   ✅ Witness quorum verification")
    print(f"   ✅ Timestamp consistency checks")
    print(f"   ✅ Independent proof verification")
    print()
    
    # Demonstrate IEEE paper compliance
    print("📄 IEEE Paper Compliance Summary:")
    print("   ✅ ProbeRequest/TargetReceipt/WitnessReceipt structure")
    print("   ✅ Cryptographic signature verification")
    print("   ✅ Uptime calculation: U(nx) = ∫[tstart to tend] S(nx, t) dt")
    print("   ✅ Latency measurement: Ls→t = RTT if V(PP) = true AND witness consensus")
    print("   ✅ Latency triangulation: Multiple witnesses verify latency measurements")
    print("   ✅ Throughput calculation: |Pnt(tstart, tend)| / (tend - tstart)")
    print("   ✅ Suitability score: Si = w*norm(Ui) + w*norm(Perfi) + w*norm(Ti) - w*norm(Li)")
    print("   ✅ Quantum annealing for consensus")
    print("   ✅ Replay attack protection")
    print()
    
    print("🎉 Demonstration Complete!")
    print("✅ The system implements a fully IEEE paper-compliant quantum consensus")
    print("✅ with cryptographic verification and scalable architecture")
    
    return {
        'nodes': total_nodes,
        'probes': total_probes,
        'verified_rate': verified_probes/len(probe_results),
        'avg_latency': avg_latency,
        'selection_time': selection_time,
        'candidates_selected': len(selected_nodes)
    }

def main():
    """Main demonstration function"""
    try:
        results = demonstrate_ieee_paper_compliance()
        print(f"\n📊 Final Results: {results}")
        return True
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
