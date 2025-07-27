#!/usr/bin/env python3
"""
Multi-Node Transaction Test

Test transaction submission to all nodes and monitor block creation.
"""

import requests
import json
import time
from blockchain.transaction.transaction import Transaction
from blockchain.transaction.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils

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

def create_test_transaction():
    """Create a test transaction"""
    private_key, sender_public_key = load_keys()
    if not private_key:
        return None
        
    wallet = Wallet()
    wallet.from_key(private_key)
    
    transaction = Transaction(
        sender_public_key=sender_public_key,
        receiver_public_key=sender_public_key,
        amount=100.0,
        type="TRANSFER"
    )
    
    signature = wallet.sign(transaction.payload())
    transaction.sign(signature)
    
    return transaction

def submit_to_all_nodes(transaction):
    """Submit transaction to all available nodes"""
    nodes = [11000, 11001, 11002]
    results = {}
    
    encoded_transaction = BlockchainUtils.encode(transaction)
    payload = {"transaction": encoded_transaction}
    
    for port in nodes:
        try:
            url = f"http://localhost:{port}/api/v1/transaction/create/"
            response = requests.post(url, json=payload, timeout=5)
            results[port] = {
                "status": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text
            }
            print(f"📤 Node {port}: {response.status_code}")
        except Exception as e:
            results[port] = {"error": str(e)}
            print(f"❌ Node {port}: {e}")
    
    return results

def monitor_all_nodes():
    """Monitor blockchain state across all nodes"""
    nodes = [11000, 11001, 11002]
    results = {}
    
    for port in nodes:
        try:
            # Get blockchain state
            blockchain_url = f"http://localhost:{port}/api/v1/blockchain/"
            blockchain_response = requests.get(blockchain_url, timeout=3)
            
            # Get transaction pool
            pool_url = f"http://localhost:{port}/api/v1/transaction/transaction_pool/"
            pool_response = requests.get(pool_url, timeout=3)
            
            # Get leader info
            leader_url = f"http://localhost:{port}/api/v1/blockchain/leader/current/"
            leader_response = requests.get(leader_url, timeout=3)
            
            results[port] = {
                "blocks": len(blockchain_response.json().get('blocks', [])) if blockchain_response.status_code == 200 else "error",
                "pool_size": len(pool_response.json()) if pool_response.status_code == 200 else "error",
                "current_slot": leader_response.json().get('current_leader_info', {}).get('current_slot', 'error') if leader_response.status_code == 200 else "error"
            }
        except Exception as e:
            results[port] = {"error": str(e)}
    
    return results

def check_transaction_in_blocks(transaction_id):
    """Check if transaction appears in any block across all nodes"""
    nodes = [11000, 11001, 11002]
    
    for port in nodes:
        try:
            url = f"http://localhost:{port}/api/v1/blockchain/"
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                blockchain_data = response.json()
                for block in blockchain_data.get('blocks', []):
                    for tx in block.get('transactions', []):
                        if tx.get('id') == transaction_id:
                            return port, block
        except Exception as e:
            continue
    
    return None, None

def main():
    print("🌐 MULTI-NODE TRANSACTION TEST")
    print("=" * 50)
    
    # Step 1: Check initial state
    print("📊 Step 1: Initial blockchain state")
    initial_state = monitor_all_nodes()
    for port, state in initial_state.items():
        print(f"   Node {port}: {state.get('blocks', 'error')} blocks, pool: {state.get('pool_size', 'error')}, slot: {state.get('current_slot', 'error')}")
    
    # Step 2: Create transaction
    print("\n💰 Step 2: Creating transaction...")
    transaction = create_test_transaction()
    if not transaction:
        print("❌ Failed to create transaction")
        return False
    
    print(f"✅ Transaction created: {transaction.id}")
    
    # Step 3: Submit to all nodes
    print("\n📤 Step 3: Submitting to all nodes...")
    submission_results = submit_to_all_nodes(transaction)
    
    # Step 4: Monitor for 15 seconds
    print("\n⏳ Step 4: Monitoring for block creation (15 seconds)...")
    
    found_in_block = False
    for i in range(15):
        time.sleep(1)
        
        # Check if transaction appears in any block
        node_with_tx, block_with_tx = check_transaction_in_blocks(transaction.id)
        if node_with_tx:
            print(f"\n🎉 SUCCESS: Transaction found in block on node {node_with_tx}!")
            print(f"   Block number: {block_with_tx.get('block_count', 'unknown')}")
            print(f"   Transactions in block: {len(block_with_tx.get('transactions', []))}")
            found_in_block = True
            break
        
        # Show progress every 3 seconds
        if (i + 1) % 3 == 0:
            current_state = monitor_all_nodes()
            changes = []
            for port in [11000, 11001, 11002]:
                initial_blocks = initial_state.get(port, {}).get('blocks', 0)
                current_blocks = current_state.get(port, {}).get('blocks', 0)
                if current_blocks != initial_blocks:
                    changes.append(f"Node {port}: {initial_blocks} → {current_blocks}")
            
            if changes:
                print(f"   📈 Block changes: {', '.join(changes)}")
            else:
                print(f"   ⏳ No new blocks yet... ({i+1}/15)")
    
    # Step 5: Final state
    print("\n📊 Step 5: Final state")
    final_state = monitor_all_nodes()
    for port, state in final_state.items():
        initial_blocks = initial_state.get(port, {}).get('blocks', 0)
        final_blocks = state.get('blocks', 0)
        print(f"   Node {port}: {initial_blocks} → {final_blocks} blocks, pool: {state.get('pool_size', 'error')}")
    
    if found_in_block:
        print("\n🎉 SUCCESS: Transaction successfully included in blockchain!")
        return True
    else:
        print("\n❌ FAILED: Transaction not found in any block")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
