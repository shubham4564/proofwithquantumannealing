#!/usr/bin/env python3
"""
Enhanced Node Availability Checker
==================================

This version works directly with the blockchain framework and provides
comprehensive node availability checking for transaction processing.
"""

import requests
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import socket


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


def get_node_health(api_port: int) -> Dict:
    """Get comprehensive health information for a node"""
    node_info = {
        'node_id': api_port - 11000 + 1,
        'api_port': api_port,
        'p2p_port': 10000 + (api_port - 11000),
        'tpu_port': 13000 + (api_port - 11000),
        'process_running': False,
        'api_responding': False,
        'api_response_time': float('inf'),
        'blockchain_accessible': False,
        'transaction_endpoint_working': False,
        'leader_schedule_available': False,
        'quantum_metrics_available': False,
        'node_status_available': False,
        'blocks_count': 0,
        'quantum_healthy': False,
        'availability_score': 0,
        'status': 'offline',
        'transaction_ready': False
    }
    
    # Check if process is running
    node_info['process_running'] = check_process_on_port(api_port)
    
    if not node_info['process_running']:
        return node_info
    
    try:
        # Test API responsiveness
        start_time = time.time()
        response = requests.get(f'http://localhost:{api_port}/api/v1/blockchain/', timeout=3)
        node_info['api_response_time'] = time.time() - start_time
        
        if response.status_code == 200:
            node_info['api_responding'] = True
            node_info['blockchain_accessible'] = True
            
            data = response.json()
            blocks = data.get('blocks', [])
            node_info['blocks_count'] = len(blocks)
    
    except Exception:
        pass
    
    # Test transaction endpoint
    try:
        response = requests.get(f'http://localhost:{api_port}/api/v1/transaction/create/', timeout=2)
        # Even 405 (Method Not Allowed) means the endpoint exists
        node_info['transaction_endpoint_working'] = response.status_code in [200, 405, 400, 422]
    except Exception:
        pass
    
    # Test leader schedule
    try:
        response = requests.get(f'http://localhost:{api_port}/api/v1/blockchain/leader/current/', timeout=2)
        node_info['leader_schedule_available'] = response.status_code == 200
    except Exception:
        pass
    
    # Test quantum metrics
    try:
        response = requests.get(f'http://localhost:{api_port}/api/v1/blockchain/quantum-metrics/', timeout=2)
        if response.status_code == 200:
            node_info['quantum_metrics_available'] = True
            data = response.json()
            # Consider quantum healthy if it has active nodes or reasonable metrics
            active_nodes = data.get('active_nodes', 0)
            total_nodes = data.get('total_nodes', 0)
            node_info['quantum_healthy'] = active_nodes > 0 or total_nodes > 0
    except Exception:
        pass
    
    # Test node status endpoint
    try:
        response = requests.get(f'http://localhost:{api_port}/api/v1/node/status', timeout=2)
        node_info['node_status_available'] = response.status_code == 200
    except Exception:
        pass
    
    # Calculate availability score
    score = 0
    if node_info['process_running']:
        score += 20
    if node_info['api_responding']:
        score += 25
    if node_info['api_response_time'] < 1.0:
        score += 15
    elif node_info['api_response_time'] < 3.0:
        score += 10
    if node_info['transaction_endpoint_working']:
        score += 20
    if node_info['leader_schedule_available']:
        score += 10
    if node_info['quantum_metrics_available']:
        score += 5
    if node_info['quantum_healthy']:
        score += 5
    
    node_info['availability_score'] = score
    
    # Determine overall status
    if score >= 80:
        node_info['status'] = 'excellent'
        node_info['transaction_ready'] = True
    elif score >= 60:
        node_info['status'] = 'good'
        node_info['transaction_ready'] = True
    elif score >= 40:
        node_info['status'] = 'limited'
        node_info['transaction_ready'] = True  # Can still handle transactions
    elif node_info['process_running']:
        node_info['status'] = 'degraded'
        node_info['transaction_ready'] = False
    else:
        node_info['status'] = 'offline'
        node_info['transaction_ready'] = False
    
    return node_info


