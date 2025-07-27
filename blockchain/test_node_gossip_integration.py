#!/usr/bin/env python3
"""
Test Node + Gossip Protocol Integration

This script demonstrates how nodes are started with gossip protocol integration
and shows the port allocation strategy.
"""

import asyncio
import json
import time
from blockchain.node import Node
from blockchain.utils.logger import logger

def test_node_gossip_integration():
    """Test node creation with gossip protocol integration"""
    
    print("🧪 Testing Node + Gossip Protocol Integration")
    print("=" * 60)
    
    # Test 1: Create a node with default configuration
    print("1. Creating node with integrated gossip protocol...")
    node = Node(ip="127.0.0.1", port=10000, key="keys/genesis_private_key.pem")
    
    print(f"   ✅ Node created:")
    print(f"      IP: {node.ip}")
    print(f"      P2P Port: {node.port}")
    print(f"      Gossip Port: {node.gossip_port}")
    print(f"      TPU Port: {node.tpu_port}")
    print(f"      TVU Port: {node.tvu_port}")
    print(f"      Public Key: {node.wallet.public_key_string()[:30]}...")
    
    # Test 2: Check blockchain integration
    print("\n2. Checking blockchain gossip integration...")
    blockchain_status = node.blockchain.get_integration_status()
    
    print(f"   ✅ Blockchain Integration Status:")
    print(f"      Gossip Node Initialized: {blockchain_status['gossip_protocol']['initialized']}")
    print(f"      Auto-Integrated: {blockchain_status['gossip_protocol']['auto_integrated']}")
    print(f"      All Components: {blockchain_status['integration_health']['all_components_initialized']}")
    
    # Test 3: Show port allocation strategy
    print("\n3. Port Allocation Strategy:")
    print("   📊 Standard Node Ports:")
    for i in range(5):
        node_port = 10000 + i
        gossip_port = 12000 + i
        tpu_port = 13000 + i
        tvu_port = 14000 + i
        api_port = 11000 + i
        
        print(f"      Node {i+1}: P2P={node_port}, Gossip={gossip_port}, TPU={tpu_port}, TVU={tvu_port}, API={api_port}")
    
    # Test 4: Get comprehensive node status
    print("\n4. Comprehensive Node Status:")
    try:
        status = node.get_node_status()
        print("   ✅ Node Status Retrieved:")
        print(f"      Node Info: {json.dumps(status['node_info'], indent=8)}")
        print(f"      Gossip Stats: {json.dumps(status['gossip_protocol'], indent=8)}")
        print(f"      Integration Health: {json.dumps(status['blockchain_status']['integration_health'], indent=8)}")
    except Exception as e:
        print(f"   ❌ Error getting node status: {e}")
    
    # Test 5: Demonstrate multiple node port allocation
    print("\n5. Multiple Node Port Allocation Demo:")
    nodes = []
    for i in range(3):
        node_port = 10001 + i
        try:
            test_node = Node(ip="127.0.0.1", port=node_port, key="keys/genesis_private_key.pem")
            nodes.append(test_node)
            print(f"   ✅ Node {i+1}: P2P={test_node.port}, Gossip={test_node.gossip_port}, TPU={test_node.tpu_port}, TVU={test_node.tvu_port}")
        except Exception as e:
            print(f"   ❌ Failed to create node {i+1}: {e}")
    
    # Test 6: Show gossip protocol status
    print("\n6. Gossip Protocol Details:")
    if node.blockchain.gossip_node:
        gossip_stats = node.blockchain.get_gossip_stats()
        print("   ✅ Gossip Protocol Active:")
        print(f"      Active Peers: {gossip_stats.get('active_peers', 0)}")
        print(f"      Known Peers: {gossip_stats.get('known_peers', 0)}")
        print(f"      CRDS Size: {gossip_stats.get('crds_size', 0)}")
        print(f"      Messages Sent: {gossip_stats.get('gossip_stats', {}).get('messages_sent', 0)}")
    else:
        print("   ⚠️  Gossip protocol not yet started (requires async start)")
    
    print("\n" + "=" * 60)
    print("✅ Node + Gossip Integration Test Complete!")
    
    return node

def show_current_integration_status():
    """Show the current integration architecture"""
    
    print("\n🏗️  Current Architecture Overview")
    print("=" * 60)
    
    print("📡 Node Startup Flow:")
    print("   1. run_node.py --ip localhost --node_port 10000 --api_port 11000 --key_file keys/genesis_private_key.pem")
    print("   2. Node.__init__() → creates wallet, loads key")
    print("   3. Blockchain(genesis_public_key=wallet.public_key) → auto-initializes gossip")
    print("   4. start_p2p() → starts P2P + gossip protocol")
    print("   5. start_node_api() → starts REST API server")
    
    print("\n🔌 Port Allocation:")
    print("   📊 Port Ranges:")
    print("      P2P Communication: 10000-10099")
    print("      API Endpoints:     11000-11099") 
    print("      Gossip Protocol:   12000-12999    ← NEW!")
    print("      TPU (Tx Process):  13000-13999    ← NEW!")
    print("      TVU (Tx Validate): 14000-14999    ← NEW!")
    
    print("\n🔗 Integration Points:")
    print("   ✅ Wallet → Blockchain: Public key passed for gossip initialization")
    print("   ✅ Gossip → Leader Schedule: Auto-publishes schedule updates")
    print("   ✅ Node → Gossip: Calculated ports based on P2P port")
    print("   ✅ Status → Gossip: Comprehensive status includes gossip metrics")
    
    print("\n🚀 What's Changed:")
    print("   ✅ Node now passes wallet public key to Blockchain")
    print("   ✅ Gossip protocol auto-initializes with proper ports")
    print("   ✅ Port allocation follows Solana-style separation")
    print("   ✅ Comprehensive status monitoring includes gossip")
    print("   ✅ Leader schedules auto-publish to gossip network")

if __name__ == "__main__":
    try:
        # Show current architecture
        show_current_integration_status()
        
        # Run integration test
        node = test_node_gossip_integration()
        
        print(f"\n💡 To test the full integration:")
        print(f"   1. Start multiple nodes: ./start_nodes.sh 3")
        print(f"   2. Check gossip protocol: curl http://localhost:11000/api/v1/blockchain/")
        print(f"   3. Monitor leader schedules: check node logs for 'Published leader schedule'")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")
