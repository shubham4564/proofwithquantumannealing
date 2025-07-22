#!/usr/bin/env python3
"""
Simple Performance Metrics Tool for Quantum Annealing Blockchain

This tool provides essential performance metrics without external dependencies:
1. Transaction timing and throughput
2. Consensus performance 
3. Block production analysis
4. Response time statistics

Usage:
    python simple_performance.py --benchmark --transactions 50
    python simple_performance.py --measure-consensus --duration 60
    python simple_performance.py --throughput-test --nodes 3
"""

import os
import sys
import json
import time
import requests
import argparse
import statistics
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

# Add the parent directory to Python path to find blockchain modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from blockchain.transaction.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils


class SimplePerformanceAnalyzer:
    """Simple blockchain performance analyzer"""
    
    def __init__(self, num_nodes: int = 3):
        self.num_nodes = num_nodes
        self.base_api_port = 8050
        self.wallets = []
        self.create_test_wallets()
    
    def create_test_wallets(self):
        """Create test wallets"""
        print("🔑 Creating test wallets...")
        for i in range(10):
            wallet = Wallet()
            self.wallets.append(wallet)
    
    def check_nodes(self) -> List[int]:
        """Check which nodes are available"""
        available = []
        print("🔍 Checking node availability...")
        for i in range(self.num_nodes):
            try:
                api_port = self.base_api_port + i
                response = requests.get(f"http://localhost:{api_port}/api/v1/blockchain/", timeout=3)
                if response.status_code == 200:
                    available.append(i)
                    print(f"  ✅ Node {i} (port {api_port}): Available")
                else:
                    print(f"  ❌ Node {i} (port {api_port}): Unavailable")
            except:
                print(f"  ❌ Node {i} (port {api_port}): Connection failed")
        return available
    
    def measure_transaction_performance(self, sender: Wallet, receiver: Wallet, 
                                      amount: float, node_id: int = 0) -> Dict:
        """Measure single transaction performance"""
        api_port = self.base_api_port + node_id
        
        # Create transaction
        start_time = time.time()
        transaction = sender.create_transaction(receiver.public_key_string(), amount, "TRANSFER")
        creation_time = time.time() - start_time
        
        # Submit transaction
        submit_start = time.time()
        url = f"http://localhost:{api_port}/api/v1/transaction/create/"
        package = {"transaction": BlockchainUtils.encode(transaction)}
        
        try:
            response = requests.post(url, json=package, timeout=15)
            submit_time = time.time() - submit_start
            total_time = time.time() - start_time
            
            return {
                'success': response.status_code == 200,
                'creation_time': creation_time,
                'submit_time': submit_time,
                'total_time': total_time,
                'status_code': response.status_code,
                'timestamp': start_time,
                'node_id': node_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'creation_time': creation_time,
                'submit_time': time.time() - submit_start,
                'total_time': time.time() - start_time,
                'timestamp': start_time,
                'node_id': node_id
            }
    
    def run_throughput_test(self, num_transactions: int = 50, concurrent: bool = True) -> Dict:
        """Run transaction throughput test"""
        print(f"🚀 Running throughput test with {num_transactions} transactions...")
        
        # Fund wallets first
        self.fund_wallets()
        time.sleep(10)
        
        results = []
        start_time = time.time()
        
        if concurrent:
            # Concurrent transaction submission
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                
                for i in range(num_transactions):
                    sender = self.wallets[i % len(self.wallets)]
                    receiver = self.wallets[(i + 1) % len(self.wallets)]
                    node_id = i % self.num_nodes
                    
                    future = executor.submit(
                        self.measure_transaction_performance,
                        sender, receiver, 1.0, node_id
                    )
                    futures.append(future)
                
                # Collect results
                for i, future in enumerate(futures):
                    try:
                        result = future.result(timeout=30)
                        result['tx_index'] = i
                        results.append(result)
                        print(f"  TX {i+1}/{num_transactions}: {'✅' if result['success'] else '❌'} ({result['total_time']:.3f}s)")
                    except Exception as e:
                        print(f"  TX {i+1}/{num_transactions}: ⚠️ Timeout/Error")
        else:
            # Sequential transaction submission
            for i in range(num_transactions):
                sender = self.wallets[i % len(self.wallets)]
                receiver = self.wallets[(i + 1) % len(self.wallets)]
                node_id = i % self.num_nodes
                
                result = self.measure_transaction_performance(sender, receiver, 1.0, node_id)
                result['tx_index'] = i
                results.append(result)
                print(f"  TX {i+1}/{num_transactions}: {'✅' if result['success'] else '❌'} ({result['total_time']:.3f}s)")
                
                # Small delay between transactions
                time.sleep(0.1)
        
        total_duration = time.time() - start_time
        successful_txs = [r for r in results if r['success']]
        
        # Calculate metrics
        metrics = {
            'total_transactions': num_transactions,
            'successful_transactions': len(successful_txs),
            'failed_transactions': num_transactions - len(successful_txs),
            'success_rate': len(successful_txs) / num_transactions,
            'total_duration': total_duration,
            'transactions_per_second': len(successful_txs) / total_duration,
            'concurrent_mode': concurrent
        }
        
        if successful_txs:
            creation_times = [r['creation_time'] for r in successful_txs]
            submit_times = [r['submit_time'] for r in successful_txs]
            total_times = [r['total_time'] for r in successful_txs]
            
            metrics.update({
                'avg_creation_time': statistics.mean(creation_times),
                'avg_submit_time': statistics.mean(submit_times),
                'avg_total_time': statistics.mean(total_times),
                'median_total_time': statistics.median(total_times),
                'min_total_time': min(total_times),
                'max_total_time': max(total_times)
            })
        
        return metrics
    
    def measure_consensus_metrics(self, duration: int = 60) -> Dict:
        """Measure consensus performance over time"""
        print(f"🔬 Measuring consensus metrics for {duration} seconds...")
        
        consensus_data = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            for node_id in range(self.num_nodes):
                try:
                    api_port = self.base_api_port + node_id
                    response = requests.get(f"http://localhost:{api_port}/api/v1/blockchain/quantum-metrics/", timeout=5)
                    
                    if response.status_code == 200:
                        data = response.json()
                        consensus_data.append({
                            'timestamp': time.time(),
                            'node_id': node_id,
                            'total_nodes': data.get('total_nodes', 0),
                            'active_nodes': data.get('active_nodes', 0),
                            'probe_count': data.get('probe_count', 0),
                            'node_scores_count': len(data.get('node_scores', {}))
                        })
                        break  # Only need data from one node per iteration
                except:
                    continue
            
            time.sleep(5)  # Sample every 5 seconds
        
        if not consensus_data:
            return {'error': 'No consensus data collected'}
        
        # Analyze consensus data
        probe_counts = [d['probe_count'] for d in consensus_data]
        active_nodes = [d['active_nodes'] for d in consensus_data]
        
        return {
            'samples_collected': len(consensus_data),
            'duration': duration,
            'avg_probe_count': statistics.mean(probe_counts) if probe_counts else 0,
            'max_probe_count': max(probe_counts) if probe_counts else 0,
            'min_probe_count': min(probe_counts) if probe_counts else 0,
            'avg_active_nodes': statistics.mean(active_nodes) if active_nodes else 0,
            'consensus_stability': len(set(active_nodes)) <= 2  # Stable if active nodes don't vary much
        }
    
    def analyze_block_production(self, duration: int = 60) -> Dict:
        """Analyze block production performance"""
        print(f"⛓️ Analyzing block production for {duration} seconds...")
        
        # Get initial blockchain state
        initial_state = {}
        for node_id in range(self.num_nodes):
            try:
                api_port = self.base_api_port + node_id
                response = requests.get(f"http://localhost:{api_port}/api/v1/blockchain/", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    initial_state[node_id] = {
                        'block_count': len(data.get('blocks', [])),
                        'blocks': data.get('blocks', [])
                    }
            except:
                continue
        
        # Wait for the duration
        time.sleep(duration)
        
        # Get final blockchain state
        final_state = {}
        for node_id in range(self.num_nodes):
            try:
                api_port = self.base_api_port + node_id
                response = requests.get(f"http://localhost:{api_port}/api/v1/blockchain/", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    final_state[node_id] = {
                        'block_count': len(data.get('blocks', [])),
                        'blocks': data.get('blocks', [])
                    }
            except:
                continue
        
        # Analyze block production
        blocks_produced = 0
        block_times = []
        
        for node_id in final_state:
            if node_id in initial_state:
                initial_count = initial_state[node_id]['block_count']
                final_count = final_state[node_id]['block_count']
                blocks_produced += max(0, final_count - initial_count)
                
                # Calculate block times for new blocks
                final_blocks = final_state[node_id]['blocks']
                for i in range(initial_count, len(final_blocks)):
                    if i > 0:
                        prev_timestamp = final_blocks[i-1].get('timestamp', 0)
                        curr_timestamp = final_blocks[i].get('timestamp', 0)
                        if curr_timestamp > prev_timestamp:
                            block_times.append(curr_timestamp - prev_timestamp)
                break  # Only analyze one node's blocks
        
        return {
            'duration': duration,
            'blocks_produced': blocks_produced,
            'blocks_per_minute': (blocks_produced / duration) * 60 if duration > 0 else 0,
            'avg_block_time': statistics.mean(block_times) if block_times else 0,
            'median_block_time': statistics.median(block_times) if block_times else 0,
            'block_time_consistency': statistics.stdev(block_times) if len(block_times) > 1 else 0
        }
    
    def fund_wallets(self):
        """Fund test wallets"""
        print("💰 Funding test wallets...")
        
        exchange = self.wallets[0]
        funded_count = 0
        
        for i, wallet in enumerate(self.wallets[1:6]):  # Fund first 5 wallets
            try:
                transaction = exchange.create_transaction(wallet.public_key_string(), 1000.0, "EXCHANGE")
                url = f"http://localhost:{self.base_api_port}/api/v1/transaction/create/"
                package = {"transaction": BlockchainUtils.encode(transaction)}
                
                response = requests.post(url, json=package, timeout=10)
                if response.status_code == 200:
                    funded_count += 1
                    print(f"  ✅ Funded wallet {i+1}")
                else:
                    print(f"  ❌ Failed to fund wallet {i+1}")
            except Exception as e:
                print(f"  ⚠️ Error funding wallet {i+1}: {e}")
        
        print(f"💰 Successfully funded {funded_count}/5 wallets")
    
    def generate_report(self, throughput_metrics: Dict = None, 
                       consensus_metrics: Dict = None, 
                       block_metrics: Dict = None) -> str:
        """Generate performance report"""
        report = []
        
        report.append("🎯 BLOCKCHAIN PERFORMANCE REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        if throughput_metrics:
            report.append("🚀 THROUGHPUT METRICS")
            report.append("-" * 30)
            report.append(f"Total Transactions: {throughput_metrics['total_transactions']}")
            report.append(f"Successful: {throughput_metrics['successful_transactions']}")
            report.append(f"Failed: {throughput_metrics['failed_transactions']}")
            report.append(f"Success Rate: {throughput_metrics['success_rate']:.2%}")
            report.append(f"TPS: {throughput_metrics['transactions_per_second']:.2f}")
            report.append(f"Test Duration: {throughput_metrics['total_duration']:.2f}s")
            
            if 'avg_total_time' in throughput_metrics:
                report.append(f"Avg Response Time: {throughput_metrics['avg_total_time']:.3f}s")
                report.append(f"Median Response Time: {throughput_metrics['median_total_time']:.3f}s")
                report.append(f"Min Response Time: {throughput_metrics['min_total_time']:.3f}s")
                report.append(f"Max Response Time: {throughput_metrics['max_total_time']:.3f}s")
            
            report.append("")
        
        if consensus_metrics and 'error' not in consensus_metrics:
            report.append("🔬 CONSENSUS METRICS")
            report.append("-" * 30)
            report.append(f"Measurement Duration: {consensus_metrics['duration']}s")
            report.append(f"Samples Collected: {consensus_metrics['samples_collected']}")
            report.append(f"Avg Probe Count: {consensus_metrics['avg_probe_count']:.1f}")
            report.append(f"Avg Active Nodes: {consensus_metrics['avg_active_nodes']:.1f}")
            report.append(f"Consensus Stability: {'✅ Stable' if consensus_metrics['consensus_stability'] else '⚠️ Variable'}")
            report.append("")
        
        if block_metrics:
            report.append("⛓️ BLOCK PRODUCTION")
            report.append("-" * 30)
            report.append(f"Duration: {block_metrics['duration']}s")
            report.append(f"Blocks Produced: {block_metrics['blocks_produced']}")
            report.append(f"Blocks per Minute: {block_metrics['blocks_per_minute']:.2f}")
            report.append(f"Avg Block Time: {block_metrics['avg_block_time']:.2f}s")
            report.append(f"Block Time Consistency: {block_metrics['block_time_consistency']:.2f}s std dev")
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Simple Blockchain Performance Analyzer")
    parser.add_argument("--nodes", type=int, default=3, help="Number of nodes")
    parser.add_argument("--benchmark", action="store_true", help="Run full benchmark")
    parser.add_argument("--throughput-test", action="store_true", help="Run throughput test only")
    parser.add_argument("--measure-consensus", action="store_true", help="Measure consensus only")
    parser.add_argument("--measure-blocks", action="store_true", help="Measure block production only")
    parser.add_argument("--transactions", type=int, default=30, help="Number of transactions")
    parser.add_argument("--duration", type=int, default=60, help="Measurement duration")
    parser.add_argument("--sequential", action="store_true", help="Send transactions sequentially")
    
    args = parser.parse_args()
    
    print("🎯 SIMPLE BLOCKCHAIN PERFORMANCE ANALYZER")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = SimplePerformanceAnalyzer(args.nodes)
    
    # Check node availability
    available_nodes = analyzer.check_nodes()
    if not available_nodes:
        print("\n❌ No nodes available. Please start nodes first:")
        print("Example: python start_nodes.py --nodes 3")
        return
    
    print(f"\n📊 Found {len(available_nodes)} active nodes")
    print("")
    
    throughput_metrics = None
    consensus_metrics = None
    block_metrics = None
    
    if args.benchmark:
        # Run full benchmark
        print("🚀 Running full performance benchmark...")
        throughput_metrics = analyzer.run_throughput_test(args.transactions, not args.sequential)
        time.sleep(5)  # Brief pause between tests
        consensus_metrics = analyzer.measure_consensus_metrics(args.duration)
        time.sleep(5)
        block_metrics = analyzer.analyze_block_production(args.duration)
        
    elif args.throughput_test:
        throughput_metrics = analyzer.run_throughput_test(args.transactions, not args.sequential)
        
    elif args.measure_consensus:
        consensus_metrics = analyzer.measure_consensus_metrics(args.duration)
        
    elif args.measure_blocks:
        block_metrics = analyzer.analyze_block_production(args.duration)
        
    else:
        # Quick throughput test by default
        print("Running quick throughput test (use --benchmark for full analysis)...")
        throughput_metrics = analyzer.run_throughput_test(20, True)
    
    # Generate and display report
    report = analyzer.generate_report(throughput_metrics, consensus_metrics, block_metrics)
    print(report)
    
    # Save report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"performance_report_{timestamp}.txt"
    with open(filename, 'w') as f:
        f.write(report)
    print(f"📄 Report saved to: {filename}")


if __name__ == "__main__":
    main()
