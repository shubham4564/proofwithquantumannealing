"""
Enhanced Node Configuration for Decentralized Network
===================================================

This module extends the existing Node class to support:
1. Dynamic peer discovery in subnet networks
2. Automatic genesis synchronization
3. Cross-computer node communication
4. Network health monitoring
"""

import json
import os
import time
import threading
import socket
import requests
from pathlib import Path
from typing import Dict, List, Optional

class NetworkDiscovery:
    """Handle peer discovery and network configuration"""
    
    def __init__(self, node_ip: str, node_ports: Dict, network_config_file: str = None):
        self.node_ip = node_ip
        self.node_ports = node_ports
        self.network_config_file = network_config_file or "network_config.json"
        self.peers = {}
        self.discovery_active = False
        
    def start_discovery(self):
        """Start peer discovery process"""
        self.discovery_active = True
        
        # Load existing network configuration
        self.load_network_config()
        
        # Start discovery threads
        discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
        discovery_thread.start()
        
        health_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        health_thread.start()
        
        print(f"🔍 Network discovery started for {self.node_ip}")
    
    def stop_discovery(self):
        """Stop peer discovery"""
        self.discovery_active = False
    
    def load_network_config(self):
        """Load network configuration from file"""
        try:
            if os.path.exists(self.network_config_file):
                with open(self.network_config_file, 'r') as f:
                    config = json.load(f)
                
                # Extract peer information
                for node_info in config.get('nodes', []):
                    if node_info['ip_address'] != self.node_ip:  # Don't add self
                        peer_id = f"{node_info['ip_address']}:{node_info['ports']['p2p']}"
                        self.peers[peer_id] = {
                            'ip': node_info['ip_address'],
                            'ports': node_info['ports'],
                            'last_seen': 0,
                            'status': 'unknown',
                            'computer_id': node_info.get('computer_id', 0)
                        }
                
                print(f"📋 Loaded {len(self.peers)} potential peers from config")
        
        except Exception as e:
            print(f"⚠️ Could not load network config: {e}")
    
    def scan_subnet_for_peers(self, subnet_prefix: str, port_range: tuple):
        """Scan subnet for blockchain nodes"""
        active_peers = []
        
        try:
            import ipaddress
            
            # Generate subnet IPs to scan
            network = ipaddress.IPv4Network(f"{subnet_prefix}.0/24", strict=False)
            
            print(f"🔍 Scanning subnet {subnet_prefix}.0/24 for blockchain nodes...")
            
            for ip in network.hosts():
                ip_str = str(ip)
                if ip_str == self.node_ip:  # Skip self
                    continue
                
                # Try to connect to potential API ports
                for port_offset in range(10):  # Check first 10 possible nodes
                    api_port = port_range[0] + port_offset
                    if self._check_blockchain_node(ip_str, api_port):
                        active_peers.append({
                            'ip': ip_str,
                            'api_port': api_port,
                            'p2p_port': 10000 + port_offset  # Assume standard port mapping
                        })
                        break
            
            print(f"✅ Found {len(active_peers)} active blockchain nodes in subnet")
            return active_peers
        
        except Exception as e:
            print(f"❌ Subnet scan failed: {e}")
            return []
    
    def _check_blockchain_node(self, ip: str, port: int, timeout: float = 2.0) -> bool:
        """Check if there's a blockchain node at given IP:port"""
        try:
            response = requests.get(
                f"http://{ip}:{port}/api/v1/blockchain/",
                timeout=timeout
            )
            
            # Check if response looks like our blockchain API
            if response.status_code == 200:
                data = response.json()
                return 'blocks' in data or 'blockchain' in data
        
        except Exception:
            pass
        
        return False
    
    def _discovery_loop(self):
        """Main discovery loop"""
        while self.discovery_active:
            try:
                # Check configured peers
                self._check_configured_peers()
                
                # Optionally scan for new peers in subnet
                if hasattr(self, 'subnet_prefix'):
                    new_peers = self.scan_subnet_for_peers(
                        self.subnet_prefix, 
                        (11000, 11099)  # API port range
                    )
                    self._add_discovered_peers(new_peers)
                
                time.sleep(30)  # Discovery every 30 seconds
            
            except Exception as e:
                print(f"❌ Discovery loop error: {e}")
                time.sleep(10)
    
    def _check_configured_peers(self):
        """Check health of configured peers"""
        for peer_id, peer_info in self.peers.items():
            try:
                api_port = peer_info['ports']['api']
                if self._check_blockchain_node(peer_info['ip'], api_port, timeout=3.0):
                    peer_info['last_seen'] = time.time()
                    peer_info['status'] = 'active'
                else:
                    peer_info['status'] = 'inactive'
            
            except Exception as e:
                peer_info['status'] = 'error'
    
    def _add_discovered_peers(self, discovered_peers: List[Dict]):
        """Add newly discovered peers to peer list"""
        for peer in discovered_peers:
            peer_id = f"{peer['ip']}:{peer['p2p_port']}"
            if peer_id not in self.peers:
                self.peers[peer_id] = {
                    'ip': peer['ip'],
                    'ports': {
                        'api': peer['api_port'],
                        'p2p': peer['p2p_port']
                    },
                    'last_seen': time.time(),
                    'status': 'discovered',
                    'computer_id': 'unknown'
                }
                print(f"🆕 Discovered new peer: {peer_id}")
    
    def _health_check_loop(self):
        """Monitor network health"""
        while self.discovery_active:
            try:
                active_peers = [p for p in self.peers.values() if p['status'] == 'active']
                total_peers = len(self.peers)
                
                if total_peers > 0:
                    health_pct = (len(active_peers) / total_peers) * 100
                    print(f"🌐 Network Health: {len(active_peers)}/{total_peers} peers active ({health_pct:.1f}%)")
                
                time.sleep(60)  # Health check every minute
            
            except Exception as e:
                print(f"❌ Health check error: {e}")
                time.sleep(30)
    
    def get_active_peers(self) -> List[Dict]:
        """Get list of currently active peers"""
        return [
            {
                'ip': peer['ip'],
                'ports': peer['ports'],
                'last_seen': peer['last_seen']
            }
            for peer in self.peers.values() 
            if peer['status'] == 'active'
        ]
    
    def get_network_status(self) -> Dict:
        """Get comprehensive network status"""
        current_time = time.time()
        
        status_counts = {}
        for peer in self.peers.values():
            status = peer['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total_configured_peers': len(self.peers),
            'status_breakdown': status_counts,
            'active_peers': len([p for p in self.peers.values() if p['status'] == 'active']),
            'network_health_percentage': (status_counts.get('active', 0) / max(len(self.peers), 1)) * 100,
            'discovery_active': self.discovery_active,
            'last_update': current_time
        }

