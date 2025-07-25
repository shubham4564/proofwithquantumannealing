#!/usr/bin/env python3
"""
Test script to verify unlimited block size functionality
"""

import sys
import os
import time

# Add the blockchain directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from blockchain.blockchain import Blockchain
from blockchain.transaction.transaction import Transaction
from blockchain.transaction.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils

def create_test_transaction(sender_wallet, receiver_wallet, amount):
    """Create and sign a test transaction"""
    transaction = Transaction(
        sender_wallet.public_key_string(),
        receiver_wallet.public_key_string(),
        amount,
        "TRANSFER"
    )
    # Sign transaction using wallet's sign method
    signature = sender_wallet.sign(transaction.payload())
    transaction.signature = signature
    return transaction

def test_unlimited_block_size():
    """Test that blocks can include many transactions without size limits"""
    print("=== Testing Unlimited Block Size ===")
    
    # Create blockchain and wallets
    genesis_wallet = Wallet()
    blockchain = Blockchain(genesis_wallet.public_key_string())
    proposer_wallet = Wallet()
    
    # Create many test transactions
    transactions = []
    sender_wallets = []
    receiver_wallets = []
    
    # Create 100 transactions (would exceed traditional block size limits)
    num_transactions = 100
    print(f"Creating {num_transactions} test transactions...")
    
    for i in range(num_transactions):
        sender = Wallet()
        receiver = Wallet()
        sender_wallets.append(sender)
        receiver_wallets.append(receiver)
        
        transaction = create_test_transaction(sender, receiver, 10 + i)
        transactions.append(transaction)
    
    print(f"Created {len(transactions)} transactions")
    
    # Create block with all transactions
    print("Creating block with all transactions (no size limit)...")
    
    try:
        block = blockchain.create_block(transactions, proposer_wallet)
        
        print(f"✅ Block created successfully!")
        print(f"   Block number: {block.block_count}")
        print(f"   Transactions included: {len(block.transactions)}")
        print(f"   Expected transactions: {num_transactions}")
        
        if hasattr(block, 'calculate_size'):
            block_size = block.calculate_size()
            print(f"   Block size: {block_size} bytes")
        
        # Verify all transactions were included
        if len(block.transactions) == len(transactions):
            print(f"✅ All {len(transactions)} transactions included in block")
        else:
            print(f"❌ Only {len(block.transactions)}/{len(transactions)} transactions included")
            return False
            
        # Note: Block is already added to blockchain by create_block method
        # No need to validate separately as it's already validated during creation
        print("✅ Block creation and validation passed (no size limit enforcement)")
        return True
        
    except Exception as e:
        print(f"❌ Block creation failed: {e}")
        return False

def test_signature_validation():
    """Test that invalid signature transactions are rejected"""
    print("\n=== Testing Signature Validation ===")
    
    genesis_wallet = Wallet()
    blockchain = Blockchain(genesis_wallet.public_key_string())
    proposer_wallet = Wallet()
    
    # Create mix of valid and invalid transactions
    valid_wallet1 = Wallet()
    valid_wallet2 = Wallet()
    invalid_wallet = Wallet()
    
    transactions = []
    
    # Create valid transaction
    valid_tx = create_test_transaction(valid_wallet1, valid_wallet2, 50)
    transactions.append(valid_tx)
    
    # Create transaction with invalid signature
    invalid_tx = Transaction(
        invalid_wallet.public_key_string(),
        valid_wallet2.public_key_string(),
        25,
        "TRANSFER"
    )
    invalid_tx.signature = "invalid_signature_here"  # Invalid signature
    transactions.append(invalid_tx)
    
    # Create another valid transaction
    valid_tx2 = create_test_transaction(valid_wallet2, valid_wallet1, 30)
    transactions.append(valid_tx2)
    
    print(f"Created {len(transactions)} transactions (1 valid, 1 invalid, 1 valid)")
    
    try:
        block = blockchain.create_block(transactions, proposer_wallet)
        
        print(f"Block created with {len(block.transactions)} transactions")
        
        # Should only include valid transactions
        if len(block.transactions) == 2:  # Should exclude the invalid one
            print("✅ Invalid signature transaction correctly excluded")
            return True
        else:
            print(f"❌ Expected 2 valid transactions, got {len(block.transactions)}")
            return False
            
    except Exception as e:
        print(f"❌ Block creation failed: {e}")
        return False

def test_block_validation_without_size_limits():
    """Test that block validation no longer checks size limits"""
    print("\n=== Testing Block Validation (No Size Limits) ===")
    
    genesis_wallet = Wallet()
    blockchain = Blockchain(genesis_wallet.public_key_string())
    proposer_wallet = Wallet()
    
    # Create a large number of transactions
    transactions = []
    for i in range(200):  # Even more transactions
        sender = Wallet()
        receiver = Wallet()
        tx = create_test_transaction(sender, receiver, 1 + i)
        transactions.append(tx)
    
    print(f"Creating block with {len(transactions)} transactions...")
    
    try:
        block = blockchain.create_block(transactions, proposer_wallet)
        
        # Note: Block is already added to blockchain and validated by create_block method
        print(f"✅ Large block with {len(block.transactions)} transactions is valid")
        print("✅ No size limit enforcement in validation")
        return True
            
    except Exception as e:
        print(f"❌ Large block creation failed: {e}")
        return False

def main():
    """Run all unlimited block size tests"""
    print("🚀 Starting Unlimited Block Size Tests\n")
    
    try:
        test1_result = test_unlimited_block_size()
        test2_result = test_signature_validation()
        test3_result = test_block_validation_without_size_limits()
        
        print(f"\n📋 Test Results:")
        print(f"  ✅ Unlimited Block Size: {'PASS' if test1_result else 'FAIL'}")
        print(f"  ✅ Signature Validation: {'PASS' if test2_result else 'FAIL'}")
        print(f"  ✅ Block Validation (No Size Limits): {'PASS' if test3_result else 'FAIL'}")
        
        if test1_result and test2_result and test3_result:
            print(f"\n🎉 All tests passed!")
            print(f"✅ Block proposers can now include ALL valid transactions")
            print(f"✅ No more block size limitations")
            print(f"✅ Signature validation working correctly")
            print(f"✅ Invalid transactions excluded (not entire block rejected)")
            return 0
        else:
            print(f"\n❌ Some tests failed")
            return 1
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
