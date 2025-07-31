#!/usr/bin/env python3
"""
Blockchain Network Health Checker
================================

This tool validates the health and synchronization of your blockchain network,
whether running on a single computer or distributed across multiple computers.

Usage:
    python network_health_checker.py --mode single
    python network_health_checker.py --mode distributed --subnet 192.168.1
"""

import argparse
import requests
import json
import time
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass
import concurrent.futures
from threading import Timer

@dataclass
class NodeInfo:
    computer_id: int
    ip: str
    api_port: int
    p2p_port: int
    status: str = "unknown"
    blockchain_height: int = 0
    peer_count: int = 0
    last_block_time: float = 0
    response_time_ms: float = 0
    genesis_hash: str = ""
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class NetworkHealthChecker:
    def __init__(self, mode: str, subnet_prefix: str = None):
        self.mode = mode
        self.subnet_prefix = subnet_prefix
        self.nodes = []
        self.consensus_threshold = 0.67  # 67% of nodes must agree
        
        # Configure nodes based on mode
        if mode == "single":
            self._setup_single_computer_nodes()
        elif mode == "distributed":
            if not subnet_prefix:
                raise ValueError("Distributed mode requires subnet prefix")
            self._setup_distributed_nodes()
        else:
            raise ValueError("Mode must be 'single' or 'distributed'")
    
    def _setup_single_computer_nodes(self):
        """Setup nodes for single computer configuration"""
        for i in range(6):
            node = NodeInfo(
                computer_id=i + 1,
                ip="127.0.0.1",
                api_port=11000 + i,
                p2p_port=10000 + i
            )
            self.nodes.append(node)
    
    def _setup_distributed_nodes(self):
        """Setup nodes for distributed configuration"""
        for i in range(6):
            node = NodeInfo(
                computer_id=i + 1,
                ip=f"{self.subnet_prefix}.{i + 1}",
                api_port=11000 + i,
                p2p_port=10000 + i
            )
            self.nodes.append(node)
    
    def check_node_health(self, node: NodeInfo, timeout: float = 5.0) -> NodeInfo:
        """Check health of a single node"""
        start_time = time.time()
        
        try:
            # Test API connectivity
            response = requests.get(
                f"http://{node.ip}:{node.api_port}/api/v1/blockchain/",
                timeout=timeout
            )
            
            node.response_time_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract blockchain information
                blocks = data.get('blocks', [])
                node.blockchain_height = len(blocks)
                
                if blocks:
                    node.genesis_hash = blocks[0].get('hash', '')[:16]
                    if len(blocks) > 1:
                        node.last_block_time = blocks[-1].get('timestamp', 0)
                
                node.status = "healthy"
                
                # Try to get network status for peer count
                try:
                    network_response = requests.get(
                        f"http://{node.ip}:{node.api_port}/api/v1/blockchain/network-status/",
                        timeout=2.0
                    )
                    if network_response.status_code == 200:
                        network_data = network_response.json()
                        node.peer_count = network_data.get('connected_peers', 0)
                except:
                    pass  # Network status is optional
                
            else:
                node.status = "api_error"
                node.errors.append(f"API returned status {response.status_code}")
        
        except requests.exceptions.ConnectRefused:
            node.status = "offline"
            node.errors.append("Connection refused - node may not be running")
        except requests.exceptions.Timeout:
            node.status = "timeout"
            node.errors.append(f"Request timed out after {timeout}s")
        except Exception as e:
            node.status = "error"
            node.errors.append(str(e))
        
        return node
    
    def check_all_nodes(self, parallel: bool = True) -> List[NodeInfo]:
        """Check health of all nodes"""
        print(f"🔍 Checking health of {len(self.nodes)} nodes...")
        
        if parallel:
            # Check nodes in parallel for faster results
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                future_to_node = {
                    executor.submit(self.check_node_health, node): node 
                    for node in self.nodes
                }
                
                results = []
                for future in concurrent.futures.as_completed(future_to_node):
                    node = future.result()
                    results.append(node)
                
                # Sort results by computer_id to maintain order
                results.sort(key=lambda x: x.computer_id)
                self.nodes = results
        else:
            # Check nodes sequentially
            for i, node in enumerate(self.nodes):
                self.nodes[i] = self.check_node_health(node)
        
        return self.nodes
    
    def analyze_network_consensus(self) -> Dict:
        """Analyze network consensus and synchronization"""
        healthy_nodes = [n for n in self.nodes if n.status == "healthy"]
        
        if not healthy_nodes:
            return {
                "status": "critical",
                "message": "No healthy nodes found",
                "consensus_possible": False
            }
        
        # Check genesis hash consensus
        genesis_hashes = [n.genesis_hash for n in healthy_nodes if n.genesis_hash]
        genesis_consensus = len(set(genesis_hashes)) <= 1 if genesis_hashes else False
        
        # Check blockchain height consensus
        heights = [n.blockchain_height for n in healthy_nodes]
        max_height = max(heights) if heights else 0
        min_height = min(heights) if heights else 0
        height_variance = max_height - min_height
        
        # Determine consensus status
        healthy_ratio = len(healthy_nodes) / len(self.nodes)
        consensus_possible = healthy_ratio >= self.consensus_threshold
        
        if height_variance == 0 and genesis_consensus:
            sync_status = "synchronized"
        elif height_variance <= 2:
            sync_status = "mostly_synchronized"
        else:
            sync_status = "out_of_sync"
        
        return {
            "status": "healthy" if consensus_possible and sync_status == "synchronized" else "degraded",
            "healthy_nodes": len(healthy_nodes),
            "total_nodes": len(self.nodes),
            "healthy_percentage": healthy_ratio * 100,
            "consensus_possible": consensus_possible,
            "genesis_consensus": genesis_consensus,
            "blockchain_heights": {
                "min": min_height,
                "max": max_height,
                "variance": height_variance
            },
            "sync_status": sync_status
        }
    
    def print_detailed_report(self):
        """Print detailed health report"""
        print("\n" + "="*80)
        print("🌐 BLOCKCHAIN NETWORK HEALTH REPORT")
        print("="*80)
        
        # Network overview
        consensus = self.analyze_network_consensus()
        
        status_emoji = {
            "healthy": "🟢",
            "degraded": "🟡", 
            "critical": "🔴"
        }
        
        print(f"\n📊 Network Overview:")
        print(f"   Status: {status_emoji.get(consensus['status'], '⚪')} {consensus['status'].upper()}")
        print(f"   Healthy Nodes: {consensus['healthy_nodes']}/{consensus['total_nodes']} ({consensus['healthy_percentage']:.1f}%)")
        print(f"   Consensus Possible: {'✅' if consensus['consensus_possible'] else '❌'}")
        print(f"   Genesis Consensus: {'✅' if consensus['genesis_consensus'] else '❌'}")
        print(f"   Sync Status: {consensus['sync_status'].replace('_', ' ').title()}")
        
        if consensus['blockchain_heights']['variance'] > 0:
            print(f"   Height Variance: {consensus['blockchain_heights']['variance']} blocks")
            print(f"   Height Range: {consensus['blockchain_heights']['min']} - {consensus['blockchain_heights']['max']}")
        
        # Individual node status
        print(f"\n🖥️ Individual Node Status:")
        print(f"{'ID':<3} {'IP':<15} {'API':<5} {'Status':<12} {'Height':<7} {'Peers':<6} {'Response':<8} {'Errors'}")
        print("-" * 80)
        
        for node in self.nodes:
            status_emoji = {
                "healthy": "🟢",
                "offline": "🔴",
                "timeout": "🟡",
                "error": "❌",
                "api_error": "⚠️",
                "unknown": "⚪"
            }
            
            error_summary = ", ".join(node.errors[:2]) if node.errors else ""
            if len(error_summary) > 25:
                error_summary = error_summary[:22] + "..."
            
            print(f"{node.computer_id:<3} {node.ip:<15} {node.api_port:<5} "
                  f"{status_emoji.get(node.status, '⚪')} {node.status:<10} "
                  f"{node.blockchain_height:<7} {node.peer_count:<6} "
                  f"{node.response_time_ms:<7.0f}ms {error_summary}")
        
        # Network connectivity analysis
        print(f"\n🔗 Network Connectivity:")
        online_nodes = [n for n in self.nodes if n.status == "healthy"]
        
        if len(online_nodes) >= 2:
            total_possible_connections = len(online_nodes) * (len(online_nodes) - 1)
            actual_connections = sum(n.peer_count for n in online_nodes)
            connectivity_ratio = actual_connections / total_possible_connections if total_possible_connections > 0 else 0
            
            print(f"   Online Nodes: {len(online_nodes)}")
            print(f"   Total P2P Connections: {actual_connections}")
            print(f"   Connectivity Ratio: {connectivity_ratio:.2f}")
            
            if connectivity_ratio > 0.5:
                print("   Network Density: 🟢 Well Connected")
            elif connectivity_ratio > 0.2:
                print("   Network Density: 🟡 Moderately Connected")
            else:
                print("   Network Density: 🔴 Poorly Connected")
        else:
            print("   ❌ Insufficient nodes online for connectivity analysis")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        
        offline_nodes = [n for n in self.nodes if n.status in ["offline", "error", "timeout"]]
        if offline_nodes:
            print(f"   • Restart {len(offline_nodes)} offline nodes:")
            for node in offline_nodes:
                print(f"     - Node {node.computer_id} ({node.ip}:{node.api_port})")
        
        if consensus['blockchain_heights']['variance'] > 2:
            print("   • Blockchain synchronization issues detected")
            print("     - Allow more time for sync or restart nodes in sequence")
        
        if not consensus['genesis_consensus']:
            print("   • Genesis block mismatch detected")
            print("     - Ensure all nodes use the same genesis configuration")
        
        if consensus['healthy_percentage'] < 67:
            print("   • Network consensus at risk")
            print("     - Bring more nodes online to ensure byzantine fault tolerance")
        
        # Performance metrics
        healthy_response_times = [n.response_time_ms for n in self.nodes if n.status == "healthy"]
        if healthy_response_times:
            avg_response = sum(healthy_response_times) / len(healthy_response_times)
            max_response = max(healthy_response_times)
            
            print(f"\n⚡ Performance Metrics:")
            print(f"   Average Response Time: {avg_response:.1f}ms")
            print(f"   Maximum Response Time: {max_response:.1f}ms")
            
            if avg_response < 100:
                print("   Performance: 🟢 Excellent")
            elif avg_response < 500:
                print("   Performance: 🟡 Good")
            else:
                print("   Performance: 🔴 Needs Improvement")
    
    def print_summary(self):
        """Print brief network summary"""
        consensus = self.analyze_network_consensus()
        healthy_count = consensus['healthy_nodes']
        total_count = consensus['total_nodes']
        
        status_emoji = {
            "healthy": "🟢",
            "degraded": "🟡",
            "critical": "🔴"
        }
        
        print(f"\n{status_emoji.get(consensus['status'], '⚪')} Network Status: {consensus['status'].upper()}")
        print(f"📊 Nodes: {healthy_count}/{total_count} healthy ({consensus['healthy_percentage']:.1f}%)")
        print(f"🔗 Consensus: {'Possible' if consensus['consensus_possible'] else 'At Risk'}")
        print(f"📈 Sync: {consensus['sync_status'].replace('_', ' ').title()}")
    
    def monitor_network(self, interval: int = 30, duration: int = 0):
        """Monitor network health continuously"""
        print(f"🔄 Starting network monitoring (checking every {interval}s)")
        if duration > 0:
            print(f"⏱️ Monitoring for {duration} seconds")
        else:
            print("♾️ Monitoring indefinitely (Ctrl+C to stop)")
        
        start_time = time.time()
        check_count = 0
        
        def stop_monitoring():
            print("\n⏰ Monitoring duration completed")
            sys.exit(0)
        
        if duration > 0:
            timer = Timer(duration, stop_monitoring)
            timer.start()
        
        try:
            while True:
                check_count += 1
                elapsed = time.time() - start_time
                
                print(f"\n🔍 Health Check #{check_count} (elapsed: {elapsed:.0f}s)")
                print("-" * 50)
                
                self.check_all_nodes()
                self.print_summary()
                
                # Brief node status
                for node in self.nodes:
                    if node.status != "healthy":
                        print(f"⚠️ Node {node.computer_id} ({node.ip}): {node.status}")
                
                if check_count == 1:
                    print(f"\n💡 Use Ctrl+C to stop monitoring")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            if duration == 0:
                print("\n🛑 Monitoring stopped by user")
                sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description="Check blockchain network health and synchronization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check single computer network
  python network_health_checker.py --mode single
  
  # Check distributed network
  python network_health_checker.py --mode distributed --subnet 192.168.1
  
  # Monitor network continuously
  python network_health_checker.py --mode single --monitor --interval 30
  
  # Detailed report
  python network_health_checker.py --mode distributed --subnet 192.168.1 --detailed
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['single', 'distributed'],
        required=True,
        help='Network deployment mode'
    )
    
    parser.add_argument(
        '--subnet',
        type=str,
        help='Subnet prefix for distributed mode (e.g., 192.168.1)'
    )
    
    parser.add_argument(
        '--monitor',
        action='store_true',
        help='Continuously monitor network health'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Monitoring interval in seconds (default: 30)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=0,
        help='Monitoring duration in seconds (0 = infinite)'
    )
    
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed report'
    )
    
    parser.add_argument(
        '--timeout',
        type=float,
        default=5.0,
        help='Request timeout in seconds (default: 5.0)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.mode == 'distributed' and not args.subnet:
        parser.error("Distributed mode requires --subnet argument")
    
    try:
        # Create health checker
        checker = NetworkHealthChecker(args.mode, args.subnet)
        
        if args.monitor:
            # Start monitoring mode
            checker.monitor_network(args.interval, args.duration)
        else:
            # Single check mode
            print(f"🔍 Checking {args.mode} network health...")
            
            checker.check_all_nodes()
            
            if args.detailed:
                checker.print_detailed_report()
            else:
                checker.print_summary()
            
            # Exit with appropriate code
            consensus = checker.analyze_network_consensus()
            exit_code = 0 if consensus['status'] == 'healthy' else 1
            sys.exit(exit_code)
    
    except KeyboardInterrupt:
        print("\n🛑 Health check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
