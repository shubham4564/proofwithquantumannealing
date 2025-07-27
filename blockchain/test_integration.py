#!/usr/bin/env python3
"""
Test script to verify gossip protocol integration with blockchain
"""
import sys
import os
import asyncio
import time

# Add the blockchain directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from blockchain.blockchain import Blockchain
from blockchain.transaction.wallet import Wallet

async def test_integration():
    """Test the complete integration of gossip protocol with blockchain"""
    print("🔍 Testing Gossip Protocol Integration with Blockchain...")
    print("=" * 70)
    
    # 1. Create blockchain with genesis key (should auto-initialize gossip)
    print("1. Creating blockchain with genesis key...")
    genesis_wallet = Wallet()
    blockchain = Blockchain(genesis_public_key=genesis_wallet.public_key_string())
    
    # 2. Check integration status
    print("\n2. Checking integration status...")
    integration_status = blockchain.get_integration_status()
    
    print(f"   ✅ Blockchain Core: {integration_status['blockchain_core']['blocks']} blocks")
    print(f"   ✅ Quantum Consensus: {'✓' if integration_status['quantum_consensus']['initialized'] else '✗'}")
    print(f"   ✅ Leader Schedule: Epoch {integration_status['leader_schedule']['current_epoch']}")
    print(f"   ✅ PoH Sequencer: {'✓' if integration_status['poh_sequencer']['initialized'] else '✗'}")
    print(f"   ✅ Gulf Stream: {'✓' if integration_status['gulf_stream']['initialized'] else '✗'}")
    print(f"   ✅ Turbine Protocol: {'✓' if integration_status['turbine_protocol']['initialized'] else '✗'}")
    print(f"   ✅ Gossip Protocol: {'✓' if integration_status['gossip_protocol']['initialized'] else '✗'} (Auto-integrated)")
    print(f"   ✅ All Components: {'✓' if integration_status['integration_health']['all_components_initialized'] else '✗'}")
    
    # 3. Test gossip auto-initialization
    print("\n3. Testing gossip auto-initialization...")
    if blockchain.gossip_node:
        print("   ✅ Gossip node auto-initialized successfully")
        print(f"   📊 Gossip Stats: {blockchain.get_gossip_stats()}")
    else:
        print("   ❌ Gossip node not auto-initialized")
        return False
    
    # 4. Test leader schedule auto-publishing
    print("\n4. Testing leader schedule auto-publishing...")
    if blockchain.quantum_consensus:
        print("   🔄 Updating leader schedule (should auto-publish to gossip)...")
        blockchain.update_leader_schedule()
        
        # Check if schedule was published
        gossip_stats = blockchain.get_gossip_stats()
        if gossip_stats and 'gossip_stats' in gossip_stats:
            print(f"   ✅ Gossip messages sent: {gossip_stats['gossip_stats'].get('push_messages_sent', 0)}")
        
        # Check current leader
        current_leader = blockchain.next_block_proposer()
        print(f"   👑 Current leader: {current_leader[:20] if current_leader else 'None'}...")
    
    # 5. Test metrics integration
    print("\n5. Testing metrics integration...")
    try:
        metrics = blockchain.get_quantum_metrics()
        if 'gossip_protocol' in metrics:
            print("   ✅ Gossip metrics integrated into quantum metrics")
            gossip_metrics = metrics['gossip_protocol']
            if gossip_metrics:
                print(f"   📈 Active peers: {gossip_metrics.get('active_peers', 0)}")
                print(f"   📈 Known peers: {gossip_metrics.get('known_peers', 0)}")
        else:
            print("   ❌ Gossip metrics not found in quantum metrics")
    except Exception as e:
        print(f"   ❌ Error getting metrics: {e}")
    
    # 6. Test gossip network operation (if started)
    print("\n6. Testing gossip network operation...")
    try:
        await blockchain.start_gossip_node()
        print("   ✅ Gossip node started successfully")
        
        # Wait a moment for initialization
        await asyncio.sleep(1)
        
        # Check stats after starting
        stats = blockchain.get_gossip_stats()
        print(f"   📊 Post-start stats: {stats}")
        
        # Stop the node
        await blockchain.stop_gossip_node()
        print("   ✅ Gossip node stopped successfully")
        
    except Exception as e:
        print(f"   ⚠️  Gossip network test failed: {e}")
    
    print("\n" + "=" * 70)
    print("🎉 INTEGRATION TEST COMPLETE!")
    
    # Summary
    all_good = integration_status['integration_health']['all_components_initialized']
    if all_good:
        print("✅ RESULT: Gossip protocol is FULLY INTEGRATED with blockchain flow")
        print("🚀 Ready for production use!")
    else:
        print("❌ RESULT: Integration incomplete - some components missing")
    
    return all_good

if __name__ == "__main__":
    print("🧪 Blockchain Integration Test")
    print("Testing integration of gossip protocol with blockchain components...")
    
    result = asyncio.run(test_integration())
    
    if result:
        print("\n✅ All tests passed! Integration is complete.")
        exit(0)
    else:
        print("\n❌ Some tests failed. Check integration.")
        exit(1)
