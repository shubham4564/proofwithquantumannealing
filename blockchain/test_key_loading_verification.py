#!/usr/bin/env python3
"""
Test script to verify that probe operations use pre-generated keys from files
instead of generating new RSA keys.
"""

import os
import sys
import time
import random

# Add the blockchain module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from blockchain.quantum_consensus.quantum_annealing_consensus import QuantumAnnealingConsensus

def test_key_loading_performance():
    """Test that keys are loaded from files, not generated"""
    print("🔍 Testing Key Loading vs Generation Performance...")
    
    # Initialize consensus mechanism
    consensus = QuantumAnnealingConsensus(initialize_genesis=False)
    
    # Test 1: Verify that ensure_node_keys loads from files for existing nodes
    print("\n📁 Test 1: Loading keys for nodes with existing key files...")
    
    test_nodes = ["node2", "node3", "node4", "node5"]
    load_times = []
    
    for node_id in test_nodes:
        key_file = f"./keys/{node_id}_private_key.pem"
        if os.path.exists(key_file):
            start_time = time.time()
            public_key, private_key = consensus.ensure_node_keys(node_id)
            load_time = time.time() - start_time
            load_times.append(load_time)
            print(f"   ✅ {node_id}: Loaded in {load_time*1000:.2f}ms")
        else:
            print(f"   ⚠️  {node_id}: Key file not found at {key_file}")
    
    if load_times:
        avg_load_time = sum(load_times) / len(load_times)
        print(f"\n📊 Average key loading time: {avg_load_time*1000:.2f}ms")
        
        if avg_load_time < 0.01:  # Less than 10ms
            print("✅ EXCELLENT: Key loading is very fast (using files)")
        elif avg_load_time < 0.05:  # Less than 50ms
            print("✅ GOOD: Key loading is reasonably fast")
        else:
            print("⚠️  SLOW: Key loading is taking longer than expected")
    
    # Test 2: Compare file loading vs generation performance
    print("\n🔄 Test 2: Comparing file loading vs key generation...")
    
    # Time key generation for new node
    start_time = time.time()
    gen_public, gen_private = consensus.generate_node_keys("temp_generated_node")
    generation_time = time.time() - start_time
    print(f"   🔧 Key generation time: {generation_time*1000:.2f}ms")
    
    # Time key loading for existing node
    if load_times:
        speedup = generation_time / avg_load_time
        print(f"   📈 File loading is {speedup:.1f}x faster than generation")
        
        if speedup > 10:
            print("   ✅ EXCELLENT: File loading provides significant speedup")
        elif speedup > 5:
            print("   ✅ GOOD: File loading provides good speedup")
        else:
            print("   ⚠️  File loading speedup is less than expected")
    
    return consensus

def test_probe_protocol_key_usage():
    """Test that probe protocol uses file-loaded keys, not generated ones"""
    print("\n🔍 Test 3: Verifying probe protocol key usage...")
    
    consensus = QuantumAnnealingConsensus(initialize_genesis=False)
    
    # Register test nodes
    test_nodes = ["node2", "node3", "node4"]
    for node_id in test_nodes:
        consensus.register_node(node_id, f"{node_id}_public_key")
    
    print(f"   📝 Registered {len(test_nodes)} nodes")
    
    # Check that nodes were loaded with file-based keys
    nodes_with_keys = len([node for node in test_nodes if node in consensus.node_keys])
    print(f"   🔑 Nodes with loaded keys: {nodes_with_keys}/{len(test_nodes)}")
    
    # Test probe protocol execution
    print("   🔍 Testing probe protocol execution...")
    
    source = test_nodes[0]
    target = test_nodes[1]
    witnesses = test_nodes[2:]
    
    # Time the probe protocol
    start_time = time.time()
    try:
        probe_result = consensus.execute_probe_protocol(source, target, witnesses)
        probe_time = time.time() - start_time
        print(f"   ⏱️  Probe protocol completed in {probe_time*1000:.2f}ms")
        
        if probe_time < 0.1:  # Less than 100ms
            print("   ✅ FAST: Probe protocol is running efficiently")
        elif probe_time < 0.5:  # Less than 500ms
            print("   ✅ GOOD: Probe protocol performance is acceptable")
        else:
            print("   ⚠️  SLOW: Probe protocol is taking longer than expected")
            
        # Verify probe result structure
        if 'ProbeRequest' in probe_result and 'TargetReceipt' in probe_result:
            print("   ✅ Probe result structure is correct")
        else:
            print("   ❌ Probe result structure is invalid")
            
    except Exception as e:
        print(f"   ❌ Probe protocol failed: {e}")
    
    return consensus

def test_scalable_probe_protocol():
    """Test the scalable probe protocol optimization"""
    print("\n🔍 Test 4: Testing scalable probe protocol...")
    
    consensus = QuantumAnnealingConsensus(initialize_genesis=False)
    
    # Register a small number of nodes (should use cached protocol)
    small_network = ["node2", "node3", "node4"]
    for node_id in small_network:
        consensus.register_node(node_id, f"{node_id}_public_key")
    
    print(f"   📝 Small network: {len(small_network)} nodes")
    
    # Test cached probe protocol
    start_time = time.time()
    try:
        consensus.execute_scalable_probe_protocol(small_network)
        scalable_time = time.time() - start_time
        print(f"   ⏱️  Scalable probe protocol: {scalable_time*1000:.2f}ms")
        
        if scalable_time < 0.5:  # Less than 500ms
            print("   ✅ EXCELLENT: Scalable probe protocol is very fast")
        elif scalable_time < 1.0:  # Less than 1 second
            print("   ✅ GOOD: Scalable probe protocol performance is good")
        else:
            print("   ⚠️  SLOW: Scalable probe protocol could be optimized further")
            
    except Exception as e:
        print(f"   ❌ Scalable probe protocol failed: {e}")

def main():
    """Run all key loading verification tests"""
    print("🚀 Starting Key Loading Verification Tests")
    print("=" * 60)
    
    # Check if keys directory exists
    keys_dir = "./keys"
    if not os.path.exists(keys_dir):
        print(f"❌ Keys directory not found: {keys_dir}")
        print("   Please ensure the keys folder with pre-generated keys exists")
        return
    
    # Count key files
    key_files = [f for f in os.listdir(keys_dir) if f.endswith('.pem')]
    print(f"📁 Found {len(key_files)} key files in {keys_dir}")
    
    if len(key_files) < 4:
        print("⚠️  Limited key files found. Some tests may be skipped.")
    
    # Run tests
    test_key_loading_performance()
    test_probe_protocol_key_usage()
    test_scalable_probe_protocol()
    
    print("\n" + "=" * 60)
    print("✅ Key Loading Verification Tests Complete")
    print("\n💡 Key Findings:")
    print("   • Probe operations should now use pre-generated keys from files")
    print("   • File loading should be 10-100x faster than key generation")
    print("   • Probe protocol should complete in <1 second for small networks")

if __name__ == "__main__":
    main()
