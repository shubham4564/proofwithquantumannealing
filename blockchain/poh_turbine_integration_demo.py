#!/usr/bin/env python3
"""
Integration example showing how PoH and Turbine work with the existing node system.

This demonstrates:
1. How a leader node uses PoH sequencing when creating blocks
2. How other nodes receive and verify PoH-sequenced blocks
3. How Turbine protocol integrates with the P2P network
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

def simulate_leader_slot_with_poh():
    """Simulate a leader node's slot using PoH sequencing"""
    print("\n=== Leader Node: PoH Sequencing During Slot ===")
    
    # Initialize leader blockchain
    leader_wallet = Wallet()
    leader_blockchain = Blockchain(leader_wallet.public_key_string())
    
    print(f"Leader node initialized: {leader_wallet.public_key_string()[:30]}...")
    
    # Register the leader in Turbine network
    leader_id = "leader_node_001"
    leader_blockchain.register_turbine_validator(leader_id, 5000.0, "192.168.1.100")
    
    # Simulate incoming transactions during the slot
    incoming_transactions = []
    
    # Create test wallets for transaction senders
    alice = Wallet()
    bob = Wallet()
    charlie = Wallet()
    
    print("Simulating transaction flow during leader slot...")
    
    # Transactions arrive at different times during the slot
    print("  Time 0.1s: Alice funding transaction arrives")
    tx1 = leader_wallet.create_transaction(alice.public_key_string(), 1000.0, "EXCHANGE")
    incoming_transactions.append(tx1)
    
    print("  Time 0.3s: Bob funding transaction arrives")
    tx2 = leader_wallet.create_transaction(bob.public_key_string(), 500.0, "EXCHANGE")
    incoming_transactions.append(tx2)
    
    print("  Time 0.7s: Alice->Charlie transfer arrives")
    tx3 = alice.create_transaction(charlie.public_key_string(), 250.0, "TRANSFER")
    incoming_transactions.append(tx3)
    
    print("  Time 1.2s: Bob->Charlie transfer arrives")
    tx4 = bob.create_transaction(charlie.public_key_string(), 100.0, "TRANSFER")
    incoming_transactions.append(tx4)
    
    print("  Time 1.8s: Charlie->Alice transfer arrives")
    tx5 = charlie.create_transaction(alice.public_key_string(), 50.0, "TRANSFER")
    incoming_transactions.append(tx5)
    
    print(f"\nLeader collected {len(incoming_transactions)} transactions during slot")
    
    # Leader creates block using PoH sequencing
    print("\nLeader creating block with PoH sequencing...")
    start_time = time.time()
    block = leader_blockchain.create_block(incoming_transactions, leader_wallet)
    creation_time = time.time() - start_time
    
    print(f"Block created in {creation_time:.3f} seconds")
    print(f"Block hash: {block.payload()}")
    print(f"PoH entries: {len(block.poh_sequence) if hasattr(block, 'poh_sequence') else 0}")
    
    # Prepare for Turbine broadcast
    transmission_tasks = leader_blockchain.broadcast_block_with_turbine(block, leader_id)
    print(f"Turbine transmission tasks prepared: {len(transmission_tasks)}")
    
    return leader_blockchain, block, transmission_tasks

def simulate_validator_nodes_receiving_block(leader_blockchain, block, transmission_tasks):
    """Simulate validator nodes receiving and verifying the PoH block"""
    print("\n=== Validator Nodes: Receiving PoH Block via Turbine ===")
    
    # Create validator nodes
    validators = []
    for i in range(3):
        validator_wallet = Wallet()
        validator_blockchain = Blockchain(validator_wallet.public_key_string())
        validator_id = f"validator_{i+1}"
        
        # Register in Turbine tree
        stake_weight = 1000.0 - (i * 200)  # Decreasing stake
        validator_blockchain.register_turbine_validator(validator_id, stake_weight, f"192.168.1.{110+i}")
        
        validators.append({
            'id': validator_id,
            'wallet': validator_wallet,
            'blockchain': validator_blockchain,
            'stake': stake_weight
        })
        
        print(f"Validator {validator_id} initialized (stake: {stake_weight})")
    
    # Simulate shred reception and block reconstruction
    print("\nSimulating Turbine shred propagation...")
    
    if transmission_tasks:
        # Get first transmission task (to highest-stake validator)
        first_task = transmission_tasks[0]
        first_validator = validators[0]  # Assume this corresponds to highest stake
        
        print(f"Transmitting {len(first_task['shreds'])} shreds to {first_validator['id']}")
        
        # Simulate receiving each shred
        received_shreds = []
        for i, shred in enumerate(first_task['shreds']):
            shred_bytes = shred.to_bytes()
            result = first_validator['blockchain'].process_turbine_shred(shred_bytes, first_validator['id'])
            
            print(f"  Shred {i+1} received and processed")
            
            # Check if block is reconstructed
            if result['reconstruction_status'] and result['reconstruction_status']['is_reconstructed']:
                print(f"  ✅ Block reconstructed from {result['reconstruction_status']['shreds_received']} shreds!")
                break
        
        # Forward shreds to other validators
        forwarding_tasks = result.get('forwarding_tasks', [])
        if forwarding_tasks:
            print(f"  Forwarding shreds to {len(forwarding_tasks)} child validators")
    
    # Simulate PoH verification on reconstructed block
    print("\nValidators verifying PoH sequence...")
    
    for validator in validators:
        start_time = time.time()
        is_valid = validator['blockchain'].verify_poh_sequence(block)
        verification_time = time.time() - start_time
        
        print(f"  {validator['id']}: PoH verification {'PASSED' if is_valid else 'FAILED'} ({verification_time:.4f}s)")
        
        # Simulate block validation
        if is_valid:
            start_time = time.time()
            block_valid = validator['blockchain'].block_valid(block)
            validation_time = time.time() - start_time
            
            print(f"  {validator['id']}: Block validation {'PASSED' if block_valid else 'FAILED'} ({validation_time:.4f}s)")

