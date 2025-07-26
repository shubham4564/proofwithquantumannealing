#!/usr/bin/env python3
"""
Gulf Stream Transaction Flow Demonstration

This script demonstrates the complete Gulf Stream workflow:
1. Leader schedule pre-computed 1 minute ahead (2-minute total epoch)
2. Transactions forwarded to upcoming leaders
3. Leaders receive transactions before their slot
4. 2-second slot duration for fast block creation
"""

import sys
import os
import time
import json

# Add blockchain module to path
sys.path.append('/Users/shubham/Documents/fromgithub/proofwithquantumannealing/blockchain')

from blockchain.blockchain import Blockchain
from blockchain.transaction.wallet import Wallet
from blockchain.transaction.transaction import Transaction
from blockchain.utils.logger import logger

def demonstrate_gulf_stream_flow():
    """Demonstrate complete Gulf Stream transaction forwarding"""
    
    print("🌊 GULF STREAM TRANSACTION FLOW DEMONSTRATION")
    print("=" * 70)
    
    # PHASE 1: NETWORK INITIALIZATION WITH LEADER SCHEDULE
    print("\n🚀 PHASE 1: NETWORK INITIALIZATION")
    print("-" * 40)
    
    # Create blockchain with leader schedule
    genesis_wallet = Wallet()
    blockchain = Blockchain(genesis_wallet.public_key_string())
    
    # Register multiple nodes as potential leaders
    validators = []
    for i in range(5):
        validator_wallet = Wallet()
        validator_id = f"validator_{i+1}"
        
        # Register in quantum consensus (so they can be selected as leaders)
        if blockchain.quantum_consensus:
            blockchain.quantum_consensus.register_node(validator_wallet.public_key_string(), validator_id)
        
        # Register in Turbine for block propagation
        stake_weight = 1000.0 - (i * 100)
        blockchain.register_turbine_validator(validator_id, stake_weight)
        
        validators.append({
            'id': validator_id,
            'wallet': validator_wallet,
            'stake': stake_weight
        })
        
        print(f"✅ Validator {validator_id} registered (stake: {stake_weight})")
    
    print(f"📊 Network initialized with {len(validators)} validators")
    
    # PHASE 2: LEADER SCHEDULE GENERATION
    print("\n📅 PHASE 2: LEADER SCHEDULE GENERATION")
    print("-" * 40)
    
    # Update leader schedule to generate upcoming leaders
    blockchain.update_leader_schedule()
    
    # Show leader schedule info
    schedule_info = blockchain.leader_schedule.get_schedule_info()
    print(f"📊 Leader schedule status:")
    print(f"   ├─ Current epoch: {schedule_info['current_epoch']}")
    print(f"   ├─ Current slot: {schedule_info['current_slot']}")
    print(f"   ├─ Slot duration: {blockchain.leader_schedule.slot_duration_seconds} seconds")
    print(f"   ├─ Current leader: {schedule_info['current_leader']}")
    print(f"   └─ Schedule ready: {schedule_info['schedule_health']['next_schedule_ready']}")
    
    # Show upcoming leaders (Gulf Stream targets)
    gulf_stream_targets = blockchain.leader_schedule.get_gulf_stream_targets()
    print(f"\n🎯 Gulf Stream targets (next 10 leaders):")
    for i, target in enumerate(gulf_stream_targets[:10]):
        print(f"   {i+1}. Slot {target['slot']}: {target['leader'][:20]}... (in {target['time_until_slot']:.1f}s)")
    
    # PHASE 3: TRANSACTION CREATION AND SUBMISSION
    print("\n💰 PHASE 3: TRANSACTION SUBMISSION WITH GULF STREAM")
    print("-" * 40)
    
    # Create user wallets
    alice = Wallet()
    bob = Wallet()
    charlie = Wallet()
    
    print(f"👤 Created user wallets:")
    print(f"   ├─ Alice: {alice.public_key_string()[:30]}...")
    print(f"   ├─ Bob: {bob.public_key_string()[:30]}...")
    print(f"   └─ Charlie: {charlie.public_key_string()[:30]}...")
    
    # Create and submit transactions
    transactions = []
    
    # Transaction 1: Genesis -> Alice (funding)
    tx1 = genesis_wallet.create_transaction(alice.public_key_string(), 1000.0, "EXCHANGE")
    result1 = blockchain.submit_transaction(tx1)
    transactions.append(tx1)
    print(f"\n📤 Transaction 1 submitted: Genesis -> Alice (1000 tokens)")
    print(f"   └─ Gulf Stream forwarded to {len(result1['gulf_stream_status']['forwarding_stats'])} leaders")
    
    time.sleep(0.5)  # Small delay to show different forwarding
    
    # Transaction 2: Alice -> Bob
    tx2 = alice.create_transaction(bob.public_key_string(), 300.0, "TRANSFER")
    result2 = blockchain.submit_transaction(tx2)
    transactions.append(tx2)
    print(f"\n📤 Transaction 2 submitted: Alice -> Bob (300 tokens)")
    
    time.sleep(0.5)
    
    # Transaction 3: Alice -> Charlie
    tx3 = alice.create_transaction(charlie.public_key_string(), 200.0, "TRANSFER")
    result3 = blockchain.submit_transaction(tx3)
    transactions.append(tx3)
    print(f"\n📤 Transaction 3 submitted: Alice -> Charlie (200 tokens)")
    
    # PHASE 4: GULF STREAM STATUS
    print("\n🌊 PHASE 4: GULF STREAM STATUS")
    print("-" * 40)
    
    gulf_stream_status = blockchain.gulf_stream_node.get_gulf_stream_status()
    
    print(f"📊 Gulf Stream forwarding statistics:")
    stats = gulf_stream_status['forwarding_stats']
    print(f"   ├─ Total transactions forwarded: {stats['total_forwarded']}")
    print(f"   ├─ Successful forwards: {stats['successful_forwards']}")
    print(f"   ├─ Success rate: {stats['success_rate']:.1f}%")
    print(f"   ├─ Active forwarding pools: {stats['active_forward_pools']}")
    print(f"   └─ Total queued transactions: {stats['total_queued_transactions']}")
    
    # Show network view
    network_view = gulf_stream_status['network_view']
    print(f"\n🌐 Network view (upcoming leaders):")
    for i, leader_info in enumerate(network_view['upcoming_leaders'][:5]):
        receiving = "✅" if leader_info['receiving_forwards'] else "❌"
        print(f"   {i+1}. {leader_info['leader']} (slot {leader_info['slot']}, in {leader_info['time_until_slot']}s) {receiving}")
    
    # PHASE 5: LEADER SLOT SIMULATION
    print("\n👑 PHASE 5: LEADER SLOT SIMULATION")
    print("-" * 40)
    
    # Get current leader info
    leader_info = blockchain.get_current_leader_info()
    current_leader = leader_info['current_leader']
    
    if current_leader:
        print(f"🎯 Current leader: {current_leader}")
        print(f"   ├─ Slot: {leader_info['current_slot']}")
        print(f"   ├─ Time remaining: {leader_info['time_remaining_in_slot']:.1f}s")
        print(f"   └─ Slot duration: {leader_info['slot_duration']}s")
        
        # Find corresponding validator wallet
        leader_wallet = None
        for validator in validators:
            if validator['wallet'].public_key_string() == current_leader:
                leader_wallet = validator['wallet']
                break
        
        if not leader_wallet:
            leader_wallet = genesis_wallet  # Fallback to genesis wallet
        
        # Simulate leader creating block
        print(f"\n🏗️  Leader creating block with Gulf Stream transactions...")
        
        start_time = time.time()
        block = blockchain.create_block(leader_wallet, use_gulf_stream=True)
        creation_time = time.time() - start_time
        
        print(f"✅ Block created in {creation_time:.3f}s:")
        print(f"   ├─ Block number: {block.block_count}")
        print(f"   ├─ Transactions: {len(block.transactions)}")
        print(f"   ├─ PoH entries: {len(block.poh_sequence) if hasattr(block, 'poh_sequence') else 0}")
        print(f"   └─ Leader: {block.forger[:30]}...")
        
        # PHASE 6: TURBINE PROPAGATION
        print(f"\n🌪️  PHASE 6: TURBINE BLOCK PROPAGATION")
        print("-" * 40)
        
        leader_id = "current_leader"
        transmission_tasks = blockchain.broadcast_block_with_turbine(block, leader_id)
        
        print(f"📡 Turbine propagation:")
        print(f"   ├─ Transmission tasks: {len(transmission_tasks)}")
        print(f"   ├─ Block shredded for parallel distribution")
        print(f"   └─ Fault tolerance via erasure coding")
        
        # PHASE 7: FINAL STATE
        print(f"\n🎯 PHASE 7: FINAL STATE")
        print("-" * 40)
        
        # Show account balances
        alice_balance = blockchain.account_model.get_balance(alice.public_key_string())
        bob_balance = blockchain.account_model.get_balance(bob.public_key_string())
        charlie_balance = blockchain.account_model.get_balance(charlie.public_key_string())
        
        print(f"💰 Final account balances:")
        print(f"   ├─ Alice: {alice_balance:.2f} tokens")
        print(f"   ├─ Bob: {bob_balance:.2f} tokens")
        print(f"   └─ Charlie: {charlie_balance:.2f} tokens")
        
        print(f"\n📊 Block included transactions:")
        for i, tx in enumerate(block.transactions):
            print(f"   {i+1}. {tx.id[:8]} ({tx.type}): {tx.amount} tokens")
    
    else:
        print("⚠️  No current leader found - leader schedule may need initialization")
    
    print(f"\n🎉 GULF STREAM FLOW DEMONSTRATION COMPLETE!")
    print("=" * 70)
    
    return {
        'blockchain': blockchain,
        'transactions': transactions,
        'validators': validators,
        'final_block': block if 'block' in locals() else None
    }

