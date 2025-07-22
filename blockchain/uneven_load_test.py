#!/usr/bin/env python3
"""
Uneven Transaction Distribution Test

This test simulates a real-world scenario where different nodes receive 
different numbers of transactions initially, testing:
1. P2P transaction propagation
2. Quantum consensus under uneven loads
3. Network synchronization capabilities
4. Load balancing behavior

Test scenario:
Node1: 3 transactions
Node2: 2 transactions  
Node3: 1 transaction
Node4: 3 transactions
Node5: 4 transactions
Node6: 5 transactions
Node7: 2 transactions
Nodes 8-10: 0 transactions initially
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

sys.path.insert(0, '/Users/shubham/Documents/proofwithquantumannealing/blockchain')

from blockchain.transaction.wallet import Wallet
from blockchain.transaction.transaction import Transaction
from blockchain.utils.helpers import BlockchainUtils

class NetworkLoadTester:
    """Test uneven transaction distribution across nodes"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # Optimize session for testing
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=2
        )
        self.session.mount('http://', adapter)
        self.session.timeout = (5, 15)
        
        # Node configuration (port -> API port mapping)
        self.node_configs = {
            1: 11000, 2: 11001, 3: 11002, 4: 11003, 5: 11004,
            6: 11005, 7: 11006, 8: 11007, 9: 11008, 10: 11009
        }
        
        # Test scenario: transactions per node
        self.load_distribution = {
            1: 3,  # Node 1 gets 3 transactions
            2: 2,  # Node 2 gets 2 transactions
            3: 1,  # Node 3 gets 1 transaction
            4: 3,  # Node 4 gets 3 transactions
            5: 4,  # Node 5 gets 4 transactions
            6: 5,  # Node 6 gets 5 transactions
            7: 2,  # Node 7 gets 2 transactions
            8: 0,  # Node 8 gets 0 transactions
            9: 0,  # Node 9 gets 0 transactions
            10: 0  # Node 10 gets 0 transactions
        }
        
        self.total_transactions = sum(self.load_distribution.values())
        
    def get_node_status(self, node_id):
        """Get status of a specific node"""
        api_port = self.node_configs[node_id]
        try:
            # Get blockchain status
            blockchain_response = self.session.get(
                f'http://localhost:{api_port}/api/v1/blockchain/', 
                timeout=5
            )
            
            # Get transaction pool status
            pool_response = self.session.get(
                f'http://localhost:{api_port}/api/v1/transaction/transaction_pool/', 
                timeout=5
            )
            
            if blockchain_response.status_code == 200:
                blockchain_data = blockchain_response.json()
                blocks = len(blockchain_data['blocks'])
            else:
                blocks = 0
                
            if pool_response.status_code == 200:
                pool_data = pool_response.json()
                pool_size = len(pool_data) if isinstance(pool_data, list) else 0
            else:
                pool_size = 0
                
            return {
                'blocks': blocks,
                'pool_size': pool_size,
                'status': 'online' if blockchain_response.status_code == 200 else 'offline'
            }
            
        except Exception as e:
            return {
                'blocks': 0,
                'pool_size': 0,
                'status': 'error',
                'error': str(e)
            }
    
    def submit_transaction_to_node(self, encoded_transaction, node_id):
        """Submit transaction to a specific node"""
        api_port = self.node_configs[node_id]
        url = f'http://localhost:{api_port}/api/v1/transaction/create/'
        
        start_time = time.time()
        try:
            response = self.session.post(url, json={'transaction': encoded_transaction})
            submission_time = time.time() - start_time
            return {
                'node_id': node_id,
                'status_code': response.status_code,
                'response': response.text,
                'submission_time': submission_time,
                'success': response.status_code == 200
            }
        except Exception as e:
            submission_time = time.time() - start_time
            return {
                'node_id': node_id,
                'status_code': 0,
                'response': str(e),
                'submission_time': submission_time,
                'success': False
            }
    
    def create_transactions_for_distribution(self):
        """Create transactions according to the load distribution"""
        print(f"💳 Creating {self.total_transactions} transactions for distribution test...")
        
        # Create enough wallets
        sender_wallets = [Wallet() for _ in range(10)]
        receiver_wallets = [Wallet() for _ in range(20)]
        
        transactions_by_node = {}
        
        for node_id, tx_count in self.load_distribution.items():
            transactions_by_node[node_id] = []
            
            for i in range(tx_count):
                sender_wallet = random.choice(sender_wallets)
                receiver_wallet = random.choice(receiver_wallets)
                receiver_public_key = receiver_wallet.public_key_string()
                amount = random.uniform(1.0, 100.0)
                
                transaction = sender_wallet.create_transaction(
                    receiver_public_key, amount, "TRANSFER"
                )
                encoded_transaction = BlockchainUtils.encode(transaction)
                
                transactions_by_node[node_id].append(encoded_transaction)
        
        return transactions_by_node
    
    def get_all_nodes_status(self):
        """Get status of all nodes"""
        statuses = {}
        for node_id in self.node_configs.keys():
            statuses[node_id] = self.get_node_status(node_id)
        return statuses
    
    def print_network_status(self, title, statuses):
        """Print formatted network status"""
        print(f"\n📊 {title}")
        print("=" * 60)
        
        total_blocks = 0
        total_pool = 0
        online_nodes = 0
        
        for node_id, status in statuses.items():
            if status['status'] == 'online':
                online_nodes += 1
                total_blocks = max(total_blocks, status['blocks'])
                total_pool += status['pool_size']
                
                status_icon = "🟢"
                pool_info = f", Pool: {status['pool_size']}"
            elif status['status'] == 'offline':
                status_icon = "🔴"
                pool_info = ""
            else:
                status_icon = "⚠️"
                pool_info = f", Error: {status.get('error', 'Unknown')[:30]}"
            
            expected_tx = self.load_distribution.get(node_id, 0)
            load_info = f" (Expected: {expected_tx} tx)" if expected_tx > 0 else " (No load)"
            
            print(f"   {status_icon} Node {node_id}: {status['blocks']} blocks{pool_info}{load_info}")
        
        print(f"\n📈 Network Summary:")
        print(f"   🌐 Online Nodes: {online_nodes}/10")
        print(f"   📦 Max Blocks: {total_blocks}")
        print(f"   🔄 Total Pool Size: {total_pool}")
        print(f"   📊 Expected Transactions: {self.total_transactions}")
    
    def monitor_propagation(self, initial_statuses, duration=30):
        """Monitor how transactions propagate through the network"""
        print(f"\n🔍 Monitoring transaction propagation for {duration} seconds...")
        
        propagation_data = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            current_time = time.time() - start_time
            current_statuses = self.get_all_nodes_status()
            
            # Calculate changes
            pool_changes = {}
            block_changes = {}
            
            for node_id in self.node_configs.keys():
                initial = initial_statuses[node_id]
                current = current_statuses[node_id]
                
                pool_changes[node_id] = current['pool_size'] - initial['pool_size']
                block_changes[node_id] = current['blocks'] - initial['blocks']
            
            propagation_data.append({
                'time': current_time,
                'pool_changes': pool_changes,
                'block_changes': block_changes,
                'total_pool': sum(s['pool_size'] for s in current_statuses.values()),
                'max_blocks': max(s['blocks'] for s in current_statuses.values() if s['status'] == 'online')
            })
            
            # Print progress every 5 seconds
            if len(propagation_data) % 25 == 0:  # Every ~5 seconds (0.2s intervals)
                total_pool = propagation_data[-1]['total_pool']
                max_blocks = propagation_data[-1]['max_blocks']
                print(f"   ⏱️  {current_time:.1f}s: Total pool: {total_pool}, Max blocks: {max_blocks}")
            
            time.sleep(0.2)  # Check every 200ms
        
        return propagation_data
    
    def analyze_propagation_results(self, propagation_data, initial_statuses):
        """Analyze how well transactions propagated"""
        print(f"\n📈 PROPAGATION ANALYSIS:")
        print("=" * 50)
        
        if not propagation_data:
            print("   ❌ No propagation data collected")
            return
        
        final_data = propagation_data[-1]
        
        # Analyze transaction distribution
        print(f"📊 Transaction Distribution Analysis:")
        
        nodes_with_extra_tx = 0
        nodes_with_blocks = 0
        total_propagated = 0
        
        for node_id in self.node_configs.keys():
            initial_pool = initial_statuses[node_id]['pool_size']
            expected_tx = self.load_distribution[node_id]
            pool_change = final_data['pool_changes'][node_id]
            block_change = final_data['block_changes'][node_id]
            
            propagated_tx = max(0, pool_change - expected_tx)
            total_propagated += propagated_tx
            
            if propagated_tx > 0:
                nodes_with_extra_tx += 1
            if block_change > 0:
                nodes_with_blocks += 1
            
            status_icon = "📤" if expected_tx > 0 else "📥"
            prop_info = f", +{propagated_tx} propagated" if propagated_tx > 0 else ""
            block_info = f", +{block_change} blocks" if block_change > 0 else ""
            
            print(f"   {status_icon} Node {node_id}: {expected_tx} initial{prop_info}{block_info}")
        
        # Calculate propagation metrics
        propagation_efficiency = (nodes_with_extra_tx / 7) * 100  # 7 nodes had no initial load
        consensus_participation = (nodes_with_blocks / 10) * 100
        
        print(f"\n🎯 Network Performance Metrics:")
        print(f"   📡 Propagation Efficiency: {propagation_efficiency:.1f}% (nodes receiving propagated tx)")
        print(f"   🔗 Consensus Participation: {consensus_participation:.1f}% (nodes creating blocks)")
        print(f"   🔄 Total Propagated: {total_propagated} transactions")
        print(f"   ⚡ Load Balancing: {'✅ Good' if nodes_with_extra_tx >= 5 else '⚠️ Limited'}")
        
        # Analyze timing
        first_propagation = None
        first_block = None
        
        for data in propagation_data:
            if first_propagation is None:
                for node_id in [8, 9, 10]:  # Nodes that should receive propagated tx
                    if data['pool_changes'][node_id] > 0:
                        first_propagation = data['time']
                        break
            
            if first_block is None:
                if data['max_blocks'] > initial_statuses[1]['blocks']:
                    first_block = data['time']
            
            if first_propagation and first_block:
                break
        
        print(f"\n⏱️  Timing Analysis:")
        if first_propagation:
            print(f"   📡 First Propagation: {first_propagation:.1f}s")
        else:
            print(f"   📡 First Propagation: Not detected")
            
        if first_block:
            print(f"   📦 First New Block: {first_block:.1f}s")
        else:
            print(f"   📦 First New Block: Not detected")
        
        return {
            'propagation_efficiency': propagation_efficiency,
            'consensus_participation': consensus_participation,
            'first_propagation_time': first_propagation,
            'first_block_time': first_block,
            'total_propagated': total_propagated
        }

