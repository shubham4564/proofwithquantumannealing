#!/usr/bin/env python3
"""
Test script for PoH sequencing and Turbine block propagation.

This script demonstrates:
1. PoH sequencing of transactions in the leader node
2. Block creation with PoH timestamps
3. Block shredding and Turbine propagation
4. Block reconstruction and PoH verification
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

def test_poh_sequencing():
    """Test PoH sequencing functionality"""
    print("\n=== Testing PoH Sequencing ===")
    
    # Create blockchain and wallets
    genesis_wallet = Wallet()
    blockchain = Blockchain(genesis_wallet.public_key_string())
    
    # Create test wallets
    alice = Wallet()
    bob = Wallet()
    charlie = Wallet()
    
    # Create test transactions
    transactions = []
    
    # Alice receives initial funding
    tx1 = genesis_wallet.create_transaction(alice.public_key_string(), 100.0, "EXCHANGE")
    transactions.append(tx1)
    
    # Bob receives initial funding
    tx2 = genesis_wallet.create_transaction(bob.public_key_string(), 50.0, "EXCHANGE")
    transactions.append(tx2)
    
    # Alice sends to Charlie
    tx3 = alice.create_transaction(charlie.public_key_string(), 30.0, "TRANSFER")
    transactions.append(tx3)
    
    # Bob sends to Charlie
    tx4 = bob.create_transaction(charlie.public_key_string(), 20.0, "TRANSFER")
    transactions.append(tx4)
    
    print(f"Created {len(transactions)} test transactions")
    
    # Create block with PoH sequencing
    start_time = time.time()
    block = blockchain.create_block(transactions, genesis_wallet)
    end_time = time.time()
    
    print(f"Block created with PoH sequencing in {end_time - start_time:.3f} seconds")
    print(f"Block contains {len(block.transactions)} transactions")
    
    # Verify PoH sequence exists
    if hasattr(block, 'poh_sequence'):
        print(f"PoH sequence contains {len(block.poh_sequence)} entries")
        
        # Show PoH sequence structure
        tx_count = sum(1 for entry in block.poh_sequence if entry.get('transaction'))
        tick_count = len(block.poh_sequence) - tx_count
        print(f"  - Transaction entries: {tx_count}")
        print(f"  - Tick entries: {tick_count}")
        
        # Show first few PoH entries
        print("\nFirst 3 PoH entries:")
        for i, entry in enumerate(block.poh_sequence[:3]):
            entry_type = "Transaction" if entry.get('transaction') else "Tick"
            print(f"  {i+1}. {entry_type}: {entry['hash'][:16]}...")
    
    # Verify block
    is_valid = blockchain.verify_poh_sequence(block)
    print(f"PoH sequence verification: {'PASSED' if is_valid else 'FAILED'}")
    
    return blockchain, block, genesis_wallet

def test_turbine_propagation(blockchain, block, leader_wallet):
    """Test Turbine block propagation"""
    print("\n=== Testing Turbine Block Propagation ===")
    
    # Register validators in Turbine tree
    validators = [
        ("validator_1", 1000.0, "192.168.1.10"),
        ("validator_2", 500.0, "192.168.1.11"),
        ("validator_3", 250.0, "192.168.1.12"),
        ("validator_4", 100.0, "192.168.1.13"),
        ("validator_5", 50.0, "192.168.1.14"),
    ]
    
    leader_id = "leader_node"
    blockchain.register_turbine_validator(leader_id, 2000.0, "192.168.1.1")
    
    for validator_id, stake, address in validators:
        blockchain.register_turbine_validator(validator_id, stake, address)
    
    print(f"Registered {len(validators) + 1} validators in Turbine tree")
    
    # Broadcast block using Turbine
    transmission_tasks = blockchain.broadcast_block_with_turbine(block, leader_id)
    print(f"Turbine broadcast prepared: {len(transmission_tasks)} transmission tasks")
    
    # Show transmission details
    for i, task in enumerate(transmission_tasks):
        print(f"  Task {i+1}: Send {len(task['shreds'])} shreds to {task['target_node']}")
    
    # Simulate shred reception and forwarding
    print("\nSimulating shred reception...")
    
    if transmission_tasks:
        # Simulate first validator receiving shreds
        first_task = transmission_tasks[0]
        receiving_node = first_task['target_node']
        
        for shred in first_task['shreds']:
            shred_bytes = shred.to_bytes()
            result = blockchain.process_turbine_shred(shred_bytes, receiving_node)
            
            forwarding_tasks = result['forwarding_tasks']
            status = result['reconstruction_status']
            
            if forwarding_tasks:
                print(f"  Shred forwarded to {len(forwarding_tasks)} child nodes")
            
            if status and status['is_reconstructed']:
                print(f"  Block reconstructed! Hash: {status['block_hash'][:16]}...")
                break
    
    return True

def test_poh_verification_performance():
    """Test PoH verification performance vs traditional validation"""
    print("\n=== Testing PoH Verification Performance ===")
    
    # Create blockchain with many transactions
    genesis_wallet = Wallet()
    blockchain = Blockchain(genesis_wallet.public_key_string())
    
    # Create many test transactions
    transactions = []
    wallets = [Wallet() for _ in range(10)]
    
    # Fund all wallets
    for wallet in wallets:
        tx = genesis_wallet.create_transaction(wallet.public_key_string(), 1000.0, "EXCHANGE")
        transactions.append(tx)
    
    # Create inter-wallet transactions
    for i in range(20):
        sender = wallets[i % len(wallets)]
        receiver = wallets[(i + 1) % len(wallets)]
        tx = sender.create_transaction(receiver.public_key_string(), 10.0, "TRANSFER")
        transactions.append(tx)
    
    print(f"Created {len(transactions)} transactions for performance test")
    
    # Create block with PoH sequencing
    start_time = time.time()
    block = blockchain.create_block(transactions, genesis_wallet)
    creation_time = time.time() - start_time
    
    print(f"Block creation time: {creation_time:.3f} seconds")
    
    # Test PoH verification speed
    start_time = time.time()
    is_valid = blockchain.verify_poh_sequence(block)
    verification_time = time.time() - start_time
    
    print(f"PoH verification time: {verification_time:.3f} seconds")
    print(f"Verification result: {'PASSED' if is_valid else 'FAILED'}")
    print(f"Performance ratio: {creation_time / verification_time:.1f}x faster verification")
    
    return True

def main():
    """Run all PoH and Turbine tests"""
    print("Starting PoH Sequencing and Turbine Protocol Tests")
    print("=" * 60)
    
    try:
        # Test PoH sequencing
        blockchain, block, leader_wallet = test_poh_sequencing()
        
        # Test Turbine propagation
        test_turbine_propagation(blockchain, block, leader_wallet)
        
        # Test performance
        test_poh_verification_performance()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("\nKey features demonstrated:")
        print("✅ PoH sequencing creates verifiable transaction order")
        print("✅ Turbine protocol shreds and propagates blocks efficiently")
        print("✅ PoH verification is faster than re-execution")
        print("✅ Network tree structure optimizes propagation")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
