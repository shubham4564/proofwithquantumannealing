#!/usr/bin/env python3
"""
Quick test to verify nodes are alive and leader is working
"""

import requests
import time
import json

# Test the first few nodes
NODES = [f"http://localhost:{port}" for port in range(11000, 11003)]

def test_nodes():
    print("🔍 Testing node connectivity...")
    
    for i, node_url in enumerate(NODES):
        try:
            # Test basic connectivity
            response = requests.get(f"{node_url}/api/v1/blockchain", timeout=2)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Node {i} ({node_url}): {len(data.get('blocks', []))} blocks")
            else:
                print(f"❌ Node {i} ({node_url}): HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Node {i} ({node_url}): {e}")
    
    # Test leader info
    print("\n👑 Testing leader selection...")
    try:
        response = requests.get(f"{NODES[0]}/api/v1/leader/current/", timeout=2)
        if response.status_code == 200:
            leader_info = response.json()
            current_leader_info = leader_info.get('current_leader_info', {})
            current_leader = current_leader_info.get('current_leader', 'Unknown')
            current_slot = current_leader_info.get('current_slot', 'Unknown')
            print(f"✅ Current Leader: {current_leader[:30]}...")
            print(f"✅ Current Slot: {current_slot}")
            print(f"✅ Leader API working!")
        else:
            print(f"❌ Leader info: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Leader info: {e}")

if __name__ == "__main__":
    test_nodes()
