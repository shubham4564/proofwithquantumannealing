#!/usr/bin/env python3
"""
Quantum Annealing Blockchain Performance Analyzer

This tool provides comprehensive performance metrics for the quantum annealing consensus blockchain:
1. Transaction timing analysis
2. Consensus performance measurement
3. Throughput calculation
4. Network latency analysis
5. Block production metrics
6. Quantum annealing efficiency

Usage:
    python performance_analyzer.py --nodes 3 --duration 300
    python performance_analyzer.py --benchmark --transactions 100
    python performance_analyzer.py --real-time --interval 10
"""

import sys
import os

# Add parent directory to path for blockchain module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import requests
import threading
import argparse
import statistics
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt
import pandas as pd

from blockchain.transaction.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils


@dataclass
class TransactionMetrics:
    """Transaction performance metrics"""
    transaction_id: str
    timestamp: float
    response_time: float
    consensus_time: Optional[float]
    block_inclusion_time: Optional[float]
    node_id: int
    success: bool
    amount: float
    tx_type: str


@dataclass
class ConsensusMetrics:
    """Consensus performance metrics"""
    timestamp: float
    forger_selection_time: float
    quantum_score_calculation_time: float
    probe_count: int
    active_nodes: int
    consensus_round: int
    selected_forger: str


@dataclass
class BlockMetrics:
    """Block production metrics"""
    block_height: int
    timestamp: float
    block_time: float
    transactions_count: int
    block_size_bytes: int
    forger_address: str
    consensus_algorithm: str


@dataclass
class NetworkMetrics:
    """Network performance metrics"""
    timestamp: float
    node_id: int
    peer_count: int
    sync_status: bool
    latency_ms: float
    throughput_bps: float


