#!/usr/bin/env python3
"""
Flexible Performance Test Framework

This test framework provides:
1. Generate N transactions and distribute randomly across available nodes
2. Comprehensive performance metrics collection
3. Real-time monitoring and analysis
4. Detailed timing measurements for all blockchain operations

Metrics collected:
- Transaction submission times (signing, network, verification)
- Consensus timing (per round, total time)
- Throughput analysis (transactions per second)
- Network propagation efficiency
- Block creation and validation times
"""

import sys
import os
import random
import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import statistics
from collections import defaultdict, deque

sys.path.insert(0, '/Users/shubham/Documents/proofwithquantumannealing/blockchain')

from blockchain.transaction.wallet import Wallet
from blockchain.transaction.transaction import Transaction
from blockchain.utils.helpers import BlockchainUtils

class PerformanceMetrics:
    """Comprehensive performance metrics collector"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all metrics"""
        self.transaction_times = []
        self.signing_times = []
        self.submission_times = []
        self.verification_times = []
        self.consensus_rounds = []
        self.block_creation_times = []
        self.propagation_times = []
        self.throughput_data = deque(maxlen=100)  # Rolling window
        
        self.test_start_time = None
        self.test_end_time = None
        self.first_transaction_time = None
        self.last_transaction_time = None
        self.first_block_time = None
        self.last_block_time = None
        
        self.total_transactions_generated = 0
        self.total_transactions_submitted = 0
        self.total_transactions_successful = 0
        self.total_blocks_created = 0
        
        self.node_performance = defaultdict(lambda: {
            'transactions_sent': 0,
            'transactions_successful': 0,
            'avg_response_time': 0,
            'blocks_created': 0
        })
    
    def add_transaction_time(self, signing_time, submission_time, success):
        """Add transaction timing data"""
        self.signing_times.append(signing_time)
        self.submission_times.append(submission_time)
        
        total_time = signing_time + submission_time
        self.transaction_times.append(total_time)
        
        if success:
            self.total_transactions_successful += 1
        
        # Update throughput data
        current_time = time.time()
        self.throughput_data.append(current_time)
        
        # Mark first transaction
        if self.first_transaction_time is None:
            self.first_transaction_time = current_time
        self.last_transaction_time = current_time
    
    def add_consensus_round(self, round_time, blocks_created):
        """Add consensus round data"""
        self.consensus_rounds.append(round_time)
        self.total_blocks_created += blocks_created
        
        current_time = time.time()
        if self.first_block_time is None and blocks_created > 0:
            self.first_block_time = current_time
        if blocks_created > 0:
            self.last_block_time = current_time
    
    def add_node_performance(self, node_id, response_time, success, blocks_created=0):
        """Add node-specific performance data"""
        self.node_performance[node_id]['transactions_sent'] += 1
        if success:
            self.node_performance[node_id]['transactions_successful'] += 1
        
        # Update average response time
        current_avg = self.node_performance[node_id]['avg_response_time']
        total_sent = self.node_performance[node_id]['transactions_sent']
        new_avg = ((current_avg * (total_sent - 1)) + response_time) / total_sent
        self.node_performance[node_id]['avg_response_time'] = new_avg
        
        self.node_performance[node_id]['blocks_created'] += blocks_created
    
    def calculate_throughput(self, window_seconds=10):
        """Calculate current throughput (transactions per second)"""
        if len(self.throughput_data) < 2:
            return 0
        
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        recent_transactions = [t for t in self.throughput_data if t >= cutoff_time]
        
        if len(recent_transactions) < 2:
            return 0
        
        time_span = recent_transactions[-1] - recent_transactions[0]
        if time_span == 0:
            return 0
        
        return len(recent_transactions) / time_span
    
    def get_summary(self):
        """Get comprehensive performance summary"""
        if not self.transaction_times:
            return {"error": "No transaction data available"}
        
        total_test_time = (self.test_end_time or time.time()) - (self.test_start_time or time.time())
        
        summary = {
            "test_duration": {
                "total_time_seconds": total_test_time,
                "transaction_period_seconds": (self.last_transaction_time - self.first_transaction_time) if self.first_transaction_time and self.last_transaction_time else 0,
                "consensus_period_seconds": (self.last_block_time - self.first_block_time) if self.first_block_time and self.last_block_time else 0
            },
            
            "transaction_metrics": {
                "total_generated": self.total_transactions_generated,
                "total_submitted": self.total_transactions_submitted,
                "total_successful": self.total_transactions_successful,
                "success_rate_percent": (self.total_transactions_successful / max(1, self.total_transactions_submitted)) * 100,
                
                "timing": {
                    "avg_signing_time_ms": statistics.mean(self.signing_times) * 1000 if self.signing_times else 0,
                    "avg_submission_time_ms": statistics.mean(self.submission_times) * 1000 if self.submission_times else 0,
                    "avg_total_transaction_time_ms": statistics.mean(self.transaction_times) * 1000 if self.transaction_times else 0,
                    
                    "min_transaction_time_ms": min(self.transaction_times) * 1000 if self.transaction_times else 0,
                    "max_transaction_time_ms": max(self.transaction_times) * 1000 if self.transaction_times else 0,
                    "std_transaction_time_ms": statistics.stdev(self.transaction_times) * 1000 if len(self.transaction_times) > 1 else 0
                }
            },
            
            "consensus_metrics": {
                "total_blocks_created": self.total_blocks_created,
                "total_consensus_rounds": len(self.consensus_rounds),
                "avg_consensus_time_seconds": statistics.mean(self.consensus_rounds) if self.consensus_rounds else 0,
                "min_consensus_time_seconds": min(self.consensus_rounds) if self.consensus_rounds else 0,
                "max_consensus_time_seconds": max(self.consensus_rounds) if self.consensus_rounds else 0,
                
                "blocks_per_round": self.total_blocks_created / max(1, len(self.consensus_rounds)),
                "consensus_efficiency": (self.total_blocks_created / max(1, total_test_time)) if total_test_time > 0 else 0
            },
            
            "throughput_metrics": {
                "overall_tps": self.total_transactions_successful / max(1, total_test_time) if total_test_time > 0 else 0,
                "peak_tps": self.calculate_throughput(window_seconds=5),
                "avg_tps_10s_window": self.calculate_throughput(window_seconds=10),
                "transactions_per_block": self.total_transactions_successful / max(1, self.total_blocks_created) if self.total_blocks_created > 0 else 0
            },
            
            "node_performance": dict(self.node_performance)
        }
        
        return summary

