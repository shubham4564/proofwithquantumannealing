#!/usr/bin/env python3
"""
Launch 50 Blockchain Nodes for Large Scale Testing

This script launches 50 blockchain nodes for comprehensive testing of the quantum annealing
consensus mechanism with a large number of nodes.
"""

import subprocess
import time
import os
import signal
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

class NodeLauncher:
    def __init__(self, num_nodes=50, base_node_port=8000, base_api_port=8050):
        self.num_nodes = num_nodes
        self.base_node_port = base_node_port
        self.base_api_port = base_api_port
        self.processes = []
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n🛑 Shutting down all nodes...")
        self.stop_all_nodes()
        sys.exit(0)
    
    def launch_single_node(self, node_id):
        """Launch a single node"""
        node_port = self.base_node_port + node_id
        api_port = self.base_api_port + node_id
        
        try:
            # Launch node process
            process = subprocess.Popen([
                'python', 'run_node.py',
                '--ip', 'localhost',
                '--node_port', str(node_port),
                '--api_port', str(api_port)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return {
                'node_id': node_id,
                'node_port': node_port,
                'api_port': api_port,
                'process': process,
                'status': 'launched'
            }
        except Exception as e:
            return {
                'node_id': node_id,
                'node_port': node_port,
                'api_port': api_port,
                'process': None,
                'status': f'error: {e}'
            }
    
    def launch_all_nodes(self):
        """Launch all nodes with parallel execution"""
        print(f"🚀 Launching {self.num_nodes} blockchain nodes...")
        print("📊 Node allocation:")
        print(f"   Node ports: {self.base_node_port} - {self.base_node_port + self.num_nodes - 1}")
        print(f"   API ports:  {self.base_api_port} - {self.base_api_port + self.num_nodes - 1}")
        print()
        
        launched_count = 0
        failed_count = 0
        
        # Launch nodes in batches to avoid overwhelming the system
        batch_size = 10
        for batch_start in range(0, self.num_nodes, batch_size):
            batch_end = min(batch_start + batch_size, self.num_nodes)
            batch_nodes = range(batch_start, batch_end)
            
            print(f"🔄 Launching batch {batch_start//batch_size + 1}: nodes {batch_start}-{batch_end-1}")
            
            # Launch batch in parallel
            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                future_to_node = {
                    executor.submit(self.launch_single_node, node_id): node_id 
                    for node_id in batch_nodes
                }
                
                for future in as_completed(future_to_node):
                    result = future.result()
                    if result['status'] == 'launched':
                        self.processes.append(result)
                        launched_count += 1
                        print(f"   ✅ Node {result['node_id']} (ports {result['node_port']}/{result['api_port']})")
                    else:
                        failed_count += 1
                        print(f"   ❌ Node {result['node_id']}: {result['status']}")
            
            # Brief pause between batches
            if batch_end < self.num_nodes:
                print(f"   ⏱️  Waiting 2s before next batch...")
                time.sleep(2)
        
        print(f"\n📊 Launch Summary:")
        print(f"   ✅ Successfully launched: {launched_count} nodes")
        print(f"   ❌ Failed to launch: {failed_count} nodes")
        print(f"   🎯 Total running: {len(self.processes)} nodes")
        
        if launched_count > 0:
            print(f"\n⏱️  Allowing 10 seconds for nodes to initialize and discover each other...")
            time.sleep(10)
            print("✅ Nodes should be ready for testing!")
        
        return len(self.processes)
    
    def check_running_nodes(self):
        """Check which nodes are still running"""
        running_count = 0
        for node_info in self.processes:
            if node_info['process'] and node_info['process'].poll() is None:
                running_count += 1
        return running_count
    
    def stop_all_nodes(self):
        """Stop all launched nodes"""
        print("🛑 Stopping all nodes...")
        stopped_count = 0
        
        for node_info in self.processes:
            if node_info['process'] and node_info['process'].poll() is None:
                try:
                    node_info['process'].terminate()
                    stopped_count += 1
                except:
                    pass
        
        # Wait a moment for graceful shutdown
        time.sleep(2)
        
        # Force kill any remaining processes
        for node_info in self.processes:
            if node_info['process'] and node_info['process'].poll() is None:
                try:
                    node_info['process'].kill()
                except:
                    pass
        
        print(f"✅ Stopped {stopped_count} nodes")
        self.processes.clear()
    
    def monitor_nodes(self):
        """Monitor node status"""
        print("📊 Monitoring nodes (Press Ctrl+C to stop)...")
        try:
            while True:
                running = self.check_running_nodes()
                print(f"🔄 {running}/{len(self.processes)} nodes running")
                time.sleep(30)
        except KeyboardInterrupt:
            self.stop_all_nodes()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Launch 50 Blockchain Nodes")
    parser.add_argument("--nodes", type=int, default=50, help="Number of nodes to launch")
    parser.add_argument("--base-node-port", type=int, default=8000, help="Base node port")
    parser.add_argument("--base-api-port", type=int, default=8050, help="Base API port")
    parser.add_argument("--monitor", action="store_true", help="Monitor nodes after launch")
    
    args = parser.parse_args()
    
    launcher = NodeLauncher(
        num_nodes=args.nodes,
        base_node_port=args.base_node_port,
        base_api_port=args.base_api_port
    )
    
    # Launch nodes
    launched_count = launcher.launch_all_nodes()
    
    if launched_count > 0:
        if args.monitor:
            launcher.monitor_nodes()
        else:
            print("✅ All nodes launched successfully!")
            print("💡 Run with --monitor to keep monitoring, or use monitoring_dashboard.py")
            print("🛑 Press Ctrl+C to stop all nodes when done testing")
            
            try:
                while True:
                    time.sleep(60)
                    running = launcher.check_running_nodes()
                    if running == 0:
                        print("⚠️  All nodes have stopped")
                        break
            except KeyboardInterrupt:
                launcher.stop_all_nodes()
    else:
        print("❌ No nodes were launched successfully")


if __name__ == "__main__":
    main()
