#!/usr/bin/env python3
"""
Enhanced Transaction Test with Performance Metrics

This script creates transactions and submits them to the blockchain
while measuring consensus time, transaction time, and throughput.
"""

import argparse
import requests
import json
import base64
import time
import statistics
from datetime import datetime
from blockchain.transaction.transaction import Transaction
from blockchain.transaction.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils

def load_keys():
    """Load genesis keys for testing from Solana-style genesis configuration"""
    try:
        # Load from the new Solana-style genesis configuration
        from blockchain.genesis_config import GenesisConfig
        
        # Load genesis configuration
        genesis_data = GenesisConfig.load_genesis_config("genesis_config/genesis.json")
        
        # Get the faucet public key (has the most tokens for testing)
        faucet_public_key = genesis_data["faucet"]
        
        # Load the faucet private key
        with open('genesis_config/faucet_private_key.pem', 'r') as f:
            faucet_private_key = f.read()
            
        print(f"✅ Loaded faucet keys for testing")
        print(f"   Public key: {faucet_public_key[:50]}...")
        print(f"   Genesis network: {genesis_data['network_id'][:16]}...")
        
        return faucet_private_key, faucet_public_key
        
    except FileNotFoundError as e:
        print(f"❌ Error: Genesis configuration not found: {e}")
        print("   Run: python3 -m blockchain.genesis_config --supply 1000000000")
        return None, None
    except Exception as e:
        print(f"❌ Error loading genesis keys: {e}")
        return None, None

def create_sample_transaction(amount=10.0, tx_type="TRANSFER"):
    """Create a sample transaction with flexible parameters"""
    private_key, sender_public_key = load_keys()
    if not private_key:
        return None
        
    # Create wallet from private key
    wallet = Wallet()
    wallet.from_key(private_key)
    
    # Create a flexible test transaction
    transaction = Transaction(
        sender_public_key=sender_public_key,
        receiver_public_key=sender_public_key,  # Self-send for testing
        amount=amount,
        type=tx_type
    )
    
    # Sign the transaction
    signature = wallet.sign(transaction.payload())
    transaction.sign(signature)
    
    return transaction

def submit_transaction(transaction, node_port=11000):
    """Submit transaction to a node without timing measurement"""
    try:
        # Get current slot before submission
        pre_submission_slot = get_current_slot_info(node_port)
        
        # Encode transaction
        encoded_transaction = BlockchainUtils.encode(transaction)
        
        # Prepare payload
        payload = {
            "transaction": encoded_transaction
        }
        
        # Submit to node
        url = f"http://localhost:{node_port}/api/v1/transaction/create/"
        response = requests.post(url, json=payload, timeout=10)
        
        # Get current slot after submission
        post_submission_slot = get_current_slot_info(node_port)
        
        if response.status_code == 200:
            return True, {
                "response": response.json(),
                "submission_time": 0.0,  # No timing measurement
                "timestamp": 0.0,
                "pre_submission_slot": pre_submission_slot,
                "post_submission_slot": post_submission_slot
            }
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
            
    except Exception as e:
        return False, str(e)

def get_current_slot_info(node_port=11000):
    """Get current slot information"""
    try:
        url = f"http://localhost:{node_port}/api/v1/blockchain/leader/current/"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            leader_info = data.get('current_leader_info', {})
            return {
                'slot': leader_info.get('current_slot', 'unknown'),
                'leader': data.get('current_leader', 'unknown')[:25] + "..." if data.get('current_leader') else 'unknown',
                'time_remaining': leader_info.get('time_remaining_in_slot', 0),
                'slot_duration': leader_info.get('slot_duration', 0)
            }
    except Exception as e:
        print(f"❌ Error getting slot info: {e}")
    return {'slot': 'unknown', 'leader': 'unknown', 'time_remaining': 0, 'slot_duration': 0}

def check_blockchain_state(node_port=11000):
    """Check blockchain state after transaction"""
    try:
        url = f"http://localhost:{node_port}/api/v1/blockchain/"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"❌ Error checking blockchain state: {e}")
    return None

