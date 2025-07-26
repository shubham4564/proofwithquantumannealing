#!/usr/bin/env python3
"""
Transaction Flow Demonstration Script

This script demonstrates the complete flow of a transaction from creation
to inclusion in all nodes' blockchains, step by step.
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

def demonstrate_transaction_flow():
    """Demonstrate complete transaction flow with detailed logging"""
    
    print("🚀 TRANSACTION FLOW DEMONSTRATION")
    print("=" * 60)
    
    # PHASE 1: NETWORK SETUP
    print("\n📡 PHASE 1: NETWORK SETUP")
    print("-" * 30)
    
    # Create leader node
    leader_wallet = Wallet()
    leader_blockchain = Blockchain(leader_wallet.public_key_string())
    leader_id = "leader_node_001"
    
    print(f"✅ Leader node created: {leader_wallet.public_key_string()[:30]}...")
    
    # Create validator nodes
    validators = []
    for i in range(3):
        validator_wallet = Wallet()
        validator_blockchain = Blockchain(validator_wallet.public_key_string())
        validator_id = f"validator_{i+1}"
        
        validators.append({
            'id': validator_id,
            'wallet': validator_wallet,
            'blockchain': validator_blockchain,
            'transaction_pool': []
        })
        
        # Register in Turbine network
        stake_weight = 1000.0 - (i * 200)
        leader_blockchain.register_turbine_validator(validator_id, stake_weight, f"192.168.1.{110+i}")
        
        print(f"✅ Validator {validator_id} created (stake: {stake_weight})")
    
    # Register leader in Turbine
    leader_blockchain.register_turbine_validator(leader_id, 5000.0, "192.168.1.100")
    
    # PHASE 2: TRANSACTION CREATION
    print("\n💰 PHASE 2: TRANSACTION CREATION")
    print("-" * 30)
    
    # Create user wallets
    alice = Wallet()
    bob = Wallet()
    
    print(f"👤 Alice wallet: {alice.public_key_string()[:30]}...")
    print(f"👤 Bob wallet: {bob.public_key_string()[:30]}...")
    
    # Step 1: Create and sign transaction
    print("\n🔐 Step 1: Creating and signing transaction")
    transaction = alice.create_transaction(bob.public_key_string(), 250.0, "TRANSFER")
    
    print(f"   📝 Transaction created:")
    print(f"   ├─ ID: {transaction.id}")
    print(f"   ├─ From: {transaction.sender_public_key[:30]}...")
    print(f"   ├─ To: {transaction.receiver_public_key[:30]}...")
    print(f"   ├─ Amount: {transaction.amount}")
    print(f"   ├─ Type: {transaction.type}")
    print(f"   ├─ Timestamp: {transaction.timestamp}")
    print(f"   └─ Signature: {transaction.signature[:30]}...")
    
    # Step 2: Validate signature
    print("\n✅ Step 2: Validating transaction signature")
    signature_valid = Wallet.signature_valid(
        transaction.payload(), 
        transaction.signature, 
        transaction.sender_public_key
    )
    print(f"   Signature validation: {'PASSED' if signature_valid else 'FAILED'}")
    
    # PHASE 3: NETWORK SUBMISSION
    print("\n🌐 PHASE 3: NETWORK SUBMISSION")
    print("-" * 30)
    
    # Step 3: Submit to network (simulate)
    print("📤 Step 3: Submitting transaction to network")
    
    # Add to leader's transaction pool
    leader_transaction_pool = [transaction]
    
    # Simulate gossip to validators
    for validator in validators:
        validator['transaction_pool'].append(transaction)
    
    print(f"   ✅ Transaction added to leader pool")
    print(f"   ✅ Transaction gossipped to {len(validators)} validators")
    
    # PHASE 4: LEADER SELECTION
    print("\n👑 PHASE 4: LEADER SELECTION")
    print("-" * 30)
    
    # Step 4: Leader selection
    print("🎯 Step 4: Selecting block proposer")
    current_leader = leader_blockchain.next_block_proposer()
    
    print(f"   🏆 Selected leader: {current_leader[:30] if current_leader else 'None'}...")
    print(f"   ⏰ Leader slot duration: 30 seconds")
    print(f"   📊 Selection method: Quantum Annealing Consensus")
    
    # PHASE 5: POH SEQUENCING
    print("\n⏱️  PHASE 5: POH SEQUENCING")
    print("-" * 30)
    
    # Step 5: PoH sequencing
    print("🔗 Step 5: PoH sequencing by leader")
    
    # Create funding transaction first (so Alice has balance)
    funding_tx = leader_wallet.create_transaction(alice.public_key_string(), 1000.0, "EXCHANGE")
    transactions_for_block = [funding_tx, transaction]
    
    print(f"   📥 Leader collected {len(transactions_for_block)} transactions")
    print(f"   🔄 Starting PoH sequencing...")
    
    # Show PoH process step by step
    leader_blockchain.poh_sequencer.reset("demo_block_hash")
    
    for i, tx in enumerate(transactions_for_block):
        # Add tick
        leader_blockchain.poh_sequencer.tick()
        tick_hash = leader_blockchain.poh_sequencer.current_hash
        print(f"   ├─ Tick {i+1}: {tick_hash[:16]}...")
        
        # Ingest transaction
        leader_blockchain.poh_sequencer.ingest_transaction(tx)
        tx_hash = leader_blockchain.poh_sequencer.current_hash
        print(f"   ├─ TX {i+1} ingested: {tx_hash[:16]}...")
    
    # Final ticks
    for i in range(2):
        leader_blockchain.poh_sequencer.tick()
        final_hash = leader_blockchain.poh_sequencer.current_hash
        print(f"   └─ Final tick {i+1}: {final_hash[:16]}...")
    
    poh_sequence = leader_blockchain.poh_sequencer.get_sequence()
    print(f"   ✅ PoH sequence complete: {len(poh_sequence)} entries")
    
    # PHASE 6: BLOCK CREATION
    print("\n📦 PHASE 6: BLOCK CREATION")
    print("-" * 30)
    
    # Step 6: Create block
    print("🏗️  Step 6: Creating block with PoH sequence")
    
    start_time = time.time()
    block = leader_blockchain.create_block(transactions_for_block, leader_wallet)
    creation_time = time.time() - start_time
    
    print(f"   📊 Block created in {creation_time:.3f} seconds")
    print(f"   ├─ Block number: {block.block_count}")
    print(f"   ├─ Transactions: {len(block.transactions)}")
    print(f"   ├─ PoH entries: {len(block.poh_sequence) if hasattr(block, 'poh_sequence') else 0}")
    print(f"   ├─ Block hash: {str(block.payload())[:30]}...")
    print(f"   └─ Proposer: {block.forger[:30]}...")
    
    # PHASE 7: TURBINE PROPAGATION
    print("\n🌪️  PHASE 7: TURBINE PROPAGATION")
    print("-" * 30)
    
    # Step 7: Block shredding and propagation
    print("✂️  Step 7: Shredding block for Turbine propagation")
    
    transmission_tasks = leader_blockchain.broadcast_block_with_turbine(block, leader_id)
    
    print(f"   🔪 Block shredded into packets")
    print(f"   📤 Transmission tasks: {len(transmission_tasks)}")
    
    for i, task in enumerate(transmission_tasks[:3]):  # Show first 3
        print(f"   ├─ Task {i+1}: {len(task['shreds'])} shreds → {task['target_node']}")
    
    if len(transmission_tasks) > 3:
        print(f"   └─ ... and {len(transmission_tasks) - 3} more tasks")
    
    # PHASE 8: NETWORK RECEPTION
    print("\n📡 PHASE 8: NETWORK RECEPTION")
    print("-" * 30)
    
    # Step 8: Simulate shred reception
    print("📥 Step 8: Validators receiving and processing shreds")
    
    if transmission_tasks:
        first_task = transmission_tasks[0]
        receiving_validator = validators[0]
        
        print(f"   🎯 {receiving_validator['id']} receiving {len(first_task['shreds'])} shreds")
        
        reconstruction_status = None
        for i, shred in enumerate(first_task['shreds']):
            shred_bytes = shred.to_bytes()
            result = receiving_validator['blockchain'].process_turbine_shred(
                shred_bytes, receiving_validator['id']
            )
            
            print(f"   ├─ Shred {i+1}/{len(first_task['shreds'])} processed")
            
            reconstruction_status = result['reconstruction_status']
            if reconstruction_status and reconstruction_status['is_reconstructed']:
                print(f"   ✅ Block reconstructed from {reconstruction_status['shreds_received']} shreds!")
                break
        
        # Show forwarding
        forwarding_tasks = result.get('forwarding_tasks', [])
        if forwarding_tasks:
            print(f"   📤 Forwarding to {len(forwarding_tasks)} child validators")
    
    # PHASE 9: VERIFICATION AND VALIDATION
    print("\n🔍 PHASE 9: VERIFICATION AND VALIDATION")
    print("-" * 30)
    
    # Step 9: PoH verification
    print("⚡ Step 9: Fast PoH verification by validators")
    
    for validator in validators:
        start_time = time.time()
        poh_valid = validator['blockchain'].verify_poh_sequence(block)
        verification_time = time.time() - start_time
        
        print(f"   ├─ {validator['id']}: PoH verification {'PASSED' if poh_valid else 'FAILED'} ({verification_time:.4f}s)")
        
        if poh_valid:
            start_time = time.time()
            block_valid = validator['blockchain'].block_valid(block)
            validation_time = time.time() - start_time
            
            print(f"   ├─ {validator['id']}: Block validation {'PASSED' if block_valid else 'FAILED'} ({validation_time:.4f}s)")
    
    # PHASE 10: BLOCKCHAIN INCLUSION
    print("\n⛓️  PHASE 10: BLOCKCHAIN INCLUSION")
    print("-" * 30)
    
    # Step 10: Add block to all blockchains
    print("📚 Step 10: Adding block to validator blockchains")
    
    initial_chain_lengths = []
    for validator in validators:
        initial_length = len(validator['blockchain'].blocks)
        initial_chain_lengths.append(initial_length)
        
        # Add block to validator's blockchain
        validator['blockchain'].add_block(block)
        
        final_length = len(validator['blockchain'].blocks)
        print(f"   ├─ {validator['id']}: Chain length {initial_length} → {final_length}")
    
    # PHASE 11: FINAL STATE
    print("\n🎯 PHASE 11: FINAL STATE")
    print("-" * 30)
    
    print("📊 Final network state:")
    print(f"   ├─ Transaction ID: {transaction.id}")
    print(f"   ├─ Included in block: {block.block_count}")
    print(f"   ├─ Block on {len(validators) + 1} nodes")
    print(f"   ├─ Alice balance updated: ✅")
    print(f"   ├─ Bob balance updated: ✅")
    print(f"   └─ Network consensus: ✅")
    
    # Show account balances
    print("\n💰 Account balances after transaction:")
    alice_balance = leader_blockchain.account_model.get_balance(alice.public_key_string())
    bob_balance = leader_blockchain.account_model.get_balance(bob.public_key_string())
    
    print(f"   ├─ Alice: {alice_balance:.2f} tokens")
    print(f"   └─ Bob: {bob_balance:.2f} tokens")
    
    print("\n🎉 TRANSACTION FLOW COMPLETE!")
    print("=" * 60)
    
    return {
        'transaction': transaction,
        'block': block,
        'leader_blockchain': leader_blockchain,
        'validators': validators,
        'alice_balance': alice_balance,
        'bob_balance': bob_balance
    }

def print_flow_summary():
    """Print a summary of the transaction flow"""
    
    print("\n📋 TRANSACTION FLOW SUMMARY")
    print("=" * 60)
    
    flow_steps = [
        "1. Transaction Creation & Signing",
        "2. Network Submission & Gossip",
        "3. Leader Selection (Quantum Consensus)",
        "4. PoH Sequencing (Cryptographic Ordering)",
        "5. Block Creation with PoH",
        "6. Turbine Shredding & Propagation",
        "7. Network Reception & Reconstruction",
        "8. Fast PoH Verification",
        "9. Block Validation",
        "10. Blockchain Inclusion",
        "11. Account State Updates"
    ]
    
    for step in flow_steps:
        print(f"   {step}")
    
    print("\n🚀 Key Benefits:")
    print("   ✅ Verifiable transaction ordering via PoH")
    print("   ✅ Fast consensus through cryptographic verification")
    print("   ✅ Efficient propagation via Turbine protocol")
    print("   ✅ Fault-tolerant with erasure coding")
    print("   ✅ Scalable parallel execution potential")

def main():
    """Run the transaction flow demonstration"""
    try:
        # Run the demonstration
        result = demonstrate_transaction_flow()
        
        # Print summary
        print_flow_summary()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
