#!/usr/bin/env python3
"""
Simple Transaction Generator for Load Testing
===========================================

Creates and sends transactions using the existing wallet infrastructure
to test the network with 100 transactions.
"""

import sys
import os
import time
import requests
import threading
from concurrent.futures import ThreadPoolExecutor

# Add the parent directory to sys.path to import blockchain modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blockchain.transaction.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils

def create_test_wallet():
    """Create a test wallet for transactions"""
    return Wallet()

def send_transaction_to_node(sender_wallet, receiver_wallet, amount, node_port, tx_id):
    """Send a transaction to a specific node"""
    try:
        # Create transaction using wallet
        transaction = sender_wallet.create_transaction(
            receiver_wallet.public_key_string(),
            amount,
            "EXCHANGE"  # Use EXCHANGE type for testing
        )
        
        # Encode transaction for API
        encoded_transaction = BlockchainUtils.encode(transaction)
        
        # Send to node
        response = requests.post(
            f'http://127.0.0.1:{node_port}/api/v1/transaction/create/',
            json={"transaction": encoded_transaction},
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            return {
                'success': True,
                'tx_id': tx_id,
                'node_port': node_port,
                'transaction_id': transaction.id,
                'amount': amount
            }
        else:
            return {
                'success': False,
                'tx_id': tx_id,
                'node_port': node_port,
                'error': f"HTTP {response.status_code}: {response.text[:100]}"
            }
            
    except Exception as e:
        return {
            'success': False,
            'tx_id': tx_id,
            'node_port': node_port,
            'error': str(e)
        }

def get_online_nodes():
    """Get list of online nodes"""
    online_nodes = []
    
    print("🔍 Discovering online nodes...")
    for i in range(10):
        port = 11000 + i
        node_num = i + 1
        
        try:
            response = requests.get(f'http://127.0.0.1:{port}/ping/', timeout=3)
            if response.status_code == 200:
                # Get blockchain height
                try:
                    blockchain_response = requests.get(f'http://127.0.0.1:{port}/api/v1/blockchain/', timeout=5)
                    if blockchain_response.status_code == 200:
                        blockchain_data = blockchain_response.json()
                        blockchain_height = len(blockchain_data.get('blocks', []))
                    else:
                        blockchain_height = 0
                except:
                    blockchain_height = 0
                
                online_nodes.append({
                    'node_num': node_num,
                    'port': port,
                    'blockchain_height': blockchain_height
                })
                print(f"   ✅ Node {node_num} (port {port}): {blockchain_height} blocks")
        except:
            print(f"   ❌ Node {node_num}: Offline")
    
    print(f"🌐 Found {len(online_nodes)} online nodes")
    return online_nodes

def monitor_blockchain_progress(online_nodes, initial_heights, duration=30):
    """Monitor blockchain growth over time"""
    print(f"\n📊 Monitoring blockchain growth for {duration} seconds...")
    
    start_time = time.time()
    while time.time() - start_time < duration:
        time.sleep(5)
        
        current_stats = {}
        for node in online_nodes:
            try:
                response = requests.get(f"http://127.0.0.1:{node['port']}/api/v1/blockchain/", timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    current_height = len(data.get('blocks', []))
                    initial_height = initial_heights.get(node['port'], 0)
                    new_blocks = current_height - initial_height
                    current_stats[node['node_num']] = {
                        'height': current_height,
                        'new_blocks': new_blocks
                    }
            except:
                current_stats[node['node_num']] = {'height': -1, 'new_blocks': 0}
        
        # Show progress
        total_new_blocks = sum(stats['new_blocks'] for stats in current_stats.values() if stats['height'] > 0)
        elapsed = int(time.time() - start_time)
        print(f"   [{elapsed:2d}s] Total new blocks across network: {total_new_blocks}")
        
        # Show per-node details every 10 seconds
        if elapsed % 10 == 0:
            for node_num, stats in current_stats.items():
                if stats['height'] > 0:
                    print(f"      Node {node_num}: {stats['height']} blocks (+{stats['new_blocks']})")
    
    return current_stats

def main():
    print("🚀 BLOCKCHAIN LOAD TEST WITH 100 TRANSACTIONS")
    print("=" * 60)
    
    # Discover online nodes
    online_nodes = get_online_nodes()
    
    if not online_nodes:
        print("❌ No online nodes found!")
        return False
    
    # Record initial heights
    initial_heights = {node['port']: node['blockchain_height'] for node in online_nodes}
    
    # Create test wallets
    print(f"\n🏦 Creating test wallets...")
    sender_wallets = [create_test_wallet() for _ in range(20)]  # 20 sender wallets
    receiver_wallets = [create_test_wallet() for _ in range(30)]  # 30 receiver wallets
    
    print(f"   Created {len(sender_wallets)} sender wallets")
    print(f"   Created {len(receiver_wallets)} receiver wallets")
    
    # Send transactions in batches
    print(f"\n📤 Sending 100 transactions...")
    
    all_results = []
    batch_size = 10
    total_transactions = 100
    
    start_time = time.time()
    
    # Start monitoring in background
    monitor_thread = threading.Thread(
        target=lambda: monitor_blockchain_progress(online_nodes, initial_heights, 60),
        daemon=True
    )
    monitor_thread.start()
    
    for batch_num in range(0, total_transactions, batch_size):
        print(f"\n📦 Batch {batch_num // batch_size + 1}: Sending transactions {batch_num + 1}-{min(batch_num + batch_size, total_transactions)}")
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            for i in range(batch_size):
                if batch_num + i >= total_transactions:
                    break
                
                tx_id = batch_num + i
                sender = sender_wallets[tx_id % len(sender_wallets)]
                receiver = receiver_wallets[tx_id % len(receiver_wallets)]
                amount = 10.0  # Fixed amount for testing
                target_node = online_nodes[tx_id % len(online_nodes)]
                
                future = executor.submit(
                    send_transaction_to_node,
                    sender, receiver, amount, target_node['port'], tx_id
                )
                futures.append(future)
            
            # Collect results
            batch_results = [future.result() for future in futures]
            all_results.extend(batch_results)
            
            # Show batch results
            successful = len([r for r in batch_results if r['success']])
            failed = len([r for r in batch_results if not r['success']])
            print(f"   ✅ Success: {successful}, ❌ Failed: {failed}")
            
            # Show sample errors
            errors = [r for r in batch_results if not r['success']]
            if errors:
                for error in errors[:2]:  # Show first 2 errors
                    print(f"      Error: {error['error'][:80]}...")
        
        time.sleep(2)  # Brief pause between batches
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Analysis
    print(f"\n📊 TRANSACTION RESULTS")
    print("-" * 40)
    
    successful_txs = [r for r in all_results if r['success']]
    failed_txs = [r for r in all_results if not r['success']]
    
    print(f"   Total transactions: {len(all_results)}")
    print(f"   ✅ Successful: {len(successful_txs)}")
    print(f"   ❌ Failed: {len(failed_txs)}")
    print(f"   ⏱️ Total time: {total_time:.2f} seconds")
    print(f"   📈 Rate: {len(all_results) / total_time:.1f} tx/sec")
    
    success_rate = len(successful_txs) / len(all_results) * 100
    print(f"   🎯 Success rate: {success_rate:.1f}%")
    
    # Show distribution
    if successful_txs:
        node_distribution = {}
        for result in successful_txs:
            port = result['node_port']
            node_distribution[port] = node_distribution.get(port, 0) + 1
        
        print(f"\n📊 Successful transaction distribution:")
        for port, count in sorted(node_distribution.items()):
            node_num = port - 11000 + 1
            print(f"   Node {node_num} (port {port}): {count} transactions")
    
    # Give some time for block processing
    print(f"\n⏳ Waiting for block processing...")
    time.sleep(10)
    
    # Final blockchain state
    print(f"\n📊 Final blockchain state:")
    total_new_blocks = 0
    for node in online_nodes:
        try:
            response = requests.get(f"http://127.0.0.1:{node['port']}/api/v1/blockchain/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                current_height = len(data.get('blocks', []))
                initial_height = initial_heights[node['port']]
                new_blocks = current_height - initial_height
                total_new_blocks += new_blocks
                
                print(f"   Node {node['node_num']}: {initial_height} → {current_height} blocks (+{new_blocks})")
        except:
            print(f"   Node {node['node_num']}: Error checking final state")
    
    # Final assessment
    print(f"\n🎯 FINAL ASSESSMENT")
    print("-" * 25)
    print(f"   📊 Transaction success rate: {success_rate:.1f}%")
    print(f"   📦 Total new blocks created: {total_new_blocks}")
    
    if success_rate >= 50 and total_new_blocks > 0:
        print(f"   🎉 SUCCESS: Blockchain is processing transactions!")
        if total_new_blocks >= len(successful_txs) // 10:  # Roughly 1 block per 10 transactions
            print(f"   🌟 EXCELLENT: Good block creation rate!")
        return True
    else:
        print(f"   ⚠️ ISSUES: Low success rate or no block creation")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print(f"\n🎉 LOAD TEST SUCCESSFUL!")
        else:
            print(f"\n⚠️ LOAD TEST HAD ISSUES")
    except KeyboardInterrupt:
        print(f"\n🛑 Load test interrupted")
    except Exception as e:
        print(f"\n💥 Load test failed: {e}")
        import traceback
        traceback.print_exc()