def print_gulf_stream_summary():
    """Print summary of Gulf Stream benefits"""
    
    print(f"\n📋 GULF STREAM PROTOCOL BENEFITS")
    print("=" * 70)
    
    benefits = [
        "🎯 Leader Pre-selection: Leaders known 1 minute in advance (2-min epoch)",
        "⚡ Fast Slots: 2-second slot duration for rapid block creation",
        "🌊 Transaction Forwarding: Transactions sent to upcoming leaders",
        "📦 Ready Blocks: Leaders can prepare blocks before their slot",
        "🚀 Low Latency: Reduced time from transaction to confirmation",
        "🔄 High Throughput: Continuous transaction processing",
        "📊 Predictable Performance: Deterministic leader schedule",
        "🌐 Network Efficiency: Optimal transaction routing"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")
    
    print(f"\n🔄 GULF STREAM FLOW SUMMARY:")
    print(f"   1. Leader schedule pre-computed (1 min advance, 2-min epoch)")
    print(f"   2. Transaction submitted to network")
    print(f"   3. Gulf Stream forwards to upcoming leaders")
    print(f"   4. Leaders receive transactions early")
    print(f"   5. Leader slot starts (2s duration)")
    print(f"   6. Leader creates block with available transactions")
    print(f"   7. PoH sequencing provides cryptographic ordering")
    print(f"   8. Turbine propagates block across network")
    print(f"   9. Fast consensus via PoH verification")
    print(f"   10. Network ready for next slot")

def main():
    """Run the Gulf Stream demonstration"""
    try:
        # Run the demonstration
        result = demonstrate_gulf_stream_flow()
        
        # Print summary
        print_gulf_stream_summary()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