def check_all_nodes(base_port: int = 11000, max_nodes: int = 10) -> Tuple[List[Dict], List[Dict]]:
    """Check all nodes and return available and unavailable lists"""
    print(f"🔍 ENHANCED NODE AVAILABILITY CHECK")
    print(f"=" * 50)
    print(f"Checking {max_nodes} nodes starting from port {base_port}...")
    print()
    
    all_nodes = []
    available_nodes = []
    unavailable_nodes = []
    
    for i in range(max_nodes):
        api_port = base_port + i
        print(f"Checking Node {i+1:2d} (port {api_port})... ", end="", flush=True)
        
        node_info = get_node_health(api_port)
        all_nodes.append(node_info)
        
        if node_info['transaction_ready']:
            available_nodes.append(node_info)
            status_icon = {
                'excellent': '🟢',
                'good': '✅',
                'limited': '⚠️'
            }.get(node_info['status'], '✅')
            print(f"{status_icon} {node_info['status'].upper()} ({node_info['availability_score']}%)")
        else:
            unavailable_nodes.append(node_info)
            status_icon = {
                'degraded': '🔶',
                'offline': '❌'
            }.get(node_info['status'], '❌')
            print(f"{status_icon} {node_info['status'].upper()}")
    
    return available_nodes, unavailable_nodes


def print_availability_summary(available_nodes: List[Dict], unavailable_nodes: List[Dict]):
    """Print comprehensive availability summary"""
    total_nodes = len(available_nodes) + len(unavailable_nodes)
    
    print(f"\n📊 NODE AVAILABILITY SUMMARY")
    print(f"=" * 50)
    print(f"Total Nodes Checked: {total_nodes}")
    print(f"✅ Transaction-Ready: {len(available_nodes)}")
    print(f"❌ Not Ready: {len(unavailable_nodes)}")
    
    if available_nodes:
        # Sort by availability score
        available_nodes.sort(key=lambda x: x['availability_score'], reverse=True)
        
        excellent_nodes = [n for n in available_nodes if n['status'] == 'excellent']
        good_nodes = [n for n in available_nodes if n['status'] == 'good']
        limited_nodes = [n for n in available_nodes if n['status'] == 'limited']
        
        if excellent_nodes:
            print(f"\n🟢 EXCELLENT NODES ({len(excellent_nodes)}):")
            for node in excellent_nodes:
                print(f"   Node {node['node_id']:2d} (port {node['api_port']}): {node['availability_score']}% - {node['api_response_time']:.3f}s")
        
        if good_nodes:
            print(f"\n✅ GOOD NODES ({len(good_nodes)}):")
            for node in good_nodes:
                print(f"   Node {node['node_id']:2d} (port {node['api_port']}): {node['availability_score']}% - {node['api_response_time']:.3f}s")
        
        if limited_nodes:
            print(f"\n⚠️  LIMITED CAPACITY NODES ({len(limited_nodes)}):")
            for node in limited_nodes:
                print(f"   Node {node['node_id']:2d} (port {node['api_port']}): {node['availability_score']}% - {node['api_response_time']:.3f}s")
    
    if unavailable_nodes:
        degraded_nodes = [n for n in unavailable_nodes if n['status'] == 'degraded']
        offline_nodes = [n for n in unavailable_nodes if n['status'] == 'offline']
        
        if degraded_nodes:
            print(f"\n🔶 DEGRADED NODES ({len(degraded_nodes)}):")
            for node in degraded_nodes:
                print(f"   Node {node['node_id']:2d} (port {node['api_port']}): Process running but limited functionality")
        
        if offline_nodes:
            print(f"\n❌ OFFLINE NODES ({len(offline_nodes)}):")
            offline_ports = [str(n['api_port']) for n in offline_nodes]
            print(f"   Ports: {', '.join(offline_ports)}")


def print_detailed_analysis(available_nodes: List[Dict], unavailable_nodes: List[Dict]):
    """Print detailed analysis for each node"""
    print(f"\n🔬 DETAILED NODE ANALYSIS")
    print(f"=" * 60)
    
    all_nodes = available_nodes + unavailable_nodes
    all_nodes.sort(key=lambda x: x['node_id'])
    
    for node in all_nodes:
        status_icon = {
            'excellent': '🟢',
            'good': '✅',
            'limited': '⚠️',
            'degraded': '🔶',
            'offline': '❌'
        }.get(node['status'], '❓')
        
        print(f"\n{status_icon} Node {node['node_id']:2d} - {node['status'].upper()} ({node['availability_score']}%)")
        print(f"   Ports: API:{node['api_port']} | P2P:{node['p2p_port']} | TPU:{node['tpu_port']}")
        print(f"   Process Running: {'✅' if node['process_running'] else '❌'}")
        print(f"   API Responding: {'✅' if node['api_responding'] else '❌'} ({node['api_response_time']:.3f}s)")
        print(f"   Blockchain Accessible: {'✅' if node['blockchain_accessible'] else '❌'} ({node['blocks_count']} blocks)")
        print(f"   Transaction Endpoint: {'✅' if node['transaction_endpoint_working'] else '❌'}")
        print(f"   Leader Schedule: {'✅' if node['leader_schedule_available'] else '❌'}")
        print(f"   Quantum Metrics: {'✅' if node['quantum_metrics_available'] else '❌'}")
        print(f"   Node Status: {'✅' if node['node_status_available'] else '❌'}")
        print(f"   Transaction Ready: {'✅' if node['transaction_ready'] else '❌'}")


