#!/usr/bin/env python3
"""
Decentralized Blockchain Network Setup
=====================================

This script sets up a decentralized blockchain network that can run:
1. Multiple nodes on a single computer (for testing)
2. Distributed nodes across multiple computers in the same subnet

Features:
- Automatic port allocation
- Node discovery and peer connection
- Genesis block synchronization
- Quantum consensus participation
- Gossip protocol for leader schedules
- Performance monitoring

Usage:
    # Single computer with 6 nodes
    python node_network_setup.py --mode single --nodes 6
    
    # Multi-computer setup (run on each computer)
    python node_network_setup.py --mode distributed --computer-id 1 --total-computers 6 --subnet 192.168.1
"""

import argparse
import json
import subprocess
import time
import os
import sys
import signal
import threading
from pathlib import Path
import ipaddress
import socket

class BlockchainNetworkSetup:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.blockchain_dir = self.base_dir / "blockchain"
        self.genesis_config_dir = self.base_dir / "genesis_config"
        self.keys_dir = self.blockchain_dir / "keys"
        
        # Port ranges for different services
        self.port_ranges = {
            'p2p': (10000, 10099),      # P2P communication
            'api': (8050, 8149),        # REST API
            'gossip': (12000, 12099),   # Gossip protocol
            'tpu': (13000, 13099),      # Transaction Processing Unit
            'tvu': (14000, 14099),      # Transaction Validation Unit
            'gulf_stream': (15000, 15099)  # Gulf Stream UDP forwarding
        }
        
        self.running_processes = []
        self.node_configs = []
        
    def get_local_ip(self, subnet_prefix=None):
        """Get the local IP address, optionally filtering by subnet"""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            if subnet_prefix and not local_ip.startswith(subnet_prefix):
                # Try to find an interface in the specified subnet
                import netifaces
                for interface in netifaces.interfaces():
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        for addr in addrs[netifaces.AF_INET]:
                            ip = addr['addr']
                            if ip.startswith(subnet_prefix) and ip != '127.0.0.1':
                                return ip
            
            return local_ip
        except Exception as e:
            print(f"Warning: Could not determine local IP: {e}")
            return "127.0.0.1"
    
    def check_port_available(self, ip, port):
        """Check if a port is available for binding"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((ip, port))
                return True
        except OSError:
            return False
    
    def allocate_ports(self, node_count, ip_address):
        """Allocate unique ports for each node"""
        port_assignments = []
        
        for node_id in range(node_count):
            node_ports = {}
            
            for service, (start_port, end_port) in self.port_ranges.items():
                port = start_port + node_id
                if port > end_port:
                    raise ValueError(f"Too many nodes for {service} port range. Max: {end_port - start_port + 1}")
                
                # Verify port is available
                if not self.check_port_available(ip_address, port):
                    raise ValueError(f"Port {port} is already in use on {ip_address}")
                
                node_ports[service] = port
            
            port_assignments.append(node_ports)
        
        return port_assignments
    
    def create_node_key(self, node_id):
        """Create or load a node's private key"""
        key_file = self.keys_dir / f"node_{node_id}_private_key.pem"
        
        if not key_file.exists():
            # Generate new key
            from blockchain.transaction.wallet import Wallet
            wallet = Wallet()
            wallet.save_to_file(str(key_file))
            print(f"✓ Generated new key for node {node_id}: {key_file}")
        else:
            print(f"✓ Using existing key for node {node_id}: {key_file}")
        
        return str(key_file)
    
    def ensure_genesis_config(self):
        """Ensure genesis configuration exists and is valid"""
        genesis_file = self.genesis_config_dir / "genesis.json"
        
        if not genesis_file.exists():
            print("⚠️ Genesis configuration not found. Creating new genesis setup...")
            
            # Import and create genesis configuration
            sys.path.append(str(self.blockchain_dir))
            from blockchain.genesis_config import GenesisConfig
            
            genesis_config = GenesisConfig()
            genesis_file_path = genesis_config.create_complete_genesis_setup()
            print(f"✓ Genesis configuration created: {genesis_file_path}")
        else:
            print(f"✓ Using existing genesis configuration: {genesis_file}")
        
        return str(genesis_file)
    
    def create_network_config(self, mode, node_configs, computer_id=None, total_computers=None, subnet_prefix=None):
        """Create network configuration file for peer discovery"""
        network_config = {
            "mode": mode,
            "computer_id": computer_id,
            "total_computers": total_computers,
            "subnet_prefix": subnet_prefix,
            "timestamp": time.time(),
            "nodes": []
        }
        
        for i, config in enumerate(node_configs):
            node_info = {
                "node_id": i,
                "computer_id": computer_id or 0,
                "public_key": None,  # Will be populated after node starts
                "ip_address": config['ip'],
                "ports": config['ports'],
                "status": "configured"
            }
            network_config["nodes"].append(node_info)
        
        config_file = self.base_dir / "network_config.json"
        with open(config_file, 'w') as f:
            json.dump(network_config, f, indent=2)
        
        print(f"✓ Network configuration saved: {config_file}")
        return str(config_file)
    
    def start_single_computer_network(self, node_count):
        """Start multiple nodes on a single computer"""
        print(f"🚀 Starting {node_count} nodes on single computer...")
        
        # Use localhost for single computer setup
        ip_address = "127.0.0.1"
        
        # Allocate ports for all nodes
        port_assignments = self.allocate_ports(node_count, ip_address)
        
        # Ensure genesis configuration exists
        genesis_file = self.ensure_genesis_config()
        
        # Create node configurations
        for node_id in range(node_count):
            ports = port_assignments[node_id]
            key_file = self.create_node_key(node_id)
            
            node_config = {
                'node_id': node_id,
                'ip': ip_address,
                'ports': ports,
                'key_file': key_file,
                'genesis_file': genesis_file
            }
            self.node_configs.append(node_config)
        
        # Create network configuration for peer discovery
        network_config_file = self.create_network_config("single", self.node_configs)
        
        # Start each node
        for config in self.node_configs:
            self.start_node(config, network_config_file)
            time.sleep(2)  # Stagger startup to avoid conflicts
        
        print(f"✅ All {node_count} nodes started successfully!")
        self.print_network_status()
    
    def start_distributed_network(self, computer_id, total_computers, subnet_prefix):
        """Start node for distributed network across multiple computers"""
        print(f"🌐 Starting distributed node (Computer {computer_id}/{total_computers})...")
        
        # Get local IP address in the specified subnet
        ip_address = self.get_local_ip(subnet_prefix)
        
        if not ip_address.startswith(subnet_prefix):
            raise ValueError(f"Could not find network interface in subnet {subnet_prefix}.x")
        
        print(f"📍 Using IP address: {ip_address}")
        
        # For distributed mode, run one primary node per computer
        port_assignments = self.allocate_ports(1, ip_address)
        
        # Ensure genesis configuration exists
        genesis_file = self.ensure_genesis_config()
        
        # Create node configuration
        key_file = self.create_node_key(computer_id)
        
        node_config = {
            'node_id': 0,  # Single node per computer
            'computer_id': computer_id,
            'ip': ip_address,
            'ports': port_assignments[0],
            'key_file': key_file,
            'genesis_file': genesis_file
        }
        self.node_configs.append(node_config)
        
        # Create network configuration
        network_config_file = self.create_network_config(
            "distributed", 
            self.node_configs, 
            computer_id, 
            total_computers, 
            subnet_prefix
        )
        
        # Start the node
        self.start_node(node_config, network_config_file)
        
        print(f"✅ Distributed node started on computer {computer_id}!")
        self.print_network_status()
    
    def start_node(self, config, network_config_file):
        """Start a single blockchain node"""
        node_id = config['node_id']
        ports = config['ports']
        
        print(f"🔄 Starting node {node_id} on {config['ip']}...")
        
        # Prepare environment variables
        env = os.environ.copy()
        env.update({
            'NETWORK_CONFIG_FILE': network_config_file,
            'NODE_ID': str(node_id),
            'COMPUTER_ID': str(config.get('computer_id', 0)),
            'GENESIS_CONFIG_FILE': config['genesis_file']
        })
        
        # Build command to start node
        cmd = [
            sys.executable,
            str(self.blockchain_dir / "run_node.py"),
            "--ip", config['ip'],
            "--node_port", str(ports['p2p']),
            "--api_port", str(ports['api']),
            "--key_file", config['key_file'],
            "--p2p_mode", "enhanced"
        ]
        
        # Start node process
        try:
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.running_processes.append({
                'process': process,
                'config': config,
                'cmd': ' '.join(cmd)
            })
            
            print(f"✓ Node {node_id} started (PID: {process.pid})")
            print(f"   P2P: {config['ip']}:{ports['p2p']}")
            print(f"   API: http://{config['ip']}:{ports['api']}")
            print(f"   Gossip: {ports['gossip']}, TPU: {ports['tpu']}, TVU: {ports['tvu']}")
            
            # Monitor node output in background thread
            output_thread = threading.Thread(
                target=self.monitor_node_output,
                args=(process, node_id),
                daemon=True
            )
            output_thread.start()
            
        except Exception as e:
            print(f"❌ Failed to start node {node_id}: {e}")
            raise
    
    def monitor_node_output(self, process, node_id):
        """Monitor node output and print important messages"""
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    # Filter and print important log messages
                    if any(keyword in line.lower() for keyword in [
                        'error', 'warning', 'started', 'failed', 'connected', 
                        'block', 'consensus', 'leader', 'metrics'
                    ]):
                        print(f"[Node-{node_id}] {line.strip()}")
        except Exception as e:
            print(f"[Node-{node_id}] Output monitoring stopped: {e}")
    
    def print_network_status(self):
        """Print current network status"""
        print("\n📊 Network Status:")
        print("=" * 60)
        
        for i, proc_info in enumerate(self.running_processes):
            config = proc_info['config']
            process = proc_info['process']
            ports = config['ports']
            
            status = "🟢 Running" if process.poll() is None else "🔴 Stopped"
            
            print(f"Node {config['node_id']} ({config['ip']}):")
            print(f"  Status: {status}")
            print(f"  API: http://{config['ip']}:{ports['api']}")
            print(f"  P2P: {config['ip']}:{ports['p2p']}")
            print(f"  PID: {process.pid}")
            print()
        
        print("🔗 Network Endpoints:")
        print(f"  Total Active Nodes: {len([p for p in self.running_processes if p['process'].poll() is None])}")
        
        if self.node_configs:
            first_node = self.node_configs[0]
            print(f"  Blockchain Explorer: http://{first_node['ip']}:{first_node['ports']['api']}/api/v1/blockchain/")
            print(f"  Performance Metrics: http://{first_node['ip']}:{first_node['ports']['api']}/api/v1/blockchain/performance-metrics/")
            print(f"  Network Status: http://{first_node['ip']}:{first_node['ports']['api']}/api/v1/blockchain/network-status/")
    
    def stop_all_nodes(self):
        """Stop all running nodes gracefully"""
        print("\n🛑 Stopping all nodes...")
        
        for proc_info in self.running_processes:
            process = proc_info['process']
            node_id = proc_info['config']['node_id']
            
            if process.poll() is None:  # Process is still running
                print(f"Stopping node {node_id}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                    print(f"✓ Node {node_id} stopped gracefully")
                except subprocess.TimeoutExpired:
                    print(f"⚠️ Force killing node {node_id}")
                    process.kill()
        
        self.running_processes.clear()
        print("✅ All nodes stopped")
    
    def wait_for_shutdown(self):
        """Wait for shutdown signal and cleanup"""
        def signal_handler(signum, frame):
            print(f"\n🔄 Received signal {signum}, shutting down...")
            self.stop_all_nodes()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            print("\n🌐 Network is running. Press Ctrl+C to stop all nodes.")
            while True:
                # Check if any process has died
                active_processes = [p for p in self.running_processes if p['process'].poll() is None]
                if len(active_processes) != len(self.running_processes):
                    print("⚠️ Some nodes have stopped. Checking status...")
                    self.print_network_status()
                
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n🔄 Shutdown requested by user")
            self.stop_all_nodes()

def main():
    parser = argparse.ArgumentParser(
        description="Setup and run decentralized blockchain network",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run 6 nodes on single computer for testing
  python node_network_setup.py --mode single --nodes 6
  
  # Run distributed network on 6 computers (run on each computer)
  # Computer 1:
  python node_network_setup.py --mode distributed --computer-id 1 --total-computers 6 --subnet 192.168.1
  
  # Computer 2:
  python node_network_setup.py --mode distributed --computer-id 2 --total-computers 6 --subnet 192.168.1
  
  # ... and so on for computers 3-6
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['single', 'distributed'],
        required=True,
        help='Network mode: single computer or distributed across computers'
    )
    
    # Single computer mode arguments
    parser.add_argument(
        '--nodes',
        type=int,
        default=6,
        help='Number of nodes to run on single computer (default: 6)'
    )
    
    # Distributed mode arguments
    parser.add_argument(
        '--computer-id',
        type=int,
        help='ID of this computer (1-N) for distributed mode'
    )
    
    parser.add_argument(
        '--total-computers',
        type=int,
        help='Total number of computers in distributed network'
    )
    
    parser.add_argument(
        '--subnet',
        type=str,
        help='Subnet prefix (e.g., 192.168.1) for distributed mode'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.mode == 'single':
        if args.nodes < 1 or args.nodes > 20:
            parser.error("Number of nodes must be between 1 and 20 for single computer mode")
    
    elif args.mode == 'distributed':
        if not args.computer_id or not args.total_computers or not args.subnet:
            parser.error("Distributed mode requires --computer-id, --total-computers, and --subnet")
        
        if args.computer_id < 1 or args.computer_id > args.total_computers:
            parser.error(f"Computer ID must be between 1 and {args.total_computers}")
        
        # Validate subnet format
        try:
            test_ip = f"{args.subnet}.1"
            ipaddress.ip_address(test_ip)
        except ValueError:
            parser.error(f"Invalid subnet format: {args.subnet}")
    
    # Create and run network setup
    try:
        setup = BlockchainNetworkSetup()
        
        print("🔗 Decentralized Blockchain Network Setup")
        print("=" * 50)
        
        if args.mode == 'single':
            setup.start_single_computer_network(args.nodes)
        else:
            setup.start_distributed_network(args.computer_id, args.total_computers, args.subnet)
        
        # Wait for shutdown
        setup.wait_for_shutdown()
        
    except KeyboardInterrupt:
        print("\n🔄 Setup interrupted by user")
        if 'setup' in locals():
            setup.stop_all_nodes()
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        if 'setup' in locals():
            setup.stop_all_nodes()
        sys.exit(1)

if __name__ == "__main__":
    main()