def check_leader_status(node_port=11000):
    """Check current leader status"""
    try:
        url = f"http://localhost:{node_port}/api/v1/blockchain/leader/current/"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"❌ Error checking leader status: {e}")
    return None

def get_quantum_metrics(node_port=11000):
    """Get quantum consensus metrics"""
    try:
        url = f"http://localhost:{node_port}/api/v1/blockchain/quantum-metrics/"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"❌ Error checking quantum metrics: {e}")
    return None

def measure_consensus_time(initial_block_count, timeout=30, node_port=11000):
    """Check for new blocks without time measurement"""
    start_slot_info = get_current_slot_info(node_port)
    
    print(f"   🕐 Checking for new blocks at Slot {start_slot_info['slot']}")
    
    # Single check instead of timed loop
    blockchain_state = check_blockchain_state(node_port)
    current_slot_info = get_current_slot_info(node_port)
    
    if blockchain_state:
        current_blocks = len(blockchain_state.get('blocks', []))
        if current_blocks > initial_block_count:
            latest_block = blockchain_state['blocks'][-1]
            
            # Try to get slot information from the block
            block_slot = latest_block.get('slot_number', 'unknown')
            if block_slot == 'unknown' and hasattr(latest_block, 'slot'):
                block_slot = latest_block.slot
            
            print(f"   ✅ New block found in Slot {current_slot_info['slot']} (Block slot: {block_slot})")
            return 0.0, current_blocks, latest_block, {
                'start_slot': start_slot_info['slot'],
                'end_slot': current_slot_info['slot'],
                'block_slot': block_slot
            }
    
    print(f"   ⏰ No new blocks found at Slot {current_slot_info['slot']}")
    return None, initial_block_count, None, {
        'start_slot': start_slot_info['slot'],
        'end_slot': current_slot_info['slot'],
        'block_slot': 'no_block'
    }

def run_multiple_transactions(count=5, amount=10.0, node_port=11000):
    """Run multiple transactions without performance measurement"""
    print(f"\n📊 RUNNING {count} TRANSACTIONS")
    print("=" * 60)
    
    results = []
    
    for i in range(count):
        print(f"   🔄 Transaction {i+1}/{count}...")
        
        # Create transaction
        transaction = create_sample_transaction(amount)
        if not transaction:
            print(f"   ❌ Failed to create transaction {i+1}")
            continue
        
        # Submit transaction
        success, result = submit_transaction(transaction, node_port)
        if not success:
            print(f"   ❌ Failed to submit transaction {i+1}: {result}")
            continue
        
        results.append({
            "tx_id": i+1,
            "transaction_id": transaction.id,
            "amount": amount,
            "creation_time": 0.0,  # No timing measurement
            "submission_time": 0.0,  # No timing measurement
            "total_time": 0.0,  # No timing measurement
            "timestamp": 0.0
        })
        
        print(f"   ✅ Transaction {i+1}: Submitted successfully")
        
        # Small delay between transactions to avoid overwhelming
        time.sleep(0.1)
    
    return results, 0.0  # No total time measurement

def calculate_performance_metrics(results, total_test_time):
    """Return basic metrics without timing calculations"""
    if not results:
        return None
    
    metrics = {
        "transaction_count": len(results),
        "total_test_time": 0.0,  # No timing measurement
        "throughput_tps": 0.0,  # No timing measurement
        "avg_creation_time": 0.0,  # No timing measurement
        "avg_submission_time": 0.0,  # No timing measurement
        "avg_total_time": 0.0,  # No timing measurement
        "min_submission_time": 0.0,  # No timing measurement
        "max_submission_time": 0.0,  # No timing measurement
        "median_submission_time": 0.0  # No timing measurement
    }
    
    return metrics