def demonstrate_poh_ordering_benefits():
    """Demonstrate how PoH ordering enables parallel execution"""
    print("\n=== PoH Ordering Benefits: Parallel Execution Potential ===")
    
    blockchain = Blockchain()
    
    # Create wallets for demonstration
    wallets = [Wallet() for _ in range(6)]
    wallet_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank']
    
    # Fund all wallets
    funding_txs = []
    for wallet in wallets:
        tx = blockchain.genesis_public_key
        if tx:  # If we have a genesis key
            genesis_wallet = Wallet()
            genesis_wallet.from_key('keys/genesis_private_key.pem')
            funding_tx = genesis_wallet.create_transaction(wallet.public_key_string(), 1000.0, "EXCHANGE")
            funding_txs.append(funding_tx)
    
    print(f"Created {len(funding_txs)} funding transactions")
    
    # Create a set of transactions that can be executed in parallel
    parallel_txs = []
    
    # Group 1: Alice->Bob, Charlie->Diana (no conflicts)
    if len(wallets) >= 4:
        tx1 = wallets[0].create_transaction(wallets[1].public_key_string(), 100.0, "TRANSFER")  # Alice->Bob
        tx2 = wallets[2].create_transaction(wallets[3].public_key_string(), 150.0, "TRANSFER")  # Charlie->Diana
        parallel_txs.extend([tx1, tx2])
    
    # Group 2: Eve->Frank (independent)
    if len(wallets) >= 6:
        tx3 = wallets[4].create_transaction(wallets[5].public_key_string(), 200.0, "TRANSFER")  # Eve->Frank
        parallel_txs.append(tx3)
    
    print(f"Created {len(parallel_txs)} transactions that can execute in parallel")
    
    # Show PoH ordering
    all_transactions = funding_txs + parallel_txs
    if all_transactions:
        # Reset PoH sequencer and sequence transactions
        blockchain.poh_sequencer.reset("demo_hash")
        
        print("\nPoH sequencing transactions...")
        for i, tx in enumerate(all_transactions):
            blockchain.poh_sequencer.tick()
            blockchain.poh_sequencer.ingest_transaction(tx)
            print(f"  {i+1}. Transaction ingested at PoH hash: {blockchain.poh_sequencer.current_hash[:16]}...")
        
        poh_sequence = blockchain.poh_sequencer.get_sequence()
        print(f"\nPoH sequence created with {len(poh_sequence)} entries")
        print("Benefits of PoH ordering:")
        print("✅ Transactions have cryptographic timestamps")
        print("✅ Order is verifiable without re-execution")
        print("✅ Non-conflicting transactions can be executed in parallel")
        print("✅ Validators can verify order quickly")

def main():
    """Run the complete PoH and Turbine integration demonstration"""
    print("PoH Sequencing and Turbine Protocol Integration Demo")
    print("=" * 70)
    
    try:
        # Simulate leader slot with PoH
        leader_blockchain, block, transmission_tasks = simulate_leader_slot_with_poh()
        
        # Simulate validator nodes receiving block
        simulate_validator_nodes_receiving_block(leader_blockchain, block, transmission_tasks)
        
        # Demonstrate PoH benefits
        demonstrate_poh_ordering_benefits()
        
        print("\n" + "=" * 70)
        print("Integration Demo Completed Successfully!")
        print("\n🚀 Key Integration Points:")
        print("1. Leader uses PoH sequencing during slot")
        print("2. Block contains cryptographic transaction ordering")
        print("3. Turbine protocol shreds block for efficient propagation")
        print("4. Validators reconstruct block from shreds")
        print("5. PoH verification is much faster than re-execution")
        print("6. Network achieves high throughput with verifiable ordering")
        
        return True
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