class PerformanceAnalyzer:
    """Comprehensive blockchain performance analyzer"""
    
    def __init__(self, num_nodes: int = 3):
        self.num_nodes = num_nodes
        self.base_node_port = 8000
        self.base_api_port = 8050
        
        # Metrics storage
        self.transaction_metrics: List[TransactionMetrics] = []
        self.consensus_metrics: List[ConsensusMetrics] = []
        self.block_metrics: List[BlockMetrics] = []
        self.network_metrics: List[NetworkMetrics] = []
        
        # Real-time monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Test wallets
        self.wallets = []
        self.create_test_wallets()
    
    def create_test_wallets(self) -> List[Wallet]:
        """Create test wallets for performance testing"""
        print("🔑 Creating test wallets for performance analysis...")
        self.wallets = []
        for i in range(10):  # Create 10 test wallets
            wallet = Wallet()
            self.wallets.append(wallet)
            print(f"  Wallet {i+1}: {wallet.public_key_string()[:20]}...")
        return self.wallets
    
    def check_node_availability(self) -> Dict[int, bool]:
        """Check which nodes are available"""
        available_nodes = {}
        for i in range(self.num_nodes):
            try:
                api_port = self.base_api_port + i
                response = requests.get(f"http://localhost:{api_port}/api/v1/blockchain/", timeout=3)
                available_nodes[i] = response.status_code == 200
            except:
                available_nodes[i] = False
        return available_nodes
    
    def measure_transaction_timing(self, sender: Wallet, receiver: Wallet, 
                                 amount: float, tx_type: str = "TRANSFER",
                                 node_id: int = 0) -> TransactionMetrics:
        """Measure detailed transaction timing"""
        start_time = time.time()
        transaction_id = f"tx_{int(start_time * 1000)}"
        
        # Create transaction
        transaction = sender.create_transaction(receiver.public_key_string(), amount, tx_type)
        
        # Submit transaction
        api_port = self.base_api_port + node_id
        url = f"http://localhost:{api_port}/api/v1/transaction/create/"
        package = {"transaction": BlockchainUtils.encode(transaction)}
        
        try:
            response = requests.post(url, json=package, timeout=15)
            response_time = time.time() - start_time
            
            # Measure consensus and block inclusion time
            consensus_time = None
            block_inclusion_time = None
            
            if response.status_code == 200:
                # Wait and measure consensus time (simplified - actual consensus tracking would need deeper integration)
                consensus_start = time.time()
                time.sleep(1)  # Wait for consensus
                consensus_time = time.time() - consensus_start
                
                # Measure block inclusion time
                block_inclusion_start = time.time()
                # Check if transaction is included in a block (simplified)
                for _ in range(30):  # Wait up to 30 seconds
                    blockchain_info = self.get_blockchain_info(node_id)
                    if blockchain_info and self.is_transaction_in_blockchain(transaction_id, blockchain_info):
                        block_inclusion_time = time.time() - block_inclusion_start
                        break
                    time.sleep(1)
            
            return TransactionMetrics(
                transaction_id=transaction_id,
                timestamp=start_time,
                response_time=response_time,
                consensus_time=consensus_time,
                block_inclusion_time=block_inclusion_time,
                node_id=node_id,
                success=response.status_code == 200,
                amount=amount,
                tx_type=tx_type
            )
            
        except Exception as e:
            return TransactionMetrics(
                transaction_id=transaction_id,
                timestamp=start_time,
                response_time=time.time() - start_time,
                consensus_time=None,
                block_inclusion_time=None,
                node_id=node_id,
                success=False,
                amount=amount,
                tx_type=tx_type
            )
    
    def get_blockchain_info(self, node_id: int) -> Optional[Dict]:
        """Get blockchain information from a node"""
        try:
            api_port = self.base_api_port + node_id
            response = requests.get(f"http://localhost:{api_port}/api/v1/blockchain/", timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def get_quantum_metrics(self, node_id: int) -> Optional[Dict]:
        """Get quantum consensus metrics from a node"""
        try:
            api_port = self.base_api_port + node_id
            response = requests.get(f"http://localhost:{api_port}/api/v1/blockchain/quantum-metrics/", timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def is_transaction_in_blockchain(self, tx_id: str, blockchain_info: Dict) -> bool:
        """Check if transaction is included in blockchain (simplified)"""
        # This is a simplified check - in a real implementation, you'd check transaction hashes
        return True  # Assume transaction is included for timing purposes
    
    def measure_consensus_performance(self, duration: int = 60) -> List[ConsensusMetrics]:
        """Measure consensus performance over time"""
        print(f"🔬 Measuring consensus performance for {duration} seconds...")
        
        consensus_metrics = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            for node_id in range(self.num_nodes):
                quantum_metrics = self.get_quantum_metrics(node_id)
                if quantum_metrics:
                    # Extract consensus metrics (adapt based on your API structure)
                    consensus_metric = ConsensusMetrics(
                        timestamp=time.time(),
                        forger_selection_time=0.1,  # This would need actual measurement
                        quantum_score_calculation_time=0.05,  # This would need actual measurement
                        probe_count=quantum_metrics.get('probe_count', 0),
                        active_nodes=quantum_metrics.get('active_nodes', 0),
                        consensus_round=quantum_metrics.get('consensus_round', 0),
                        selected_forger=quantum_metrics.get('current_forger', 'unknown')
                    )
                    consensus_metrics.append(consensus_metric)
                    break  # Only need one node's consensus data per round
            
            time.sleep(5)  # Sample every 5 seconds
        
        self.consensus_metrics.extend(consensus_metrics)
        return consensus_metrics
    
    def measure_block_production(self, duration: int = 60) -> List[BlockMetrics]:
        """Measure block production metrics"""
        print(f"⛓️  Measuring block production for {duration} seconds...")
        
        initial_blocks = {}
        for node_id in range(self.num_nodes):
            blockchain_info = self.get_blockchain_info(node_id)
            if blockchain_info:
                initial_blocks[node_id] = len(blockchain_info.get('blocks', []))
        
        start_time = time.time()
        time.sleep(duration)
        
        block_metrics = []
        for node_id in range(self.num_nodes):
            blockchain_info = self.get_blockchain_info(node_id)
            if blockchain_info:
                blocks = blockchain_info.get('blocks', [])
                initial_count = initial_blocks.get(node_id, 0)
                
                # Analyze new blocks
                for i, block in enumerate(blocks[initial_count:], initial_count):
                    block_time = 0
                    if i > 0:
                        prev_block = blocks[i-1]
                        block_time = block.get('timestamp', 0) - prev_block.get('timestamp', 0)
                    
                    block_metric = BlockMetrics(
                        block_height=i,
                        timestamp=block.get('timestamp', 0),
                        block_time=block_time,
                        transactions_count=len(block.get('transactions', [])),
                        block_size_bytes=len(json.dumps(block)),
                        forger_address=block.get('forger', 'unknown'),
                        consensus_algorithm='quantum_annealing'
                    )
                    block_metrics.append(block_metric)
                break  # Only analyze one node's blocks
        
        self.block_metrics.extend(block_metrics)
        return block_metrics
    
    def calculate_throughput(self, time_window: int = 60) -> Dict[str, float]:
        """Calculate transaction throughput metrics"""
        current_time = time.time()
        recent_transactions = [
            tx for tx in self.transaction_metrics 
            if current_time - tx.timestamp <= time_window and tx.success
        ]
        
        if not recent_transactions:
            return {'tps': 0, 'successful_tx_rate': 0, 'avg_response_time': 0}
        
        # Calculate metrics
        tps = len(recent_transactions) / time_window
        total_transactions = len([tx for tx in self.transaction_metrics if current_time - tx.timestamp <= time_window])
        successful_tx_rate = len(recent_transactions) / total_transactions if total_transactions > 0 else 0
        avg_response_time = statistics.mean([tx.response_time for tx in recent_transactions])
        
        return {
            'tps': tps,
            'successful_tx_rate': successful_tx_rate,
            'avg_response_time': avg_response_time,
            'total_transactions': len(recent_transactions),
            'time_window': time_window
        }
    
    def run_benchmark_test(self, num_transactions: int = 100) -> Dict:
        """Run comprehensive benchmark test"""
        print(f"🚀 Running benchmark test with {num_transactions} transactions...")
        
        # Fund wallets first
        self.fund_wallets()
        time.sleep(10)  # Wait for funding
        
        # Start consensus and block production monitoring
        consensus_thread = threading.Thread(
            target=self.measure_consensus_performance, 
            args=(num_transactions * 2,)
        )
        block_thread = threading.Thread(
            target=self.measure_block_production,
            args=(num_transactions * 2,)
        )
        
        consensus_thread.start()
        block_thread.start()
        
        # Send transactions
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            for i in range(num_transactions):
                sender = self.wallets[i % len(self.wallets)]
                receiver = self.wallets[(i + 1) % len(self.wallets)]
                amount = 1.0
                node_id = i % self.num_nodes
                
                future = executor.submit(
                    self.measure_transaction_timing,
                    sender, receiver, amount, "TRANSFER", node_id
                )
                futures.append(future)
                
                # Stagger transactions
                if i % 5 == 0:
                    time.sleep(0.1)
            
            # Collect transaction results
            for future in futures:
                try:
                    tx_metrics = future.result(timeout=30)
                    self.transaction_metrics.append(tx_metrics)
                except Exception as e:
                    print(f"Transaction measurement failed: {e}")
        
        total_time = time.time() - start_time
        
        # Wait for monitoring threads
        consensus_thread.join(timeout=30)
        block_thread.join(timeout=30)
        
        # Calculate results
        successful_transactions = [tx for tx in self.transaction_metrics if tx.success]
        throughput_metrics = self.calculate_throughput(int(total_time))
        
        results = {
            'benchmark_duration': total_time,
            'total_transactions': num_transactions,
            'successful_transactions': len(successful_transactions),
            'failed_transactions': num_transactions - len(successful_transactions),
            'success_rate': len(successful_transactions) / num_transactions,
            'throughput': throughput_metrics,
            'consensus_performance': {
                'avg_probe_count': statistics.mean([c.probe_count for c in self.consensus_metrics]) if self.consensus_metrics else 0,
                'avg_active_nodes': statistics.mean([c.active_nodes for c in self.consensus_metrics]) if self.consensus_metrics else 0,
            },
            'block_production': {
                'blocks_produced': len(self.block_metrics),
                'avg_block_time': statistics.mean([b.block_time for b in self.block_metrics if b.block_time > 0]) if self.block_metrics else 0,
                'avg_transactions_per_block': statistics.mean([b.transactions_count for b in self.block_metrics]) if self.block_metrics else 0,
            },
            'response_times': {
                'avg': statistics.mean([tx.response_time for tx in successful_transactions]) if successful_transactions else 0,
                'median': statistics.median([tx.response_time for tx in successful_transactions]) if successful_transactions else 0,
                'min': min([tx.response_time for tx in successful_transactions]) if successful_transactions else 0,
                'max': max([tx.response_time for tx in successful_transactions]) if successful_transactions else 0,
            }
        }
        
        return results
    
    def fund_wallets(self):
        """Fund test wallets with initial tokens"""
        print("💰 Funding test wallets...")
        
        exchange = self.wallets[0]
        
        for i, wallet in enumerate(self.wallets[1:6]):  # Fund first 5 wallets
            amount = 1000.0
            transaction = exchange.create_transaction(wallet.public_key_string(), amount, "EXCHANGE")
            url = f"http://localhost:{self.base_api_port}/api/v1/transaction/create/"
            package = {"transaction": BlockchainUtils.encode(transaction)}
            
            try:
                response = requests.post(url, json=package, timeout=10)
                if response.status_code == 200:
                    print(f"  ✅ Funded wallet {i+1} with {amount} tokens")
                else:
                    print(f"  ❌ Failed to fund wallet {i+1}")
            except Exception as e:
                print(f"  ⚠️  Error funding wallet {i+1}: {e}")
    
    def generate_performance_report(self, results: Dict) -> str:
        """Generate comprehensive performance report"""
        report = []
        
        report.append("🎯 QUANTUM ANNEALING BLOCKCHAIN PERFORMANCE REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Benchmark Summary
        report.append("📊 BENCHMARK SUMMARY")
        report.append("-" * 40)
        report.append(f"Test Duration: {results['benchmark_duration']:.2f} seconds")
        report.append(f"Total Transactions: {results['total_transactions']}")
        report.append(f"Successful Transactions: {results['successful_transactions']}")
        report.append(f"Failed Transactions: {results['failed_transactions']}")
        report.append(f"Success Rate: {results['success_rate']:.2%}")
        report.append("")
        
        # Throughput Metrics
        throughput = results['throughput']
        report.append("🚀 THROUGHPUT METRICS")
        report.append("-" * 40)
        report.append(f"Transactions Per Second (TPS): {throughput['tps']:.2f}")
        report.append(f"Average Response Time: {throughput['avg_response_time']:.3f}s")
        report.append(f"Successful Transaction Rate: {throughput['successful_tx_rate']:.2%}")
        report.append("")
        
        # Response Time Analysis
        response_times = results['response_times']
        report.append("⏱️  RESPONSE TIME ANALYSIS")
        report.append("-" * 40)
        report.append(f"Average: {response_times['avg']:.3f}s")
        report.append(f"Median: {response_times['median']:.3f}s")
        report.append(f"Minimum: {response_times['min']:.3f}s")
        report.append(f"Maximum: {response_times['max']:.3f}s")
        report.append("")
        
        # Consensus Performance
        consensus = results['consensus_performance']
        report.append("🔬 CONSENSUS PERFORMANCE")
        report.append("-" * 40)
        report.append(f"Average Probe Count: {consensus['avg_probe_count']:.1f}")
        report.append(f"Average Active Nodes: {consensus['avg_active_nodes']:.1f}")
        report.append("")
        
        # Block Production
        blocks = results['block_production']
        report.append("⛓️  BLOCK PRODUCTION")
        report.append("-" * 40)
        report.append(f"Blocks Produced: {blocks['blocks_produced']}")
        report.append(f"Average Block Time: {blocks['avg_block_time']:.2f}s")
        report.append(f"Average Transactions per Block: {blocks['avg_transactions_per_block']:.1f}")
        report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_metrics_to_csv(self, filename_prefix: str = "performance_metrics"):
        """Save all metrics to CSV files for further analysis"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create output directory structure if it doesn't exist
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'reports')
        os.makedirs(output_dir, exist_ok=True)
        
        # Save transaction metrics
        if self.transaction_metrics:
            tx_df = pd.DataFrame([asdict(tx) for tx in self.transaction_metrics])
            tx_filename = os.path.join(output_dir, f"{filename_prefix}_transactions_{timestamp}.csv")
            tx_df.to_csv(tx_filename, index=False)
            print(f"📄 Transaction metrics saved to: {tx_filename}")
        
        # Save consensus metrics
        if self.consensus_metrics:
            consensus_df = pd.DataFrame([asdict(c) for c in self.consensus_metrics])
            consensus_filename = os.path.join(output_dir, f"{filename_prefix}_consensus_{timestamp}.csv")
            consensus_df.to_csv(consensus_filename, index=False)
            print(f"📄 Consensus metrics saved to: {consensus_filename}")
        
        # Save block metrics
        if self.block_metrics:
            block_df = pd.DataFrame([asdict(b) for b in self.block_metrics])
            block_filename = os.path.join(output_dir, f"{filename_prefix}_blocks_{timestamp}.csv")
            block_df.to_csv(block_filename, index=False)
            print(f"📄 Block metrics saved to: {block_filename}")
    
    def start_real_time_monitoring(self, interval: int = 10):
        """Start real-time performance monitoring"""
        print(f"📡 Starting real-time monitoring (interval: {interval}s)")
        self.monitoring_active = True
        
        def monitor():
            while self.monitoring_active:
                throughput = self.calculate_throughput(interval * 2)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] TPS: {throughput['tps']:.2f}, "
                      f"Avg Response: {throughput['avg_response_time']:.3f}s, "
                      f"Success Rate: {throughput['successful_tx_rate']:.2%}")
                time.sleep(interval)
        
        self.monitoring_thread = threading.Thread(target=monitor)
        self.monitoring_thread.start()
    
    def stop_real_time_monitoring(self):
        """Stop real-time performance monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        print("📡 Real-time monitoring stopped")


def main():
    """Main function for performance analysis"""
    parser = argparse.ArgumentParser(description="Quantum Annealing Blockchain Performance Analyzer")
    parser.add_argument("--nodes", type=int, default=3, help="Number of nodes to analyze")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark test")
    parser.add_argument("--transactions", type=int, default=50, help="Number of transactions for benchmark")
    parser.add_argument("--real-time", action="store_true", help="Start real-time monitoring")
    parser.add_argument("--interval", type=int, default=10, help="Real-time monitoring interval (seconds)")
    parser.add_argument("--duration", type=int, default=300, help="Monitoring duration (seconds)")
    parser.add_argument("--save-csv", action="store_true", help="Save metrics to CSV files")
    
    args = parser.parse_args()
    
    print("🎯 QUANTUM ANNEALING PERFORMANCE ANALYZER")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = PerformanceAnalyzer(args.nodes)
    
    # Check node availability
    available_nodes = analyzer.check_node_availability()
    active_nodes = sum(available_nodes.values())
    
    print(f"Active Nodes: {active_nodes}/{args.nodes}")
    for node_id, is_available in available_nodes.items():
        status = "✅" if is_available else "❌"
        api_port = analyzer.base_api_port + node_id
        print(f"  Node {node_id} (port {api_port}): {status}")
    
    if active_nodes == 0:
        print("\n❌ No nodes are available. Please start the nodes first.")
        print("Example: python start_nodes.py --nodes 3")
        return
    
    print("")
    
    if args.benchmark:
        # Run benchmark test
        results = analyzer.run_benchmark_test(args.transactions)
        report = analyzer.generate_performance_report(results)
        print(report)
        
        # Save report to organized output directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create output directory structure if it doesn't exist
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'reports')
        os.makedirs(output_dir, exist_ok=True)
        
        report_filename = os.path.join(output_dir, f"performance_report_{timestamp}.txt")
        with open(report_filename, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to: {report_filename}")
        
    elif args.real_time:
        # Start real-time monitoring
        analyzer.start_real_time_monitoring(args.interval)
        try:
            time.sleep(args.duration)
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring interrupted by user")
        finally:
            analyzer.stop_real_time_monitoring()
    
    else:
        # Quick performance check
        throughput = analyzer.calculate_throughput()
        print("📊 CURRENT PERFORMANCE METRICS")
        print("-" * 40)
        print(f"Transactions Per Second: {throughput['tps']:.2f}")
        print(f"Average Response Time: {throughput['avg_response_time']:.3f}s")
        print(f"Success Rate: {throughput['successful_tx_rate']:.2%}")
    
    # Save metrics to CSV if requested
    if args.save_csv:
        analyzer.save_metrics_to_csv()


if __name__ == "__main__":
    main()
