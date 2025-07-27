#!/usr/bin/env python3
"""
Simple API Test Script for Leader Selection Monitoring

This script demonstrates the exact API calls you can use to monitor
current and upcoming leaders in your blockchain network.
"""

import requests
import json
import sys

def test_leader_apis(node_port=11001):
    """Test all the leader-related API endpoints"""
    
    base_url = f"http://localhost:{node_port}/api/v1/blockchain"
    
    print(f"🔍 TESTING LEADER APIs on Node {node_port}")
    print("=" * 60)
    
    # Test 1: Current Leader Information
    print("\n1️⃣ CURRENT LEADER API:")
    print(f"   GET {base_url}/leader/current/")
    try:
        response = requests.get(f"{base_url}/leader/current/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            leader_info = data.get('current_leader_info', {})
            consensus = data.get('consensus_context', {})
            
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Current Leader: {leader_info.get('current_leader', 'None')}")
            print(f"   🕐 Current Slot: {leader_info.get('current_slot', 'Unknown')}")
            print(f"   ⏱️  Time Remaining: {leader_info.get('time_remaining_in_slot', 0):.1f}s")
            print(f"   👑 Am I Leader: {data.get('am_i_current_leader', False)}")
            print(f"   🌐 Total Nodes: {consensus.get('total_nodes', 0)}")
            print(f"   🔗 Gossip Peers: {consensus.get('gossip_peers', 0)}")
        else:
            print(f"   ❌ Error: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    # Test 2: Upcoming Leaders
    print(f"\n2️⃣ UPCOMING LEADERS API:")
    print(f"   GET {base_url}/leader/upcoming/")
    try:
        response = requests.get(f"{base_url}/leader/upcoming/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            upcoming = data.get('upcoming_leaders', [])
            
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📅 Upcoming Count: {len(upcoming)}")
            print(f"   🎯 Am I Upcoming: {data.get('my_upcoming_leadership') is not None}")
            print(f"   📊 Current Epoch: {data.get('leader_schedule_epoch', 'Unknown')}")
            print(f"   ⏱️  Slot Duration: {data.get('slot_duration_seconds', 'Unknown')}s")
            
            if upcoming:
                print(f"   📋 Next Leaders:")
                for i, leader in enumerate(upcoming[:3]):
                    slot = leader.get('slot', '?')
                    time_until = leader.get('time_until_slot', 0)
                    leader_key = leader.get('leader', 'Unknown')[:20] + "..."
                    print(f"      {i+1}. Slot {slot}: {leader_key} ({time_until:.1f}s)")
            else:
                print(f"   📋 No upcoming leaders scheduled")
        else:
            print(f"   ❌ Error: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    # Test 3: Quantum Leader Selection
    print(f"\n3️⃣ QUANTUM SELECTION API:")
    print(f"   GET {base_url}/leader/quantum-selection/")
    try:
        response = requests.get(f"{base_url}/leader/quantum-selection/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            node_scores = data.get('node_scores', {})
            
            print(f"   ✅ Status: {response.status_code}")
            print(f"   🔮 Quantum Enabled: {data.get('quantum_consensus_enabled', False)}")
            print(f"   🎯 Next Proposer: {data.get('next_quantum_proposer', 'None')[:30]}...")
            print(f"   📊 Total Nodes: {data.get('total_registered_nodes', 0)}")
            print(f"   ✅ Active Nodes: {data.get('active_nodes', 0)}")
            print(f"   📝 Node Scores:")
            
            for i, (node_key, scores) in enumerate(node_scores.items()):
                effective_score = scores.get('effective_score', 0)
                success_rate = scores.get('proposals_success', 0)
                uptime = scores.get('uptime', 0)
                print(f"      Node {i+1}: Score {effective_score:.6f}, Success: {success_rate}, Uptime: {uptime}")
        else:
            print(f"   ❌ Error: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    # Test 4: Full Leader Schedule
    print(f"\n4️⃣ LEADER SCHEDULE API:")
    print(f"   GET {base_url}/leader/schedule/")
    try:
        response = requests.get(f"{base_url}/leader/schedule/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            current_schedule = data.get('current_schedule', {})
            next_schedule = data.get('next_schedule', {})
            
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Current Epoch: {data.get('current_epoch', 'Unknown')}")
            print(f"   🕐 Current Slot: {data.get('current_slot', 'Unknown')}")
            print(f"   📅 Current Schedule Size: {len(current_schedule)}")
            print(f"   📅 Next Schedule Size: {len(next_schedule)}")
            print(f"   ⏱️  Slot Duration: {data.get('slot_duration_seconds', 'Unknown')}s")
            
            if current_schedule:
                print(f"   📋 Current Schedule Sample:")
                sorted_slots = sorted([int(slot) for slot in current_schedule.keys()])
                for slot in sorted_slots[:3]:
                    leader = current_schedule[str(slot)]
                    print(f"      Slot {slot}: {leader[:30]}...")
            else:
                print(f"   📋 No current schedule available")
        else:
            print(f"   ❌ Error: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")

def test_multiple_nodes(start_port=11000, num_nodes=3):
    """Test leader APIs across multiple nodes"""
    print(f"\n🌐 TESTING ACROSS {num_nodes} NODES")
    print("=" * 60)
    
    for i in range(num_nodes):
        port = start_port + i
        print(f"\n📡 Node {i+1} (Port {port}):")
        
        # Quick test of current leader
        try:
            response = requests.get(f"http://localhost:{port}/api/v1/blockchain/leader/current/", timeout=3)
            if response.status_code == 200:
                data = response.json()
                leader_info = data.get('current_leader_info', {})
                leader = leader_info.get('current_leader', 'None')
                slot = leader_info.get('current_slot', '?')
                am_leader = data.get('am_i_current_leader', False)
                consensus = data.get('consensus_context', {})
                
                print(f"   ✅ Online | Leader: {leader[:20] + '...' if leader != 'None' else 'None'}")
                print(f"   🕐 Slot: {slot} | Am I Leader: {am_leader}")
                print(f"   🌐 Total Nodes: {consensus.get('total_nodes', 0)} | Gossip: {consensus.get('gossip_peers', 0)}")
            else:
                print(f"   ❌ Offline | HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Offline | {str(e)[:50]}...")

def main():
    """Main function with usage examples"""
    if len(sys.argv) > 1:
        try:
            node_port = int(sys.argv[1])
        except ValueError:
            print("Usage: python api_test.py [node_port] [num_nodes]")
            sys.exit(1)
    else:
        node_port = 11001
    
    if len(sys.argv) > 2:
        try:
            num_nodes = int(sys.argv[2])
            test_multiple_nodes(node_port - 1, num_nodes)  # Adjust for 0-based indexing
            return
        except ValueError:
            pass
    
    # Test single node
    test_leader_apis(node_port)
    
    print(f"\n\n💡 USAGE EXAMPLES:")
    print(f"   Single Node:  python api_test.py 11001")
    print(f"   Multi Nodes:  python api_test.py 11001 3")
    print(f"   \n📋 Available Endpoints:")
    print(f"   • /api/v1/blockchain/leader/current/")
    print(f"   • /api/v1/blockchain/leader/upcoming/")
    print(f"   • /api/v1/blockchain/leader/quantum-selection/")
    print(f"   • /api/v1/blockchain/leader/schedule/")
    print(f"   • /api/v1/blockchain/quantum-metrics/")

if __name__ == "__main__":
    main()
