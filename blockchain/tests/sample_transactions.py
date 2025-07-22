import os
import sys
import requests
import time
import json
from datetime import datetime

# Add the parent directory to Python path to find blockchain modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from blockchain.transaction.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils


def post_transaction(sender, receiver, amount, type, api_port=11001, verbose=True):
    """Post a transaction and measure timing"""
    start_time = time.time()
    transaction = sender.create_transaction(receiver.public_key_string(), amount, type)
    url = f"http://localhost:{api_port}/api/v1/transaction/create/"
    package = {"transaction": BlockchainUtils.encode(transaction)}
    
    try:
        response = requests.post(url, json=package, timeout=15)
        end_time = time.time()
        response_time = end_time - start_time
        
        if verbose:
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{timestamp} {status} {type} {amount} tokens ({response_time:.3f}s) -> {response.status_code}")
            if response.status_code != 200:
                print(f"    Error: {response.text}")
        
        return {
            'success': response.status_code == 200,
            'response_time': response_time,
            'status_code': response.status_code,
            'timestamp': start_time,
            'type': type,
            'amount': amount
        }
    except Exception as e:
        end_time = time.time()
        if verbose:
            print(f"❌ {type} transaction failed: {e}")
        return {
            'success': False,
            'response_time': end_time - start_time,
            'error': str(e),
            'timestamp': start_time,
            'type': type,
            'amount': amount
        }


