#!/usr/bin/env python3
"""
100 Transaction Stress Test for Quantum Annealing Blockchain

This script sends 100 transactions to test the quantum consensus mechanism
and monitors which nodes get to propose blocks.
"""

import json
import time
import requests
import threading
from datetime import datetime
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import string
import sys
import os

# Add the parent directory to Python path to find blockchain modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from blockchain.transaction.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils

class TransactionStressTester:
    def __init__(self, num_nodes=50, base_api_port=8050, num_transactions=100):
        self.num_nodes = num_nodes
        self.base_api_port = base_api_port
        self.num_transactions = num_transactions
        
        # Create wallets for testing
        self.wallets = []
        print("🔧 Creating test wallets...")
        for i in range(min(20, num_transactions // 2)):  # Create up to 20 wallets
            wallet = Wallet()
            self.wallets.append(wallet)
        print(f"✅ Created {len(self.wallets)} test wallets")
        
        # Transaction tracking
        self.transactions_sent = []
        self.transaction_results = []
        self.block_proposals = {}  # Track which nodes propose blocks
        self.quantum_metrics_before = {}
        self.quantum_metrics_after = {}
        
        # Test configuration
        self.batch_size = 10  # Send transactions in batches
        self.batch_delay = 1.0  # Delay between batches in seconds
    
    def generate_random_transaction(self, tx_id):
        """Generate a random transaction using proper wallet format"""
        # Randomly select sender and receiver wallets
        sender_wallet = random.choice(self.wallets)
        receiver_wallet = random.choice([w for w in self.wallets if w != sender_wallet])
        
        amount = round(random.uniform(0.1, 100.0), 2)
        transaction_type = random.choice(["transfer", "payment", "exchange"])
        
        # Create proper transaction using wallet
        transaction = sender_wallet.create_transaction(
            receiver_wallet.public_key_string(), 
            amount, 
            transaction_type
        )
        
        return {
            "tx_id": tx_id,
            "transaction": transaction,
            "sender": sender_wallet.public_key_string()[:16] + "...",
            "receiver": receiver_wallet.public_key_string()[:16] + "...",
            "amount": amount,
            "timestamp": datetime.now().isoformat(),
            "type": transaction_type
        }
    
    def find_available_nodes(self):
        """Find which nodes are available for testing"""
        available_nodes = []
        print("🔍 Discovering available nodes...")
        
        for node_id in range(self.num_nodes):
            api_port = self.base_api_port + node_id
            try:
                response = requests.get(
                    f"http://localhost:{api_port}/api/v1/blockchain/",
                    timeout=2
                )
                if response.status_code == 200:
                    available_nodes.append({
                        'node_id': node_id,
                        'api_port': api_port,
                        'status': 'available'
                    })
                    print(f"   ✅ Node {node_id} (port {api_port}) - Available")
                else:
                    print(f"   ⚠️  Node {node_id} (port {api_port}) - HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ Node {node_id} (port {api_port}) - Offline")
        
        print(f"\n📊 Found {len(available_nodes)} available nodes out of {self.num_nodes}")
        return available_nodes
    
    def collect_quantum_metrics_snapshot(self, available_nodes):
        """Collect quantum metrics from all available nodes"""
        metrics = {}
        print("📊 Collecting quantum metrics snapshot...")
        
        for node in available_nodes:
            try:
                response = requests.get(
                    f"http://localhost:{node['api_port']}/api/v1/blockchain/quantum-metrics/",
                    timeout=3
                )
                if response.status_code == 200:
                    data = response.json()
                    metrics[node['node_id']] = {
                        'total_nodes': data.get('total_nodes', 0),
                        'active_nodes': data.get('active_nodes', 0),
                        'probe_count': data.get('probe_count', 0),
                        'suitability_score': data.get('suitability_score', 0.0),
                        'successful_proposals': data.get('successful_proposals', 0),
                        'timestamp': datetime.now().isoformat()
                    }
                    print(f"   ✅ Node {node['node_id']}: "
                          f"probes={data.get('probe_count', 0)}, "
                          f"score={data.get('suitability_score', 0.0):.4f}")
                else:
                    print(f"   ⚠️  Node {node['node_id']}: Failed to get quantum metrics")
            except Exception as e:
                print(f"   ❌ Node {node['node_id']}: Error - {e}")
        
        print(f"📈 Collected metrics from {len(metrics)} nodes\n")
        return metrics
    
    def send_single_transaction(self, transaction_data, target_node):
        """Send a single transaction to a specific node"""
        try:
            start_time = time.time()
            
            # Prepare the transaction package in the correct format
            package = {"transaction": BlockchainUtils.encode(transaction_data["transaction"])}
            
            response = requests.post(
                f"http://localhost:{target_node['api_port']}/api/v1/transaction/create/",
                json=package,
                timeout=5
            )
            end_time = time.time()
            
            return {
                'tx_id': transaction_data['tx_id'],
                'target_node': target_node['node_id'],
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'success': response.status_code == 200,
                'response_data': response.json() if response.status_code == 200 else response.text,
                'timestamp': datetime.now().isoformat(),
                'amount': transaction_data['amount'],
                'type': transaction_data['type']
            }
        except Exception as e:
            return {
                'tx_id': transaction_data['tx_id'],
                'target_node': target_node['node_id'],
                'status_code': 0,
                'response_time': 999.0,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'amount': transaction_data.get('amount', 0),
                'type': transaction_data.get('type', 'unknown')
            }
    
    def send_transaction_batch(self, batch_transactions, available_nodes):
        """Send a batch of transactions in parallel"""
        batch_results = []
        
        with ThreadPoolExecutor(max_workers=min(10, len(batch_transactions))) as executor:
            future_to_tx = {}
            
            for transaction_data in batch_transactions:
                # Randomly select a node to send the transaction to
                target_node = random.choice(available_nodes)
                future = executor.submit(self.send_single_transaction, transaction_data, target_node)
                future_to_tx[future] = transaction_data['tx_id']
            
            for future in as_completed(future_to_tx):
                result = future.result()
                batch_results.append(result)
        
        return batch_results
    
    def monitor_block_creation(self, available_nodes, duration_seconds=30):
        """Monitor which nodes create blocks during the test"""
        print(f"🔍 Monitoring block creation for {duration_seconds} seconds...")
        
        # Get initial block counts
        initial_blocks = {}
        for node in available_nodes:
            try:
                response = requests.get(
                    f"http://localhost:{node['api_port']}/api/v1/blockchain/",
                    timeout=3
                )
                if response.status_code == 200:
                    data = response.json()
                    initial_blocks[node['node_id']] = len(data.get('blocks', []))
            except:
                initial_blocks[node['node_id']] = 0
        
        # Monitor for new blocks
        start_time = time.time()
        block_events = []
        
        while time.time() - start_time < duration_seconds:
            for node in available_nodes:
                try:
                    response = requests.get(
                        f"http://localhost:{node['api_port']}/api/v1/blockchain/",
                        timeout=2
                    )
                    if response.status_code == 200:
                        data = response.json()
                        current_blocks = len(data.get('blocks', []))
                        initial_count = initial_blocks.get(node['node_id'], 0)
                        
                        if current_blocks > initial_count:
                            # New block detected
                            new_blocks = current_blocks - initial_count
                            for i in range(new_blocks):
                                block_events.append({
                                    'proposer_node': node['node_id'],
                                    'block_height': initial_count + i + 1,
                                    'timestamp': datetime.now().isoformat()
                                })
                            initial_blocks[node['node_id']] = current_blocks
                            print(f"   🎯 Node {node['node_id']} proposed new block(s)! Total: {current_blocks}")
                except:
                    pass
            
            time.sleep(2)  # Check every 2 seconds
        
        return block_events
    
    def run_stress_test(self):
        """Run the complete stress test"""
        print("🚀 STARTING 100-TRANSACTION STRESS TEST")
        print("=" * 60)
        
        # Step 1: Find available nodes
        available_nodes = self.find_available_nodes()
        if len(available_nodes) == 0:
            print("❌ No available nodes found! Please start some nodes first.")
            return
        
        # Step 2: Collect initial quantum metrics
        print("\n" + "="*60)
        print("📊 COLLECTING INITIAL METRICS")
        print("="*60)
        self.quantum_metrics_before = self.collect_quantum_metrics_snapshot(available_nodes)
        
        # Step 3: Generate all transactions
        print("🔧 Generating 100 test transactions...")
        all_transactions = []
        for i in range(self.num_transactions):
            transaction = self.generate_random_transaction(f"stress_test_{i+1}")
            all_transactions.append(transaction)
        print(f"✅ Generated {len(all_transactions)} transactions\n")
        
        # Step 4: Start block monitoring in background
        block_monitor_thread = threading.Thread(
            target=lambda: setattr(self, 'block_events', 
                                  self.monitor_block_creation(available_nodes, duration_seconds=60))
        )
        block_monitor_thread.daemon = True
        block_monitor_thread.start()
        
        # Step 5: Send transactions in batches
        print("="*60)
        print("📤 SENDING TRANSACTIONS")
        print("="*60)
        
        all_results = []
        successful_transactions = 0
        failed_transactions = 0
        
        for batch_num in range(0, len(all_transactions), self.batch_size):
            batch_end = min(batch_num + self.batch_size, len(all_transactions))
            batch_transactions = all_transactions[batch_num:batch_end]
            
            print(f"🔄 Sending batch {batch_num//self.batch_size + 1}: "
                  f"transactions {batch_num+1}-{batch_end}")
            
            # Send batch
            batch_start_time = time.time()
            batch_results = self.send_transaction_batch(batch_transactions, available_nodes)
            batch_end_time = time.time()
            
            # Process results
            batch_success = sum(1 for r in batch_results if r['success'])
            batch_failed = len(batch_results) - batch_success
            successful_transactions += batch_success
            failed_transactions += batch_failed
            
            all_results.extend(batch_results)
            
            print(f"   ✅ Batch completed: {batch_success}/{len(batch_results)} successful "
                  f"(took {batch_end_time - batch_start_time:.2f}s)")
            
            # Brief delay between batches
            if batch_end < len(all_transactions):
                time.sleep(self.batch_delay)
        
        # Step 6: Wait for block monitoring to complete
        print(f"\n⏱️  Waiting for block monitoring to complete...")
        block_monitor_thread.join(timeout=30)
        
        # Step 7: Collect final quantum metrics
        print("\n" + "="*60)
        print("📊 COLLECTING FINAL METRICS")
        print("="*60)
        self.quantum_metrics_after = self.collect_quantum_metrics_snapshot(available_nodes)
        
        # Step 8: Generate comprehensive report
        self.generate_comprehensive_report(all_results, successful_transactions, failed_transactions)
    
    def generate_comprehensive_report(self, transaction_results, successful_tx, failed_tx):
        """Generate a comprehensive test report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE STRESS TEST REPORT")
        print("="*80)
        
        # Transaction Summary
        print("\n🔥 TRANSACTION SUMMARY")
        print("-" * 40)
        print(f"Total Transactions Sent: {len(transaction_results)}")
        print(f"Successful Transactions: {successful_tx} ({successful_tx/len(transaction_results)*100:.1f}%)")
        print(f"Failed Transactions: {failed_tx} ({failed_tx/len(transaction_results)*100:.1f}%)")
        
        # Performance Metrics
        response_times = [r['response_time'] for r in transaction_results if r['success']]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            print(f"\n⚡ PERFORMANCE METRICS")
            print("-" * 40)
            print(f"Average Response Time: {avg_response_time:.3f}s")
            print(f"Min Response Time: {min_response_time:.3f}s")
            print(f"Max Response Time: {max_response_time:.3f}s")
        
        # Node Usage Distribution
        node_usage = {}
        for result in transaction_results:
            node_id = result['target_node']
            if node_id not in node_usage:
                node_usage[node_id] = {'total': 0, 'successful': 0}
            node_usage[node_id]['total'] += 1
            if result['success']:
                node_usage[node_id]['successful'] += 1
        
        print(f"\n🎯 NODE USAGE DISTRIBUTION")
        print("-" * 40)
        for node_id in sorted(node_usage.keys()):
            stats = node_usage[node_id]
            success_rate = stats['successful'] / stats['total'] * 100 if stats['total'] > 0 else 0
            print(f"Node {node_id:2}: {stats['total']:2} txs, {stats['successful']:2} successful ({success_rate:5.1f}%)")
        
        # Block Proposal Analysis
        if hasattr(self, 'block_events'):
            print(f"\n🏗️  BLOCK PROPOSAL ANALYSIS")
            print("-" * 40)
            if self.block_events:
                proposer_counts = {}
                for event in self.block_events:
                    proposer = event['proposer_node']
                    proposer_counts[proposer] = proposer_counts.get(proposer, 0) + 1
                
                print(f"Total Blocks Created: {len(self.block_events)}")
                print("Block Proposers:")
                for proposer in sorted(proposer_counts.keys()):
                    count = proposer_counts[proposer]
                    percentage = count / len(self.block_events) * 100
                    print(f"  Node {proposer:2}: {count:2} blocks ({percentage:5.1f}%)")
            else:
                print("No new blocks were created during the test period")
        
        # Quantum Metrics Comparison
        print(f"\n🔬 QUANTUM METRICS COMPARISON")
        print("-" * 40)
        print("Before Test vs After Test:")
        
        all_node_ids = set(self.quantum_metrics_before.keys()) | set(self.quantum_metrics_after.keys())
        for node_id in sorted(all_node_ids):
            before = self.quantum_metrics_before.get(node_id, {})
            after = self.quantum_metrics_after.get(node_id, {})
            
            before_probes = before.get('probe_count', 0)
            after_probes = after.get('probe_count', 0)
            probe_increase = after_probes - before_probes
            
            before_score = before.get('suitability_score', 0.0)
            after_score = after.get('suitability_score', 0.0)
            score_change = after_score - before_score
            
            print(f"  Node {node_id:2}: Probes {before_probes:3} → {after_probes:3} (+{probe_increase:2}), "
                  f"Score {before_score:.4f} → {after_score:.4f} ({score_change:+.4f})")
        
        # Top Performers Analysis
        print(f"\n🏆 TOP PERFORMING NODES")
        print("-" * 40)
        
        # Rank by final suitability score
        node_rankings = []
        for node_id, metrics in self.quantum_metrics_after.items():
            node_rankings.append({
                'node_id': node_id,
                'suitability_score': metrics.get('suitability_score', 0.0),
                'probe_count': metrics.get('probe_count', 0),
                'successful_proposals': metrics.get('successful_proposals', 0)
            })
        
        node_rankings.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        print("Ranked by Suitability Score:")
        for i, node in enumerate(node_rankings[:10]):  # Top 10
            print(f"  {i+1:2}. Node {node['node_id']:2}: Score {node['suitability_score']:.4f}, "
                  f"Probes {node['probe_count']:3}, Proposals {node['successful_proposals']}")
        
        print(f"\n✅ STRESS TEST COMPLETED SUCCESSFULLY!")
        print("="*80)


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="100 Transaction Stress Test")
    parser.add_argument("--nodes", type=int, default=50, help="Number of nodes to test against")
    parser.add_argument("--transactions", type=int, default=100, help="Number of transactions to send")
    parser.add_argument("--api-port", type=int, default=8050, help="Base API port")
    parser.add_argument("--batch-size", type=int, default=10, help="Transaction batch size")
    parser.add_argument("--batch-delay", type=float, default=1.0, help="Delay between batches (seconds)")
    
    args = parser.parse_args()
    
    # Create and run stress tester
    tester = TransactionStressTester(
        num_nodes=args.nodes,
        base_api_port=args.api_port,
        num_transactions=args.transactions
    )
    
    tester.batch_size = args.batch_size
    tester.batch_delay = args.batch_delay
    
    tester.run_stress_test()


if __name__ == "__main__":
    main()
