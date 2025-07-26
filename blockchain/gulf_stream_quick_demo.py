#!/usr/bin/env python3
"""
Gulf Stream Quick Demo - Simplified version for fast demonstration

This script demonstrates the Gulf Stream workflow without heavy quantum consensus
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


def create_simple_leader_schedule(blockchain, validators):
    """Create a simple round-robin leader schedule for demo"""
    
    # Bypass heavy quantum consensus and create simple schedule
    simple_schedule = {}
    leader_keys = [v['wallet'].public_key_string() for v in validators]
    
    # Create 30 slots (1 minute worth) with round-robin leaders
    for slot in range(30):
        leader_index = slot % len(leader_keys)
        simple_schedule[slot] = leader_keys[leader_index]
    
    # Set the schedule directly
    blockchain.leader_schedule.current_schedule = simple_schedule
    blockchain.leader_schedule.slots_per_epoch = 30  # Shorter for demo
    
    print(f"✅ Simple leader schedule created:")
    for slot in range(min(10, len(simple_schedule))):
        leader = simple_schedule[slot]
        print(f"   Slot {slot}: {leader[:20]}...")
    
    return simple_schedule


def demonstrate_gulf_stream_quick():
    """Quick Gulf Stream demonstration without heavy quantum consensus"""
    
    print("🌊 GULF STREAM QUICK DEMONSTRATION")
    print("=" * 50)
    
    # PHASE 1: NETWORK INITIALIZATION
    print("\n🚀 PHASE 1: NETWORK INITIALIZATION")
    print("-" * 30)
    
    # Create blockchain
    genesis_wallet = Wallet()
    blockchain = Blockchain(genesis_wallet.public_key_string())
    
    # Create validators
    validators = []
    for i in range(3):  # Just 3 validators for quick demo
        validator_wallet = Wallet()
        validator_id = f"validator_{i+1}"
        
        # Register in Turbine for block propagation
        stake_weight = 1000.0 - (i * 100)
        blockchain.register_turbine_validator(validator_id, stake_weight)
        
        validators.append({
            'id': validator_id,
            'wallet': validator_wallet,
            'stake': stake_weight
        })
        
        print(f"✅ Validator {validator_id} registered (stake: {stake_weight})")
    
    # PHASE 2: SIMPLE LEADER SCHEDULE
    print("\n📅 PHASE 2: LEADER SCHEDULE CREATION")
    print("-" * 30)
    
    simple_schedule = create_simple_leader_schedule(blockchain, validators)
    
    # Show current leader info
    current_slot = blockchain.leader_schedule.get_current_slot()
    current_leader = blockchain.leader_schedule.get_current_leader()
    
    print(f"\n📊 Current status:")
    print(f"   ├─ Current slot: {current_slot}")
    print(f"   ├─ Current leader: {current_leader[:20] if current_leader else 'None'}...")
    print(f"   └─ Total slots in epoch: {len(simple_schedule)}")
    
    # Show Gulf Stream targets
    upcoming = blockchain.leader_schedule.get_upcoming_leaders(10)
    print(f"\n🎯 Gulf Stream targets (next 5 leaders):")
    for i, (slot, leader, slot_time) in enumerate(upcoming[:5]):
        time_until = slot_time - time.time()
        print(f"   {i+1}. Slot {slot}: {leader[:20]}... (in {time_until:.1f}s)")
    
    # PHASE 3: TRANSACTION SUBMISSION
    print("\n💰 PHASE 3: TRANSACTION SUBMISSION")
    print("-" * 30)
    
    # Create user wallets
    alice = Wallet()
    bob = Wallet()
    
    print(f"👤 Created wallets:")
    print(f"   ├─ Alice: {alice.public_key_string()[:20]}...")
    print(f"   └─ Bob: {bob.public_key_string()[:20]}...")
    
    # Create transactions
    tx1 = genesis_wallet.create_transaction(alice.public_key_string(), 1000.0, "FUNDING")
    tx2 = alice.create_transaction(bob.public_key_string(), 300.0, "TRANSFER")
    
    print(f"\n📤 Submitting transactions via Gulf Stream:")
    
    # Submit via Gulf Stream
    result1 = blockchain.submit_transaction(tx1)
    print(f"   ├─ TX1 submitted: Genesis -> Alice (1000 tokens)")
    print(f"   └─ Forwarded to {len(result1.get('gulf_stream_status', {}).get('forwarding_stats', {}))} leaders")
    
    result2 = blockchain.submit_transaction(tx2)
    print(f"   ├─ TX2 submitted: Alice -> Bob (300 tokens)")
    print(f"   └─ Forwarded to {len(result2.get('gulf_stream_status', {}).get('forwarding_stats', {}))} leaders")
    
    # PHASE 4: GULF STREAM STATUS
    print("\n🌊 PHASE 4: GULF STREAM STATUS")
    print("-" * 30)
    
    gulf_stream_status = blockchain.gulf_stream_node.get_gulf_stream_status()
    stats = gulf_stream_status['forwarding_stats']
    
    print(f"📊 Gulf Stream statistics:")
    print(f"   ├─ Total transactions forwarded: {stats['total_forwarded']}")
    print(f"   ├─ Active forwarding pools: {stats['active_forward_pools']}")
    print(f"   └─ Total queued transactions: {stats['total_queued_transactions']}")
    
    # PHASE 5: BLOCK CREATION
    print("\n👑 PHASE 5: BLOCK CREATION SIMULATION")
    print("-" * 30)
    
    # Get current leader
    current_leader_key = blockchain.leader_schedule.get_current_leader()
    if current_leader_key:
        # Find the validator wallet for this leader
        leader_wallet = None
        for validator in validators:
            if validator['wallet'].public_key_string() == current_leader_key:
                leader_wallet = validator['wallet']
                break
        
        if not leader_wallet:
            leader_wallet = genesis_wallet  # Fallback
        
        print(f"🎯 Current leader creating block...")
        print(f"   Leader: {current_leader_key[:20]}...")
        
        # Create block with Gulf Stream transactions
        start_time = time.time()
        block = blockchain.create_block(leader_wallet, use_gulf_stream=True)
        creation_time = time.time() - start_time
        
        print(f"✅ Block created successfully:")
        print(f"   ├─ Block number: {block.block_count}")
        print(f"   ├─ Transactions included: {len(block.transactions)}")
        print(f"   ├─ Creation time: {creation_time:.3f}s")
        print(f"   └─ Leader: {block.forger[:20]}...")
        
        # PHASE 6: TURBINE PROPAGATION
        print(f"\n🌪️  PHASE 6: TURBINE PROPAGATION")
        print("-" * 30)
        
        leader_id = "current_leader"
        transmission_tasks = blockchain.broadcast_block_with_turbine(block, leader_id)
        
        print(f"📡 Turbine propagation initiated:")
        print(f"   ├─ Transmission tasks: {len(transmission_tasks)}")
        print(f"   ├─ Block shredded for parallel transmission")
        print(f"   └─ Erasure coding for fault tolerance")
        
        # PHASE 7: FINAL STATE
        print(f"\n🎯 PHASE 7: FINAL STATE")
        print("-" * 30)
        
        # Show account balances
        alice_balance = blockchain.account_model.get_balance(alice.public_key_string())
        bob_balance = blockchain.account_model.get_balance(bob.public_key_string())
        
        print(f"💰 Final account balances:")
        print(f"   ├─ Alice: {alice_balance:.2f} tokens")
        print(f"   └─ Bob: {bob_balance:.2f} tokens")
        
        print(f"\n📋 Block transaction summary:")
        for i, tx in enumerate(block.transactions):
            print(f"   {i+1}. {tx.id[:8]} ({tx.type}): {tx.amount} tokens")
    
    else:
        print("⚠️  No current leader available")
    
    print(f"\n🎉 GULF STREAM DEMONSTRATION COMPLETE!")
    print("=" * 50)


def print_gulf_stream_summary():
    """Print summary of Gulf Stream benefits"""
    
    print(f"\n📋 GULF STREAM PROTOCOL SUMMARY")
    print("=" * 50)
    
    benefits = [
        "🎯 Pre-computed Leaders: Deterministic schedule avoids delays",
        "⚡ Fast Slots: 2-second slots for rapid block creation", 
        "🌊 Transaction Forwarding: Early delivery to upcoming leaders",
        "📦 Block Preparation: Leaders can pre-build blocks",
        "🚀 Low Latency: Minimal time from submission to inclusion",
        "📊 Predictable Timing: Deterministic leader rotation",
        "🌐 Efficient Routing: Optimal transaction forwarding"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")
    
    print(f"\n🔄 WORKFLOW SUMMARY:")
    print(f"   1. Leader schedule computed in advance")
    print(f"   2. Transaction submitted to network")
    print(f"   3. Gulf Stream forwards to upcoming leaders")
    print(f"   4. Leaders prepare blocks early")
    print(f"   5. Leader slot begins (2-second duration)")
    print(f"   6. Pre-built block published immediately")
    print(f"   7. PoH provides cryptographic ordering")
    print(f"   8. Turbine broadcasts block efficiently")
    print(f"   9. Network moves to next slot")


def main():
    """Run the quick Gulf Stream demonstration"""
    try:
        # Run the demonstration
        demonstrate_gulf_stream_quick()
        
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