def get_blockchain_info(api_port=11001):
    """Get current blockchain information"""
    try:
        response = requests.get(f"http://localhost:{api_port}/api/v1/blockchain/", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error getting blockchain info: {e}")
    return None


def get_quantum_metrics(api_port=11001):
    """Get quantum annealing consensus metrics"""
    try:
        response = requests.get(f"http://localhost:{api_port}/api/v1/blockchain/quantum-metrics/", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error getting quantum metrics: {e}")
    return None


def display_blockchain_summary(api_port=11001):
    """Display summary of current blockchain state"""
    print("\n" + "="*60)
    print("📊 BLOCKCHAIN STATE SUMMARY")
    print("="*60)
    
    blockchain_info = get_blockchain_info(api_port)
    if blockchain_info:
        blocks = blockchain_info.get('blocks', [])
        print(f"Total Blocks: {len(blocks)}")
        
        if len(blocks) > 1:
            # Calculate block times
            block_times = []
            for i in range(1, len(blocks)):
                prev_time = blocks[i-1].get('timestamp', 0)
                curr_time = blocks[i].get('timestamp', 0)
                if curr_time > prev_time:
                    block_times.append(curr_time - prev_time)
            
            if block_times:
                avg_block_time = sum(block_times) / len(block_times)
                print(f"Average Block Time: {avg_block_time:.2f} seconds")
                print(f"Latest Block Time: {block_times[-1]:.2f} seconds")
        
        # Show latest block details
        if blocks:
            latest_block = blocks[-1]
            transactions = latest_block.get('transactions', [])
            print(f"Latest Block Transactions: {len(transactions)}")
            print(f"Latest Block Forger: {latest_block.get('forger', 'Unknown')[:20]}...")
    
    # Show quantum metrics
    quantum_metrics = get_quantum_metrics(api_port)
    if quantum_metrics:
        print("\n🔬 QUANTUM CONSENSUS METRICS")
        print("-"*40)
        print(f"Total Nodes: {quantum_metrics.get('total_nodes', 0)}")
        print(f"Active Nodes: {quantum_metrics.get('active_nodes', 0)}")
        print(f"Probe Count: {quantum_metrics.get('probe_count', 0)}")
        
        node_scores = quantum_metrics.get('node_scores', {})
        if node_scores:
            print("Top Node Scores:")
            # Handle nested score dictionaries
            try:
                if isinstance(next(iter(node_scores.values())), dict):
                    # Nested format: node -> {suitability_score, effective_score, etc.}
                    sorted_scores = sorted(
                        node_scores.items(), 
                        key=lambda x: x[1].get('suitability_score', 0), 
                        reverse=True
                    )
                    for i, (node, score_data) in enumerate(sorted_scores[:3]):
                        suitability = score_data.get('suitability_score', 0)
                        effective = score_data.get('effective_score', 0)
                        print(f"  {i+1}. {node[:20]}...: suitability={suitability:.4f}, effective={effective:.4f}")
                else:
                    # Simple format: node -> score
                    sorted_scores = sorted(node_scores.items(), key=lambda x: x[1], reverse=True)
                    for i, (node, score) in enumerate(sorted_scores[:3]):
                        print(f"  {i+1}. {node[:20]}...: {score:.4f}")
            except (StopIteration, TypeError):
                print("  No valid scores available")


if __name__ == "__main__":
    print("🚀 QUANTUM ANNEALING CONSENSUS - SAMPLE TRANSACTIONS")
    print("="*60)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create wallets
    print("🔑 Creating wallets...")
    john = Wallet()
    jane = Wallet()
    exchange = Wallet()
    
    print(f"  ✓ John: {john.public_key_string()[:20]}...")
    print(f"  ✓ Jane: {jane.public_key_string()[:20]}...")
    print(f"  ✓ Exchange: {exchange.public_key_string()[:20]}...")
    
    # Track all transactions
    transaction_results = []
    
    print("\n📋 PHASE 1: Initial Exchange Transactions")
    print("-"*40)
    
    # Block size: 2 transactions / block
    # Forger: Genesis (initially)
    transaction_results.append(post_transaction(exchange, jane, 100, "EXCHANGE"))
    time.sleep(1)
    transaction_results.append(post_transaction(exchange, john, 100, "EXCHANGE"))
    time.sleep(1)
    transaction_results.append(post_transaction(exchange, john, 10, "EXCHANGE"))
    time.sleep(2)  # Wait for block to be created
    
    print("\n📋 PHASE 2: Quantum Consensus Node Registration")
    print("-"*40)
    print("All nodes are automatically eligible for quantum consensus!")
    print("No staking required - any registered node can be selected as forger.")
    print("Transaction participants are automatically registered in quantum consensus.")
    
    # Wait for quantum consensus to be ready
    print("⏳ Waiting for quantum consensus to process...")
    time.sleep(5)
    
    display_blockchain_summary()
    
    print("\n📋 PHASE 3: Transfer Transactions")
    print("-"*40)
    print("Now using quantum annealing consensus for forger selection...")
    
    # Forger: Determined by quantum annealing consensus
    transaction_results.append(post_transaction(jane, john, 1, "TRANSFER"))
    time.sleep(1)
    transaction_results.append(post_transaction(jane, john, 1, "TRANSFER"))
    time.sleep(2)
    
    # One remaining in transaction pool
    transaction_results.append(post_transaction(jane, john, 1, "TRANSFER"))
    time.sleep(1)
    
    print("\n📋 PHASE 4: Additional Transactions to Trigger More Blocks")
    print("-"*40)
    
    # More transactions to see quantum consensus in action
    for i in range(5):
        sender = jane if i % 2 == 0 else john
        receiver = john if i % 2 == 0 else jane
        amount = 1 + (i % 3)
        
        transaction_results.append(post_transaction(sender, receiver, amount, "TRANSFER"))
        time.sleep(1)
    
    # Wait for final processing
    print("\n⏳ Waiting for final transactions to be processed...")
    time.sleep(15)
    
    # Final blockchain summary
    display_blockchain_summary()
    
    # Transaction performance summary
    print("\n📈 TRANSACTION PERFORMANCE SUMMARY")
    print("="*60)
    
    successful_txs = [tx for tx in transaction_results if tx['success']]
    failed_txs = [tx for tx in transaction_results if not tx['success']]
    
    print(f"Total Transactions: {len(transaction_results)}")
    print(f"Successful: {len(successful_txs)} ({len(successful_txs)/len(transaction_results)*100:.1f}%)")
    print(f"Failed: {len(failed_txs)} ({len(failed_txs)/len(transaction_results)*100:.1f}%)")
    
    if successful_txs:
        response_times = [tx['response_time'] for tx in successful_txs]
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        print(f"Average Response Time: {avg_response_time:.3f}s")
        print(f"Min Response Time: {min_response_time:.3f}s")
        print(f"Max Response Time: {max_response_time:.3f}s")
    
    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n✅ Sample transactions completed!")
    print("\nNext steps:")
    print("1. Check blockchain state: http://localhost:11001/api/v1/blockchain/")
    print("2. Check quantum metrics: http://localhost:11001/api/v1/blockchain/quantum-metrics/")
    print("3. Run multi-node test: python multi_node_test.py")
    print("4. Run quantum demo: python quantum_demo.py")
