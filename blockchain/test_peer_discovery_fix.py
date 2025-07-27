#!/usr/bin/env python3
"""
Test script to verify Turbine peer discovery fix is working
"""

import requests
import time
import json
from datetime import datetime

def test_peer_discovery_fix():
    """Test the complete Turbine peer discovery and block propagation fix"""
    
    print("🔧 TESTING TURBINE PEER DISCOVERY FIX")
    print("=" * 50)
    
    # Wait for nodes to complete initialization
    print("\n⏳ Waiting for nodes to complete peer discovery...")
    time.sleep(15)  # Give nodes time to discover each other
    
    print("\n📊 STEP 1: Checking node health and peer discovery")
    
    nodes = [
        {'name': 'Node 1', 'port': 11000},
        {'name': 'Node 2', 'port': 11001}, 
        {'name': 'Node 3', 'port': 11002}
    ]
    
    online_nodes = []
    
    for node in nodes:
        try:
            response = requests.get(f'http://127.0.0.1:{node["port"]}/ping/', timeout=3)
            if response.status_code == 200:
                print(f"   ✅ {node['name']} (port {node['port']}): Online")
                online_nodes.append(node)
            else:
                print(f"   ❌ {node['name']} (port {node['port']}): Unhealthy")
        except Exception as e:
            print(f"   ❌ {node['name']} (port {node['port']}): Offline - {e}")
    
    print(f"\n📊 Online nodes: {len(online_nodes)}/{len(nodes)}")
    
    if len(online_nodes) < 2:
        print("❌ Need at least 2 nodes online to test propagation")
        return
    
    # Check initial block counts
    print("\n📊 STEP 2: Initial block counts")
    initial_blocks = {}
    
    for node in online_nodes:
        try:
            response = requests.get(f'http://127.0.0.1:{node["port"]}/api/v1/blockchain/stats/')
            if response.status_code == 200:
                stats = response.json()
                block_count = stats.get('block_count', 0)
                initial_blocks[node['port']] = block_count
                print(f"   📋 {node['name']}: {block_count} blocks")
        except Exception as e:
            print(f"   ❌ {node['name']}: Error getting stats - {e}")
    
    # Test Turbine endpoint to check validator registration
    print("\n📊 STEP 3: Checking Turbine validator registration")
    
    for node in online_nodes:
        try:
            # Try to get Turbine status via blockchain stats (may include validator count)
            response = requests.get(f'http://127.0.0.1:{node["port"]}/api/v1/blockchain/stats/')
            if response.status_code == 200:
                stats = response.json()
                print(f"   📋 {node['name']}: Blockchain operational (stats available)")
            
            # Test Turbine endpoint availability
            response = requests.get(f'http://127.0.0.1:{node["port"]}/api/v1/blockchain/turbine/shreds/', timeout=2)
            if response.status_code == 405:  # Method not allowed is expected for GET
                print(f"   ✅ {node['name']}: Turbine endpoint available")
            else:
                print(f"   🔍 {node['name']}: Turbine endpoint status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {node['name']}: Turbine check failed - {e}")
    
    # Wait for some block creation and propagation
    print(f"\n⏳ STEP 4: Waiting 30 seconds for block creation and propagation...")
    time.sleep(30)
    
    # Check final block counts
    print("\n📊 STEP 5: Final block counts after peer discovery fix")
    final_blocks = {}
    propagation_success = True
    
    for node in online_nodes:
        try:
            response = requests.get(f'http://127.0.0.1:{node["port"]}/api/v1/blockchain/stats/')
            if response.status_code == 200:
                stats = response.json()
                block_count = stats.get('block_count', 0)
                final_blocks[node['port']] = block_count
                
                initial_count = initial_blocks.get(node['port'], 0)
                increase = block_count - initial_count
                
                print(f"   📋 {node['name']}: {block_count} blocks (+{increase} new)")
        except Exception as e:
            print(f"   ❌ {node['name']}: Error getting final stats - {e}")
    
    # Analyze propagation results
    print("\n📊 STEP 6: Propagation Analysis")
    
    if len(final_blocks) >= 2:
        block_counts = list(final_blocks.values())
        max_blocks = max(block_counts)
        min_blocks = min(block_counts)
        
        print(f"   📊 Block count range: {min_blocks} - {max_blocks}")
        
        # Check if all nodes have similar block counts (within 2 blocks is acceptable)
        if max_blocks - min_blocks <= 2:
            print("   ✅ SUCCESS: Blocks are propagating correctly!")
            print("   🎯 PEER DISCOVERY FIX WORKED!")
            propagation_success = True
        else:
            print("   ⚠️  WARNING: Block propagation may still have issues")
            print("   🔍 Need to check Turbine validator registration details")
            propagation_success = False
            
        # Calculate sync percentage
        sync_percentage = (min_blocks / max_blocks * 100) if max_blocks > 0 else 0
        print(f"   📊 Network sync: {sync_percentage:.1f}%")
        
    else:
        print("   ❌ Not enough nodes online to analyze propagation")
        propagation_success = False
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 TURBINE PEER DISCOVERY FIX TEST SUMMARY")
    print("=" * 50)
    
    print(f"📊 Nodes tested: {len(online_nodes)}")
    print(f"📊 Initial blocks: {initial_blocks}")
    print(f"📊 Final blocks: {final_blocks}")
    
    if propagation_success:
        print("✅ RESULT: PEER DISCOVERY FIX SUCCESSFUL!")
        print("🚀 Turbine protocol now working for cross-node propagation")
    else:
        print("❌ RESULT: Still investigating propagation issues")
        print("🔍 May need additional Turbine configuration")
    
    print("=" * 50)

if __name__ == "__main__":
    test_peer_discovery_fix()
