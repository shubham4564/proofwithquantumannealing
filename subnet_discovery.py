#!/usr/bin/env python3
"""
Dynamic Node Discovery for Blockchain Network
============================================
Scans the local subnet to find other running blockchain nodes
"""

import socket
import threading
import time
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_local_subnet():
    """Get the local subnet (e.g., 192.168.0)"""
    try:
        # Get default route interface
        result = subprocess.run(['route', 'get', 'default'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'interface:' in line:
                    interface = line.split(':')[1].strip()
                    break
        
        # Get IP from interface
        result = subprocess.run(['ifconfig', interface], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'inet ' in line and '127.0.0.1' not in line:
                    ip = line.split()[1]
                    subnet = '.'.join(ip.split('.')[:-1])
                    return subnet, ip
    except:
        pass
    
    # Fallback method
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        subnet = '.'.join(local_ip.split('.')[:-1])
        return subnet, local_ip
    except:
        return None, None

def check_blockchain_node(ip, port_range=(11000, 11006)):
    """Check if there's a blockchain node running at the given IP"""
    for port in range(port_range[0], port_range[1]):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, port))
            sock.close()
            
            if result == 0:
                # Port is open, try to verify it's a blockchain node
                try:
                    import requests
                    response = requests.get(f'http://{ip}:{port}/api/v1/blockchain/', 
                                          timeout=2)
                    if response.status_code == 200:
                        data = response.json()
                        if 'blocks' in data:
                            return {
                                'ip': ip,
                                'api_port': port,
                                'p2p_port': port - 1000,  # P2P is 1000 less than API
                                'status': 'active',
                                'blocks': len(data.get('blocks', []))
                            }
                except:
                    # Might be a blockchain node but API not ready
                    return {
                        'ip': ip,
                        'api_port': port,
                        'p2p_port': port - 1000,
                        'status': 'detected',
                        'blocks': 0
                    }
        except:
            continue
    
    return None

def scan_subnet_for_nodes(subnet, exclude_ip=None, max_workers=50):
    """Scan subnet for blockchain nodes"""
    print(f"🔍 Scanning subnet {subnet}.x for blockchain nodes...")
    
    discovered_nodes = []
    
    def scan_ip(ip):
        if ip != exclude_ip:
            return check_blockchain_node(ip)
        return None
    
    # Generate IPs to scan (1-254)
    ips_to_scan = [f"{subnet}.{i}" for i in range(1, 255)]
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ip = {executor.submit(scan_ip, ip): ip for ip in ips_to_scan}
        
        completed = 0
        for future in as_completed(future_to_ip):
            completed += 1
            if completed % 50 == 0:
                print(f"   Scanned {completed}/254 addresses...")
            
            try:
                result = future.result()
                if result:
                    discovered_nodes.append(result)
                    print(f"✅ Found blockchain node: {result['ip']}:{result['api_port']} ({result['status']})")
            except Exception as e:
                pass
    
    return discovered_nodes

def create_dynamic_network_config(local_ip, discovered_nodes, computer_id):
    """Create network config with discovered nodes"""
    subnet = '.'.join(local_ip.split('.')[:-1])
    
    config = {
        "mode": "distributed",
        "computer_id": computer_id,
        "total_computers": len(discovered_nodes) + 1,  # +1 for self
        "subnet_prefix": subnet,
        "local_ip": local_ip,
        "timestamp": int(time.time()),
        "discovered_nodes": discovered_nodes,
        "expected_nodes": []
    }
    
    # Add self to the list
    local_api_port = 11000 + computer_id - 1
    config["expected_nodes"].append({
        "computer_id": computer_id,
        "ip": local_ip,
        "p2p_port": 10000 + computer_id - 1,
        "api_port": local_api_port,
        "gossip_port": 12000 + computer_id - 1,
        "tpu_port": 13000 + computer_id - 1,
        "tvu_port": 14000 + computer_id - 1,
        "status": "self"
    })
    
    # Add discovered nodes
    for i, node in enumerate(discovered_nodes):
        config["expected_nodes"].append({
            "computer_id": i + 2 if computer_id == 1 else (i + 1 if i + 1 < computer_id else i + 2),
            "ip": node["ip"],
            "p2p_port": node["p2p_port"],
            "api_port": node["api_port"],
            "gossip_port": node["api_port"] + 1000,
            "tpu_port": node["api_port"] + 2000,
            "tvu_port": node["api_port"] + 3000,
            "status": node["status"]
        })
    
    return config

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 subnet_discovery.py <computer_id>")
        sys.exit(1)
    
    computer_id = int(sys.argv[1])
    
    # Get local network info
    subnet, local_ip = get_local_subnet()
    if not subnet or not local_ip:
        print("❌ Could not determine local network information")
        sys.exit(1)
    
    print(f"🌐 Local Network Discovery")
    print(f"📍 Local IP: {local_ip}")
    print(f"🔍 Subnet: {subnet}.x")
    print()
    
    # Scan for other nodes
    discovered_nodes = scan_subnet_for_nodes(subnet, exclude_ip=local_ip)
    
    print()
    print(f"📊 Discovery Results:")
    print(f"   Found {len(discovered_nodes)} other blockchain nodes")
    
    if discovered_nodes:
        print("   Nodes:")
        for node in discovered_nodes:
            print(f"     • {node['ip']}:{node['api_port']} (P2P: {node['p2p_port']}) - {node['status']}")
    else:
        print("   ⚠️  No other nodes found - this will be a standalone node")
    
    # Create dynamic network configuration
    config = create_dynamic_network_config(local_ip, discovered_nodes, computer_id)
    
    # Save configuration
    with open('dynamic_network_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print()
    print(f"✅ Dynamic network configuration saved to: dynamic_network_config.json")
    print(f"🚀 Ready to start blockchain node with {len(discovered_nodes)} peers")
    
    return config

if __name__ == "__main__":
    main()