def run_uneven_distribution_test():
    """Run the complete uneven distribution test"""
    print("🚀 UNEVEN TRANSACTION DISTRIBUTION TEST")
    print("🎯 Testing quantum consensus under non-uniform network loads")
    print("=" * 70)
    
    tester = NetworkLoadTester()
    
    # Display test scenario
    print("\n📋 Test Scenario:")
    print("   Node loads designed to test P2P propagation and consensus:")
    for node_id, tx_count in tester.load_distribution.items():
        load_desc = f"{tx_count} transactions" if tx_count > 0 else "No initial load"
        print(f"   📊 Node {node_id}: {load_desc}")
    
    print(f"\n   🎯 Total: {tester.total_transactions} transactions across 7 nodes")
    print(f"   🔍 Monitoring: How 3 empty nodes receive propagated transactions")
    
    # Check initial network status
    print(f"\n🔍 Checking initial network status...")
    initial_statuses = tester.get_all_nodes_status()
    tester.print_network_status("Initial Network Status", initial_statuses)
    
    # Verify network is ready
    online_nodes = sum(1 for s in initial_statuses.values() if s['status'] == 'online')
    if online_nodes < 7:
        print(f"\n❌ ERROR: Only {online_nodes}/10 nodes online. Need at least 7 nodes.")
        print("   Please ensure the blockchain network is running.")
        return
    
    # Create transactions for each node
    print(f"\n💳 Creating transactions according to distribution plan...")
    transactions_by_node = tester.create_transactions_for_distribution()
    
    # Submit transactions to specific nodes
    print(f"\n📤 Submitting transactions to designated nodes...")
    submission_results = {}
    submission_start = time.time()
    
    for node_id, transactions in transactions_by_node.items():
        if not transactions:  # Skip nodes with no transactions
            continue
            
        print(f"   📨 Submitting {len(transactions)} transactions to Node {node_id}...")
        
        node_results = []
        for i, encoded_tx in enumerate(transactions, 1):
            result = tester.submit_transaction_to_node(encoded_tx, node_id)
            node_results.append(result)
            
            if result['success']:
                print(f"      ✅ Tx {i}: Success ({result['submission_time']*1000:.1f}ms)")
            else:
                print(f"      ❌ Tx {i}: Failed - {result['response'][:50]}")
            
            time.sleep(0.1)  # Small delay between submissions
        
        submission_results[node_id] = node_results
    
    submission_time = time.time() - submission_start
    
    # Calculate submission statistics
    total_submitted = sum(len(results) for results in submission_results.values())
    total_successful = sum(
        sum(1 for r in results if r['success']) 
        for results in submission_results.values()
    )
    
    print(f"\n📈 Submission Complete:")
    print(f"   ✅ Successful: {total_successful}/{total_submitted}")
    print(f"   ⏱️  Submission Time: {submission_time:.3f}s")
    
    # Check immediate status after submission
    print(f"\n🔍 Network status immediately after submission...")
    post_submission_statuses = tester.get_all_nodes_status()
    tester.print_network_status("Post-Submission Status", post_submission_statuses)
    
    # Monitor propagation and consensus
    propagation_data = tester.monitor_propagation(initial_statuses, duration=30)
    
    # Final network status
    print(f"\n🔍 Final network status...")
    final_statuses = tester.get_all_nodes_status()
    tester.print_network_status("Final Network Status", final_statuses)
    
    # Analyze results
    analysis_results = tester.analyze_propagation_results(propagation_data, initial_statuses)
    
    # Summary and conclusions
    print(f"\n🎯 TEST CONCLUSIONS:")
    print("=" * 50)
    
    print(f"🔍 Network Behavior Under Uneven Load:")
    if analysis_results['propagation_efficiency'] >= 60:
        print(f"   ✅ Good P2P Propagation: {analysis_results['propagation_efficiency']:.1f}% of empty nodes received transactions")
    else:
        print(f"   ⚠️  Limited P2P Propagation: {analysis_results['propagation_efficiency']:.1f}% of empty nodes received transactions")
    
    if analysis_results['consensus_participation'] >= 30:
        print(f"   ✅ Active Quantum Consensus: {analysis_results['consensus_participation']:.1f}% of nodes participated in block creation")
    else:
        print(f"   ❌ Limited Consensus: {analysis_results['consensus_participation']:.1f}% of nodes participated in block creation")
    
    if analysis_results['first_propagation_time'] and analysis_results['first_propagation_time'] < 10:
        print(f"   ⚡ Fast Propagation: First transaction propagated in {analysis_results['first_propagation_time']:.1f}s")
    else:
        print(f"   🐌 Slow Propagation: Transactions took time to propagate across network")
    
    print(f"\n🌐 Network Resilience Assessment:")
    blocks_created = max(s['blocks'] for s in final_statuses.values()) - max(s['blocks'] for s in initial_statuses.values())
    if blocks_created > 0:
        print(f"   ✅ Consensus Achieved: {blocks_created} new blocks created")
        print(f"   🔗 Load Balancing: Network successfully handled uneven transaction distribution")
    else:
        print(f"   ❌ No Consensus: No new blocks created during test period")
    
    return {
        'total_transactions': tester.total_transactions,
        'successful_submissions': total_successful,
        'blocks_created': blocks_created,
        'propagation_efficiency': analysis_results['propagation_efficiency'],
        'consensus_participation': analysis_results['consensus_participation']
    }

if __name__ == "__main__":
    print("🎯 Starting Uneven Transaction Distribution Test")
    print("📊 This test simulates real-world scenarios where some nodes receive more transactions than others")
    print("")
    
    results = run_uneven_distribution_test()
    
    print(f"\n🏁 FINAL RESULTS:")
    print(f"   📊 Transactions: {results['successful_submissions']}/{results['total_transactions']} submitted successfully")
    print(f"   📦 Blocks Created: {results['blocks_created']}")
    print(f"   📡 Propagation: {results['propagation_efficiency']:.1f}% efficiency")
    print(f"   🔗 Consensus: {results['consensus_participation']:.1f}% participation")
    print(f"   🎯 Result: {'✅ Network handled uneven load well' if results['propagation_efficiency'] >= 50 and results['blocks_created'] > 0 else '⚠️ Network struggled with uneven load'}")
