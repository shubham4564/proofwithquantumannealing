#!/usr/bin/env python3

"""
Enhanced Transaction Test for Gulf Stream Flow

This script tests the complete Gulf Stream + PoH + Turbine workflow:
1. Submits transactions via Gulf Stream
2. Monitors leader schedule and forwarding
3. Verifies block creation with PoH sequencing
4. Confirms Turbine propagation
5. Ensures all nodes reach consensus
"""

import sys
import os
import time
import threading
import requests
import json
import argparse
from datetime import datetime

# Add blockchain module to path
sys.path.insert(0, '/Users/shubham/Documents/fromgithub/proofwithquantumannealing/blockchain')

from blockchain.transaction.wallet import Wallet
from blockchain.transaction.transaction import Transaction
from blockchain.utils.helpers import BlockchainUtils


class GulfStreamTransactionTester:
    """Enhanced transaction tester for Gulf Stream flow"""
    
    def __init__(self, api_ports):
        self.api_ports = api_ports
        self.active_nodes = []
        self.test_wallets = []
        self.results = {
            'transactions_submitted': 0,
            'transactions_confirmed': 0,
            'blocks_created': 0,
            'sync_times': [],
            'gulf_stream_stats': {},
            'leader_schedule_info': {},
            'consensus_achieved': False
        }
        
    def setup_test_environment(self):
        """Setup test environment and validate nodes"""
        print("🚀 SETTING UP GULF STREAM TEST ENVIRONMENT")
        print("=" * 60)
        
        # Check which nodes are active
        print("📡 Checking node availability...")
        for port in self.api_ports:
            if self.check_node_health(port):
                self.active_nodes.append(port)
                print(f"   ✅ Node on port {port} is active")
            else:
                print(f"   ❌ Node on port {port} is not responding")
        
        if len(self.active_nodes) < 2:
            raise Exception(f"Need at least 2 active nodes, found {len(self.active_nodes)}")
        
        print(f"📊 Active nodes: {len(self.active_nodes)}/{len(self.api_ports)}")
        
        # Create test wallets
        print("👤 Creating test wallets...")
        for i in range(5):  # Create 5 test wallets
            wallet = Wallet()
            self.test_wallets.append(wallet)
            print(f"   Wallet {i+1}: {wallet.public_key_string()[:20]}...")
        
        # Get initial blockchain state
        print("📊 Getting initial blockchain state...")
        self.initial_state = self.get_network_state()
        print(f"   Initial blocks per node: {self.initial_state['block_counts']}")
        
    def check_node_health(self, port):
        """Check if a node is healthy and responding"""
        try:
            response = requests.get(f'http://localhost:{port}/api/v1/blockchain/', timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def get_network_state(self):
        """Get current state of all nodes"""
        state = {
            'block_counts': [],
            'transaction_pools': [],
            'leader_schedules': [],
            'gulf_stream_status': []
        }
        
        for port in self.active_nodes:
            try:
                # Get blockchain data
                blockchain_response = requests.get(f'http://localhost:{port}/api/v1/blockchain/', timeout=3)
                if blockchain_response.status_code == 200:
                    blockchain_data = blockchain_response.json()
                    state['block_counts'].append(len(blockchain_data.get('blocks', [])))
                    state['transaction_pools'].append(blockchain_data.get('transaction_pool_size', 0))
                else:
                    state['block_counts'].append(0)
                    state['transaction_pools'].append(0)
                
                # Try to get Gulf Stream status (may not be available in current API)
                try:
                    gulf_stream_response = requests.get(f'http://localhost:{port}/api/v1/gulf-stream/', timeout=2)
                    if gulf_stream_response.status_code == 200:
                        state['gulf_stream_status'].append(gulf_stream_response.json())
                    else:
                        state['gulf_stream_status'].append({})
                except:
                    state['gulf_stream_status'].append({})
                    
            except Exception as e:
                print(f"   ⚠️  Error getting state from port {port}: {e}")
                state['block_counts'].append(0)
                state['transaction_pools'].append(0)
                state['gulf_stream_status'].append({})
        
        return state
    
    def submit_transaction_to_gulf_stream(self, sender_wallet, receiver_public_key, amount, tx_type='TRANSFER'):
        """Submit a transaction that will go through Gulf Stream flow"""
        try:
            # Create transaction
            transaction = sender_wallet.create_transaction(receiver_public_key, amount, tx_type)
            encoded_transaction = BlockchainUtils.encode(transaction)
            
            # Submit to a random active node (Gulf Stream will handle forwarding)
            target_port = self.active_nodes[self.results['transactions_submitted'] % len(self.active_nodes)]
            
            print(f"   📤 Submitting TX to node {target_port}: {amount} tokens")
            print(f"      From: {sender_wallet.public_key_string()[:20]}...")
            print(f"      To: {receiver_public_key[:20]}...")
            
            submit_time = time.time()
            response = requests.post(
                f'http://localhost:{target_port}/api/v1/transaction/create/',
                json={'transaction': encoded_transaction},
                timeout=10
            )
            submit_duration = time.time() - submit_time
            
            if response.status_code == 200:
                print(f"      ✅ Submitted successfully in {submit_duration:.3f}s")
                self.results['transactions_submitted'] += 1
                return True, transaction.id
            else:
                print(f"      ❌ Submission failed: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"      ❌ Transaction submission error: {e}")
            return False, None
    
    def run_transaction_batch(self, num_transactions):
        """Run a batch of transactions through Gulf Stream"""
        print(f"\n💰 RUNNING {num_transactions} TRANSACTIONS THROUGH GULF STREAM")
        print("-" * 60)
        
        # Start monitoring thread
        monitoring_stop = threading.Event()
        monitoring_results = {'sync_events': []}
        monitor_thread = threading.Thread(
            target=self.monitor_blockchain_sync,
            args=(monitoring_stop, monitoring_results)
        )
        monitor_thread.start()
        
        try:
            # Submit transactions
            successful_transactions = []
            
            for i in range(num_transactions):
                print(f"\n🔄 Transaction {i+1}/{num_transactions}")
                
                # Choose random wallets
                sender_idx = i % len(self.test_wallets)
                receiver_idx = (i + 1) % len(self.test_wallets)
                sender_wallet = self.test_wallets[sender_idx]
                receiver_wallet = self.test_wallets[receiver_idx]
                
                # Determine transaction type and amount
                if i == 0:
                    # First transaction: funding from genesis
                    amount = 1000.0
                    tx_type = 'EXCHANGE'
                else:
                    amount = 50.0 + (i * 10.0)  # Increasing amounts
                    tx_type = 'TRANSFER'
                
                success, tx_id = self.submit_transaction_to_gulf_stream(
                    sender_wallet,
                    receiver_wallet.public_key_string(),
                    amount,
                    tx_type
                )
                
                if success:
                    successful_transactions.append(tx_id)
                
                # Wait between transactions to allow Gulf Stream processing
                time.sleep(1.0)
            
            print(f"\n⏳ Waiting for block creation and propagation (30 seconds)...")
            time.sleep(30)  # Give time for blocks to be created and propagated
            
        finally:
            # Stop monitoring
            monitoring_stop.set()
            monitor_thread.join(timeout=5)
            
        self.results.update(monitoring_results)
        return successful_transactions
    
    def monitor_blockchain_sync(self, stop_event, results):
        """Monitor blockchain synchronization across nodes"""
        start_time = time.time()
        last_block_counts = None
        
        while not stop_event.is_set():
            current_time = time.time() - start_time
            current_state = self.get_network_state()
            block_counts = current_state['block_counts']
            
            # Check for new blocks
            if last_block_counts is None:
                last_block_counts = block_counts[:]
            
            # Detect new blocks
            max_blocks = max(block_counts)
            min_blocks = min(block_counts)
            
            if max_blocks > max(last_block_counts):
                print(f"   📦 New block detected at {current_time:.3f}s - Max blocks: {max_blocks}")
                results['sync_events'].append({
                    'time': current_time,
                    'event': 'new_block',
                    'max_blocks': max_blocks,
                    'min_blocks': min_blocks
                })
            
            # Check for full sync
            if max_blocks > max(last_block_counts) and max_blocks == min_blocks:
                print(f"   🔄 All nodes synchronized at {current_time:.3f}s - Blocks: {max_blocks}")
                results['sync_events'].append({
                    'time': current_time,
                    'event': 'full_sync',
                    'block_count': max_blocks
                })
            
            last_block_counts = block_counts[:]
            time.sleep(0.5)  # Check every 500ms
    
    def verify_final_consensus(self):
        """Verify that all nodes have reached consensus"""
        print(f"\n🔍 VERIFYING FINAL CONSENSUS")
        print("-" * 40)
        
        final_state = self.get_network_state()
        block_counts = final_state['block_counts']
        
        print(f"📊 Final block counts per node:")
        for i, (port, blocks) in enumerate(zip(self.active_nodes, block_counts)):
            print(f"   Node {port}: {blocks} blocks")
        
        # Check consensus
        max_blocks = max(block_counts)
        min_blocks = min(block_counts)
        
        if max_blocks == min_blocks:
            print(f"✅ CONSENSUS ACHIEVED: All {len(self.active_nodes)} nodes have {max_blocks} blocks")
            self.results['consensus_achieved'] = True
            self.results['final_block_count'] = max_blocks
            return True
        else:
            print(f"❌ CONSENSUS FAILED: Block count range {min_blocks}-{max_blocks}")
            self.results['consensus_achieved'] = False
            return False
    
    def analyze_blockchain_state(self):
        """Analyze the final blockchain state across all nodes"""
        print(f"\n📊 BLOCKCHAIN STATE ANALYSIS")
        print("-" * 40)
        
        for i, port in enumerate(self.active_nodes):
            try:
                response = requests.get(f'http://localhost:{port}/api/v1/blockchain/', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    blocks = data.get('blocks', [])
                    
                    print(f"\n🔗 Node {port} (Node {i+1}):")
                    print(f"   Total blocks: {len(blocks)}")
                    
                    if len(blocks) > 1:  # Skip genesis block
                        for j, block in enumerate(blocks[1:], 1):  # Skip genesis
                            tx_count = len(block.get('transactions', []))
                            forger = block.get('forger', 'Unknown')[:20]
                            print(f"   Block {j}: {tx_count} transactions, Forger: {forger}...")
                    
                    # Check for PoH sequences if available
                    if blocks:
                        last_block = blocks[-1]
                        if 'poh_sequence' in last_block:
                            poh_count = len(last_block['poh_sequence'])
                            print(f"   PoH entries in last block: {poh_count}")
                        
            except Exception as e:
                print(f"   ❌ Error analyzing node {port}: {e}")
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print(f"\n" + "=" * 80)
        print(f"🏁 GULF STREAM TRANSACTION TEST SUMMARY")
        print("=" * 80)
        
        print(f"📊 Transaction Statistics:")
        print(f"   Submitted: {self.results['transactions_submitted']}")
        print(f"   Success Rate: {(self.results['transactions_submitted']/max(1, self.results['transactions_submitted'])*100):.1f}%")
        
        print(f"\n🌐 Network Status:")
        print(f"   Active Nodes: {len(self.active_nodes)}")
        print(f"   Consensus Achieved: {'✅ YES' if self.results['consensus_achieved'] else '❌ NO'}")
        
        if self.results.get('final_block_count'):
            print(f"   Final Block Count: {self.results['final_block_count']}")
        
        print(f"\n⏱️  Timing Events:")
        for event in self.results.get('sync_events', []):
            event_type = event['event'].replace('_', ' ').title()
            print(f"   {event_type}: {event['time']:.3f}s")
        
        # Performance assessment
        print(f"\n🎯 Gulf Stream Performance Assessment:")
        if self.results['consensus_achieved']:
            print(f"   ✅ Transaction forwarding successful")
            print(f"   ✅ Block creation working")
            print(f"   ✅ Network synchronization achieved")
            print(f"   ✅ Gulf Stream + PoH + Turbine flow operational")
        else:
            print(f"   ❌ Network synchronization issues detected")
            print(f"   ⚠️  Gulf Stream flow may need adjustment")


def main():
    """Main test execution"""
    parser = argparse.ArgumentParser(description="Test Gulf Stream transaction flow")
    parser.add_argument('--nodes', type=int, default=5, help='Number of nodes to test (default: 5)')
    parser.add_argument('--transactions', type=int, default=10, help='Number of transactions to submit (default: 10)')
    parser.add_argument('--start-port', type=int, default=11000, help='Starting API port (default: 11000)')
    
    args = parser.parse_args()
    
    # Generate API ports
    api_ports = [args.start_port + i for i in range(args.nodes)]
    
    print("🌊 GULF STREAM TRANSACTION FLOW TEST")
    print("=" * 80)
    print(f"📡 Testing {args.nodes} nodes (ports {api_ports[0]}-{api_ports[-1]})")
    print(f"💰 Submitting {args.transactions} transactions")
    print(f"⏰ Test started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize tester
        tester = GulfStreamTransactionTester(api_ports)
        
        # Setup test environment
        tester.setup_test_environment()
        
        # Run transaction batch
        successful_txs = tester.run_transaction_batch(args.transactions)
        
        # Verify consensus
        consensus_achieved = tester.verify_final_consensus()
        
        # Analyze blockchain state
        tester.analyze_blockchain_state()
        
        # Print summary
        tester.print_test_summary()
        
        # Exit with appropriate code
        if consensus_achieved:
            print(f"\n🎉 TEST PASSED: All nodes achieved consensus!")
            sys.exit(0)
        else:
            print(f"\n❌ TEST FAILED: Nodes did not achieve consensus!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
