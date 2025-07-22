#!/usr/bin/env python3
"""
Multi-Node Quantum Annealing Consensus Test Suite

This script sets up multiple blockchain nodes to test:
1. Transaction processing across multiple nodes
2. Quantum annealing consensus performance
3. Block timing and transaction throughput
4. Network synchronization and validation

Usage:
    python multi_node_test.py --nodes 4 --transactions 50 --duration 300
"""

import os
import sys
import json
import time
import requests
import threading
import argparse
import statistics
from datetime import datetime
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

# Add the parent directory to Python path to find blockchain modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from blockchain.transaction.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils


class NodeManager:
    """Manages multiple blockchain nodes for testing"""
    
    def __init__(self, num_nodes: int = 3):
        self.num_nodes = num_nodes
        self.nodes = []
        self.wallets = []
        self.metrics = {
            'transactions': [],
            'blocks': [],
            'consensus_times': [],
            'network_delays': [],
            'throughput_data': []
        }
        
        # Base ports for nodes
        self.base_node_port = 8000
        self.base_api_port = 8050
        
    def create_test_wallets(self) -> List[Wallet]:
        """Create test wallets for transactions"""
        print("🔑 Creating test wallets...")
        
        # Create exchange wallet (for initial funding)
        exchange = Wallet()
        
        # Create user wallets
        wallets = []
        for i in range(self.num_nodes + 2):  # Extra wallets for testing
            wallet = Wallet()
            wallets.append(wallet)
            print(f"  ✓ Wallet {i+1}: {wallet.public_key_string()[:20]}...")
        
        self.wallets = [exchange] + wallets
        return self.wallets
    
    def wait_for_nodes(self, timeout: int = 30) -> bool:
        """Wait for all nodes to be ready"""
        print(f"⏳ Waiting for {self.num_nodes} nodes to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            ready_count = 0
            
            for i in range(self.num_nodes):
                try:
                    api_port = self.base_api_port + i
                    response = requests.get(f"http://localhost:{api_port}/api/v1/blockchain/", timeout=2)
                    if response.status_code == 200:
                        ready_count += 1
                except:
                    pass
            
            if ready_count == self.num_nodes:
                print(f"  ✅ All {self.num_nodes} nodes are ready!")
                return True
            
            print(f"  📡 {ready_count}/{self.num_nodes} nodes ready...")
            time.sleep(2)
        
        print(f"  ❌ Timeout waiting for nodes to be ready")
        return False
    
    def post_transaction(self, sender: Wallet, receiver: Wallet, amount: int, tx_type: str, node_id: int = 0) -> Dict:
        """Post a transaction to a specific node"""
        try:
            transaction = sender.create_transaction(receiver.public_key_string(), amount, tx_type)
            api_port = self.base_api_port + node_id
            url = f"http://localhost:{api_port}/api/v1/transaction/create/"
            package = {"transaction": BlockchainUtils.encode(transaction)}
            
            start_time = time.time()
            response = requests.post(url, json=package, timeout=10)
            end_time = time.time()
            
            return {
                'success': response.status_code == 200,
                'response_time': end_time - start_time,
                'status_code': response.status_code,
                'timestamp': start_time,
                'tx_type': tx_type,
                'amount': amount,
                'node_id': node_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': time.time(),
                'tx_type': tx_type,
                'amount': amount,
                'node_id': node_id
            }
    
    def get_blockchain_state(self, node_id: int = 0) -> Dict:
        """Get blockchain state from a specific node"""
        try:
            api_port = self.base_api_port + node_id
            response = requests.get(f"http://localhost:{api_port}/api/v1/blockchain/", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error getting blockchain state from node {node_id}: {e}")
        return {}
    
    def get_quantum_metrics(self, node_id: int = 0) -> Dict:
        """Get quantum annealing consensus metrics"""
        try:
            api_port = self.base_api_port + node_id
            response = requests.get(f"http://localhost:{api_port}/api/v1/blockchain/quantum-metrics/", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error getting quantum metrics from node {node_id}: {e}")
        return {}
    
    def fund_wallets(self) -> bool:
        """Fund test wallets with initial tokens"""
        print("💰 Funding test wallets...")
        
        exchange = self.wallets[0]
        
        # Fund each wallet
        for i, wallet in enumerate(self.wallets[1:], 1):
            result = self.post_transaction(exchange, wallet, 1000, "EXCHANGE", 0)
            if result['success']:
                print(f"  ✓ Funded wallet {i}: 1000 tokens")
            else:
                print(f"  ❌ Failed to fund wallet {i}: {result.get('error', 'Unknown error')}")
                return False
            time.sleep(0.5)  # Small delay between transactions
        
        return True
    
    def setup_quantum_consensus(self) -> bool:
        """Initialize quantum consensus - nodes auto-register during transactions"""
        print("🏗️  Quantum consensus ready - nodes will auto-register during transactions...")
        print("  ℹ️  No staking required - quantum annealing selects forgers automatically")
        return True
    
    def run_transaction_load_test(self, num_transactions: int, duration: int) -> List[Dict]:
        """Run a load test with multiple transactions"""
        print(f"🚀 Running transaction load test: {num_transactions} transactions over {duration} seconds")
        
        results = []
        start_time = time.time()
        transaction_interval = duration / num_transactions if num_transactions > 0 else 1
        
        with ThreadPoolExecutor(max_workers=min(10, self.num_nodes)) as executor:
            futures = []
            
            for i in range(num_transactions):
                # Random sender and receiver (excluding exchange wallet)
                sender_idx = (i % (len(self.wallets) - 1)) + 1
                receiver_idx = ((i + 1) % (len(self.wallets) - 1)) + 1
                
                sender = self.wallets[sender_idx]
                receiver = self.wallets[receiver_idx]
                amount = 1 + (i % 10)  # 1-10 tokens
                node_id = i % self.num_nodes
                
                # Submit transaction
                future = executor.submit(
                    self.post_transaction, 
                    sender, receiver, amount, "TRANSFER", node_id
                )
                futures.append(future)
                
                # Wait for next transaction
                if i < num_transactions - 1:
                    time.sleep(transaction_interval)
            
            # Collect results
            for i, future in enumerate(futures):
                try:
                    result = future.result(timeout=30)
                    result['tx_id'] = i
                    results.append(result)
                    
                    if result['success']:
                        print(f"  ✅ TX {i+1}/{num_transactions}: {result['response_time']:.3f}s")
                    else:
                        print(f"  ❌ TX {i+1}/{num_transactions}: Failed")
                        
                except Exception as e:
                    print(f"  ⚠️  TX {i+1}/{num_transactions}: Timeout/Error - {e}")
        
        self.metrics['transactions'] = results
        return results
    
    def analyze_blockchain_growth(self) -> Dict:
        """Analyze blockchain growth and block timing"""
        print("📊 Analyzing blockchain growth and timing...")
        
        analysis = {
            'nodes': {},
            'block_times': [],
            'consensus_performance': {},
            'synchronization': {}
        }
        
        # Get blockchain state from all nodes
        for i in range(self.num_nodes):
            try:
                blockchain_data = self.get_blockchain_state(i)
                quantum_metrics = self.get_quantum_metrics(i)
                
                if blockchain_data:
                    blocks = blockchain_data.get('blocks', [])
                    analysis['nodes'][f'node_{i}'] = {
                        'block_count': len(blocks),
                        'blocks': blocks,
                        'quantum_metrics': quantum_metrics
                    }
                    
                    # Analyze block timing
                    if len(blocks) > 1:
                        for j in range(1, len(blocks)):
                            prev_time = blocks[j-1].get('timestamp', 0)
                            curr_time = blocks[j].get('timestamp', 0)
                            if curr_time > prev_time:
                                block_time = curr_time - prev_time
                                analysis['block_times'].append(block_time)
                
            except Exception as e:
                print(f"  ⚠️  Error analyzing node {i}: {e}")
        
        return analysis
    
    def generate_performance_report(self, analysis: Dict, transaction_results: List[Dict]) -> str:
        """Generate comprehensive performance report"""
        print("📋 Generating performance report...")
        
        report = []
        report.append("=" * 80)
        report.append("🚀 QUANTUM ANNEALING CONSENSUS PERFORMANCE REPORT")
        report.append("=" * 80)
        report.append(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Number of Nodes: {self.num_nodes}")
        report.append("")
        
        # Transaction Performance
        successful_txs = [tx for tx in transaction_results if tx['success']]
        failed_txs = [tx for tx in transaction_results if not tx['success']]
        
        report.append("📈 TRANSACTION PERFORMANCE")
        report.append("-" * 40)
        report.append(f"Total Transactions: {len(transaction_results)}")
        report.append(f"Successful: {len(successful_txs)} ({len(successful_txs)/len(transaction_results)*100:.1f}%)")
        report.append(f"Failed: {len(failed_txs)} ({len(failed_txs)/len(transaction_results)*100:.1f}%)")
        
        if successful_txs:
            response_times = [tx['response_time'] for tx in successful_txs]
            report.append(f"Average Response Time: {statistics.mean(response_times):.3f}s")
            report.append(f"Median Response Time: {statistics.median(response_times):.3f}s")
            report.append(f"Min Response Time: {min(response_times):.3f}s")
            report.append(f"Max Response Time: {max(response_times):.3f}s")
        
        report.append("")
        
        # Block Performance
        block_times = analysis.get('block_times', [])
        if block_times:
            report.append("⛓️  BLOCK PERFORMANCE")
            report.append("-" * 40)
            report.append(f"Average Block Time: {statistics.mean(block_times):.3f}s")
            report.append(f"Median Block Time: {statistics.median(block_times):.3f}s")
            report.append(f"Min Block Time: {min(block_times):.3f}s")
            report.append(f"Max Block Time: {max(block_times):.3f}s")
            
            # Calculate throughput
            if successful_txs and block_times:
                total_time = sum(block_times)
                throughput = len(successful_txs) / total_time if total_time > 0 else 0
                report.append(f"Transaction Throughput: {throughput:.2f} tx/s")
        
        report.append("")
        
        # Node Synchronization
        report.append("🔄 NODE SYNCHRONIZATION")
        report.append("-" * 40)
        block_counts = []
        for node_id, node_data in analysis['nodes'].items():
            block_count = node_data['block_count']
            block_counts.append(block_count)
            report.append(f"{node_id}: {block_count} blocks")
        
        if block_counts:
            sync_diff = max(block_counts) - min(block_counts)
            report.append(f"Synchronization Difference: {sync_diff} blocks")
            if sync_diff <= 1:
                report.append("✅ Excellent synchronization")
            elif sync_diff <= 3:
                report.append("⚠️  Good synchronization")
            else:
                report.append("❌ Poor synchronization")
        
        report.append("")
        
        # Quantum Consensus Metrics
        report.append("🔬 QUANTUM CONSENSUS METRICS")
        report.append("-" * 40)
        
        for node_id, node_data in analysis['nodes'].items():
            quantum_metrics = node_data.get('quantum_metrics', {})
            if quantum_metrics:
                report.append(f"\n{node_id.upper()}:")
                report.append(f"  Total Nodes: {quantum_metrics.get('total_nodes', 0)}")
                report.append(f"  Active Nodes: {quantum_metrics.get('active_nodes', 0)}")
                report.append(f"  Probe Count: {quantum_metrics.get('probe_count', 0)}")
                
                node_scores = quantum_metrics.get('node_scores', {})
                if node_scores:
                    report.append("  Node Scores:")
                    try:
                        if isinstance(next(iter(node_scores.values())), dict):
                            # Nested format: node -> {suitability_score, effective_score, etc.}
                            sorted_items = sorted(
                                node_scores.items(), 
                                key=lambda x: x[1].get('suitability_score', 0), 
                                reverse=True
                            )
                            for node, score_data in sorted_items[:3]:  # Show top 3
                                suitability = score_data.get('suitability_score', 0)
                                report.append(f"    {node[:20]}...: {suitability:.4f}")
                        else:
                            # Simple format: node -> score
                            for node, score in list(node_scores.items())[:3]:  # Show top 3
                                report.append(f"    {node[:20]}...: {score:.4f}")
                    except (StopIteration, TypeError):
                        report.append("    No valid scores available")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Main function to run multi-node testing"""
    parser = argparse.ArgumentParser(description="Multi-node quantum consensus test")
    parser.add_argument("--nodes", type=int, default=3, help="Number of nodes to test")
    parser.add_argument("--transactions", type=int, default=30, help="Number of transactions to send")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    parser.add_argument("--wait-time", type=int, default=30, help="Time to wait for nodes to be ready")
    
    args = parser.parse_args()
    
    print("🌟 QUANTUM ANNEALING MULTI-NODE TEST SUITE")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  Nodes: {args.nodes}")
    print(f"  Transactions: {args.transactions}")
    print(f"  Duration: {args.duration}s")
    print("")
    
    # Initialize node manager
    manager = NodeManager(args.nodes)
    
    # Create test wallets
    wallets = manager.create_test_wallets()
    
    # Wait for nodes to be ready
    if not manager.wait_for_nodes(args.wait_time):
        print("❌ Not all nodes are ready. Please ensure nodes are running:")
        for i in range(args.nodes):
            node_port = manager.base_node_port + i
            api_port = manager.base_api_port + i
            print(f"  Node {i}: python run_node.py --ip localhost --node_port {node_port} --api_port {api_port}")
        return
    
    # Fund wallets
    if not manager.fund_wallets():
        print("❌ Failed to fund wallets")
        return
    
    # Wait for funding to process
    print("⏳ Waiting for funding transactions to process...")
    time.sleep(10)
    
    # Initialize quantum consensus
    if not manager.setup_quantum_consensus():
        print("❌ Failed to initialize quantum consensus")
        return
    
    # Wait for quantum consensus to be ready
    print("⏳ Waiting for quantum consensus to initialize...")
    time.sleep(5)
    
    # Run transaction load test
    transaction_results = manager.run_transaction_load_test(args.transactions, args.duration)
    
    # Wait for final transactions to process
    print("⏳ Waiting for final transactions to process...")
    time.sleep(20)
    
    # Analyze results
    analysis = manager.analyze_blockchain_growth()
    
    # Generate and display report
    report = manager.generate_performance_report(analysis, transaction_results)
    print("\n" + report)
    
    # Save report to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"quantum_consensus_report_{timestamp}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"\n📄 Report saved to: {report_file}")


if __name__ == "__main__":
    main()
