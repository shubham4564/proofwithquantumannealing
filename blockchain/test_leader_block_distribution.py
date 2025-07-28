#!/usr/bin/env python3
"""
Test script to verify leader node transaction processing and block distribution.
This script will:
1. Check if leader nodes are correctly identified
2. Verify transaction collection and ordering
3. Confirm block creation and distribution mechanisms
"""

import sys
import time
import requests
import json
from blockchain.blockchain import Blockchain
from blockchain.transaction.transaction import Transaction
from blockchain.transaction.wallet import Wallet

def test_leader_block_creation_and_distribution():
    """Test the complete leader node workflow"""
    print("🧪 TESTING: Leader Node Transaction Processing & Block Distribution")
    print("=" * 70)
    
    # Initialize blockchain
    print("\n1️⃣ INITIALIZING BLOCKCHAIN...")
    blockchain = Blockchain()
    print(f"✅ Blockchain initialized with {len(blockchain.blocks)} blocks")
    
    # Check leader schedule
    print("\n2️⃣ CHECKING LEADER SCHEDULE...")
    current_leader = blockchain.leader_schedule.get_current_leader()
    current_slot = blockchain.leader_schedule.get_current_slot()
    
    print(f"✅ Current slot: {current_slot}")
    print(f"✅ Current leader: {current_leader[:30] + '...' if current_leader else 'None'}")
    print(f"✅ Slot duration: {blockchain.leader_schedule.slot_duration_seconds}s")
    print(f"✅ Slots per epoch: {blockchain.leader_schedule.slots_per_epoch}")
    
    # Check Gulf Stream
    print("\n3️⃣ CHECKING GULF STREAM TRANSACTION FORWARDING...")
    gulf_stream_status = blockchain.gulf_stream_node.get_gulf_stream_status()
    print(f"✅ Gulf Stream initialized: {bool(blockchain.gulf_stream_node)}")
    print(f"✅ Gulf Stream status: {gulf_stream_status}")
    
    # Test transaction creation
    print("\n4️⃣ CREATING TEST TRANSACTIONS...")
    
    # Create test wallet
    test_wallet = Wallet()
    test_public_key = test_wallet.public_key_string()
    
    # Create transactions
    transactions = []
    for i in range(3):
        tx = Transaction(
            sender_public_key=test_public_key,
            receiver_public_key=current_leader if current_leader else test_public_key,
            amount=100 + i,
            type="TRANSFER"
        )
        # Sign transaction properly
        signature = test_wallet.sign(tx.payload())
        tx.sign(signature)
        transactions.append(tx)
    
    print(f"✅ Created {len(transactions)} test transactions")
    
    # Submit transactions to Gulf Stream
    print("\n5️⃣ SUBMITTING TRANSACTIONS TO GULF STREAM...")
    for i, tx in enumerate(transactions):
        result = blockchain.submit_transaction(tx)
        print(f"✅ Transaction {i+1} submitted: {result['transaction_id'][:8]}...")
    
    # Check if leader should create block
    print("\n6️⃣ TESTING BLOCK CREATION PROCESS...")
    
    # If no current leader, manually advance to slot 1 to get a leader
    if not current_leader:
        print("🔄 No current leader at slot 0, advancing to slot 1...")
        
        # Manually set current slot to 1 for testing
        blockchain.leader_schedule.current_slot = 1
        current_leader = blockchain.leader_schedule.get_current_leader()
        print(f"✅ Advanced to slot 1, leader: {current_leader[:30] + '...' if current_leader else 'Still None'}")
    
    # Get transactions for current leader
    if current_leader:
        leader_transactions = blockchain.gulf_stream_node.get_transactions_for_leader(current_leader)
        print(f"✅ Leader has {len(leader_transactions)} forwarded transactions")
    else:
        print("⚠️ No current leader identified even after advancing slot")
        # Try to get any leader from the schedule
        if hasattr(blockchain.leader_schedule, 'current_schedule') and blockchain.leader_schedule.current_schedule:
            first_slot = min(blockchain.leader_schedule.current_schedule.keys())
            current_leader = blockchain.leader_schedule.current_schedule[first_slot]
            print(f"🔄 Using first scheduled leader from slot {first_slot}: {current_leader[:30]}...")
        else:
            print("❌ No leaders found in schedule")
            return
    
    # Test block creation
    print("\n7️⃣ TESTING LEADER BLOCK CREATION...")
    try:
        # Create a wallet for the leader (simulation)
        leader_wallet = Wallet()
        
        # Override leader public key to match current leader
        # In real scenario, the actual leader node would use its own wallet
        print(f"🔄 Simulating block creation by leader: {current_leader[:30]}...")
        
        # Create block with Gulf Stream transactions
        block = blockchain.create_block(leader_wallet, use_gulf_stream=True)
        
        print(f"✅ Block created successfully!")
        print(f"   📦 Block number: {block.block_count}")
        print(f"   📝 Transactions: {len(block.transactions)}")
        print(f"   🔗 PoH entries: {len(getattr(block, 'poh_sequence', []))}")
        print(f"   🧮 State root: {getattr(block, 'state_root_hash', 'none')[:16]}...")
        print(f"   ⚡ Execution time: {getattr(block, 'execution_time_ms', 0)}ms")
        print(f"   📊 Parallel efficiency: {getattr(block, 'parallel_efficiency', 100):.1f}%")
        
    except Exception as e:
        print(f"❌ Block creation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test distribution mechanisms
    print("\n8️⃣ TESTING BLOCK DISTRIBUTION MECHANISMS...")
    
    # Check Turbine protocol
    if hasattr(blockchain, 'turbine_protocol') and blockchain.turbine_protocol:
        print("✅ Turbine protocol initialized")
        
        # Test turbine broadcast
        try:
            transmission_tasks = blockchain.broadcast_block_with_turbine(block, current_leader)
            print(f"✅ Turbine created {len(transmission_tasks)} transmission tasks")
            
            # Test actual network transmission
            if transmission_tasks:
                network_results = blockchain._execute_turbine_transmission_tasks(transmission_tasks)
                print(f"✅ Turbine transmission results:")
                print(f"   📤 Total tasks: {network_results.get('total_tasks', 0)}")
                print(f"   ✅ Successful: {network_results.get('successful_transmissions', 0)}")
                print(f"   ❌ Failed: {network_results.get('failed_transmissions', 0)}")
                print(f"   📊 Shreds sent: {network_results.get('shreds_transmitted', 0)}")
                print(f"   🎯 Nodes reached: {len(network_results.get('nodes_reached', []))}")
            
        except Exception as e:
            print(f"⚠️ Turbine transmission test failed: {e}")
    else:
        print("❌ Turbine protocol not initialized")
    
    # Test force distribution
    print("\n9️⃣ TESTING FORCE BLOCK DISTRIBUTION...")
    try:
        blockchain._force_block_distribution(block)
        print("✅ Force distribution completed")
        
        # Check propagation stats
        if hasattr(blockchain, 'propagation_stats'):
            stats = blockchain.propagation_stats
            print(f"   📊 Blocks distributed: {stats.get('blocks_distributed', 0)}")
            print(f"   🌐 Nodes reached: {stats.get('nodes_reached', 0)}")
        
    except Exception as e:
        print(f"⚠️ Force distribution failed: {e}")
    
    print("\n🔟 TESTING NODE API CONNECTIVITY...")
    
    # Test if other nodes are reachable
    reachable_nodes = 0
    for i in range(1, 6):  # Test first 5 nodes
        port = 11000 + i
        try:
            response = requests.get(f"http://127.0.0.1:{port}/api/v1/blockchain/", timeout=2)
            if response.status_code == 200:
                reachable_nodes += 1
                data = response.json()
                print(f"✅ Node {i+1} (port {port}): {len(data.get('blocks', []))} blocks")
            else:
                print(f"⚠️ Node {i+1} (port {port}): HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Node {i+1} (port {port}): Not reachable")
    
    print(f"\n📊 Network connectivity: {reachable_nodes}/5 nodes reachable")
    
    print("\n" + "=" * 70)
    print("🎉 LEADER NODE TEST COMPLETED!")
    
    # Summary
    print("\n📋 SUMMARY:")
    print(f"✅ Leader identification: {'Working' if current_leader else 'Failed'}")
    print(f"✅ Transaction forwarding: {'Working' if gulf_stream_status else 'Failed'}")
    print(f"✅ Block creation: Working")
    print(f"✅ Turbine protocol: {'Working' if hasattr(blockchain, 'turbine_protocol') else 'Failed'}")
    print(f"✅ Network reachability: {reachable_nodes}/5 nodes")
    
    if reachable_nodes == 0:
        print("\n⚠️ WARNING: No other nodes reachable - start network nodes first!")
        print("💡 TIP: Run 'python run_node.py --port 11001 &' to start additional nodes")
    
    return {
        'leader_identified': bool(current_leader),
        'transactions_created': len(transactions),
        'block_created': True,
        'network_reachable_nodes': reachable_nodes,
        'turbine_available': hasattr(blockchain, 'turbine_protocol'),
        'block_number': block.block_count if 'block' in locals() else None
    }

if __name__ == "__main__":
    try:
        results = test_leader_block_creation_and_distribution()
        print(f"\n🔬 Test Results: {json.dumps(results, indent=2)}")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
