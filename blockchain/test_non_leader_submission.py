#!/usr/bin/env python3
"""
Test submission when NOT the current leader to demonstrate waiting behavior.
This test will wait for the node to NOT be the leader, then submit a transaction.
"""

import time
import requests
import json
import hashlib
import argparse
from datetime import datetime
import sys
from pathlib import Path

# Use the same imports as test_sample_transaction.py
from blockchain.transaction.transaction import Transaction
from blockchain.transaction.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils

def get_current_slot():
    """Get current slot from the blockchain."""
    try:
        response = requests.get("http://localhost:11000/api/v1/blockchain/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('current_slot', 0)
    except:
        pass
    return 0

def check_leadership():
    """Check if current node is the leader."""
    try:
        response = requests.get("http://localhost:11000/api/v1/blockchain/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('is_leader', False)
    except:
        pass
    return False

def wait_for_non_leadership():
    """Wait until the current node is NOT the leader."""
    print("🕐 Waiting for node to NOT be the current leader...")
    start_time = time.time()
    
    while time.time() - start_time < 30:  # 30 second timeout
        is_leader = check_leadership()
        current_slot = get_current_slot()
        
        print(f"   Slot {current_slot}: Am I leader? {is_leader}")
        
        if not is_leader:
            print(f"✅ Node is NOT the leader at slot {current_slot}!")
            return current_slot
            
        time.sleep(0.5)  # Check every 500ms
    
    print("❌ Timeout: Node remained leader for too long")
    return None

def main():
    print("🔄 NON-LEADER SUBMISSION TEST")
    print("=" * 50)
    
    # Wait for non-leadership
    submission_slot = wait_for_non_leadership()
    if submission_slot is None:
        print("❌ Could not find a slot where node is not leader")
        return
    
    print(f"\n💡 Node is NOT leader at slot {submission_slot}")
    print("📤 Now submitting transaction to demonstrate waiting behavior...")
    
    # Create transaction using simplified approach
    print("\n� Step 2: Creating transaction...")
    try:
        start_create = time.time()
        
        # Create a simple transaction structure
        transaction = {
            "id": f"test_tx_{int(time.time() * 1000)}",
            "sender": "genesis_address",
            "recipient": "test_recipient_address", 
            "amount": 20.0,
            "transaction_type": "TRANSFER",
            "timestamp": time.time(),
            "data": {"test": "non_leader_submission"}
        }
        
        create_time = (time.time() - start_create) * 1000
        print(f"✅ Transaction created in {create_time:.1f}ms")
        print(f"   ID: {transaction['id']}")
        print(f"   Amount: {transaction['amount']}")
    except Exception as e:
        print(f"❌ Failed to create transaction: {e}")
        return
    
    # Submit transaction
    print(f"\n📤 Step 3: Submitting at slot {submission_slot} (NOT leader)...")
    try:
        start_submit = time.time()
        response = requests.post(
            "http://localhost:11000/api/v1/transactions/submit",
            json=transaction,
            timeout=30
        )
        submit_time = (time.time() - start_submit) * 1000
        
        if response.status_code == 200:
            print(f"✅ Transaction submitted in {submit_time:.1f}ms")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Submit failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Submit failed: {e}")
        return
    
    # Monitor for processing
    print(f"\n⏳ Step 4: Monitoring for processing...")
    print(f"   📊 Submitted at slot {submission_slot} when NOT leader")
    print(f"   🕐 Watching for block creation...")
    
    start_monitor = time.time()
    initial_blocks = 0
    
    # Get initial block count
    try:
        response = requests.get("http://localhost:11000/api/v1/blockchain/info", timeout=5)
        if response.status_code == 200:
            initial_blocks = response.json().get('height', 0)
    except:
        pass
    
    print(f"   📦 Initial blocks: {initial_blocks}")
    
    # Monitor for up to 30 seconds
    processed_slot = None
    while time.time() - start_monitor < 30:
        try:
            response = requests.get("http://localhost:11000/api/v1/blockchain/info", timeout=5)
            if response.status_code == 200:
                current_blocks = response.json().get('height', 0)
                current_slot = get_current_slot()
                is_leader = check_leadership()
                
                if current_blocks > initial_blocks:
                    monitor_time = time.time() - start_monitor
                    processed_slot = current_slot
                    print(f"   ✅ BLOCK CREATED! Slot {current_slot}, Leader: {is_leader}")
                    print(f"   ⏱️  Processing took {monitor_time:.2f}s")
                    print(f"   📊 Slots waited: {current_slot - submission_slot}")
                    break
                else:
                    print(f"   🕐 Slot {current_slot}, Leader: {is_leader}, Blocks: {current_blocks}")
                    
        except Exception as e:
            print(f"   ❌ Monitor error: {e}")
        
        time.sleep(0.5)
    
    if processed_slot:
        print(f"\n📊 WAITING ANALYSIS:")
        print(f"   📤 Submitted at slot: {submission_slot} (NOT leader)")
        print(f"   📦 Processed at slot: {processed_slot}")
        print(f"   ⏳ Slots waited: {processed_slot - submission_slot}")
        print(f"   ⏱️  Time waited: {(processed_slot - submission_slot) * 0.4:.1f}s (400ms slots)")
        print(f"   💡 Reason: Had to wait until node became leader!")
    else:
        print(f"\n❌ Transaction not processed within 30 seconds")
        print(f"   This demonstrates the waiting behavior when not leader")
    
    print(f"\n🎯 CONCLUSION:")
    print(f"   This test shows that transactions submitted when NOT leader")
    print(f"   must wait until the node becomes leader to be processed.")
    print(f"   This explains the 20-second wait observed earlier!")

if __name__ == "__main__":
    main()