class FlexiblePerformanceTest:
    """Flexible performance test framework"""
    
    def __init__(self, base_port=11000, max_nodes=10):
        self.session = requests.Session()
        
        # Optimize session for high-performance testing
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=20,
            pool_maxsize=50,
            max_retries=1
        )
        self.session.mount('http://', adapter)
        self.session.timeout = (3, 10)
        
        self.base_port = base_port
        self.max_nodes = max_nodes
        self.available_nodes = []
        self.metrics = PerformanceMetrics()
        
        # Pre-generate wallets for better performance
        self.sender_wallets = [Wallet() for _ in range(50)]
        self.receiver_wallets = [Wallet() for _ in range(100)]
    
    def discover_available_nodes(self):
        """Discover which nodes are currently online"""
        print("🔍 Discovering available nodes...")
        self.available_nodes = []
        
        for node_id in range(1, self.max_nodes + 1):
            api_port = self.base_port + node_id - 1
            try:
                response = self.session.get(
                    f'http://localhost:{api_port}/api/v1/blockchain/', 
                    timeout=2
                )
                if response.status_code == 200:
                    self.available_nodes.append(node_id)
                    print(f"   ✅ Node {node_id} (port {api_port}): Online")
                else:
                    print(f"   ❌ Node {node_id} (port {api_port}): HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ Node {node_id} (port {api_port}): {str(e)[:50]}")
        
        print(f"\n📊 Found {len(self.available_nodes)} available nodes: {self.available_nodes}")
        return self.available_nodes
    
    def get_node_status(self, node_id):
        """Get detailed status of a specific node"""
        api_port = self.base_port + node_id - 1
        try:
            # Get blockchain status
            blockchain_response = self.session.get(
                f'http://localhost:{api_port}/api/v1/blockchain/', 
                timeout=3
            )
            
            # Get transaction pool status
            pool_response = self.session.get(
                f'http://localhost:{api_port}/api/v1/transaction/transaction_pool/', 
                timeout=3
            )
            
            blockchain_data = blockchain_response.json() if blockchain_response.status_code == 200 else {}
            pool_data = pool_response.json() if pool_response.status_code == 200 else []
            
            return {
                'node_id': node_id,
                'online': blockchain_response.status_code == 200,
                'blocks': len(blockchain_data.get('blocks', [])),
                'pool_size': len(pool_data) if isinstance(pool_data, list) else 0,
                'api_port': api_port
            }
            
        except Exception as e:
            return {
                'node_id': node_id,
                'online': False,
                'blocks': 0,
                'pool_size': 0,
                'error': str(e),
                'api_port': api_port
            }
    
    def create_transaction(self):
        """Create a single transaction with timing"""
        start_time = time.time()
        
        sender_wallet = random.choice(self.sender_wallets)
        receiver_wallet = random.choice(self.receiver_wallets)
        receiver_public_key = receiver_wallet.public_key_string()
        amount = random.uniform(1.0, 100.0)
        
        # Time the signing process
        signing_start = time.time()
        transaction = sender_wallet.create_transaction(
            receiver_public_key, amount, "TRANSFER"
        )
        signing_time = time.time() - signing_start
        
        encoded_transaction = BlockchainUtils.encode(transaction)
        
        total_creation_time = time.time() - start_time
        
        return {
            'encoded_transaction': encoded_transaction,
            'signing_time': signing_time,
            'creation_time': total_creation_time,
            'amount': amount
        }
    
    def submit_transaction_to_node(self, encoded_transaction, node_id):
        """Submit transaction to a specific node with detailed timing"""
        api_port = self.base_port + node_id - 1
        url = f'http://localhost:{api_port}/api/v1/transaction/create/'
        
        submission_start = time.time()
        try:
            response = self.session.post(url, json={'transaction': encoded_transaction})
            submission_time = time.time() - submission_start
            
            success = response.status_code == 200
            
            return {
                'node_id': node_id,
                'success': success,
                'status_code': response.status_code,
                'submission_time': submission_time,
                'response': response.text if not success else "Success"
            }
            
        except Exception as e:
            submission_time = time.time() - submission_start
            return {
                'node_id': node_id,
                'success': False,
                'status_code': 0,
                'submission_time': submission_time,
                'response': str(e)
            }
    
    def monitor_network_changes(self, initial_statuses, duration=30):
        """Monitor network for consensus and block creation"""
        print(f"🔍 Monitoring network for {duration} seconds...")
        
        monitoring_data = []
        start_time = time.time()
        last_consensus_check = start_time
        
        while time.time() - start_time < duration:
            current_time = time.time()
            current_statuses = {node_id: self.get_node_status(node_id) for node_id in self.available_nodes}
            
            # Check for new blocks
            new_blocks = 0
            for node_id in self.available_nodes:
                initial_blocks = initial_statuses[node_id]['blocks']
                current_blocks = current_statuses[node_id]['blocks']
                new_blocks += max(0, current_blocks - initial_blocks)
            
            # Calculate consensus round time if new blocks detected
            if new_blocks > 0:
                consensus_round_time = current_time - last_consensus_check
                self.metrics.add_consensus_round(consensus_round_time, new_blocks)
                last_consensus_check = current_time
                print(f"   📦 {current_time - start_time:.1f}s: {new_blocks} new blocks created (consensus time: {consensus_round_time:.3f}s)")
            
            monitoring_data.append({
                'time': current_time - start_time,
                'statuses': current_statuses,
                'new_blocks': new_blocks,
                'total_pool': sum(s['pool_size'] for s in current_statuses.values()),
                'max_blocks': max(s['blocks'] for s in current_statuses.values())
            })
            
            # Print progress every 5 seconds
            if len(monitoring_data) % 25 == 0:
                latest = monitoring_data[-1]
                throughput = self.metrics.calculate_throughput()
                print(f"   ⏱️  {latest['time']:.1f}s: Pool: {latest['total_pool']}, Blocks: {latest['max_blocks']}, TPS: {throughput:.2f}")
            
            time.sleep(0.2)
        
        return monitoring_data
    
    def run_performance_test(self, num_transactions, batch_size=10, monitor_duration=30):
        """Run comprehensive performance test"""
        print(f"🚀 FLEXIBLE PERFORMANCE TEST")
        print(f"🎯 Testing {num_transactions} transactions with comprehensive metrics")
        print("=" * 70)
        
        # Discover available nodes
        self.discover_available_nodes()
        if len(self.available_nodes) < 2:
            print("❌ Need at least 2 nodes online for testing")
            return None
        
        # Reset metrics
        self.metrics.reset()
        self.metrics.test_start_time = time.time()
        self.metrics.total_transactions_generated = num_transactions
        
        # Get initial network status
        print(f"\n📊 Initial network status...")
        initial_statuses = {node_id: self.get_node_status(node_id) for node_id in self.available_nodes}
        
        for node_id, status in initial_statuses.items():
            print(f"   📡 Node {node_id}: {status['blocks']} blocks, {status['pool_size']} pending tx")
        
        # Generate and submit transactions
        print(f"\n💳 Generating and submitting {num_transactions} transactions...")
        print(f"📦 Batch size: {batch_size}, Target nodes: {len(self.available_nodes)}")
        
        submitted_count = 0
        successful_count = 0
        
        # Process transactions in batches for better performance
        for batch_start in range(0, num_transactions, batch_size):
            batch_end = min(batch_start + batch_size, num_transactions)
            batch_transactions = []
            
            # Create batch of transactions
            batch_creation_start = time.time()
            for i in range(batch_start, batch_end):
                tx_data = self.create_transaction()
                batch_transactions.append(tx_data)
            batch_creation_time = time.time() - batch_creation_start
            
            # Submit batch in parallel
            batch_submission_start = time.time()
            with ThreadPoolExecutor(max_workers=min(len(self.available_nodes), 10)) as executor:
                futures = []
                
                for tx_data in batch_transactions:
                    # Randomly select node for this transaction
                    target_node = random.choice(self.available_nodes)
                    
                    future = executor.submit(
                        self.submit_transaction_to_node,
                        tx_data['encoded_transaction'],
                        target_node
                    )
                    futures.append((future, tx_data, target_node))
                
                # Collect results
                for future, tx_data, target_node in futures:
                    result = future.result()
                    submitted_count += 1
                    
                    # Record metrics
                    self.metrics.add_transaction_time(
                        tx_data['signing_time'],
                        result['submission_time'],
                        result['success']
                    )
                    
                    self.metrics.add_node_performance(
                        target_node,
                        result['submission_time'],
                        result['success']
                    )
                    
                    if result['success']:
                        successful_count += 1
                    
                    self.metrics.total_transactions_submitted = submitted_count
            
            batch_submission_time = time.time() - batch_submission_start
            
            # Progress update
            progress = (batch_end / num_transactions) * 100
            current_throughput = self.metrics.calculate_throughput()
            print(f"   📈 Progress: {progress:.1f}% ({successful_count}/{submitted_count} successful, {current_throughput:.2f} TPS)")
            
            # Small delay between batches to avoid overwhelming the network
            if batch_end < num_transactions:
                time.sleep(0.1)
        
        print(f"\n✅ Transaction submission complete!")
        print(f"   📊 Total: {successful_count}/{submitted_count} successful")
        print(f"   ⚡ Average throughput: {self.metrics.calculate_throughput():.2f} TPS")
        
        # Monitor network for consensus
        monitoring_data = self.monitor_network_changes(initial_statuses, monitor_duration)
        
        # Finalize metrics
        self.metrics.test_end_time = time.time()
        
        # Get final network status
        print(f"\n📊 Final network status...")
        final_statuses = {node_id: self.get_node_status(node_id) for node_id in self.available_nodes}
        
        total_new_blocks = 0
        for node_id, status in final_statuses.items():
            initial_blocks = initial_statuses[node_id]['blocks']
            current_blocks = status['blocks']
            new_blocks = current_blocks - initial_blocks
            total_new_blocks = max(total_new_blocks, new_blocks)
            print(f"   📡 Node {node_id}: {current_blocks} blocks (+{new_blocks}), {status['pool_size']} pending tx")
        
        # Generate comprehensive report
        summary = self.metrics.get_summary()
        self.print_performance_report(summary)
        
        return {
            'summary': summary,
            'monitoring_data': monitoring_data,
            'initial_statuses': initial_statuses,
            'final_statuses': final_statuses
        }
    
    def print_performance_report(self, summary):
        """Print comprehensive performance report"""
        print(f"\n📈 COMPREHENSIVE PERFORMANCE REPORT")
        print("=" * 70)
        
        # Test Overview
        print(f"\n🎯 Test Overview:")
        print(f"   ⏱️  Total Test Duration: {summary['test_duration']['total_time_seconds']:.3f}s")
        print(f"   💳 Transactions Generated: {summary['transaction_metrics']['total_generated']}")
        print(f"   📤 Transactions Submitted: {summary['transaction_metrics']['total_submitted']}")
        print(f"   ✅ Transactions Successful: {summary['transaction_metrics']['total_successful']}")
        print(f"   📊 Success Rate: {summary['transaction_metrics']['success_rate_percent']:.1f}%")
        
        # Transaction Performance
        print(f"\n⚡ Transaction Performance:")
        tx_metrics = summary['transaction_metrics']['timing']
        print(f"   🔐 Average Signing Time: {tx_metrics['avg_signing_time_ms']:.2f}ms")
        print(f"   📡 Average Submission Time: {tx_metrics['avg_submission_time_ms']:.2f}ms")
        print(f"   ⏱️  Average Total Transaction Time: {tx_metrics['avg_total_transaction_time_ms']:.2f}ms")
        print(f"   📈 Min/Max Transaction Time: {tx_metrics['min_transaction_time_ms']:.2f}ms / {tx_metrics['max_transaction_time_ms']:.2f}ms")
        print(f"   📊 Standard Deviation: {tx_metrics['std_transaction_time_ms']:.2f}ms")
        
        # Consensus Performance
        print(f"\n🔗 Consensus Performance:")
        consensus_metrics = summary['consensus_metrics']
        print(f"   📦 Total Blocks Created: {consensus_metrics['total_blocks_created']}")
        print(f"   🔄 Total Consensus Rounds: {consensus_metrics['total_consensus_rounds']}")
        print(f"   ⏱️  Average Consensus Time: {consensus_metrics['avg_consensus_time_seconds']:.3f}s")
        print(f"   📈 Min/Max Consensus Time: {consensus_metrics['min_consensus_time_seconds']:.3f}s / {consensus_metrics['max_consensus_time_seconds']:.3f}s")
        print(f"   📊 Blocks per Round: {consensus_metrics['blocks_per_round']:.2f}")
        print(f"   ⚡ Consensus Efficiency: {consensus_metrics['consensus_efficiency']:.3f} blocks/second")
        
        # Throughput Analysis
        print(f"\n🚀 Throughput Analysis:")
        throughput_metrics = summary['throughput_metrics']
        print(f"   📊 Overall TPS: {throughput_metrics['overall_tps']:.2f} transactions/second")
        print(f"   ⚡ Peak TPS (5s window): {throughput_metrics['peak_tps']:.2f} transactions/second")
        print(f"   📈 Average TPS (10s window): {throughput_metrics['avg_tps_10s_window']:.2f} transactions/second")
        print(f"   📦 Transactions per Block: {throughput_metrics['transactions_per_block']:.2f}")
        
        # Node Performance
        print(f"\n🌐 Node Performance:")
        node_perf = summary['node_performance']
        for node_id, perf in sorted(node_perf.items()):
            success_rate = (perf['transactions_successful'] / max(1, perf['transactions_sent'])) * 100
            print(f"   📡 Node {node_id}: {perf['transactions_successful']}/{perf['transactions_sent']} tx ({success_rate:.1f}%), {perf['avg_response_time']*1000:.1f}ms avg, {perf['blocks_created']} blocks")
        
        # Performance Assessment
        print(f"\n🎯 Performance Assessment:")
        overall_tps = throughput_metrics['overall_tps']
        success_rate = summary['transaction_metrics']['success_rate_percent']
        blocks_created = consensus_metrics['total_blocks_created']
        
        if overall_tps >= 10 and success_rate >= 90 and blocks_created > 0:
            assessment = "🟢 Excellent Performance"
        elif overall_tps >= 5 and success_rate >= 80 and blocks_created > 0:
            assessment = "🟡 Good Performance"
        elif overall_tps >= 1 and success_rate >= 50:
            assessment = "🟠 Moderate Performance"
        else:
            assessment = "🔴 Performance Issues Detected"
        
        print(f"   {assessment}")
        print(f"   💡 Network can handle {overall_tps:.1f} TPS with {success_rate:.1f}% reliability")
        
        if blocks_created > 0:
            print(f"   ✅ Consensus working: {blocks_created} blocks created")
        else:
            print(f"   ⚠️  No blocks created during test period")

