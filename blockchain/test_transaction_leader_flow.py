#!/usr/bin/env python3
"""
Transaction Leader Flow Test
============================

This script tests whether transactions are actually reaching the current leader
through the Fast Gulf Stream and regular Gulf Stream systems.
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime

async def test_transaction_leader_flow():
    """Test if transactions reach the current leader"""
    print("🎯 TESTING TRANSACTION FLOW TO CURRENT LEADER")
    print("=" * 60)
    
    nodes = [
        ("http://localhost:11000", "Node1"),
        ("http://localhost:11001", "Node2"), 
        ("http://localhost:11002", "Node3")
    ]
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Check which nodes are running
        print("📊 Checking node status...")
        running_nodes = []
        for node_url, node_name in nodes:
            try:
                async with session.get(f"{node_url}/api/v1/blockchain/", timeout=3) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print(f"✅ {node_name}: {len(data.get('blocks', []))} blocks")
                        running_nodes.append((node_url, node_name))
                    else:
                        print(f"❌ {node_name}: HTTP {resp.status}")
            except Exception as e:
                print(f"❌ {node_name}: {e}")
        
        if len(running_nodes) < 2:
            print(f"❌ Need at least 2 nodes running, found {len(running_nodes)}")
            return False
        
        # Step 2: Identify current leader
        print(f"\n🏛️ Identifying current leader...")
        current_leader_node = None
        current_leader_info = None
        
        for node_url, node_name in running_nodes:
            try:
                async with session.get(f"{node_url}/api/v1/blockchain/leader/current/") as resp:
                    if resp.status == 200:
                        leader_data = await resp.json()
                        slot = leader_data['current_leader_info']['current_slot']
                        am_leader = leader_data['am_i_current_leader']
                        leader_id = leader_data['current_leader_info'].get('node_id', 'unknown')
                        
                        print(f"📍 {node_name}: Slot {slot}, Am Leader: {am_leader}, Current Leader: {leader_id[:20]}...")
                        
                        if am_leader:
                            current_leader_node = (node_url, node_name)
                            current_leader_info = leader_data
                            print(f"🎯 FOUND CURRENT LEADER: {node_name}")
                        
            except Exception as e:
                print(f"❌ {node_name} leader check failed: {e}")
        
        if not current_leader_node:
            print("❌ No current leader found!")
            return False
        
        leader_url, leader_name = current_leader_node
        
        # Step 3: Check transaction pools BEFORE submitting
        print(f"\n📦 Transaction pools BEFORE submission:")
        leader_pools_before = await get_transaction_pools(session, leader_url, leader_name)
        
        # Step 4: Submit transaction to a NON-leader node
        non_leader_nodes = [node for node in running_nodes if node != current_leader_node]
        if not non_leader_nodes:
            print("❌ No non-leader nodes available for testing forwarding")
            return False
        
        submission_node = non_leader_nodes[0]
        submission_url, submission_name = submission_node
        
        print(f"\n📤 Submitting transaction to {submission_name} (NON-leader)")
        print(f"🎯 Should forward to current leader: {leader_name}")
        
        transaction_data = {
            "transaction": {
                "sender_public_key": "test_leader_flow_sender",
                "receiver_public_key": "test_leader_flow_receiver",
                "amount": 99.9,
                "transaction_type": "TRANSFER",
                "timestamp": time.time(),
                "transaction_id": f"leader_flow_test_{int(time.time())}"
            }
        }
        
        submission_success = False
        try:
            async with session.post(
                f"{submission_url}/api/v1/transaction/create/",
                json=transaction_data,
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status == 200:
                    result = await resp.text()
                    print(f"✅ Transaction submitted successfully to {submission_name}")
                    submission_success = True
                else:
                    error_text = await resp.text()
                    print(f"❌ Transaction submission failed: {resp.status}")
                    print(f"📋 Error: {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Transaction submission error: {e}")
            return False
        
        # Step 5: Wait for forwarding and check leader's transaction pools
        print(f"\n⏳ Waiting 5 seconds for transaction forwarding...")
        await asyncio.sleep(5)
        
        print(f"\n📦 Transaction pools AFTER submission:")
        leader_pools_after = await get_transaction_pools(session, leader_url, leader_name)
        
        # Step 6: Check Fast Gulf Stream metrics
        print(f"\n🌊 Fast Gulf Stream metrics:")
        await check_fast_gulf_stream_metrics(session, running_nodes, leader_name)
        
        # Step 7: Check if leader received the transaction
        print(f"\n🔍 ANALYZING TRANSACTION FLOW TO LEADER:")
        transaction_reached_leader = await analyze_transaction_flow(
            leader_pools_before, leader_pools_after, transaction_data, leader_name
        )
        
        # Step 8: Summary
        print(f"\n" + "=" * 60)
        print(f"🏁 TRANSACTION LEADER FLOW TEST RESULTS")
        print(f"=" * 60)
        print(f"📤 Submission to {submission_name}: {'✅ Success' if submission_success else '❌ Failed'}")
        print(f"🎯 Current Leader: {leader_name}")
        print(f"📦 Transaction reached leader: {'✅ YES' if transaction_reached_leader else '❌ NO'}")
        
        if transaction_reached_leader:
            print(f"🎉 SUCCESS: Fast Gulf Stream forwarding is working!")
            print(f"   💨 Transactions are properly forwarded to current leaders")
        else:
            print(f"💥 PROBLEM: Transaction did not reach the current leader")
            print(f"   🔧 Gulf Stream forwarding may not be working properly")
        
        return transaction_reached_leader

async def get_transaction_pools(session, node_url, node_name):
    """Get transaction pool information for a node"""
    try:
        async with session.get(f"{node_url}/api/v1/blockchain/node-stats/") as resp:
            if resp.status == 200:
                data = await resp.json()
                pools = data.get('mempool', {})
                legacy_pool = data.get('legacy_transaction_pool', {})
                
                print(f"📦 {node_name} Transaction Pools:")
                print(f"   💾 Mempool: {pools.get('mempool_size', 0)} transactions")
                print(f"   📜 Legacy Pool: {legacy_pool.get('size', 0)} transactions")
                
                return {
                    'mempool_size': pools.get('mempool_size', 0),
                    'legacy_pool_size': legacy_pool.get('size', 0),
                    'raw_data': data
                }
    except Exception as e:
        print(f"❌ Failed to get transaction pools for {node_name}: {e}")
    return {'mempool_size': 0, 'legacy_pool_size': 0, 'raw_data': {}}

async def check_fast_gulf_stream_metrics(session, running_nodes, leader_name):
    """Check Fast Gulf Stream forwarding metrics"""
    for node_url, node_name in running_nodes:
        try:
            async with session.get(f"{node_url}/api/v1/blockchain/node-stats/") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    # Look for Fast Gulf Stream data in the enhanced stats
                    if 'get_enhanced_node_stats' in str(data) or 'transaction_pools' in data:
                        print(f"🌊 {node_name} Fast Gulf Stream status:")
                        print(f"   ℹ️  Enhanced stats available: {bool(data)}")
                        
                        # Check if there are any Fast Gulf Stream indicators
                        pools_data = data.get('mempool', {})
                        performance = pools_data.get('performance_stats', {})
                        
                        print(f"   📊 Total received: {performance.get('total_received', 0)}")
                        print(f"   📤 Total announced: {performance.get('total_announced', 0)}")
                        
                        if node_name == leader_name:
                            print(f"   🎯 THIS IS THE CURRENT LEADER - should receive forwarded transactions")
                    else:
                        print(f"🌊 {node_name}: Basic stats only")
        except Exception as e:
            print(f"❌ Failed to get Fast Gulf Stream metrics for {node_name}: {e}")

async def analyze_transaction_flow(pools_before, pools_after, transaction_data, leader_name):
    """Analyze if the transaction reached the leader"""
    print(f"🔍 Transaction Flow Analysis for {leader_name}:")
    
    # Check if any pool sizes increased
    mempool_increase = pools_after['mempool_size'] - pools_before['mempool_size']
    legacy_increase = pools_after['legacy_pool_size'] - pools_before['legacy_pool_size']
    
    print(f"   📈 Mempool change: {pools_before['mempool_size']} → {pools_after['mempool_size']} ({mempool_increase:+d})")
    print(f"   📈 Legacy pool change: {pools_before['legacy_pool_size']} → {pools_after['legacy_pool_size']} ({legacy_increase:+d})")
    
    # Any increase suggests transaction forwarding is working
    if mempool_increase > 0 or legacy_increase > 0:
        print(f"   ✅ Transaction pool increased - forwarding likely working!")
        return True
    else:
        print(f"   ❌ No transaction pool increase - forwarding may not be working")
        
        # Additional debugging info
        print(f"   🔍 Raw transaction data sent:")
        print(f"      - ID: {transaction_data['transaction']['transaction_id']}")
        print(f"      - Amount: {transaction_data['transaction']['amount']}")
        print(f"      - From: {transaction_data['transaction']['sender_public_key']}")
        
        return False

if __name__ == "__main__":
    print("🚀 Starting transaction leader flow test...")
    success = asyncio.run(test_transaction_leader_flow())
    
    if success:
        print(f"\n🎉 TEST PASSED: Transactions are reaching the current leader! 🎉")
    else:
        print(f"\n💥 TEST FAILED: Transactions are NOT reaching the current leader")
        print(f"🔧 Debugging needed for Gulf Stream forwarding")