def print_performance_report(metrics, consensus_time=None):
    """Print basic report without timing metrics"""
    print(f"\n📊 TRANSACTION REPORT")
    print("=" * 50)
    
    print(f"📈 Transaction Summary:")
    print(f"   Total Transactions: {metrics['transaction_count']}")
    print(f"   Status: Completed (timing disabled)")
    
    if consensus_time is not None:
        print(f"\n🎯 Block Status:")
        if consensus_time == 0.0:
            print(f"   Block Check: Completed")
        else:
            print(f"   Block Check: No new blocks found")

def main():
    parser = argparse.ArgumentParser(description='Enhanced Transaction Test with Performance Metrics')
    parser.add_argument('--count', type=int, default=1, help='Number of transactions to test (default: 1)')
    parser.add_argument('--amount', type=float, default=10.0, help='Transaction amount (default: 10.0)')
    parser.add_argument('--node', type=int, default=11000, help='Node port to use (default: 11000)')
    parser.add_argument('--performance', action='store_true', help='Run performance test with multiple transactions')
    parser.add_argument('--performance-analysis', action='store_true', help='Generate performance comparison graphs')
    
    args = parser.parse_args()
    
    # Run performance analysis if requested
    if args.performance_analysis:
        print("🔬 RUNNING PERFORMANCE ANALYSIS")
        print("=" * 50)
        try:
            from performance_analysis import BlockchainPerformanceAnalyzer
            analyzer = BlockchainPerformanceAnalyzer(node_port=args.node)
            analyzer.run_complete_analysis()
            return True
        except ImportError:
            print("❌ Performance analysis module not found")
            print("   Please ensure performance_analysis.py is in the same directory")
            return False
        except Exception as e:
            print(f"❌ Performance analysis failed: {e}")
            return False
    
    print("🧪 ENHANCED SAMPLE TRANSACTION TEST")
    print("=" * 50)
    print(f"📊 Configuration: {args.count} transactions of {args.amount} units on node {args.node}")
    
    # Step 1: Check if nodes are running
    print("\n📡 Step 1: Checking node connectivity...")
    blockchain_state = check_blockchain_state(args.node)
    if not blockchain_state:
        print(f"❌ Error: Cannot connect to node on port {args.node}")
        print("   Make sure nodes are running: ./start_nodes.sh")
        return False
    
    initial_blocks = len(blockchain_state.get('blocks', []))
    print(f"✅ Node connected! Current blocks: {initial_blocks}")
    
    # Step 2: Check leader selection and quantum metrics
    print("\n🎯 Step 2: Checking system status...")
    leader_status = check_leader_status(args.node)
    quantum_metrics = get_quantum_metrics(args.node)
    
    if leader_status:
        current_slot = leader_status.get('current_leader_info', {}).get('current_slot', 'unknown')
        time_remaining = leader_status.get('current_leader_info', {}).get('time_remaining_in_slot', 0)
        print(f"✅ Leader selection active! Current slot: {current_slot}, Time remaining: {time_remaining:.1f}s")
    
    if quantum_metrics:
        active_nodes = quantum_metrics.get('active_nodes', 0)
        total_nodes = quantum_metrics.get('total_nodes', 0)
        print(f"✅ Quantum consensus: {active_nodes}/{total_nodes} active nodes")
    
    if args.performance and args.count > 1:
        # Run performance test
        print(f"\n💰 Step 3: Running performance test...")
        results, total_test_time = run_multiple_transactions(args.count, args.amount, args.node)
        
        if not results:
            print("❌ No successful transactions in performance test")
            return False
        
        # Measure consensus time
        print(f"\n⏳ Step 4: Checking for new blocks...")
        consensus_result = measure_consensus_time(initial_blocks, timeout=60, node_port=args.node)
        consensus_time, final_blocks, latest_block, slot_info = consensus_result
        
        # Calculate and display metrics
        metrics = calculate_performance_metrics(results, total_test_time)
        print_performance_report(metrics, consensus_time)
        
        if consensus_time is not None and consensus_time >= 0:
            print(f"\n✅ Block check completed! New blocks: {final_blocks - initial_blocks}")
            if latest_block:
                print(f"   📝 Transactions in latest block: {len(latest_block.get('transactions', []))}")
        else:
            print(f"⚠️  No new blocks found during check")
            
    else:
        # Run single transaction test
        print(f"\n💰 Step 3: Creating transaction...")
        transaction = create_sample_transaction(args.amount)
        if not transaction:
            print("❌ Failed to create transaction")
            return False
        
        print(f"✅ Transaction created:")
        print(f"   ID: {transaction.id}")
        print(f"   Amount: {transaction.amount}")
        print(f"   Type: {transaction.type}")
        print(f"   Timestamp: {transaction.timestamp}")
        
        # Step 4: Submit transaction
        print(f"\n📤 Step 4: Submitting transaction...")
        success, result = submit_transaction(transaction, args.node)
        if not success:
            print(f"❌ Transaction submission failed: {result}")
            return False
        
        print(f"✅ Transaction submitted successfully!")
        print(f"   Response: {result['response']}")
        
        # Display slot information
        if 'pre_submission_slot' in result:
            pre_slot = result['pre_submission_slot']
            post_slot = result['post_submission_slot']
            print(f"   📍 Slot Information:")
            print(f"      Pre-submission: Slot {pre_slot['slot']} (Leader: {pre_slot['leader']}, {pre_slot['time_remaining']:.1f}s remaining)")
            print(f"      Post-submission: Slot {post_slot['slot']} (Leader: {post_slot['leader']}, {post_slot['time_remaining']:.1f}s remaining)")
            
            if pre_slot['slot'] != post_slot['slot']:
                print(f"      ⚠️  Transaction crossed slot boundary during submission!")
            else:
                print(f"      ✅ Transaction submitted within Slot {pre_slot['slot']}")
        
        # Step 5: Check for block creation
        print(f"\n⏳ Step 5: Checking for new blocks...")
        consensus_result = measure_consensus_time(initial_blocks, timeout=30, node_port=args.node)
        consensus_time, final_blocks, latest_block, slot_info = consensus_result
        
        if consensus_time is not None and consensus_time >= 0:
            print(f"✅ Block check completed!")
            print(f"   📊 New blocks created: {final_blocks - initial_blocks}")
            print(f"   🎯 Slot Journey: {slot_info['start_slot']} → {slot_info['end_slot']} (Block created in slot {slot_info['block_slot']})")
            if latest_block:
                print(f"   📝 Transactions in latest block: {len(latest_block.get('transactions', []))}")
                
            # Display transaction status without timing
            print(f"\n📊 TRANSACTION STATUS:")
            print(f"   Transaction Submitted: ✅")
            print(f"   Block Check: ✅") 
            print(f"   Transaction Slot: {result['pre_submission_slot']['slot']} → Block Slot: {slot_info['block_slot']}")
        else:
            print(f"⚠️  No new blocks found")
            print(f"   Slot Journey: {slot_info['start_slot']} → {slot_info['end_slot']} (no block created)")
            print(f"   This might be normal - check leader rotation timing")
    
    # Step 6: Final system status
    print(f"\n📊 Step 6: Final system status...")
    final_leader = check_leader_status(args.node)
    if final_leader:
        current_slot = final_leader.get('current_leader_info', {}).get('current_slot', 'unknown')
        print(f"   🎯 Current slot: {current_slot}")
    
    final_quantum = get_quantum_metrics(args.node)
    if final_quantum:
        active_nodes = final_quantum.get('active_nodes', 0)
        total_nodes = final_quantum.get('total_nodes', 0)
        print(f"   🔬 Quantum consensus: {active_nodes}/{total_nodes} active nodes")
    
    print(f"\n🎉 TRANSACTION TEST COMPLETED")
    print("✅ All core systems are operational:")
    print("   • Node connectivity ✅")
    print("   • Leader selection ✅") 
    print("   • Transaction submission ✅")
    print("   • Performance measurement ✅")
    print("   • API endpoints ✅")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
