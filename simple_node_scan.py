#!/usr/bin/env python3
"""
Simple Node Availability Test
============================

A simplified version that tests basic node availability without external dependencies.
"""

import socket
import subprocess
import json
from typing import List, Dict

def check_port_availability(host: str, port: int, timeout: int = 3) -> bool:
    """Check if a port is accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def check_process_on_port(port: int) -> bool:
    """Check if a process is running on the given port using lsof"""
    try:
        result = subprocess.run(['lsof', '-i', f':{port}'], 
                              capture_output=True, text=True, timeout=5)
        return len(result.stdout.strip()) > 0
    except Exception:
        return False

def simple_node_scan(base_port: int = 11000, max_nodes: int = 10) -> Dict:
    """Simple scan for available nodes"""
    print(f"🔍 SIMPLE NODE AVAILABILITY SCAN")
    print(f"=" * 40)
    print(f"Checking ports {base_port} to {base_port + max_nodes - 1}...")
    print()
    
    available_nodes = []
    unavailable_nodes = []
    
    for i in range(max_nodes):
        api_port = base_port + i
        p2p_port = 10000 + i
        
        print(f"Checking Node {i+1:2d} (API port {api_port})... ", end="")
        
        # Check if process is running on API port
        process_running = check_process_on_port(api_port)
        
        # Check if API port is accessible
        api_accessible = check_port_availability('localhost', api_port, timeout=2)
        
        # Check P2P port
        p2p_accessible = check_port_availability('localhost', p2p_port, timeout=1)
        
        if process_running and api_accessible:
            print("✅ Available")
            available_nodes.append({
                'node_id': i + 1,
                'api_port': api_port,
                'p2p_port': p2p_port,
                'process_running': process_running,
                'api_accessible': api_accessible,
                'p2p_accessible': p2p_accessible,
                'status': 'available'
            })
        elif process_running:
            print("⚠️  Process running but API not accessible")
            unavailable_nodes.append({
                'node_id': i + 1,
                'api_port': api_port,
                'p2p_port': p2p_port,
                'process_running': process_running,
                'api_accessible': api_accessible,
                'p2p_accessible': p2p_accessible,
                'status': 'degraded'
            })
        else:
            print("❌ Offline")
            unavailable_nodes.append({
                'node_id': i + 1,
                'api_port': api_port,
                'p2p_port': p2p_port,
                'process_running': process_running,
                'api_accessible': api_accessible,
                'p2p_accessible': p2p_accessible,
                'status': 'offline'
            })
    
    print()
    print(f"📊 SCAN RESULTS")
    print(f"─" * 20)
    print(f"✅ Available nodes: {len(available_nodes)}")
    print(f"⚠️  Degraded nodes: {len([n for n in unavailable_nodes if n['status'] == 'degraded'])}")
    print(f"❌ Offline nodes: {len([n for n in unavailable_nodes if n['status'] == 'offline'])}")
    
    if available_nodes:
        print(f"\n🚀 AVAILABLE NODES FOR TRANSACTIONS:")
        for node in available_nodes:
            p2p_status = "✅" if node['p2p_accessible'] else "❌"
            print(f"   Node {node['node_id']:2d}: API port {node['api_port']} | P2P {p2p_status}")
        
        print(f"\n💡 USAGE SUGGESTIONS:")
        best_node = available_nodes[0]
        print(f"   Test with best node:")
        print(f"     python batch_transaction_test.py --node {best_node['api_port']}")
        
        if len(available_nodes) > 1:
            print(f"   Test with multiple nodes:")
            for node in available_nodes[:3]:
                print(f"     python batch_transaction_test.py --node {node['api_port']} --batch-size 50 &")
    
    else:
        print(f"\n❌ NO AVAILABLE NODES FOUND!")
        print(f"💡 To start nodes:")
        print(f"   cd blockchain && ./start_nodes.sh 5")
        print(f"   # Wait 10 seconds, then run this scan again")
    
    return {
        'available_nodes': available_nodes,
        'unavailable_nodes': unavailable_nodes,
        'total_scanned': max_nodes
    }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Node Availability Scanner')
    parser.add_argument('--base-port', type=int, default=11000, help='Base API port (default: 11000)')
    parser.add_argument('--max-nodes', type=int, default=10, help='Number of nodes to check (default: 10)')
    
    args = parser.parse_args()
    
    results = simple_node_scan(args.base_port, args.max_nodes)
    
    # Return appropriate exit code
    available_count = len(results['available_nodes'])
    return 0 if available_count > 0 else 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
