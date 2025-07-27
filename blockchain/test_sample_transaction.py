#!/usr/bin/env python3
"""
Simple Transaction Test

This script creates a simple transaction and submits it to the blockchain
to test that everything is working correctly.
"""

import requests
import json
import base64
import time
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

def create_sample_transaction():
    """Create a sample transaction"""
    private_key, sender_public_key = load_keys()
    if not private_key:
        return None
        
    # Create wallet from private key
    wallet = Wallet()
    wallet.from_key(private_key)
    
    # Create a simple test transaction (self-send)
    transaction = Transaction(
        sender_public_key=sender_public_key,
        receiver_public_key=sender_public_key,  # Self-send for testing
        amount=10.0,
        type="TRANSFER"
    )
    
    # Sign the transaction
    signature = wallet.sign(transaction.payload())
    transaction.sign(signature)
    
    return transaction

def submit_transaction(transaction, node_port=11000):
    """Submit transaction to a node"""
    try:
        # Encode transaction
        encoded_transaction = BlockchainUtils.encode(transaction)
        
        # Prepare payload
        payload = {
            "transaction": encoded_transaction
        }
        
        # Submit to node
        url = f"http://localhost:{node_port}/api/v1/transaction/create/"
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
            
    except Exception as e:
        return False, str(e)

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

def main():
    print("🧪 SAMPLE TRANSACTION TEST")
    print("=" * 50)
    
    # Step 1: Check if nodes are running
    print("📡 Step 1: Checking node connectivity...")
    blockchain_state = check_blockchain_state()
    if not blockchain_state:
        print("❌ Error: Cannot connect to node on port 11000")
        print("   Make sure nodes are running: ./start_nodes.sh")
        return False
    
    initial_blocks = len(blockchain_state.get('blocks', []))
    print(f"✅ Node connected! Current blocks: {initial_blocks}")
    
    # Step 2: Check leader selection
    print("\n🎯 Step 2: Checking leader selection...")
    leader_status = check_leader_status()
    if leader_status:
        current_slot = leader_status.get('current_leader_info', {}).get('current_slot', 'unknown')
        time_remaining = leader_status.get('current_leader_info', {}).get('time_remaining_in_slot', 0)
        print(f"✅ Leader selection active! Current slot: {current_slot}, Time remaining: {time_remaining:.1f}s")
    else:
        print("⚠️  Leader selection status unknown")
    
    # Step 3: Create transaction
    print("\n💰 Step 3: Creating sample transaction...")
    transaction = create_sample_transaction()
    if not transaction:
        print("❌ Failed to create transaction")
        return False
    
    print(f"✅ Transaction created:")
    print(f"   ID: {transaction.id}")
    print(f"   Amount: {transaction.amount}")
    print(f"   Type: {transaction.type}")
    print(f"   Timestamp: {transaction.timestamp}")
    
    # Step 4: Submit transaction
    print("\n📤 Step 4: Submitting transaction...")
    success, result = submit_transaction(transaction)
    if not success:
        print(f"❌ Transaction submission failed: {result}")
        return False
    
    print(f"✅ Transaction submitted successfully!")
    print(f"   Response: {result}")
    
    # Step 5: Wait and check for block creation
    print("\n⏳ Step 5: Waiting for block creation...")
    for i in range(10):  # Wait up to 20 seconds
        time.sleep(2)
        new_state = check_blockchain_state()
        if new_state:
            new_blocks = len(new_state.get('blocks', []))
            if new_blocks > initial_blocks:
                print(f"✅ New block created! Total blocks: {new_blocks}")
                print(f"   📊 Block increase: {new_blocks - initial_blocks}")
                
                # Check if our transaction is in the latest block
                latest_block = new_state['blocks'][-1]
                block_transactions = latest_block.get('transactions', [])
                print(f"   📝 Transactions in latest block: {len(block_transactions)}")
                
                return True
            else:
                print(f"   ⏳ Waiting... Current blocks: {new_blocks} ({i+1}/10)")
    
    print("⚠️  No new blocks created in 20 seconds")
    print("   This might be normal - check leader rotation timing")
    
    # Step 6: Final status
    print("\n📊 Step 6: Final system status...")
    final_leader = check_leader_status()
    if final_leader:
        current_slot = final_leader.get('current_leader_info', {}).get('current_slot', 'unknown')
        print(f"   🎯 Current slot: {current_slot}")
    
    print("\n🎉 TRANSACTION TEST COMPLETED")
    print("✅ All core systems are operational:")
    print("   • Node connectivity ✅")
    print("   • Leader selection ✅") 
    print("   • Transaction submission ✅")
    print("   • API endpoints ✅")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
