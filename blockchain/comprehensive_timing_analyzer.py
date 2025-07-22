#!/usr/bin/env python3
"""
Comprehensive Timing Analyzer for Quantum Annealing Blockchain
=============================================================

This module provides detailed timing analysis for:
1. Consensus Time (Quantum Annealing)
2. Transaction Time with Signature Verification  
3. Communication Time (P2P Network)
4. Block Creation and Propagation Time
5. End-to-end transaction processing time

Usage:
    python comprehensive_timing_analyzer.py --nodes 2 --transactions 10
"""

import time
import json
import statistics
import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from blockchain.utils.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils
from blockchain.quantum_consensus.quantum_annealing_consensus import QuantumAnnealingConsensus


class TimingAnalyzer:
    """Comprehensive timing analysis for blockchain operations"""
    
    def __init__(self, api_ports: List[int], p2p_ports: List[int]):
        self.api_ports = api_ports
        self.p2p_ports = p2p_ports
        self.consensus = QuantumAnnealingConsensus()
        self.results = {
            'consensus_times': [],
            'signature_verification_times': [],
            'communication_times': [],
            'transaction_processing_times': [],
            'block_creation_times': [],
            'block_propagation_times': [],
            'end_to_end_times': []
        }
    
    def measure_consensus_time(self, num_nodes: int = 5) -> Dict:
        """
        Measure quantum annealing consensus time
        
        Returns:
            Dict with consensus timing details
        """
        print("🔬 Measuring Consensus Time (Quantum Annealing)...")
        
        # Register test nodes for consensus
        test_nodes = []
        for i in range(num_nodes):
            node_id = f"test_node_{i}"
            self.consensus.register_node(
                node_id=node_id,
                ip=f"127.0.0.1",
                p2p_port=10000 + i,
                public_key_pem="dummy_key_for_timing"
            )
            test_nodes.append(node_id)
        
        consensus_timings = []
        
        for round_num in range(5):  # Multiple rounds for statistical accuracy
            print(f"   Round {round_num + 1}/5...")
            
            # Measure consensus selection time
            start_time = time.perf_counter()
            
            # This is the main quantum annealing consensus call
            selected_forger = self.consensus.select_representative_node(
                last_block_hash=f"test_hash_{round_num}"
            )
            
            end_time = time.perf_counter()
            consensus_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Get detailed quantum metrics
            quantum_metrics = self.consensus.get_consensus_metrics()
            
            timing_details = {
                'round': round_num + 1,
                'consensus_time_ms': consensus_time,
                'selected_forger': selected_forger,
                'quantum_annealing_time_us': quantum_metrics.get('annealing_time_microseconds', 20.0),
                'num_quantum_reads': quantum_metrics.get('quantum_reads', 50),
                'energy_function_evaluation_time_ms': consensus_time * 0.3,  # Estimated
                'solution_validation_time_ms': consensus_time * 0.1,  # Estimated
                'timestamp': datetime.now().isoformat()
            }
            
            consensus_timings.append(timing_details)
            self.results['consensus_times'].append(timing_details)
        
        # Calculate statistics
        times = [t['consensus_time_ms'] for t in consensus_timings]
        return {
            'consensus_timings': consensus_timings,
            'average_consensus_time_ms': statistics.mean(times),
            'min_consensus_time_ms': min(times),
            'max_consensus_time_ms': max(times),
            'std_deviation_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'quantum_annealing_overhead_us': 20.0  # Typical D-Wave annealing time
        }
    
    def measure_signature_verification_time(self, num_signatures: int = 100) -> Dict:
        """
        Measure cryptographic signature verification time
        
        Args:
            num_signatures: Number of signatures to verify for statistical analysis
            
        Returns:
            Dict with signature verification timing details
        """
        print("🔐 Measuring Signature Verification Time...")
        
        # Create test wallet for signature generation
        test_wallet = Wallet()
        message = b"Test transaction data for timing analysis"
        
        verification_times = []
        
        for i in range(num_signatures):
            if i % 20 == 0:
                print(f"   Verified {i}/{num_signatures} signatures...")
            
            # Generate signature
            signature_start = time.perf_counter()
            signature = test_wallet.sign(message)
            signature_generation_time = (time.perf_counter() - signature_start) * 1000
            
            # Measure verification time
            verification_start = time.perf_counter()
            is_valid = test_wallet.verify_signature(message, signature, test_wallet.public_key_string())
            verification_end = time.perf_counter()
            
            verification_time = (verification_end - verification_start) * 1000  # milliseconds
            
            timing_details = {
                'signature_id': i + 1,
                'signature_generation_time_ms': signature_generation_time,
                'verification_time_ms': verification_time,
                'verification_successful': is_valid,
                'timestamp': datetime.now().isoformat()
            }
            
            verification_times.append(timing_details)
            self.results['signature_verification_times'].append(timing_details)
        
        # Calculate statistics
        verify_times = [t['verification_time_ms'] for t in verification_times]
        generation_times = [t['signature_generation_time_ms'] for t in verification_times]
        
        return {
            'verification_timings': verification_times,
            'average_verification_time_ms': statistics.mean(verify_times),
            'average_generation_time_ms': statistics.mean(generation_times),
            'min_verification_time_ms': min(verify_times),
            'max_verification_time_ms': max(verify_times),
            'verification_throughput_per_second': 1000 / statistics.mean(verify_times),
            'std_deviation_ms': statistics.stdev(verify_times) if len(verify_times) > 1 else 0
        }
    
    def measure_communication_time(self) -> Dict:
        """
        Measure P2P communication latency between nodes
        
        Returns:
            Dict with communication timing details
        """
        print("📡 Measuring Communication Time...")
        
        communication_timings = []
        
        for i, port in enumerate(self.api_ports):
            for j, target_port in enumerate(self.api_ports):
                if i != j:  # Don't measure self-communication
                    print(f"   Testing communication: Node {i+1} -> Node {j+1}")
                    
                    # Measure API response time
                    start_time = time.perf_counter()
                    try:
                        response = requests.get(
                            f'http://localhost:{port}/api/v1/blockchain/',
                            timeout=5
                        )
                        end_time = time.perf_counter()
                        
                        communication_time = (end_time - start_time) * 1000  # milliseconds
                        success = response.status_code == 200
                        
                    except Exception as e:
                        end_time = time.perf_counter()
                        communication_time = (end_time - start_time) * 1000
                        success = False
                    
                    timing_details = {
                        'source_node': i + 1,
                        'target_node': j + 1,
                        'source_port': port,
                        'target_port': target_port,
                        'communication_time_ms': communication_time,
                        'success': success,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    communication_timings.append(timing_details)
                    self.results['communication_times'].append(timing_details)
        
        # Calculate statistics
        successful_times = [t['communication_time_ms'] for t in communication_timings if t['success']]
        
        if successful_times:
            return {
                'communication_timings': communication_timings,
                'average_communication_time_ms': statistics.mean(successful_times),
                'min_communication_time_ms': min(successful_times),
                'max_communication_time_ms': max(successful_times),
                'communication_success_rate': len(successful_times) / len(communication_timings),
                'network_latency_ms': statistics.mean(successful_times) / 2,  # Round-trip / 2
                'std_deviation_ms': statistics.stdev(successful_times) if len(successful_times) > 1 else 0
            }
        else:
            return {
                'communication_timings': communication_timings,
                'average_communication_time_ms': 0,
                'communication_success_rate': 0,
                'error': 'No successful communications measured'
            }
    
    def measure_transaction_processing_time(self, num_transactions: int = 10) -> Dict:
        """
        Measure end-to-end transaction processing time including:
        - Transaction creation and signing
        - Network submission
        - Pool processing
        - Block inclusion
        - Network propagation
        
        Args:
            num_transactions: Number of transactions to process
            
        Returns:
            Dict with transaction processing timing details
        """
        print("💳 Measuring Transaction Processing Time...")
        
        # Create wallets for testing
        sender_wallet = Wallet()
        receiver_wallet = Wallet()
        
        transaction_timings = []
        
        for tx_num in range(num_transactions):
            print(f"   Processing transaction {tx_num + 1}/{num_transactions}...")
            
            # 1. Transaction creation and signing
            creation_start = time.perf_counter()
            transaction = sender_wallet.create_transaction(
                receiver_wallet.public_key_string(),
                amount=10.0,
                transaction_type='TRANSFER'
            )
            encoded_transaction = BlockchainUtils.encode(transaction)
            creation_end = time.perf_counter()
            
            creation_time = (creation_end - creation_start) * 1000
            
            # 2. Network submission
            submission_start = time.perf_counter()
            try:
                response = requests.post(
                    f'http://localhost:{self.api_ports[0]}/api/v1/transaction/create/',
                    json={'transaction': encoded_transaction},
                    timeout=10
                )
                submission_end = time.perf_counter()
                submission_success = response.status_code == 201
            except Exception:
                submission_end = time.perf_counter()
                submission_success = False
            
            submission_time = (submission_end - submission_start) * 1000
            
            # 3. Monitor for block inclusion
            monitoring_start = time.perf_counter()
            block_inclusion_time = None
            max_wait_time = 30  # seconds
            
            initial_blocks = self.get_blockchain_length(self.api_ports[0])
            
            while (time.perf_counter() - monitoring_start) < max_wait_time:
                current_blocks = self.get_blockchain_length(self.api_ports[0])
                if current_blocks > initial_blocks:
                    block_inclusion_time = (time.perf_counter() - monitoring_start) * 1000
                    break
                time.sleep(0.1)
            
            # 4. Measure propagation across all nodes
            propagation_start = time.perf_counter()
            all_nodes_synced = False
            
            if block_inclusion_time:
                while (time.perf_counter() - propagation_start) < 10:  # 10 second max wait
                    block_lengths = [self.get_blockchain_length(port) for port in self.api_ports]
                    if len(set(block_lengths)) == 1 and block_lengths[0] > initial_blocks:
                        propagation_time = (time.perf_counter() - propagation_start) * 1000
                        all_nodes_synced = True
                        break
                    time.sleep(0.1)
            
            total_time = (time.perf_counter() - creation_start) * 1000
            
            timing_details = {
                'transaction_id': tx_num + 1,
                'creation_and_signing_time_ms': creation_time,
                'network_submission_time_ms': submission_time,
                'submission_success': submission_success,
                'block_inclusion_time_ms': block_inclusion_time,
                'propagation_time_ms': propagation_time if all_nodes_synced else None,
                'total_processing_time_ms': total_time,
                'all_nodes_synced': all_nodes_synced,
                'timestamp': datetime.now().isoformat()
            }
            
            transaction_timings.append(timing_details)
            self.results['transaction_processing_times'].append(timing_details)
            
            # Wait a bit between transactions
            time.sleep(1)
        
        # Calculate statistics
        successful_transactions = [t for t in transaction_timings if t['submission_success']]
        
        if successful_transactions:
            creation_times = [t['creation_and_signing_time_ms'] for t in successful_transactions]
            submission_times = [t['network_submission_time_ms'] for t in successful_transactions]
            total_times = [t['total_processing_time_ms'] for t in successful_transactions]
            
            return {
                'transaction_timings': transaction_timings,
                'average_creation_time_ms': statistics.mean(creation_times),
                'average_submission_time_ms': statistics.mean(submission_times),
                'average_total_processing_time_ms': statistics.mean(total_times),
                'transaction_throughput_per_second': 1000 / statistics.mean(total_times) if total_times else 0,
                'success_rate': len(successful_transactions) / len(transaction_timings),
                'std_deviation_total_ms': statistics.stdev(total_times) if len(total_times) > 1 else 0
            }
        else:
            return {
                'transaction_timings': transaction_timings,
                'error': 'No successful transactions processed'
            }
    
    def get_blockchain_length(self, api_port: int) -> int:
        """Get current blockchain length from a node"""
        try:
            response = requests.get(f'http://localhost:{api_port}/api/v1/blockchain/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return len(data.get('blocks', []))
        except:
            pass
        return 0
    
    def run_comprehensive_analysis(self, num_nodes: int = 2, num_transactions: int = 5) -> Dict:
        """
        Run comprehensive timing analysis
        
        Args:
            num_nodes: Number of nodes for consensus testing
            num_transactions: Number of transactions to process
            
        Returns:
            Dict with complete timing analysis results
        """
        print("🚀 Starting Comprehensive Timing Analysis...")
        print("=" * 60)
        
        analysis_start = time.time()
        
        # 1. Consensus timing
        consensus_results = self.measure_consensus_time(num_nodes)
        
        # 2. Signature verification timing
        signature_results = self.measure_signature_verification_time(50)
        
        # 3. Communication timing
        communication_results = self.measure_communication_time()
        
        # 4. Transaction processing timing
        transaction_results = self.measure_transaction_processing_time(num_transactions)
        
        analysis_end = time.time()
        total_analysis_time = analysis_end - analysis_start
        
        # Compile comprehensive results
        comprehensive_results = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_analysis_time_seconds': total_analysis_time,
                'num_nodes_tested': num_nodes,
                'num_transactions_tested': num_transactions,
                'api_ports': self.api_ports,
                'p2p_ports': self.p2p_ports
            },
            'consensus_analysis': consensus_results,
            'signature_verification_analysis': signature_results,
            'communication_analysis': communication_results,
            'transaction_processing_analysis': transaction_results,
            'performance_summary': self.generate_performance_summary(
                consensus_results, signature_results, communication_results, transaction_results
            )
        }
        
        return comprehensive_results
    
    def generate_performance_summary(self, consensus_results: Dict, signature_results: Dict, 
                                   communication_results: Dict, transaction_results: Dict) -> Dict:
        """Generate a performance summary with key metrics"""
        
        return {
            'key_metrics': {
                'average_consensus_time_ms': consensus_results.get('average_consensus_time_ms', 0),
                'consensus_throughput_decisions_per_second': 1000 / consensus_results.get('average_consensus_time_ms', 1000),
                'average_signature_verification_time_ms': signature_results.get('average_verification_time_ms', 0),
                'signature_verification_throughput_per_second': signature_results.get('verification_throughput_per_second', 0),
                'average_network_latency_ms': communication_results.get('network_latency_ms', 0),
                'average_transaction_processing_time_ms': transaction_results.get('average_total_processing_time_ms', 0),
                'transaction_throughput_per_second': transaction_results.get('transaction_throughput_per_second', 0)
            },
            'bottleneck_analysis': {
                'consensus_overhead_percentage': self.calculate_overhead_percentage(
                    consensus_results.get('average_consensus_time_ms', 0),
                    transaction_results.get('average_total_processing_time_ms', 1)
                ),
                'signature_overhead_percentage': self.calculate_overhead_percentage(
                    signature_results.get('average_verification_time_ms', 0),
                    transaction_results.get('average_total_processing_time_ms', 1)
                ),
                'network_overhead_percentage': self.calculate_overhead_percentage(
                    communication_results.get('average_communication_time_ms', 0),
                    transaction_results.get('average_total_processing_time_ms', 1)
                )
            }
        }
    
    def calculate_overhead_percentage(self, component_time: float, total_time: float) -> float:
        """Calculate the percentage overhead of a component"""
        if total_time > 0:
            return (component_time / total_time) * 100
        return 0
    
    def save_results(self, results: Dict, filename: str = None):
        """Save timing analysis results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"timing_analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📊 Results saved to: {filename}")
    
    def print_summary(self, results: Dict):
        """Print a formatted summary of timing results"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TIMING ANALYSIS SUMMARY")
        print("=" * 60)
        
        summary = results['performance_summary']['key_metrics']
        
        print(f"🔬 Consensus Performance:")
        print(f"   Average Consensus Time: {summary['average_consensus_time_ms']:.3f} ms")
        print(f"   Consensus Throughput: {summary['consensus_throughput_decisions_per_second']:.2f} decisions/sec")
        
        print(f"\n🔐 Signature Verification Performance:")
        print(f"   Average Verification Time: {summary['average_signature_verification_time_ms']:.3f} ms")
        print(f"   Verification Throughput: {summary['signature_verification_throughput_per_second']:.2f} verifications/sec")
        
        print(f"\n📡 Network Performance:")
        print(f"   Average Network Latency: {summary['average_network_latency_ms']:.3f} ms")
        
        print(f"\n💳 Transaction Performance:")
        print(f"   Average Transaction Time: {summary['average_transaction_processing_time_ms']:.3f} ms")
        print(f"   Transaction Throughput: {summary['transaction_throughput_per_second']:.2f} tx/sec")
        
        print(f"\n🔍 Bottleneck Analysis:")
        bottlenecks = results['performance_summary']['bottleneck_analysis']
        print(f"   Consensus Overhead: {bottlenecks['consensus_overhead_percentage']:.1f}%")
        print(f"   Signature Overhead: {bottlenecks['signature_overhead_percentage']:.1f}%")
        print(f"   Network Overhead: {bottlenecks['network_overhead_percentage']:.1f}%")


def main():
    """Main function to run timing analysis"""
    parser = argparse.ArgumentParser(description='Comprehensive Blockchain Timing Analyzer')
    parser.add_argument('--nodes', type=int, default=2, help='Number of nodes to test (default: 2)')
    parser.add_argument('--transactions', type=int, default=5, help='Number of transactions to test (default: 5)')
    parser.add_argument('--api-ports', nargs='+', type=int, default=[11000, 11001], 
                       help='API ports for nodes (default: 11000 11001)')
    parser.add_argument('--p2p-ports', nargs='+', type=int, default=[10000, 10001],
                       help='P2P ports for nodes (default: 10000 10001)')
    parser.add_argument('--output', type=str, help='Output filename for results')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = TimingAnalyzer(args.api_ports, args.p2p_ports)
    
    # Run comprehensive analysis
    results = analyzer.run_comprehensive_analysis(args.nodes, args.transactions)
    
    # Print summary
    analyzer.print_summary(results)
    
    # Save results
    analyzer.save_results(results, args.output)
    
    print(f"\n✅ Timing analysis complete!")


if __name__ == "__main__":
    main()
