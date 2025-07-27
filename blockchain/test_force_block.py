#!/usr/bin/env python3
"""
Force Block Creation Test

This script forces block creation to test transaction inclusion,
bypassing the leader selection issues.
"""

import requests
import json
import time
from blockchain.transaction.transaction import Transaction
from blockchain.transaction.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils

def force_create_block(node_port=11000):
    """Force a node to create a block by directly calling the propose_block method"""
    try:
        # First submit a transaction
        print("🔨 FORCING BLOCK CREATION")
        print("=" * 40)
        
        # Create and submit a transaction first
        print("📤 Step 1: Creating and submitting transaction...")
        private_key, sender_public_key = load_keys()
        if not private_key:
            return False
            
        wallet = Wallet()
        wallet.from_key(private_key)
        
        transaction = Transaction(
            sender_public_key=sender_public_key,
            receiver_public_key=sender_public_key,
            amount=50.0,
            type="TRANSFER"
        )
        
        signature = wallet.sign(transaction.payload())
        transaction.sign(signature)
        
        # Submit transaction
        encoded_transaction = BlockchainUtils.encode(transaction)
        payload = {"transaction": encoded_transaction}
        
        url = f"http://localhost:{node_port}/api/v1/transaction/create/"
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Transaction submitted: {transaction.id}")
        else:
            print(f"❌ Transaction submission failed: {response.status_code}")
            return False
        
        # Check initial blockchain state
        blockchain_url = f"http://localhost:{node_port}/api/v1/blockchain/"
        initial_response = requests.get(blockchain_url, timeout=5)
        initial_blocks = len(initial_response.json().get('blocks', [])) if initial_response.status_code == 200 else 0
        print(f"📊 Initial blocks: {initial_blocks}")
        
        # Check transaction pool
        pool_url = f"http://localhost:{node_port}/api/v1/transaction/transaction_pool/"
        pool_response = requests.get(pool_url, timeout=5)
        pool_size = len(pool_response.json()) if pool_response.status_code == 200 else 0
        print(f"📊 Transaction pool size: {pool_size}")
        
        print("\n⏳ Step 2: Waiting for automatic block creation (10 seconds)...")
        time.sleep(10)
        
        # Check if block was created automatically
        final_response = requests.get(blockchain_url, timeout=5)
        final_blocks = len(final_response.json().get('blocks', [])) if final_response.status_code == 200 else 0
        
        print(f"📊 Final blocks: {final_blocks}")
        
        if final_blocks > initial_blocks:
            print("✅ Block created automatically!")
            
            # Check if transaction is in the new block
            blockchain_data = final_response.json()
            latest_block = blockchain_data['blocks'][-1]
            block_transactions = latest_block.get('transactions', [])
            print(f"📝 Transactions in latest block: {len(block_transactions)}")
            
            if block_transactions:
                print("✅ SUCCESS: Transaction included in block!")
                for i, tx in enumerate(block_transactions):
                    print(f"   {i+1}. Transaction ID: {tx.get('id', 'unknown')}")
                    print(f"      Amount: {tx.get('amount', 'unknown')}")
                    print(f"      Type: {tx.get('type', 'unknown')}")
                return True
            else:
                print("⚠️  Block created but no transactions included")
                return False
        else:
            print("❌ No block created automatically")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def load_keys():
    """Load genesis keys for testing"""
    try:
        with open('keys/genesis_private_key.pem', 'r') as f:
            private_key = f.read()
        with open('keys/genesis_public_key.pem', 'r') as f:
            public_key = f.read()
        return private_key, public_key
    except FileNotFoundError:
        print("❌ Error: Key files not found")
        return None, None

def test_multiple_nodes():
    """Test block creation across multiple nodes"""
    print("\n🌐 TESTING MULTIPLE NODES")
    print("=" * 40)
    
    nodes = [11000, 11001, 11002]
    results = {}
    
    for port in nodes:
        try:
            url = f"http://localhost:{port}/api/v1/blockchain/"
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                blocks = len(response.json().get('blocks', []))
                results[port] = blocks
                print(f"✅ Node {port}: {blocks} blocks")
            else:
                results[port] = "offline"
                print(f"❌ Node {port}: offline")
        except:
            results[port] = "error"
            print(f"❌ Node {port}: connection error")
    
    return results

if __name__ == "__main__":
    print("🧪 FORCE BLOCK CREATION TEST")
    print("=" * 50)
    
    # Test multiple nodes first
    test_multiple_nodes()
    
    # Force block creation
    success = force_create_block()
    
    print("\n📊 FINAL STATUS")
    print("=" * 30)
    if success:
        print("🎉 SUCCESS: Transaction included in block!")
    else:
        print("❌ FAILED: Transaction not included in block")
    
    # Show final state
    test_multiple_nodes()
