#!/usr/bin/env python3
"""
Direct Code Timing Measurements for Quantum Annealing Blockchain
================================================================

This module provides direct code-level timing measurements for:
1. Consensus Time (Quantum Annealing Algorithm)
2. Transaction Time with Signature Verification
3. Communication Time (P2P Network)

Each function can be called independently to measure specific components.
"""

import time
import json
import requests
from typing import Dict, List, Tuple
from blockchain.utils.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils
from blockchain.quantum_consensus.quantum_annealing_consensus import QuantumAnnealingConsensus


class DirectTimingMeasurements:
    """Direct timing measurements for blockchain components"""
    
    @staticmethod
    def measure_consensus_time_direct(node_ids: List[str], last_block_hash: str = "test_hash") -> Dict:
        """
        Direct measurement of quantum annealing consensus algorithm time
        
        Args:
            node_ids: List of node IDs to participate in consensus
            last_block_hash: Hash of the last block for consensus seed
            
        Returns:
            Dict with detailed consensus timing breakdown
        """
        print("🔬 Direct Consensus Time Measurement...")
        
        # Initialize quantum consensus
        consensus = QuantumAnnealingConsensus()
        
        # Register nodes for consensus
        for i, node_id in enumerate(node_ids):
            consensus.register_node(
                node_id=node_id,
                ip="127.0.0.1",
                p2p_port=10000 + i,
                public_key_pem="dummy_key_for_timing"
            )
        
        # Measure consensus components
        timing_breakdown = {}
        
        # 1. Total consensus time
        start_total = time.perf_counter()
        
        # 2. Node eligibility calculation time
        start_eligibility = time.perf_counter()
        eligible_nodes = []
        for node_id in node_ids:
            if consensus.is_node_eligible_for_consensus(node_id):
                eligible_nodes.append(node_id)
        eligibility_time = (time.perf_counter() - start_eligibility) * 1000
        
        # 3. Quantum annealing problem formulation time
        start_formulation = time.perf_counter()
        
        # Calculate node scores (suitability for forging)
        node_scores = {}
        for node_id in eligible_nodes:
            node_scores[node_id] = consensus.calculate_node_suitability_score(node_id)
        
        formulation_time = (time.perf_counter() - start_formulation) * 1000
        
        # 4. Quantum annealing execution time
        start_quantum = time.perf_counter()
        
        # Execute the quantum annealing selection
        selected_forger = consensus.select_representative_node(last_block_hash)
        
        quantum_time = (time.perf_counter() - start_quantum) * 1000
        
        total_time = (time.perf_counter() - start_total) * 1000
        
        # Get quantum metrics
        quantum_metrics = consensus.get_consensus_metrics()
        
        timing_breakdown = {
            'total_consensus_time_ms': total_time,
            'node_eligibility_check_time_ms': eligibility_time,
            'problem_formulation_time_ms': formulation_time,
            'quantum_annealing_execution_time_ms': quantum_time,
            'quantum_annealing_time_microseconds': quantum_metrics.get('annealing_time_microseconds', 20.0),
            'num_quantum_reads': quantum_metrics.get('quantum_reads', 50),
            'eligible_nodes_count': len(eligible_nodes),
            'selected_forger': selected_forger,
            'node_scores': node_scores,
            'overhead_breakdown': {
                'eligibility_percentage': (eligibility_time / total_time) * 100,
                'formulation_percentage': (formulation_time / total_time) * 100,
                'quantum_execution_percentage': (quantum_time / total_time) * 100
            }
        }
        
        return timing_breakdown
    
    @staticmethod
    def measure_signature_verification_time_direct(message: bytes = None, num_iterations: int = 10) -> Dict:
        """
        Direct measurement of signature generation and verification time
        
        Args:
            message: Message to sign (default: test message)
            num_iterations: Number of iterations for statistical accuracy
            
        Returns:
            Dict with detailed signature timing breakdown
        """
        print("🔐 Direct Signature Verification Time Measurement...")
        
        if message is None:
            message = b"Test transaction data for direct timing measurement"
        
        # Create wallet for signing
        wallet = Wallet()
        
        timing_results = {
            'individual_measurements': [],
            'statistics': {}
        }
        
        generation_times = []
        verification_times = []
        
        for i in range(num_iterations):
            # Measure signature generation
            start_generation = time.perf_counter()
            signature = wallet.sign(message)
            generation_time = (time.perf_counter() - start_generation) * 1000  # ms
            
            # Measure signature verification
            start_verification = time.perf_counter()
            is_valid = wallet.verify_signature(message, signature, wallet.public_key_string())
            verification_time = (time.perf_counter() - start_verification) * 1000  # ms
            
            measurement = {
                'iteration': i + 1,
                'signature_generation_time_ms': generation_time,
                'signature_verification_time_ms': verification_time,
                'verification_success': is_valid,
                'total_crypto_time_ms': generation_time + verification_time
            }
            
            timing_results['individual_measurements'].append(measurement)
            generation_times.append(generation_time)
            verification_times.append(verification_time)
        
        # Calculate statistics
        timing_results['statistics'] = {
            'average_generation_time_ms': sum(generation_times) / len(generation_times),
            'average_verification_time_ms': sum(verification_times) / len(verification_times),
            'min_generation_time_ms': min(generation_times),
            'max_generation_time_ms': max(generation_times),
            'min_verification_time_ms': min(verification_times),
            'max_verification_time_ms': max(verification_times),
            'generation_throughput_per_second': 1000 / (sum(generation_times) / len(generation_times)),
            'verification_throughput_per_second': 1000 / (sum(verification_times) / len(verification_times)),
            'crypto_overhead_per_transaction_ms': (sum(generation_times) + sum(verification_times)) / len(generation_times)
        }
        
        return timing_results
    
    @staticmethod
    def measure_communication_time_direct(source_port: int, target_ports: List[int], 
                                        num_requests: int = 5) -> Dict:
        """
        Direct measurement of P2P communication time
        
        Args:
            source_port: Source API port for requests
            target_ports: List of target API ports
            num_requests: Number of requests per target for statistical accuracy
            
        Returns:
            Dict with detailed communication timing breakdown
        """
        print("📡 Direct Communication Time Measurement...")
        
        timing_results = {
            'communication_matrix': [],
            'statistics': {}
        }
        
        all_response_times = []
        
        for target_port in target_ports:
            if target_port == source_port:
                continue  # Skip self-communication
            
            port_measurements = []
            
            for request_num in range(num_requests):
                # Measure different types of communication
                
                # 1. Blockchain status request
                start_blockchain = time.perf_counter()
                try:
                    response = requests.get(
                        f'http://localhost:{target_port}/api/v1/blockchain/',
                        timeout=5
                    )
                    blockchain_time = (time.perf_counter() - start_blockchain) * 1000
                    blockchain_success = response.status_code == 200
                except Exception:
                    blockchain_time = (time.perf_counter() - start_blockchain) * 1000
                    blockchain_success = False
                
                # 2. Transaction pool request  
                start_pool = time.perf_counter()
                try:
                    response = requests.get(
                        f'http://localhost:{target_port}/api/v1/transaction/pool/',
                        timeout=5
                    )
                    pool_time = (time.perf_counter() - start_pool) * 1000
                    pool_success = response.status_code == 200
                except Exception:
                    pool_time = (time.perf_counter() - start_pool) * 1000
                    pool_success = False
                
                # 3. Quantum metrics request
                start_metrics = time.perf_counter()
                try:
                    response = requests.get(
                        f'http://localhost:{target_port}/api/v1/blockchain/quantum-metrics/',
                        timeout=5
                    )
                    metrics_time = (time.perf_counter() - start_metrics) * 1000
                    metrics_success = response.status_code == 200
                except Exception:
                    metrics_time = (time.perf_counter() - start_metrics) * 1000
                    metrics_success = False
                
                measurement = {
                    'source_port': source_port,
                    'target_port': target_port,
                    'request_number': request_num + 1,
                    'blockchain_request_time_ms': blockchain_time,
                    'transaction_pool_request_time_ms': pool_time,
                    'quantum_metrics_request_time_ms': metrics_time,
                    'blockchain_success': blockchain_success,
                    'pool_success': pool_success,
                    'metrics_success': metrics_success,
                    'average_request_time_ms': (blockchain_time + pool_time + metrics_time) / 3
                }
                
                port_measurements.append(measurement)
                all_response_times.append(measurement['average_request_time_ms'])
            
            timing_results['communication_matrix'].append({
                'target_port': target_port,
                'measurements': port_measurements,
                'port_statistics': {
                    'average_response_time_ms': sum(m['average_request_time_ms'] for m in port_measurements) / len(port_measurements),
                    'min_response_time_ms': min(m['average_request_time_ms'] for m in port_measurements),
                    'max_response_time_ms': max(m['average_request_time_ms'] for m in port_measurements),
                    'success_rate': sum(1 for m in port_measurements if m['blockchain_success']) / len(port_measurements)
                }
            })
        
        # Overall statistics
        if all_response_times:
            timing_results['statistics'] = {
                'overall_average_response_time_ms': sum(all_response_times) / len(all_response_times),
                'overall_min_response_time_ms': min(all_response_times),
                'overall_max_response_time_ms': max(all_response_times),
                'network_latency_estimate_ms': (sum(all_response_times) / len(all_response_times)) / 2,  # Round-trip / 2
                'communication_throughput_requests_per_second': 1000 / (sum(all_response_times) / len(all_response_times)),
                'total_communication_pairs_tested': len(timing_results['communication_matrix'])
            }
        
        return timing_results
    
    @staticmethod
    def measure_transaction_creation_time_direct(sender_wallet: Wallet = None, 
                                               receiver_public_key: str = None,
                                               amount: float = 10.0) -> Dict:
        """
        Direct measurement of transaction creation and encoding time
        
        Args:
            sender_wallet: Wallet for transaction creation
            receiver_public_key: Receiver's public key
            amount: Transaction amount
            
        Returns:
            Dict with detailed transaction creation timing
        """
        print("💳 Direct Transaction Creation Time Measurement...")
        
        # Create wallets if not provided
        if sender_wallet is None:
            sender_wallet = Wallet()
        
        if receiver_public_key is None:
            receiver_wallet = Wallet()
            receiver_public_key = receiver_wallet.public_key_string()
        
        timing_breakdown = {}
        
        # 1. Transaction object creation time
        start_creation = time.perf_counter()
        transaction = sender_wallet.create_transaction(
            receiver_public_key, 
            amount, 
            transaction_type='TRANSFER'
        )
        creation_time = (time.perf_counter() - start_creation) * 1000
        
        # 2. Transaction encoding time
        start_encoding = time.perf_counter()
        encoded_transaction = BlockchainUtils.encode(transaction)
        encoding_time = (time.perf_counter() - start_encoding) * 1000
        
        # 3. Transaction size calculation
        transaction_size = len(encoded_transaction.encode('utf-8'))
        
        timing_breakdown = {
            'transaction_creation_time_ms': creation_time,
            'transaction_encoding_time_ms': encoding_time,
            'total_transaction_preparation_time_ms': creation_time + encoding_time,
            'transaction_size_bytes': transaction_size,
            'encoding_efficiency_bytes_per_ms': transaction_size / encoding_time if encoding_time > 0 else 0,
            'transaction_details': {
                'amount': amount,
                'type': 'TRANSFER',
                'sender_id': sender_wallet.public_key_string()[:16] + '...',
                'receiver_id': receiver_public_key[:16] + '...'
            }
        }
        
        return timing_breakdown


