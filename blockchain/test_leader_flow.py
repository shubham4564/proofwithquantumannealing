#!/usr/bin/env python3
"""Test by submitting directly to the current leader node"""

import asyncio
import aiohttp
import json
import time
from utils.blockchain_utils import BlockchainUtils

async def test_leader_transaction_flow():
    """Test transaction submission directly to the current leader"""
    print("🚀 Testing DIRECT LEADER Transaction Flow")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Check nodes to find the current leader
        nodes = [
            ("http://localhost:11000", "Node1 (Genesis)"),
            ("http://localhost:11001", "Node2 (Likely Leader)"),
            ("http://localhost:11002", "Node3")
        ]
        
        leader_node = None
        for node_url, node_name in nodes:
            try:
                async with session.get(f"{node_url}/api/v1/blockchain/leader/current/") as resp:
                    if resp.status == 200:
                        leader_info = await resp.json()
                        print(f"✅ {node_name} connected")
                        print(f"   Current Slot: {leader_info['current_leader_info']['current_slot']}")
                        print(f"   Am I Leader: {leader_info['am_i_current_leader']}")
                        
                        if leader_info['am_i_current_leader']:
                            leader_node = (node_url, node_name)
                            print(f"🎯 FOUND LEADER: {node_name}")
                            break
                    else:
                        print(f"❌ {node_name} not responding: {resp.status}")
            except Exception as e:
                print(f"❌ {node_name} error: {e}")
        
        if not leader_node:
            print("❌ No current leader found among running nodes!")
            return
        
        leader_url, leader_name = leader_node
        print(f"\n🎯 Using leader node: {leader_name} at {leader_url}")
        
        # Get initial blockchain state from leader
        async with session.get(f"{leader_url}/api/v1/blockchain/") as resp:
            initial_state = await resp.json()
            initial_blocks = len(initial_state.get('blocks', []))
            print(f"✅ Leader has {initial_blocks} blocks initially")
        
        # Create and submit transaction
        print(f"\n📝 Creating transaction...")
        
        # Create a proper transaction
        from transaction.transaction import Transaction
        from utils.key_manager import KeyManager
        
        # Load keys
        sender_key = KeyManager.load_private_key("keys/genesis_private_key.pem")
        receiver_key = KeyManager.load_public_key("keys/node2_public_key.pem")
        
        # Create transaction
        transaction = Transaction(
            sender_public_key=KeyManager.extract_public_key(sender_key),
            receiver_public_key=receiver_key,
            amount=25.7,
            transaction_type="TRANSFER"
        )
        
        # Sign transaction
        transaction.sign_transaction(sender_key)
        print(f"✅ Transaction created and signed")
        print(f"📋 TX ID: {transaction.transaction_id[:16]}...")
        print(f"💰 Amount: {transaction.amount}")
        
        # Encode for API
        transaction_data = BlockchainUtils.encode(transaction)
        
        # Submit directly to the leader
        print(f"\n📤 Submitting transaction to LEADER {leader_name}...")
        async with session.post(
            f"{leader_url}/api/v1/transaction/create/",
            json={"transaction": transaction_data},
            headers={"Content-Type": "application/json"}
        ) as resp:
            if resp.status == 200:
                result = await resp.text()
                print(f"✅ Transaction submitted to leader successfully!")
                print(f"📋 Result: {result}")
            else:
                text = await resp.text()
                print(f"❌ Transaction submission failed: {resp.status}")
                print(f"📋 Error: {text}")
                return
        
        # Wait for block creation by the current leader
        print(f"\n⏳ Waiting 15 seconds for the leader to create a block...")
        await asyncio.sleep(15)
        
        # Check final state
        async with session.get(f"{leader_url}/api/v1/blockchain/") as resp:
            final_state = await resp.json()
            final_blocks = len(final_state.get('blocks', []))
            print(f"📊 Final block count: {initial_blocks} → {final_blocks}")
            
            if final_blocks > initial_blocks:
                print(f"🎉 SUCCESS! Leader created {final_blocks - initial_blocks} new block(s)")
                
                # Show the new block
                new_block = final_state['blocks'][-1]
                print(f"📦 New Block #{new_block['index']}")
                print(f"   Proposer: {new_block['proposer'][:20]}...")
                print(f"   Transactions: {len(new_block['transactions'])}")
                
                if new_block['transactions']:
                    print(f"   ✅ Transaction included in block!")
                    for i, tx in enumerate(new_block['transactions']):
                        print(f"      TX {i+1}: {tx['transaction_id'][:16]}... Amount: {tx['amount']}")
                else:
                    print(f"   ⚠️  Block created but no transactions included")
                
                print(f"\n🎉 LEADER TRANSACTION FLOW TEST SUCCESS! 🎉")
                return True
            else:
                print(f"❌ No new blocks created by leader")
                print(f"🔧 Leader received transaction but didn't create blocks")
                
                print(f"\n💥 LEADER TRANSACTION FLOW TEST FAILED")
                return False

if __name__ == "__main__":
    asyncio.run(test_leader_transaction_flow())