def get_recommendations(available_nodes: List[Dict]) -> Dict:
    """Get recommendations for transaction testing"""
    if not available_nodes:
        return {'message': 'No nodes available for transactions'}
    
    # Sort by availability score
    available_nodes.sort(key=lambda x: x['availability_score'], reverse=True)
    
    best_node = available_nodes[0]
    recommendations = {
        'best_node': best_node,
        'available_count': len(available_nodes),
        'single_node_commands': [],
        'multi_node_commands': [],
        'batch_sizes': []
    }
    
    # Single node recommendations
    if best_node['status'] == 'excellent':
        batch_sizes = [50, 100, 200]
    elif best_node['status'] == 'good':
        batch_sizes = [25, 50, 100]
    else:  # limited
        batch_sizes = [10, 25, 50]
    
    recommendations['batch_sizes'] = batch_sizes
    
    for batch_size in batch_sizes:
        cmd = f"python batch_transaction_test.py --node {best_node['api_port']} --batch-size {batch_size}"
        recommendations['single_node_commands'].append(cmd)
    
    # Multi-node recommendations
    if len(available_nodes) > 1:
        total_batch = sum(batch_sizes)
        for i, node in enumerate(available_nodes[:3]):
            node_batch = total_batch // min(3, len(available_nodes))
            cmd = f"python batch_transaction_test.py --node {node['api_port']} --batch-size {node_batch} &"
            recommendations['multi_node_commands'].append(cmd)
    
    return recommendations


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Node Availability Checker')
    parser.add_argument('--base-port', type=int, default=11000, help='Base API port (default: 11000)')
    parser.add_argument('--max-nodes', type=int, default=10, help='Maximum nodes to check (default: 10)')
    parser.add_argument('--detailed', action='store_true', help='Show detailed analysis')
    parser.add_argument('--export-json', type=str, help='Export results to JSON file')
    
    args = parser.parse_args()
    
    # Check nodes
    available_nodes, unavailable_nodes = check_all_nodes(args.base_port, args.max_nodes)
    
    # Print summary
    print_availability_summary(available_nodes, unavailable_nodes)
    
    # Print detailed analysis if requested
    if args.detailed:
        print_detailed_analysis(available_nodes, unavailable_nodes)
    
    # Get and print recommendations
    recommendations = get_recommendations(available_nodes)
    
    if available_nodes:
        print(f"\n🚀 RECOMMENDATIONS FOR BATCH TRANSACTION TESTING")
        print(f"=" * 60)
        
        best_node = recommendations['best_node']
        print(f"Best Node: Node {best_node['node_id']} (port {best_node['api_port']}) - {best_node['availability_score']}%")
        print(f"Status: {best_node['status'].upper()}")
        print(f"Response Time: {best_node['api_response_time']:.3f}s")
        
        print(f"\n📋 SUGGESTED COMMANDS:")
        print(f"Single Node Testing:")
        for cmd in recommendations['single_node_commands'][:3]:
            print(f"  {cmd}")
        
        if recommendations['multi_node_commands']:
            print(f"\nMulti-Node Testing:")
            for cmd in recommendations['multi_node_commands']:
                print(f"  {cmd}")
            print(f"  # Wait for all to complete, then: wait")
        
        print(f"\n💡 USAGE TIPS:")
        print(f"   • Start with smaller batch sizes for testing")
        print(f"   • Monitor node performance during tests")
        print(f"   • Use multi-node testing for load distribution")
        
    else:
        print(f"\n❌ NO NODES AVAILABLE FOR TRANSACTIONS!")
        print(f"💡 To start nodes:")
        print(f"   cd blockchain && ./start_nodes.sh 5")
        print(f"   # Wait 10 seconds, then rerun this checker")
    
    # Export to JSON if requested
    if args.export_json:
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'available_nodes': available_nodes,
            'unavailable_nodes': unavailable_nodes,
            'recommendations': recommendations
        }
        
        with open(args.export_json, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"\n📄 Results exported to {args.export_json}")
    
    return len(available_nodes) > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