def run_all_direct_measurements(node_ids: List[str] = None, api_ports: List[int] = None) -> Dict:
    """
    Run all direct timing measurements
    
    Args:
        node_ids: List of node IDs for consensus testing
        api_ports: List of API ports for communication testing
        
    Returns:
        Dict with all timing measurements
    """
    print("🚀 Running All Direct Timing Measurements...")
    print("=" * 50)
    
    if node_ids is None:
        node_ids = [f"test_node_{i}" for i in range(3)]
    
    if api_ports is None:
        api_ports = [11000, 11001]
    
    all_results = {}
    
    # 1. Consensus Time
    print("\n1. Measuring Consensus Time...")
    all_results['consensus_timing'] = DirectTimingMeasurements.measure_consensus_time_direct(node_ids)
    
    # 2. Signature Verification Time
    print("\n2. Measuring Signature Verification Time...")
    all_results['signature_timing'] = DirectTimingMeasurements.measure_signature_verification_time_direct()
    
    # 3. Communication Time
    print("\n3. Measuring Communication Time...")
    all_results['communication_timing'] = DirectTimingMeasurements.measure_communication_time_direct(
        api_ports[0], api_ports
    )
    
    # 4. Transaction Creation Time
    print("\n4. Measuring Transaction Creation Time...")
    all_results['transaction_creation_timing'] = DirectTimingMeasurements.measure_transaction_creation_time_direct()
    
    return all_results