def main():
    """Main test execution"""
    print("🎯 FLEXIBLE PERFORMANCE TEST FRAMEWORK")
    print("📊 Comprehensive blockchain performance analysis")
    print("=" * 70)
    
    # Test configuration
    num_transactions = int(input("Enter number of transactions to generate (default 100): ") or "100")
    batch_size = int(input("Enter batch size for parallel processing (default 10): ") or "10")
    monitor_duration = int(input("Enter monitoring duration in seconds (default 30): ") or "30")
    
    print(f"\n🔧 Test Configuration:")
    print(f"   💳 Transactions: {num_transactions}")
    print(f"   📦 Batch Size: {batch_size}")
    print(f"   ⏱️  Monitor Duration: {monitor_duration}s")
    
    # Run test
    tester = FlexiblePerformanceTest()
    results = tester.run_performance_test(
        num_transactions=num_transactions,
        batch_size=batch_size,
        monitor_duration=monitor_duration
    )
    
    if results:
        print(f"\n🏁 Test completed successfully!")
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_test_{timestamp}.json"
        
        with open(filename, 'w') as f:
            # Convert any non-serializable objects
            serializable_results = {
                'summary': results['summary'],
                'test_config': {
                    'num_transactions': num_transactions,
                    'batch_size': batch_size,
                    'monitor_duration': monitor_duration
                },
                'timestamp': timestamp
            }
            json.dump(serializable_results, f, indent=2)
        
        print(f"   💾 Results saved to: {filename}")
    else:
        print(f"\n❌ Test failed to complete")

if __name__ == "__main__":
    main()
