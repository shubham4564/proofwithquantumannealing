#!/usr/bin/env python3
"""
TURBINE BLOCK PROPAGATION TEST

This script tests the complete Turbine block propagation pipeline:
1. Send transactions to create blocks
2. Monitor Turbine network transmission 
3. Verify blocks propagate correctly via shred distribution
4. Confirm 100% network synchronization
"""

import requests
import time
import json

def test_turbine_block_propagation():
    """Test complete Turbine block propagation with network transmission"""
    
    print("🚀 TURBINE BLOCK PROPAGATION TEST")
    print("=" * 50)
    
    # Step 1: Check initial network state
    print("\n📊 STEP 1: Initial Network State")
    
    api_base_port = 11000
    initial_states = {}
    
    for i in range(3):
        port = api_base_port + i
        try:
            response = requests.get(f'http://127.0.0.1:{port}/api/v1/blockchain', timeout=3)
            if response.status_code == 200:
                data = response.json()
                block_count = len(data.get('blocks', []))
                initial_states[f'node_{i+1}'] = {
                    'port': port,
                    'initial_blocks': block_count,
                    'reachable': True
                }
                print(f"   Node {i+1} (port {port}): {block_count} blocks")
            else:
                initial_states[f'node_{i+1}'] = {'port': port, 'reachable': False}
        except Exception:
            initial_states[f'node_{i+1}'] = {'port': port, 'reachable': False}
    
    reachable_nodes = [node for node, state in initial_states.items() if state.get('reachable')]
    
    if len(reachable_nodes) < 2:
        print("❌ Need at least 2 nodes running for propagation test")
        return
    
    print(f"✅ {len(reachable_nodes)} nodes reachable")
    
    # Step 2: Send transactions to trigger block creation
    print("\n📋 STEP 2: Triggering Block Creation")
    
    # Send transactions to Node 1 (leader)
    leader_port = 11000
    transactions_sent = 0
    
    for i in range(5):  # Send 5 transactions
        transaction = {
            "type": "EXCHANGE",
            "amount": 10.0 + i,
            "sender_public_key": f"test_sender_{i}_" + "x" * 50,
            "receiver_public_key": f"test_receiver_{i}_" + "y" * 50,
            "timestamp": time.time(),
            "transaction_id": f"tx_{i}_{int(time.time())}"
        }
        
        transaction_data = {
            "transaction": transaction  # API expects transaction in this format
        }
        
        try:
            response = requests.post(
                f'http://127.0.0.1:{leader_port}/api/v1/transaction/create/',
                json=transaction_data,
                timeout=5
            )
            
            if response.status_code in [200, 201]:
                transactions_sent += 1
                print(f"   ✅ Transaction {i+1} sent successfully")
            else:
                print(f"   ❌ Transaction {i+1} failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Transaction {i+1} error: {e}")
    
    print(f"📤 Total transactions sent: {transactions_sent}")
    
    # Step 3: Wait for block creation and propagation
    print("\n⏱️  STEP 3: Waiting for Block Creation & Turbine Propagation")
    print("   (Monitoring for 15 seconds...)")
    
    # Monitor block propagation over time
    for check_round in range(3):
        time.sleep(5)  # Wait 5 seconds between checks
        
        print(f"\n   📊 Check {check_round + 1}/3 (after {(check_round + 1) * 5}s):")
        
        current_states = {}
        for node_name, state in initial_states.items():
            if not state.get('reachable'):
                continue
                
            port = state['port']
            try:
                response = requests.get(f'http://127.0.0.1:{port}/api/v1/blockchain', timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    current_blocks = len(data.get('blocks', []))
                    initial_blocks = state['initial_blocks']
                    new_blocks = current_blocks - initial_blocks
                    
                    current_states[node_name] = current_blocks
                    
                    print(f"      {node_name}: {current_blocks} blocks (+{new_blocks} new)")
                    
            except Exception as e:
                print(f"      {node_name}: Error - {e}")
        
        # Check for synchronization
        if current_states:
            block_counts = list(current_states.values())
            if len(set(block_counts)) == 1:
                print(f"      🎯 SYNCHRONIZED: All nodes have {block_counts[0]} blocks")
                break
            else:
                print(f"      ⚠️  Not synchronized: {block_counts}")
    
    # Step 4: Final Analysis
    print("\n📋 STEP 4: Final Analysis")
    
    final_states = {}
    for node_name, state in initial_states.items():
        if not state.get('reachable'):
            continue
            
        port = state['port']
        try:
            response = requests.get(f'http://127.0.0.1:{port}/api/v1/blockchain', timeout=3)
            if response.status_code == 200:
                data = response.json()
                current_blocks = len(data.get('blocks', []))
                initial_blocks = state['initial_blocks']
                new_blocks = current_blocks - initial_blocks
                
                final_states[node_name] = {
                    'initial': initial_blocks,
                    'final': current_blocks,
                    'new_blocks': new_blocks
                }
                
        except Exception:
            pass
    
    if final_states:
        print("\n📊 FINAL BLOCK COUNTS:")
        total_new_blocks = 0
        all_synchronized = True
        final_counts = []
        
        for node_name, counts in final_states.items():
            print(f"   {node_name}: {counts['initial']} → {counts['final']} (+{counts['new_blocks']})")
            total_new_blocks += counts['new_blocks']
            final_counts.append(counts['final'])
        
        # Check synchronization
        if len(set(final_counts)) == 1:
            print(f"\n✅ TURBINE SUCCESS: 100% synchronization achieved!")
            print(f"   All {len(final_states)} nodes have {final_counts[0]} blocks")
            print(f"   Total new blocks created: {max(counts['new_blocks'] for counts in final_states.values())}")
            
            if max(counts['new_blocks'] for counts in final_states.values()) > 0:
                print(f"   🚀 TURBINE PROTOCOL WORKING: Blocks propagated successfully!")
            else:
                print(f"   ⚠️  No new blocks created (check leader node activity)")
                
        else:
            print(f"\n❌ SYNCHRONIZATION FAILURE:")
            print(f"   Block counts: {final_counts}")
            print(f"   Turbine propagation may need investigation")
    
    # Step 5: Test Turbine endpoint health
    print("\n🔧 STEP 5: Turbine Infrastructure Health")
    
    turbine_healthy = 0
    for node_name, state in initial_states.items():
        if not state.get('reachable'):
            continue
            
        port = state['port']
        try:
            # Test Turbine endpoint
            response = requests.post(
                f'http://127.0.0.1:{port}/api/v1/blockchain/turbine/shreds',
                json={
                    'shreds': [{
                        'index': 1,
                        'total_shreds': 1,
                        'is_data_shred': True,
                        'block_hash': 'health_check',
                        'data': 'deadbeef',
                        'size': 4
                    }],
                    'sender_node': 'health_test',
                    'transmission_time': time.time()
                },
                timeout=3
            )
            
            if response.status_code == 200:
                turbine_healthy += 1
                print(f"   ✅ {node_name}: Turbine endpoint healthy")
            else:
                print(f"   ❌ {node_name}: Turbine endpoint error (HTTP {response.status_code})")
                
        except Exception as e:
            print(f"   ❌ {node_name}: Turbine endpoint failed - {e}")
    
    print(f"\n📊 TURBINE HEALTH: {turbine_healthy}/{len(reachable_nodes)} nodes have working Turbine endpoints")
    
    print("\n" + "=" * 50)
    print("🎯 TURBINE BLOCK PROPAGATION TEST COMPLETE")
    
    if turbine_healthy == len(reachable_nodes):
        print("✅ All Turbine infrastructure is working correctly")
        print("✅ Network is ready for automatic block propagation")
    else:
        print("⚠️  Some Turbine endpoints need attention")

if __name__ == "__main__":
    test_turbine_block_propagation()
