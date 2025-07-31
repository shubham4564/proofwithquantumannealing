#!/usr/bin/env python3
"""
Continuous Peer Discovery with Broadcasting
==========================================
Broadcasts node presence and continuously discovers peers
"""

import socket
import threading
import time
import json
import subprocess
import sys
import requests
from concurrent.futures import ThreadPoolExecutor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class BlockchainPeerDiscovery:
    def __init__(self, computer_id, local_ip, api_port):
        self.computer_id = computer_id
        self.local_ip = local_ip
        self.api_port = api_port
        self.subnet = '.'.join(local_ip.split('.')[:-1])
        self.broadcast_port = 19999  # UDP broadcast port
        self.discovered_peers = {}
        self.running = True
        
    def get_node_info(self):
        """Get this node's information"""
        return {
            'computer_id': self.computer_id,
            'ip': self.local_ip,
            'api_port': self.api_port,
            'p2p_port': self.api_port - 1000,
            'timestamp': int(time.time()),
            'subnet': self.subnet
        }
    
    def broadcast_presence(self):
        """Broadcast this node's presence to the subnet"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        message = json.dumps({
            'type': 'blockchain_node_announcement',
            'node': self.get_node_info()
        }).encode('utf-8')
        
        while self.running:
            try:
                # Broadcast to subnet
                broadcast_ip = f"{self.subnet}.255"
                sock.sendto(message, (broadcast_ip, self.broadcast_port))
                logger.info(f"📢 Broadcasted presence to {broadcast_ip}:{self.broadcast_port}")
                time.sleep(30)  # Broadcast every 30 seconds
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                time.sleep(10)
        
        sock.close()
    
    def listen_for_announcements(self):
        """Listen for announcements from other nodes"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            sock.bind(('', self.broadcast_port))
            logger.info(f"👂 Listening for peer announcements on port {self.broadcast_port}")
            
            while self.running:
                try:
                    data, addr = sock.recvfrom(1024)
                    message = json.loads(data.decode('utf-8'))
                    
                    if (message.get('type') == 'blockchain_node_announcement' and 
                        addr[0] != self.local_ip):  # Don't add ourselves
                        
                        node_info = message.get('node', {})
                        peer_ip = node_info.get('ip')
                        
                        if peer_ip and peer_ip not in self.discovered_peers:
                            # Verify it's actually a blockchain node
                            if self.verify_blockchain_node(node_info):
                                self.discovered_peers[peer_ip] = node_info
                                logger.info(f"✅ Discovered new peer: {peer_ip}:{node_info.get('api_port')}")
                                self.save_discovery_results()
                            
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"Listen error: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            logger.error(f"Failed to bind to broadcast port: {e}")
        finally:
            sock.close()
    
    def verify_blockchain_node(self, node_info):
        """Verify that the announced node is actually a blockchain node"""
        try:
            ip = node_info.get('ip')
            port = node_info.get('api_port')
            
            if not ip or not port:
                return False
                
            response = requests.get(f'http://{ip}:{port}/api/v1/blockchain/', timeout=3)
            if response.status_code == 200:
                data = response.json()
                return 'blocks' in data
        except:
            pass
        return False
    
    def active_scan_subnet(self):
        """Actively scan subnet for nodes (backup method)"""
        while self.running:
            try:
                logger.info("🔍 Performing active subnet scan...")
                
                def scan_ip(ip_suffix):
                    if ip_suffix == int(self.local_ip.split('.')[-1]):
                        return None  # Skip ourselves
                        
                    ip = f"{self.subnet}.{ip_suffix}"
                    
                    # Check common blockchain API ports
                    for port in range(11000, 11006):
                        try:
                            response = requests.get(f'http://{ip}:{port}/api/v1/blockchain/', timeout=1)
                            if response.status_code == 200:
                                data = response.json()
                                if 'blocks' in data:
                                    return {
                                        'ip': ip,
                                        'api_port': port,
                                        'p2p_port': port - 1000,
                                        'discovered_via': 'active_scan',
                                        'timestamp': int(time.time())
                                    }
                        except:
                            continue
                    return None
                
                # Scan in parallel
                with ThreadPoolExecutor(max_workers=20) as executor:
                    futures = [executor.submit(scan_ip, i) for i in range(1, 255)]
                    
                    for future in futures:
                        try:
                            result = future.result()
                            if result and result['ip'] not in self.discovered_peers:
                                self.discovered_peers[result['ip']] = result
                                logger.info(f"🔍 Active scan found: {result['ip']}:{result['api_port']}")
                                self.save_discovery_results()
                        except:
                            pass
                
                # Sleep before next scan
                time.sleep(120)  # Scan every 2 minutes
                
            except Exception as e:
                logger.error(f"Active scan error: {e}")
                time.sleep(60)
    
    def save_discovery_results(self):
        """Save discovered peers to config file"""
        try:
            config = {
                "mode": "distributed",
                "computer_id": self.computer_id,
                "total_computers": len(self.discovered_peers) + 1,
                "subnet_prefix": self.subnet,
                "local_ip": self.local_ip,
                "timestamp": int(time.time()),
                "discovered_nodes": list(self.discovered_peers.values()),
                "expected_nodes": []
            }
            
            # Add self
            config["expected_nodes"].append({
                "computer_id": self.computer_id,
                "ip": self.local_ip,
                "p2p_port": self.api_port - 1000,
                "api_port": self.api_port,
                "gossip_port": self.api_port + 1000,
                "tpu_port": self.api_port + 2000,
                "tvu_port": self.api_port + 3000,
                "status": "self"
            })
            
            # Add discovered peers
            for i, (ip, node_info) in enumerate(self.discovered_peers.items()):
                config["expected_nodes"].append({
                    "computer_id": node_info.get('computer_id', i + 10),
                    "ip": ip,
                    "p2p_port": node_info.get('p2p_port', node_info.get('api_port', 11000) - 1000),
                    "api_port": node_info.get('api_port', 11000),
                    "gossip_port": node_info.get('api_port', 11000) + 1000,
                    "tpu_port": node_info.get('api_port', 11000) + 2000,
                    "tvu_port": node_info.get('api_port', 11000) + 3000,
                    "status": "discovered"
                })
            
            with open('dynamic_network_config.json', 'w') as f:
                json.dump(config, f, indent=2)
                
            logger.info(f"💾 Updated network config: {len(self.discovered_peers)} peers")
            
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def start_discovery(self):
        """Start all discovery methods"""
        logger.info("🚀 Starting continuous peer discovery...")
        
        # Start background threads
        threads = [
            threading.Thread(target=self.broadcast_presence, daemon=True),
            threading.Thread(target=self.listen_for_announcements, daemon=True),
            threading.Thread(target=self.active_scan_subnet, daemon=True)
        ]
        
        for thread in threads:
            thread.start()
        
        # Initial save
        self.save_discovery_results()
        
        return threads
    
    def stop_discovery(self):
        """Stop discovery"""
        self.running = False
        logger.info("🛑 Stopping peer discovery...")

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 continuous_discovery.py <computer_id> <local_ip> <api_port>")
        sys.exit(1)
    
    computer_id = int(sys.argv[1])
    local_ip = sys.argv[2]
    api_port = int(sys.argv[3])
    
    discovery = BlockchainPeerDiscovery(computer_id, local_ip, api_port)
    
    try:
        threads = discovery.start_discovery()
        
        # Keep running
        while True:
            time.sleep(10)
            print(f"📊 Current peers: {len(discovery.discovered_peers)}")
            
    except KeyboardInterrupt:
        discovery.stop_discovery()
        print("Discovery stopped.")

if __name__ == "__main__":
    main()
