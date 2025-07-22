#!/usr/bin/env python3
"""
Multi-Node Starter Script

This script helps start multiple blockchain nodes for testing the quantum annealing consensus.
It automatically configures ports and starts nodes in the background.

Usage:
    python start_nodes.py --nod        print("📝 Next Steps:")
        print("1. Wait ~30 seconds for nodes to initialize")
        print("2. Nodes will be automatically monitored for health")
        print("3. Run the sample transactions:")
        print("   python sample_transactions.py")
        print("4. Run the multi-node test:")
        print(f"   python multi_node_test.py --nodes {self.num_nodes}")
        print("5. View the quantum demo:")
        print("   python quantum_demo.py")
        print("6. Stop nodes with Ctrl+C")
        print("\n🔍 Health monitoring will start in 30 seconds...")
        
        return True  # Successfully started all nodesthon start_nodes.py --nodes 3 --base-port 8000
"""

import os
import sys
import time
import signal
import argparse
import subprocess
import socket
import requests
from pathlib import Path
from datetime import datetime


class NodeStarter:
    """Helper class to start and manage multiple blockchain nodes"""
    
    def __init__(self, num_nodes: int = 3, base_node_port: int = 10000, base_api_port: int = 11000):
        self.num_nodes = num_nodes
        self.base_node_port = base_node_port
        self.base_api_port = base_api_port
        self.processes = []
        self.port_allocations = []  # Will store actual allocated ports
        self.node_health_status = []  # Track health status of each node
        self.last_health_check = None
        self.health_check_interval = 30  # Check every 30 seconds
    
    def check_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.bind(('localhost', port))
                return True  # Port is available if bind succeeds
        except OSError:
            return False  # Port is in use if bind fails
    
    def find_next_available_port(self, start_port: int, max_attempts: int = 100) -> int:
        """Find the next available port starting from start_port"""
        for port in range(start_port, start_port + max_attempts):
            if self.check_port_available(port):
                return port
        raise Exception(f"No available port found in range {start_port}-{start_port + max_attempts}")
    
    def check_node_health(self, node_id: int) -> dict:
        """Check if a specific node is healthy by testing its API endpoint"""
        if node_id >= len(self.port_allocations):
            return {"status": "unknown", "error": "Node ID out of range"}
        
        _, api_port = self.port_allocations[node_id]
        
        try:
            # Check if process is still running
            if node_id < len(self.processes):
                process = self.processes[node_id]
                if process.poll() is not None:
                    return {"status": "dead", "error": f"Process exited with code {process.returncode}"}
            
            # Check if API endpoint is responding
            response = requests.get(
                f"http://localhost:{api_port}/ping/",
                timeout=5
            )
            
            if response.status_code == 200:
                return {"status": "healthy", "response_time": response.elapsed.total_seconds()}
            else:
                return {"status": "unhealthy", "error": f"API returned status {response.status_code}"}
                
        except requests.exceptions.ConnectionError:
            return {"status": "unreachable", "error": "Connection refused"}
        except requests.exceptions.Timeout:
            return {"status": "timeout", "error": "Request timed out"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def perform_health_check(self) -> bool:
        """Perform health check on all nodes and alert if any issues found"""
        current_time = datetime.now()
        alerts = []
        healthy_count = 0
        
        for i in range(self.num_nodes):
            health = self.check_node_health(i)
            
            # Store current health status
            if i >= len(self.node_health_status):
                self.node_health_status.append(health)
            else:
                previous_status = self.node_health_status[i].get("status", "unknown")
                self.node_health_status[i] = health
                
                # Alert if status changed from healthy to unhealthy
                if previous_status == "healthy" and health["status"] != "healthy":
                    _, api_port = self.port_allocations[i]
                    alerts.append(f"🚨 Node {i} (API:{api_port}) went DOWN: {health.get('error', 'Unknown error')}")
                elif previous_status != "healthy" and health["status"] == "healthy":
                    _, api_port = self.port_allocations[i]
                    alerts.append(f"✅ Node {i} (API:{api_port}) is back UP")
            
            if health["status"] == "healthy":
                healthy_count += 1
        
        # Print alerts if any
        if alerts:
            print(f"\n⚠️  HEALTH CHECK ALERT [{current_time.strftime('%H:%M:%S')}]")
            print("=" * 60)
            for alert in alerts:
                print(f"  {alert}")
            print("=" * 60)
        
        # Print periodic status summary
        if self.last_health_check is None or (current_time - self.last_health_check).seconds >= 300:  # Every 5 minutes
            print(f"\n💊 Health Check Summary [{current_time.strftime('%H:%M:%S')}]")
            print(f"   Healthy Nodes: {healthy_count}/{self.num_nodes}")
            
            for i, health in enumerate(self.node_health_status):
                _, api_port = self.port_allocations[i]
                status = health["status"]
                if status == "healthy":
                    print(f"   Node {i} (API:{api_port}): ✅ {status}")
                else:
                    print(f"   Node {i} (API:{api_port}): ❌ {status} - {health.get('error', '')}")
            
            self.last_health_check = current_time
        
        return healthy_count > 0  # Return True if at least one node is healthy
    
    def check_and_allocate_ports(self):
        """Check ports and allocate available ones, skipping conflicts"""
        port_allocations = []
        
        for i in range(self.num_nodes):
            preferred_node_port = self.base_node_port + i
            preferred_api_port = self.base_api_port + i
            
            # Find available P2P port
            if self.check_port_available(preferred_node_port):
                actual_node_port = preferred_node_port
            else:
                print(f"⚠️  Node {i} preferred P2P port {preferred_node_port} is busy, finding alternative...")
                actual_node_port = self.find_next_available_port(preferred_node_port + 1)
                print(f"   Using P2P port {actual_node_port} instead")
            
            # Find available API port
            if self.check_port_available(preferred_api_port):
                actual_api_port = preferred_api_port
            else:
                print(f"⚠️  Node {i} preferred API port {preferred_api_port} is busy, finding alternative...")
                actual_api_port = self.find_next_available_port(preferred_api_port + 1)
                print(f"   Using API port {actual_api_port} instead")
            
            port_allocations.append((actual_node_port, actual_api_port))
        
        return port_allocations
        
    def start_nodes(self):
        """Start all blockchain nodes"""
        print(f"🚀 Starting {self.num_nodes} blockchain nodes...")
        print("=" * 60)
        
        # Check and allocate ports
        print("🔍 Checking port availability and allocating ports...")
        try:
            port_allocations = self.check_and_allocate_ports()
            print("✅ All ports allocated successfully")
        except Exception as e:
            print(f"❌ Failed to allocate ports: {e}")
            return False
        print()
        
        for i in range(self.num_nodes):
            node_port, api_port = port_allocations[i]
            
            # Prepare command
            cmd = [
                sys.executable, "run_node.py",
                "--ip", "localhost",
                "--node_port", str(node_port),
                "--api_port", str(api_port)
            ]
            
            # Add key file for node 0 (genesis node)
            if i == 0:
                key_file = "./keys/genesis_private_key.pem"
                if os.path.exists(key_file):
                    cmd.extend(["--key_file", key_file])
            
            print(f"Starting Node {i}:")
            print(f"  Command: {' '.join(cmd)}")
            print(f"  Node Port: {node_port}")
            print(f"  API Port: {api_port}")
            print(f"  API URL: http://localhost:{api_port}/api/v1/blockchain/")
            
            try:
                # Start node process
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.processes.append(process)
                print(f"  ✅ Node {i} started (PID: {process.pid})")
                
            except Exception as e:
                print(f"  ❌ Failed to start Node {i}: {e}")
            
            print()
            
            # Increase delay for larger networks to avoid resource conflicts
            if self.num_nodes > 10:
                delay = min(5, 2 + (i // 10))  # 2-5 second delay for large networks
            else:
                delay = 2  # Standard 2 second delay
            
            if i < self.num_nodes - 1:  # Don't delay after the last node
                print(f"⏳ Waiting {delay}s before starting next node...")
                time.sleep(delay)
        
        # Additional wait for large networks
        if self.num_nodes > 10:
            print(f"⏳ Large network detected ({self.num_nodes} nodes), waiting extra 5s for stabilization...")
            time.sleep(5)
        
        # Store port allocations for later reference
        self.port_allocations = port_allocations
        
        # Initialize health status tracking
        self.node_health_status = [{"status": "starting"} for _ in range(self.num_nodes)]
        
        print("🎯 All nodes started!")
        print("\nNode Status:")
        print("-" * 40)
        for i, process in enumerate(self.processes):
            if process.poll() is None:
                node_port, api_port = port_allocations[i]
                print(f"  Node {i}: Running (PID: {process.pid}) - P2P:{node_port}, API:{api_port}")
            else:
                print(f"  Node {i}: Stopped")
        
        print("\nAPI Endpoints:")
        print("-" * 40)
        for i in range(self.num_nodes):
            _, api_port = port_allocations[i]
            print(f"  Node {i}: http://localhost:{api_port}/api/v1/blockchain/")
            print(f"  Quantum Metrics: http://localhost:{api_port}/api/v1/blockchain/quantum-metrics/")
        
        print("\n📝 Next Steps:")
        print("1. Wait ~30 seconds for nodes to initialize")
        print("2. Run the sample transactions:")
        print("   python sample_transactions.py")
        print("3. Run the multi-node test:")
        print(f"   python multi_node_test.py --nodes {self.num_nodes}")
        print("4. View the quantum demo:")
        print("   python quantum_demo.py")
        print("5. Stop nodes with Ctrl+C")
        
        return True  # Successfully started all nodes
    
    def stop_nodes(self):
        """Stop all running nodes"""
        print("\n🛑 Stopping all nodes...")
        
        for i, process in enumerate(self.processes):
            if process.poll() is None:
                print(f"  Stopping Node {i} (PID: {process.pid})...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=5)
                    print(f"  ✅ Node {i} stopped gracefully")
                except subprocess.TimeoutExpired:
                    print(f"  ⚠️  Force killing Node {i}...")
                    process.kill()
                    process.wait()
                    print(f"  ✅ Node {i} force stopped")
            else:
                print(f"  Node {i} already stopped")
        
        print("🔴 All nodes stopped")
    
    def wait_for_interrupt(self):
        """Wait for Ctrl+C to stop nodes while monitoring their health"""
        try:
            print("\n⏳ Nodes are running... Press Ctrl+C to stop all nodes")
            
            # Wait for initial startup
            print("⏳ Waiting 30 seconds for nodes to fully initialize...")
            time.sleep(30)
            
            # Perform initial health check
            print("\n🔍 Performing initial health check...")
            self.perform_health_check()
            
            last_check_time = time.time()
            
            while True:
                time.sleep(1)
                current_time = time.time()
                
                # Perform periodic health checks
                if current_time - last_check_time >= self.health_check_interval:
                    self.perform_health_check()
                    last_check_time = current_time
                
                # Check if any process died (legacy check for immediate notification)
                dead_processes = [i for i, p in enumerate(self.processes) if p.poll() is not None]
                if dead_processes:
                    print(f"\n⚠️  Warning: Node(s) {dead_processes} have stopped unexpectedly")
                    for i in dead_processes:
                        stdout, stderr = self.processes[i].communicate()
                        print(f"\n🔍 Node {i} Debug Info:")
                        print(f"  Exit Code: {self.processes[i].returncode}")
                        if hasattr(self, 'port_allocations') and i < len(self.port_allocations):
                            node_port, api_port = self.port_allocations[i]
                            print(f"  P2P Port: {node_port}")
                            print(f"  API Port: {api_port}")
                        else:
                            print(f"  P2P Port: {self.base_node_port + i} (intended)")
                            print(f"  API Port: {self.base_api_port + i} (intended)")
                        if stdout:
                            print(f"  STDOUT: {stdout[:500]}...")
                        if stderr:
                            print(f"  STDERR: {stderr[:500]}...")
                        print("  " + "="*50)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Interrupt received...")
            self.stop_nodes()


def check_requirements():
    """Check if required files exist"""
    required_files = [
        "run_node.py",
        "blockchain/",
        "keys/"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files/directories:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        print("\nPlease ensure you're running from the blockchain directory")
        return False
    
    return True


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Start multiple blockchain nodes for testing")
    parser.add_argument("--nodes", type=int, default=3, help="Number of nodes to start (default: 3)")
    parser.add_argument("--base-node-port", type=int, default=10000, help="Base port for P2P communication (default: 10000)")
    parser.add_argument("--base-api-port", type=int, default=11000, help="Base port for API endpoints (default: 11000)")
    parser.add_argument("--no-wait", action="store_true", help="Don't wait for interrupt, just start and exit")
    parser.add_argument("--health-interval", type=int, default=30, help="Health check interval in seconds (default: 30)")
    
    args = parser.parse_args()
    
    print("🌟 QUANTUM ANNEALING MULTI-NODE STARTER")
    print("=" * 50)
    print(f"Starting {args.nodes} nodes")
    print(f"P2P ports: {args.base_node_port}-{args.base_node_port + args.nodes - 1}")
    print(f"API ports: {args.base_api_port}-{args.base_api_port + args.nodes - 1}")
    print()
    
    # Check requirements
    if not check_requirements():
        return 1
    
    # Create node starter
    starter = NodeStarter(args.nodes, args.base_node_port, args.base_api_port)
    
    # Set health check interval if specified
    if hasattr(args, 'health_interval'):
        starter.health_check_interval = args.health_interval
    
    # Set up signal handler for clean shutdown
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}")
        starter.stop_nodes()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start nodes
        if not starter.start_nodes():
            print("❌ Failed to start nodes due to port conflicts")
            return 1
        
        if not args.no_wait:
            # Wait for interrupt
            starter.wait_for_interrupt()
        else:
            print("\n✅ Nodes started. Use 'pkill -f run_node.py' to stop them later.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        starter.stop_nodes()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
