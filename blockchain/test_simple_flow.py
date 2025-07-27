#!/usr/bin/env python3
"""
Simple transaction test to verify our fixed Solana-style flow works
"""

import requests
import time
import json

def test_transaction_flow():
    print("🚀 Testing Fixed Solana-Style Transaction Flow")
    print("=" * 50)
    
    # Test node connectivity
    node_url = "http://localhost:11000"
    try:
        response = requests.get(f"{node_url}/api/v1/blockchain/", timeout=2)
        if response.status_code == 200:
            data = response.json()
            initial_blocks = len(data.get('blocks', []))
            print(f"✅ Node connected: {initial_blocks} blocks initially")
        else:
            print(f"❌ Node connection failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Node connection error: {e}")
        return False
    
    # Check current leader
    try:
        response = requests.get(f"{node_url}/api/v1/blockchain/leader/current/", timeout=2)
        if response.status_code == 200:
            leader_data = response.json()
            leader_info = leader_data.get('current_leader_info', {})
            current_leader = leader_info.get('current_leader', 'Unknown')[:50] + "..."
            current_slot = leader_info.get('current_slot', 'Unknown')
            am_i_leader = leader_data.get('am_i_current_leader', False)
            print(f"👑 Current Leader: {current_leader}")
            print(f"📍 Current Slot: {current_slot}")
            print(f"🎯 Am I Current Leader: {am_i_leader}")
        else:
            print(f"⚠️ Leader info failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"⚠️ Leader info error: {e}")
    
    # Submit transaction
    transaction_data = {
        "type": "transfer",
        "sender_public_key": "test_sender_fixed_flow",
        "receiver_public_key": "test_receiver_fixed_flow", 
        "amount": 25.0,
        "fee": 0.05,
        "timestamp": time.time(),
        "data": {
            "test_type": "fixed_solana_flow",
            "description": "Testing fixes to Solana-style transaction flow"
        }
    }
    
    print(f"\n📤 Submitting transaction...")
    try:
        response = requests.post(
            f"{node_url}/api/v1/transaction/submit/",
            json=transaction_data,
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Transaction submitted successfully!")
            print(f"📋 Result: {result.get('message', 'No message')}")
        else:
            error_text = response.text
            print(f"❌ Transaction submission failed: HTTP {response.status_code}")
            print(f"🔍 Error: {error_text}")
            return False
    except Exception as e:
        print(f"❌ Transaction submission error: {e}")
        return False
    
    # Wait for block creation
    print(f"\n⏳ Waiting 10 seconds for block creation by current leader...")
    time.sleep(10)
    
    # Check for new blocks
    try:
        response = requests.get(f"{node_url}/api/v1/blockchain/", timeout=2)
        if response.status_code == 200:
            data = response.json()
            final_blocks = len(data.get('blocks', []))
            print(f"📊 Final block count: {initial_blocks} → {final_blocks}")
            
            if final_blocks > initial_blocks:
                print(f"🎉 NEW BLOCKS CREATED! (+{final_blocks - initial_blocks})")
                
                # Check if our transaction is in a block
                blocks = data.get('blocks', [])
                transaction_found = False
                
                for i, block in enumerate(blocks[-3:], start=max(0, len(blocks)-3)):
                    transactions = block.get('transactions', [])
                    print(f"🔍 Block {i}: {len(transactions)} transactions")
                    
                    for tx in transactions:
                        if (tx.get('sender_public_key') == 'test_sender_fixed_flow' and 
                            tx.get('receiver_public_key') == 'test_receiver_fixed_flow'):
                            transaction_found = True
                            print(f"🎯 TRANSACTION FOUND in block {i}!")
                            print(f"📝 TX Details: {tx.get('type')} - {tx.get('amount')}")
                            break
                    
                    if transaction_found:
                        break
                
                if transaction_found:
                    print(f"\n✅ SUCCESS! SOLANA-STYLE FLOW WORKING!")
                    print(f"✅ Leader Selection → Gulf Stream → PoH → Block Creation ✅")
                    return True
                else:
                    print(f"\n⚠️ Blocks created but transaction not found")
                    print(f"🔧 Check if Gulf Stream → PoH integration is working")
                    return False
            else:
                print(f"❌ No new blocks created")
                print(f"🔧 Current leader may not be creating blocks with transactions")
                return False
                
        else:
            print(f"❌ Final blockchain check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Final check error: {e}")
        return False

if __name__ == "__main__":
    success = test_transaction_flow()
    
    if success:
        print(f"\n🎊 TRANSACTION FLOW TEST PASSED!")
        print(f"🔧 All our fixes are working correctly!")
    else:
        print(f"\n💥 TRANSACTION FLOW TEST FAILED")
        print(f"🔧 Need to check the integration further")
