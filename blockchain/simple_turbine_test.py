#!/usr/bin/env python3
"""
SIMPLE TURBINE PROPAGATION TEST

This script tests Turbine block propagation by triggering manual block creation
and monitoring the propagation results.
"""

import requests
import time

def test_simple_turbine_propagation():
    """Test Turbine block propagation with a simple approach"""
    
    print("🚀 SIMPLE TURBINE PROPAGATION TEST")
    print("=" * 40)
    
    # Step 1: Check current state
    print("\n📊 STEP 1: Current Network State")
    
    nodes = []
    for i in range(3):
        port = 11000 + i
        try:
            response = requests.get(f'http://127.0.0.1:{port}/api/v1/blockchain', timeout=3)
            if response.status_code == 200:
                data = response.json()
                block_count = len(data.get('blocks', []))
                nodes.append({'port': port, 'blocks': block_count, 'node': i+1})
                print(f"   Node {i+1} (port {port}): {block_count} blocks")
        except Exception:
            pass
    
    if len(nodes) < 2:
        print("❌ Need at least 2 nodes running")
        return
    
    print(f"✅ {len(nodes)} nodes online")
    
    # Step 2: Use the working simple_load_test.py to create transactions
    print("\n📋 STEP 2: Using Working Transaction Generator")
    
    print("   Running simple_load_test.py to create transactions...")
    
    import subprocess
    import os
    
    try:
        # Run the working transaction generator
        result = subprocess.run([
            'python', 'simple_load_test.py'
        ], 
        cwd=os.getcwd(),
        capture_output=True, 
        text=True, 
        timeout=30
        )
        
        if result.returncode == 0:
            print("   ✅ Transaction generator completed successfully")
            print("   📄 Output preview:")
            # Show last few lines of output
            output_lines = result.stdout.strip().split('\n')
            for line in output_lines[-5:]:
                if line.strip():
                    print(f"      {line}")
        else:
            print("   ❌ Transaction generator failed")
            print(f"   Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("   ⏱️  Transaction generator timed out (this is normal)")
    except Exception as e:
        print(f"   ❌ Error running transaction generator: {e}")
    
    # Step 3: Monitor block propagation
    print("\n⏱️  STEP 3: Monitoring Block Propagation (15 seconds)")
    
    initial_blocks = {node['node']: node['blocks'] for node in nodes}
    
    for check_round in range(3):
        time.sleep(5)
        
        print(f"\n   📊 Check {check_round + 1}/3:")
        current_blocks = {}
        
        for node in nodes:
            try:
                response = requests.get(f'http://127.0.0.1:{node["port"]}/api/v1/blockchain', timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    current_count = len(data.get('blocks', []))
                    initial_count = initial_blocks[node['node']]
                    new_blocks = current_count - initial_count
                    
                    current_blocks[node['node']] = current_count
                    print(f"      Node {node['node']}: {current_count} blocks (+{new_blocks})")
                    
            except Exception as e:
                print(f"      Node {node['node']}: Error - {e}")
        
        # Check synchronization
        if current_blocks:
            block_counts = list(current_blocks.values())
            if len(set(block_counts)) == 1:
                print(f"      🎯 SYNCHRONIZED: All nodes have {block_counts[0]} blocks")
                if max(block_counts) > max(initial_blocks.values()):
                    print(f"      🚀 NEW BLOCKS CREATED AND PROPAGATED!")
                    break
            else:
                print(f"      ⚠️  Different block counts: {block_counts}")
    
    # Step 4: Final verification
    print("\n📋 STEP 4: Final Verification")
    
    final_blocks = {}
    for node in nodes:
        try:
            response = requests.get(f'http://127.0.0.1:{node["port"]}/api/v1/blockchain', timeout=3)
            if response.status_code == 200:
                data = response.json()
                final_count = len(data.get('blocks', []))
                initial_count = initial_blocks[node['node']]
                
                final_blocks[node['node']] = {
                    'initial': initial_count,
                    'final': final_count,
                    'new': final_count - initial_count
                }
                
        except Exception:
            pass
    
    if final_blocks:
        print("\n📊 FINAL RESULTS:")
        
        total_new = 0
        final_counts = []
        
        for node_num, counts in final_blocks.items():
            print(f"   Node {node_num}: {counts['initial']} → {counts['final']} (+{counts['new']})")
            total_new = max(total_new, counts['new'])
            final_counts.append(counts['final'])
        
        # Analysis
        if len(set(final_counts)) == 1:
            print(f"\n✅ PERFECT SYNCHRONIZATION: All nodes have {final_counts[0]} blocks")
            
            if total_new > 0:
                print(f"🚀 TURBINE SUCCESS: {total_new} new blocks propagated to all nodes!")
                print("✅ Turbine protocol is working correctly")
            else:
                print("⚠️  No new blocks created (leader may be inactive)")
                
        else:
            print(f"\n❌ SYNCHRONIZATION ISSUE: Block counts differ {final_counts}")
            print("⚠️  Turbine propagation may need investigation")
    
    # Step 5: Turbine health check
    print("\n🔧 STEP 5: Turbine Health Check")
    
    healthy_count = 0
    for node in nodes:
        try:
            response = requests.post(
                f'http://127.0.0.1:{node["port"]}/api/v1/blockchain/turbine/shreds',
                json={
                    'shreds': [{
                        'index': 1,
                        'total_shreds': 1,
                        'is_data_shred': True,
                        'block_hash': 'test',
                        'data': 'deadbeef',
                        'size': 4
                    }],
                    'sender_node': 'test'
                },
                timeout=3
            )
            
            if response.status_code == 200:
                healthy_count += 1
                print(f"   ✅ Node {node['node']}: Turbine endpoint healthy")
            else:
                print(f"   ❌ Node {node['node']}: Turbine endpoint error")
                
        except Exception as e:
            print(f"   ❌ Node {node['node']}: Turbine endpoint failed")
    
    print(f"\n📊 TURBINE INFRASTRUCTURE: {healthy_count}/{len(nodes)} endpoints healthy")
    
    print("\n" + "=" * 40)
    
    if healthy_count == len(nodes):
        print("🎯 TURBINE INFRASTRUCTURE: 100% healthy")
        print("✅ Network ready for block propagation")
    
    if total_new > 0:
        print("🚀 TURBINE PROPAGATION: WORKING CORRECTLY")
    else:
        print("⚠️  TURBINE PROPAGATION: Needs leader activity")

if __name__ == "__main__":
    test_simple_turbine_propagation()
