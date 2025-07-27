#!/usr/bin/env python3
"""Simple test to submit transaction to leader"""

import asyncio
import aiohttp
import json

async def test_simple_leader():
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
            print("⏳ Waiting 3 seconds and checking again...")
            await asyncio.sleep(3)
            
            # Try again in case leader changed
            for node_url, node_name in nodes:
                try:
                    async with session.get(f"{node_url}/api/v1/blockchain/leader/current/") as resp:
                        if resp.status == 200:
                            leader_info = await resp.json()
                            if leader_info['am_i_current_leader']:
                                leader_node = (node_url, node_name)
                                print(f"🎯 FOUND LEADER: {node_name}")
                                break
                except:
                    pass
        
        if not leader_node:
            print("❌ Still no current leader found! All nodes are followers.")
            print("🔧 This suggests the leader selection is working but no node thinks it's the leader")
            return
        
        leader_url, leader_name = leader_node
        print(f"\n🎯 Using leader node: {leader_name} at {leader_url}")
        
        # Get initial blockchain state from leader
        async with session.get(f"{leader_url}/api/v1/blockchain/") as resp:
            initial_state = await resp.json()
            initial_blocks = len(initial_state.get('blocks', []))
            print(f"✅ Leader has {initial_blocks} blocks initially")
        
        # Create simple transaction data (we'll use the same format as our working test)
        transaction_data = {
            "sender_public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0yWoAanWzM1pK0K3QBbT\nHgbf4C11TaPjm2A3gYg+peyWoRZZJnqewxCC3NjcxqaaJdCjh5nN03O+FruO/Tme\nLRL8UA3fFRukD5jP/aGn6sCjOhR13LpqGLZg1X68jpIdxfMhsyCgkbjtDgnOiYnL\nIhaGpHID91IEgbxaSV6CTW4oY9gB+lB0cYYIdzJFhZiqsGr8+A2vedRRExOBJtO4\nXTf9t5cL23hBiFKPkh16m7zuiN0nYTEaWs5EtfR0dkM7aHTw7/mjBGHUZD/NlnLD\nkDRHl9OldLXI/vva++C6ig6s6wUhbP7Bk9g0X/Ah/ExDUsTVLEbKPImSGLYjGv9X\nXQIDAQAB\n-----END PUBLIC KEY-----\n",
            "receiver_public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyKlk/zJIaNLM6SJm/6LI\nyNF6hAyZ9IZb5LJl4JGTKJpjg5rGklYzfJ/bKK4aJSEr7H7t/M3fZ2TdF7GjUJZu\nE8VvIUjFj4HMZSw0JZdP6YV4N3U7fV/jK8tPJ9Nj8Y6VkPJU2T5FKjA6U4gP6g6v\nP4N1P3F9tJ0N1t0Z3F3QJ5Z1Y6v4J0TKKjGKLI8C0wXpY9I3Y3Y5L3F9fJ4J4K5Z\n1Z3Z6KJKjG5KjL6K6Z1Z3Z0P6P4P4N1P3F9tJ0N1t0Z3F3QJ5Z1Y6v4J0TKKjGK\nLI8C0wXpY9I3Y3Y5L3F9fJ4J4K5Z1Z3Z6KJKjG5KjL6K6Z1Z3Z0P6P4P4N1P3F9t\nJ0N1t0Z3F3QJ5Z1Y6v4J0TKKjGKLI8C0wXpY9I3Y3Y5L3F9fJ4J4K5Z1Z3Z6KJK\nYwIDAQAB\n-----END PUBLIC KEY-----\n",
            "amount": 30.5,
            "transaction_type": "TRANSFER",
            "timestamp": 1753605400.0,
            "transaction_id": "test123456789abc"
        }
        
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
        print(f"\n⏳ Waiting 10 seconds for the leader to create a block...")
        await asyncio.sleep(10)
        
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
    asyncio.run(test_simple_leader())