class EnhancedNodeManager:
    """Enhanced node manager with network capabilities"""
    
    def __init__(self, node_instance):
        self.node = node_instance
        self.network_discovery = None
        self.auto_sync_enabled = True
        
        # Load environment configuration
        self.load_environment_config()
        
        # Initialize network discovery if configured
        if hasattr(self, 'network_config_file'):
            self.setup_network_discovery()
    
    def load_environment_config(self):
        """Load configuration from environment variables"""
        self.network_config_file = os.getenv('NETWORK_CONFIG_FILE')
        self.node_id = os.getenv('NODE_ID', '0')
        self.computer_id = os.getenv('COMPUTER_ID', '0')
        self.genesis_config_file = os.getenv('GENESIS_CONFIG_FILE')
        
        print(f"📋 Node Environment:")
        print(f"   Node ID: {self.node_id}")
        print(f"   Computer ID: {self.computer_id}")
        print(f"   Network Config: {self.network_config_file}")
        print(f"   Genesis Config: {self.genesis_config_file}")
    
    def setup_network_discovery(self):
        """Setup network discovery for this node"""
        if not self.network_config_file:
            return
        
        try:
            node_ports = {
                'p2p': self.node.port,
                'api': 8050,  # Will be updated when API starts
                'gossip': self.node.gossip_port,
                'tpu': self.node.tpu_port,
                'tvu': self.node.tvu_port
            }
            
            self.network_discovery = NetworkDiscovery(
                self.node.ip,
                node_ports,
                self.network_config_file
            )
            
            # Start discovery
            self.network_discovery.start_discovery()
            
            print("🔍 Network discovery initialized")
        
        except Exception as e:
            print(f"⚠️ Failed to setup network discovery: {e}")
    
    def start_auto_peer_connection(self):
        """Automatically connect to discovered peers"""
        if not self.network_discovery:
            return
        
        def peer_connection_loop():
            while self.auto_sync_enabled:
                try:
                    active_peers = self.network_discovery.get_active_peers()
                    
                    for peer in active_peers:
                        # Connect to peer via P2P
                        self.connect_to_peer(peer['ip'], peer['ports']['p2p'])
                    
                    time.sleep(45)  # Check for new connections every 45 seconds
                
                except Exception as e:
                    print(f"❌ Auto peer connection error: {e}")
                    time.sleep(30)
        
        connection_thread = threading.Thread(target=peer_connection_loop, daemon=True)
        connection_thread.start()
        
        print("🔗 Auto peer connection started")
    
    def connect_to_peer(self, peer_ip: str, peer_port: int):
        """Connect to a specific peer"""
        try:
            # Use the node's existing P2P connection method
            if hasattr(self.node, 'p2p') and self.node.p2p:
                if not self.node.p2p.is_connected_to_peer(peer_ip, peer_port):
                    self.node.p2p.connect_to_peer(peer_ip, peer_port)
                    print(f"🔗 Connected to peer: {peer_ip}:{peer_port}")
        
        except Exception as e:
            print(f"⚠️ Failed to connect to peer {peer_ip}:{peer_port}: {e}")
    
    def sync_blockchain_with_network(self):
        """Synchronize blockchain with network peers"""
        if not self.network_discovery:
            return
        
        try:
            active_peers = self.network_discovery.get_active_peers()
            
            if not active_peers:
                print("⚠️ No active peers found for blockchain sync")
                return
            
            # Get blockchain length from peers
            peer_chain_info = []
            for peer in active_peers[:3]:  # Check up to 3 peers
                try:
                    api_port = peer['ports']['api']
                    response = requests.get(
                        f"http://{peer['ip']}:{api_port}/api/v1/blockchain/",
                        timeout=5.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        block_count = len(data.get('blocks', []))
                        peer_chain_info.append({
                            'peer': f"{peer['ip']}:{api_port}",
                            'block_count': block_count,
                            'genesis_hash': data.get('blocks', [{}])[0].get('hash', '') if data.get('blocks') else ''
                        })
                
                except Exception as e:
                    print(f"⚠️ Could not get chain info from {peer['ip']}: {e}")
            
            if peer_chain_info:
                local_block_count = len(self.node.blockchain.blocks)
                max_peer_blocks = max(info['block_count'] for info in peer_chain_info)
                
                print(f"📊 Blockchain Sync Status:")
                print(f"   Local blocks: {local_block_count}")
                print(f"   Network max: {max_peer_blocks}")
                
                if max_peer_blocks > local_block_count:
                    print(f"🔄 Local blockchain is {max_peer_blocks - local_block_count} blocks behind")
                    # Trigger sync process via P2P
                    self._trigger_block_sync()
                else:
                    print("✅ Local blockchain is up to date")
        
        except Exception as e:
            print(f"❌ Blockchain sync error: {e}")
    
    def _trigger_block_sync(self):
        """Trigger block synchronization via P2P"""
        try:
            if hasattr(self.node, 'p2p') and self.node.p2p:
                # Request latest blocks from connected peers
                self.node.p2p.request_blockchain_sync()
                print("🔄 Blockchain sync requested via P2P")
        
        except Exception as e:
            print(f"⚠️ Failed to trigger block sync: {e}")
    
    def get_network_status(self) -> Dict:
        """Get comprehensive network status"""
        status = {
            'node_info': {
                'node_id': self.node_id,
                'computer_id': self.computer_id,
                'ip': self.node.ip,
                'port': self.node.port,
                'public_key': self.node.wallet.public_key_string()[:20] + "...",
                'blockchain_height': len(self.node.blockchain.blocks)
            },
            'p2p_status': {
                'connected_peers': len(getattr(self.node.p2p, 'connected_peers', {})) if hasattr(self.node, 'p2p') else 0,
                'p2p_active': hasattr(self.node, 'p2p') and self.node.p2p is not None
            },
            'discovery_status': self.network_discovery.get_network_status() if self.network_discovery else None,
            'consensus_status': {
                'registered_validators': len(self.node.blockchain.quantum_consensus.nodes) if self.node.blockchain.quantum_consensus else 0,
                'current_leader': self.node.blockchain.leader_schedule.get_current_leader()[:20] + "..." if self.node.blockchain.leader_schedule.get_current_leader() else None
            }
        }
        
        return status
    
    def stop(self):
        """Stop enhanced node manager"""
        self.auto_sync_enabled = False
        
        if self.network_discovery:
            self.network_discovery.stop_discovery()
        
        print("🛑 Enhanced node manager stopped")

# Add network discovery to existing Node class
def enhance_node_with_network_discovery(node_instance):
    """Enhance an existing node instance with network discovery capabilities"""
    
    # Add enhanced manager to node
    node_instance.enhanced_manager = EnhancedNodeManager(node_instance)
    
    # Start auto peer connection
    node_instance.enhanced_manager.start_auto_peer_connection()
    
    # Start periodic blockchain sync
    def periodic_sync():
        while node_instance.enhanced_manager.auto_sync_enabled:
            try:
                time.sleep(60)  # Sync check every minute
                node_instance.enhanced_manager.sync_blockchain_with_network()
            except Exception as e:
                print(f"❌ Periodic sync error: {e}")
                time.sleep(30)
    
    sync_thread = threading.Thread(target=periodic_sync, daemon=True)
    sync_thread.start()
    
    print("🚀 Node enhanced with network discovery and auto-sync")
    
    return node_instance
