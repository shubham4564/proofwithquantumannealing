#!/usr/bin/env python3
"""
Quick test script to check if the quantum metrics are working correctly
"""

import requests
import json
import sys

def test_quantum_metrics(api_url):
    """Test quantum metrics endpoint and show detailed output"""
    try:
        print(f"Testing quantum metrics at: {api_url}")
        
        response = requests.get(f"{api_url}/quantum-metrics/")
        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            return False
            
        data = response.json()
        
        print("✅ Successfully retrieved quantum metrics")
        print("\n📊 Quantum Metrics Analysis:")
        print("-" * 40)
        
        # Basic info
        print(f"Consensus Type: {data.get('consensus_type', 'Unknown')}")
        print(f"Total Nodes: {data.get('total_nodes', 0)}")
        print(f"Active Nodes: {data.get('active_nodes', 0)}")
        
        # Protocol parameters
        if 'protocol_parameters' in data:
            params = data['protocol_parameters']
            print("\n🔧 Protocol Parameters:")
            for key, value in params.items():
                print(f"  {key}: {value}")
                
            # Check for slot duration specifically
            slot_duration = params.get('slot_duration_ms')
            if slot_duration == 450:
                print("✅ Slot duration correctly set to 450ms")
            elif slot_duration:
                print(f"⚠️ Slot duration is {slot_duration}ms (expected 450ms)")
            else:
                print("❌ Slot duration not found in protocol parameters")
        
        # Scoring weights
        if 'scoring_weights' in data:
            weights = data['scoring_weights']
            print("\n⚖️ Scoring Weights:")
            for key, value in weights.items():
                print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing quantum metrics: {e}")
        return False

def test_performance_metrics(api_url):
    """Test performance metrics endpoint"""
    try:
        print(f"\n🎯 Testing performance metrics at: {api_url}")
        
        response = requests.get(f"{api_url}/performance-metrics/")
        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            return False
            
        data = response.json()
        
        enhanced = data.get("enhanced_metrics_available", False)
        print(f"Enhanced metrics available: {enhanced}")
        
        if enhanced and "metrics" in data:
            metrics = data["metrics"]
            if "timestamp" in metrics:
                print(f"✅ Real-time metrics with timestamp: {metrics['timestamp']}")
            else:
                print("⚠️ Enhanced metrics enabled but no timestamp found")
        else:
            print("📊 Basic metrics mode")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing performance metrics: {e}")
        return False

if __name__ == "__main__":
    # Test multiple nodes to see which ones have the updated code
    test_ports = [11000, 11001, 11002, 11003]
    
    print("🧪 Testing Updated Quantum Metrics on Multiple Nodes")
    print("=" * 60)
    
    success_count = 0
    for port in test_ports:
        api_url = f"http://127.0.0.1:{port}/api/v1/blockchain"
        print(f"\n🔍 Testing Node on Port {port}")
        print("-" * 30)
        
        if test_quantum_metrics(api_url):
            success_count += 1
            test_performance_metrics(api_url)
        else:
            print(f"Node on port {port} not responding")
    
    print(f"\n📊 Summary: {success_count}/{len(test_ports)} nodes tested successfully")