def print_direct_timing_summary(results: Dict):
    """Print formatted summary of direct timing measurements"""
    print("\n" + "=" * 50)
    print("📊 DIRECT TIMING MEASUREMENTS SUMMARY")
    print("=" * 50)
    
    # Consensus Summary
    if 'consensus_timing' in results:
        consensus = results['consensus_timing']
        print(f"\n🔬 Consensus Performance:")
        print(f"   Total Consensus Time: {consensus['total_consensus_time_ms']:.3f} ms")
        print(f"   Quantum Annealing Time: {consensus['quantum_annealing_time_microseconds']:.1f} μs")
        print(f"   Eligible Nodes: {consensus['eligible_nodes_count']}")
        print(f"   Selected Forger: {consensus['selected_forger']}")
    
    # Signature Summary
    if 'signature_timing' in results:
        signature = results['signature_timing']['statistics']
        print(f"\n🔐 Signature Performance:")
        print(f"   Average Generation Time: {signature['average_generation_time_ms']:.3f} ms")
        print(f"   Average Verification Time: {signature['average_verification_time_ms']:.3f} ms")
        print(f"   Verification Throughput: {signature['verification_throughput_per_second']:.2f} verifications/sec")
    
    # Communication Summary
    if 'communication_timing' in results and 'statistics' in results['communication_timing']:
        communication = results['communication_timing']['statistics']
        print(f"\n📡 Communication Performance:")
        print(f"   Average Response Time: {communication['overall_average_response_time_ms']:.3f} ms")
        print(f"   Network Latency Estimate: {communication['network_latency_estimate_ms']:.3f} ms")
        print(f"   Communication Throughput: {communication['communication_throughput_requests_per_second']:.2f} req/sec")
    
    # Transaction Creation Summary
    if 'transaction_creation_timing' in results:
        transaction = results['transaction_creation_timing']
        print(f"\n💳 Transaction Creation Performance:")
        print(f"   Creation Time: {transaction['transaction_creation_time_ms']:.3f} ms")
        print(f"   Encoding Time: {transaction['transaction_encoding_time_ms']:.3f} ms")
        print(f"   Total Preparation Time: {transaction['total_transaction_preparation_time_ms']:.3f} ms")
        print(f"   Transaction Size: {transaction['transaction_size_bytes']} bytes")


if __name__ == "__main__":
    # Example usage
    node_ids = ["node_1", "node_2", "node_3"]
    api_ports = [11000, 11001]
    
    results = run_all_direct_measurements(node_ids, api_ports)
    print_direct_timing_summary(results)
    
    # Save results
    with open("direct_timing_measurements.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to: direct_timing_measurements.json")
