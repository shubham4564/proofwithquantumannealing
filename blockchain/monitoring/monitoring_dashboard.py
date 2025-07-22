#!/usr/bin/env python3
"""
Real-time Blockchain Monitoring Dashboard

This script provides a comprehensive real-time dashboard for monitoring
all aspects of the quantum annealing blockchain including:
- Node status and health
- Transaction performance metrics
- Quantum consensus metrics
- Network synchronization
- Historical performance trends

Usage:
    python monitoring_dashboard.py
    python monitoring_dashboard.py --interval 5 --nodes 3
    python monitoring_dashboard.py --save-logs --log-dir ./monitoring_logs
"""

import json
import time
import requests
import argparse
import os
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import threading
import signal
import sys


@dataclass
class NodeMetrics:
    """Metrics for a single node"""
    node_id: str
    port: int
    api_port: int
    status: str  # 'online', 'offline', 'error'
    block_count: int
    active_nodes: int
    probe_count: int
    response_time: float
    last_updated: datetime


@dataclass
class NetworkMetrics:
    """Network-wide metrics"""
    timestamp: datetime
    total_nodes: int
    online_nodes: int
    avg_response_time: float
    sync_difference: int
    total_probes: int
    consensus_health: str  # 'excellent', 'good', 'poor'


@dataclass
class PerformanceSnapshot:
    """Performance metrics snapshot"""
    timestamp: datetime
    transaction_success_rate: float
    avg_transaction_time: float
    network_tps: float
    quantum_consensus_score: float


class BlockchainMonitor:
    """Real-time blockchain monitoring system"""
    
    def __init__(self, num_nodes: int = 3, base_api_port: int = 8050):
        self.num_nodes = num_nodes
        self.base_api_port = base_api_port
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Data storage
        self.node_metrics: Dict[int, NodeMetrics] = {}
        self.network_history: List[NetworkMetrics] = []
        self.performance_history: List[PerformanceSnapshot] = []
        
        # Configuration
        self.max_history = 100  # Keep last 100 data points
        self.update_interval = 5  # seconds
        
        # Logging
        self.save_logs = False
        self.log_dir = "./monitoring_logs"
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n🛑 Shutting down monitoring dashboard...")
        self.stop_monitoring()
        sys.exit(0)
    
    def collect_node_metrics(self, node_id: int) -> Optional[NodeMetrics]:
        """Collect metrics from a single node"""
        api_port = self.base_api_port + node_id
        node_port = 8000 + node_id
        
        try:
            # Test basic connectivity
            start_time = time.time()
            blockchain_response = requests.get(
                f"http://localhost:{api_port}/api/v1/blockchain/", 
                timeout=3
            )
            response_time = time.time() - start_time
            
            if blockchain_response.status_code == 200:
                blockchain_data = blockchain_response.json()
                block_count = len(blockchain_data.get('blocks', []))
                
                # Get quantum metrics
                quantum_response = requests.get(
                    f"http://localhost:{api_port}/api/v1/blockchain/quantum-metrics/",
                    timeout=3
                )
                
                active_nodes = 0
                probe_count = 0
                
                if quantum_response.status_code == 200:
                    quantum_data = quantum_response.json()
                    active_nodes = quantum_data.get('active_nodes', 0)
                    probe_count = quantum_data.get('probe_count', 0)
                
                return NodeMetrics(
                    node_id=f"node_{node_id}",
                    port=node_port,
                    api_port=api_port,
                    status='online',
                    block_count=block_count,
                    active_nodes=active_nodes,
                    probe_count=probe_count,
                    response_time=response_time,
                    last_updated=datetime.now()
                )
            else:
                return NodeMetrics(
                    node_id=f"node_{node_id}",
                    port=node_port,
                    api_port=api_port,
                    status='error',
                    block_count=0,
                    active_nodes=0,
                    probe_count=0,
                    response_time=999.0,
                    last_updated=datetime.now()
                )
                
        except Exception as e:
            return NodeMetrics(
                node_id=f"node_{node_id}",
                port=node_port,
                api_port=api_port,
                status='offline',
                block_count=0,
                active_nodes=0,
                probe_count=0,
                response_time=999.0,
                last_updated=datetime.now()
            )
    
    def collect_network_metrics(self) -> NetworkMetrics:
        """Collect network-wide metrics"""
        online_nodes = []
        total_nodes = 0
        block_counts = []
        response_times = []
        total_probes = 0
        
        for node_id in range(self.num_nodes):
            total_nodes += 1
            if node_id in self.node_metrics:
                node = self.node_metrics[node_id]
                if node.status == 'online':
                    online_nodes.append(node)
                    block_counts.append(node.block_count)
                    response_times.append(node.response_time)
                    total_probes += node.probe_count
        
        # Calculate sync difference
        sync_difference = max(block_counts) - min(block_counts) if block_counts else 0
        
        # Calculate average response time
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Determine consensus health
        if sync_difference <= 1 and len(online_nodes) >= 2:
            consensus_health = 'excellent'
        elif sync_difference <= 3 and len(online_nodes) >= 2:
            consensus_health = 'good'
        else:
            consensus_health = 'poor'
        
        return NetworkMetrics(
            timestamp=datetime.now(),
            total_nodes=total_nodes,
            online_nodes=len(online_nodes),
            avg_response_time=avg_response_time,
            sync_difference=sync_difference,
            total_probes=total_probes,
            consensus_health=consensus_health
        )
    
    def measure_performance_snapshot(self) -> PerformanceSnapshot:
        """Take a quick performance measurement snapshot"""
        # This is a simplified performance measurement
        # In a real implementation, you might want to run actual transactions
        
        # Estimate based on current network state
        online_nodes = sum(1 for node in self.node_metrics.values() if node.status == 'online')
        
        if online_nodes == 0:
            return PerformanceSnapshot(
                timestamp=datetime.now(),
                transaction_success_rate=0.0,
                avg_transaction_time=999.0,
                network_tps=0.0,
                quantum_consensus_score=0.0
            )
        
        # Estimate performance based on network health
        avg_response = sum(node.response_time for node in self.node_metrics.values() 
                          if node.status == 'online') / online_nodes
        
        # Simplified estimates (in production, you'd measure actual transactions)
        estimated_success_rate = max(0.7, 1.0 - (avg_response * 0.1))  # Decreases with latency
        estimated_transaction_time = max(0.01, avg_response * 2)
        estimated_tps = min(500, max(1, 100 / estimated_transaction_time))
        
        # Quantum consensus score based on probe activity and node count
        total_probes = sum(node.probe_count for node in self.node_metrics.values())
        quantum_score = min(1.0, (total_probes / 100.0) * (online_nodes / self.num_nodes))
        
        return PerformanceSnapshot(
            timestamp=datetime.now(),
            transaction_success_rate=estimated_success_rate,
            avg_transaction_time=estimated_transaction_time,
            network_tps=estimated_tps,
            quantum_consensus_score=quantum_score
        )
    
    def update_metrics(self):
        """Update all metrics"""
        # Collect node metrics
        for node_id in range(self.num_nodes):
            self.node_metrics[node_id] = self.collect_node_metrics(node_id)
        
        # Collect network metrics
        network_metrics = self.collect_network_metrics()
        self.network_history.append(network_metrics)
        
        # Collect performance snapshot
        performance_snapshot = self.measure_performance_snapshot()
        self.performance_history.append(performance_snapshot)
        
        # Trim history
        if len(self.network_history) > self.max_history:
            self.network_history = self.network_history[-self.max_history:]
        if len(self.performance_history) > self.max_history:
            self.performance_history = self.performance_history[-self.max_history:]
    
    def display_dashboard(self):
        """Display the monitoring dashboard"""
        # Clear screen
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🎯 QUANTUM ANNEALING BLOCKCHAIN MONITORING DASHBOARD")
        print("=" * 80)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 🔄 Update interval: {self.update_interval}s")
        print()
        
        # Node Status Section - Optimized for many nodes
        print("🖥️  NODE STATUS")
        print("-" * 50)
        
        online_nodes = []
        offline_nodes = []
        error_nodes = []
        
        for node_id in range(self.num_nodes):
            if node_id in self.node_metrics:
                node = self.node_metrics[node_id]
                if node.status == 'online':
                    online_nodes.append(node)
                elif node.status == 'offline':
                    offline_nodes.append(node)
                else:
                    error_nodes.append(node)
        
        print(f"  📊 Network Status: {len(online_nodes)}/{self.num_nodes} nodes online")
        
        # Show top performing nodes if we have many nodes
        if len(online_nodes) > 10:
            print(f"\n  🏆 TOP 10 PERFORMING NODES (by blocks):")
            top_nodes = sorted(online_nodes, key=lambda x: x.block_count, reverse=True)[:10]
            for i, node in enumerate(top_nodes, 1):
                print(f"    {i:2}. {node.node_id:8} | Port: {node.api_port} | "
                      f"Blocks: {node.block_count:3} | Probes: {node.probe_count:3} | "
                      f"Response: {node.response_time:.3f}s")
            
            print(f"\n  🔍 COMPLETE NODE SUMMARY:")
            block_counts = [node.block_count for node in online_nodes]
            probe_counts = [node.probe_count for node in online_nodes]
            response_times = [node.response_time for node in online_nodes]
            
            print(f"    Blocks - Min: {min(block_counts)}, Max: {max(block_counts)}, Avg: {sum(block_counts)/len(block_counts):.1f}")
            print(f"    Probes - Min: {min(probe_counts)}, Max: {max(probe_counts)}, Avg: {sum(probe_counts)/len(probe_counts):.1f}")
            print(f"    Response - Min: {min(response_times):.3f}s, Max: {max(response_times):.3f}s, Avg: {sum(response_times)/len(response_times):.3f}s")
        else:
            # Show all nodes if we have few nodes
            for node_id in range(self.num_nodes):
                if node_id in self.node_metrics:
                    node = self.node_metrics[node_id]
                    status_emoji = "✅" if node.status == 'online' else "❌" if node.status == 'offline' else "⚠️"
                    
                    if node.status == 'online':
                        print(f"  {status_emoji} {node.node_id:8} | Port: {node.api_port} | "
                              f"Blocks: {node.block_count:3} | Probes: {node.probe_count:3} | "
                              f"Response: {node.response_time:.3f}s")
                    else:
                        print(f"  {status_emoji} {node.node_id:8} | Port: {node.api_port} | Status: {node.status}")
                else:
                    print(f"  ❓ node_{node_id:8} | Port: {self.base_api_port + node_id} | Status: unknown")
        
        if len(error_nodes) > 0:
            print(f"\n  ⚠️  {len(error_nodes)} nodes with errors")
        if len(offline_nodes) > 0:
            print(f"  ❌ {len(offline_nodes)} nodes offline")
        
        print()
        
        # Network Metrics Section
        if self.network_history:
            latest_network = self.network_history[-1]
            print("🌐 NETWORK METRICS")
            print("-" * 50)
            print(f"  Online Nodes: {latest_network.online_nodes}/{latest_network.total_nodes}")
            print(f"  Avg Response Time: {latest_network.avg_response_time:.3f}s")
            print(f"  Sync Difference: {latest_network.sync_difference} blocks")
            print(f"  Total Probes: {latest_network.total_probes}")
            
            health_emoji = "✅" if latest_network.consensus_health == 'excellent' else \
                          "⚠️" if latest_network.consensus_health == 'good' else "❌"
            print(f"  Consensus Health: {health_emoji} {latest_network.consensus_health.title()}")
            print()
        
        # Performance Metrics Section
        if self.performance_history:
            latest_perf = self.performance_history[-1]
            print("🚀 PERFORMANCE METRICS")
            print("-" * 50)
            print(f"  Estimated Success Rate: {latest_perf.transaction_success_rate:.1%}")
            print(f"  Avg Transaction Time: {latest_perf.avg_transaction_time:.3f}s")
            print(f"  Estimated TPS: {latest_perf.network_tps:.1f}")
            print(f"  Quantum Consensus Score: {latest_perf.quantum_consensus_score:.3f}")
            print()
        
        # Historical Trends Section
        if len(self.network_history) >= 2:
            print("📈 TRENDS (Last 10 samples)")
            print("-" * 50)
            
            recent_history = self.network_history[-10:]
            recent_performance = self.performance_history[-10:]
            
            # Response time trend
            response_times = [h.avg_response_time for h in recent_history]
            response_trend = "📈" if response_times[-1] > response_times[0] else "📉"
            print(f"  Response Time {response_trend}: {response_times[0]:.3f}s → {response_times[-1]:.3f}s")
            
            # TPS trend
            if recent_performance:
                tps_values = [p.network_tps for p in recent_performance]
                tps_trend = "📈" if tps_values[-1] > tps_values[0] else "📉"
                print(f"  TPS {tps_trend}: {tps_values[0]:.1f} → {tps_values[-1]:.1f}")
            
            # Sync health trend
            sync_diffs = [h.sync_difference for h in recent_history]
            sync_trend = "📈" if sync_diffs[-1] > sync_diffs[0] else "📉"
            print(f"  Sync Difference {sync_trend}: {sync_diffs[0]} → {sync_diffs[-1]} blocks")
            print()
        
        # Quantum Consensus Details
        print("🔬 QUANTUM CONSENSUS DETAILS")
        print("-" * 50)
        online_nodes_for_quantum = [node for node in self.node_metrics.values() if node.status == 'online']
        
        if len(online_nodes_for_quantum) > 10:
            # Show only top nodes by probe count if we have many nodes
            top_quantum_nodes = sorted(online_nodes_for_quantum, key=lambda x: x.probe_count, reverse=True)[:10]
            print(f"  🏆 TOP 10 NODES BY PROBE ACTIVITY:")
            for i, node in enumerate(top_quantum_nodes, 1):
                print(f"    {i:2}. {node.node_id}: {node.probe_count} probes, {node.active_nodes} active nodes")
            
            # Summary statistics
            total_probes = sum(node.probe_count for node in online_nodes_for_quantum)
            avg_probes = total_probes / len(online_nodes_for_quantum) if online_nodes_for_quantum else 0
            max_probes = max(node.probe_count for node in online_nodes_for_quantum) if online_nodes_for_quantum else 0
            
            print(f"\n  📊 QUANTUM CONSENSUS SUMMARY:")
            print(f"    Total Probes Across Network: {total_probes}")
            print(f"    Average Probes per Node: {avg_probes:.1f}")
            print(f"    Maximum Probes (single node): {max_probes}")
            
            # Find nodes with highest probe activity
            active_proposers = [node for node in online_nodes_for_quantum if node.probe_count > avg_probes]
            print(f"    Active Consensus Participants: {len(active_proposers)} nodes")
        else:
            # Show all nodes if we have few nodes
            for node_id in range(self.num_nodes):
                if node_id in self.node_metrics and self.node_metrics[node_id].status == 'online':
                    node = self.node_metrics[node_id]
                    print(f"  {node.node_id}: {node.probe_count} probes, {node.active_nodes} active nodes")
        print()
        
        # Instructions
        print("⌨️  CONTROLS")
        print("-" * 50)
        print("  Press Ctrl+C to stop monitoring")
        if self.save_logs:
            print(f"  📁 Logs saved to: {self.log_dir}")
        print()
        print("=" * 80)
    
    def save_metrics_to_logs(self):
        """Save metrics to log files"""
        if not self.save_logs:
            return
        
        os.makedirs(self.log_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # Save node metrics
        node_log_file = os.path.join(self.log_dir, f'node_metrics_{timestamp}.csv')
        file_exists = os.path.exists(node_log_file)
        
        with open(node_log_file, 'a', newline='') as csvfile:
            fieldnames = ['timestamp', 'node_id', 'status', 'block_count', 'active_nodes', 
                         'probe_count', 'response_time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            for node in self.node_metrics.values():
                writer.writerow({
                    'timestamp': node.last_updated.isoformat(),
                    'node_id': node.node_id,
                    'status': node.status,
                    'block_count': node.block_count,
                    'active_nodes': node.active_nodes,
                    'probe_count': node.probe_count,
                    'response_time': node.response_time
                })
        
        # Save network metrics
        if self.network_history:
            network_log_file = os.path.join(self.log_dir, f'network_metrics_{timestamp}.csv')
            file_exists = os.path.exists(network_log_file)
            
            with open(network_log_file, 'a', newline='') as csvfile:
                fieldnames = ['timestamp', 'total_nodes', 'online_nodes', 'avg_response_time',
                             'sync_difference', 'total_probes', 'consensus_health']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                # Save only the latest metric to avoid duplicates
                latest = self.network_history[-1]
                writer.writerow({
                    'timestamp': latest.timestamp.isoformat(),
                    'total_nodes': latest.total_nodes,
                    'online_nodes': latest.online_nodes,
                    'avg_response_time': latest.avg_response_time,
                    'sync_difference': latest.sync_difference,
                    'total_probes': latest.total_probes,
                    'consensus_health': latest.consensus_health
                })
    
    def monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                self.update_metrics()
                self.display_dashboard()
                self.save_metrics_to_logs()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(self.update_interval)
    
    def start_monitoring(self, interval: int = 5, save_logs: bool = False, log_dir: str = "./monitoring_logs"):
        """Start the monitoring dashboard"""
        self.update_interval = interval
        self.save_logs = save_logs
        self.log_dir = log_dir
        self.monitoring_active = True
        
        print("🚀 Starting Quantum Annealing Blockchain Monitor...")
        print(f"📊 Monitoring {self.num_nodes} nodes with {interval}s intervals")
        if save_logs:
            print(f"📁 Saving logs to: {log_dir}")
        print("\nPress Ctrl+C to stop monitoring\n")
        
        # Start monitoring in a separate thread
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        # Keep main thread alive
        try:
            while self.monitoring_active:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop the monitoring dashboard"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        print("✅ Monitoring stopped")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Real-time Blockchain Monitoring Dashboard")
    parser.add_argument("--nodes", type=int, default=3, help="Number of nodes to monitor")
    parser.add_argument("--interval", type=int, default=5, help="Update interval in seconds")
    parser.add_argument("--save-logs", action="store_true", help="Save metrics to CSV logs")
    parser.add_argument("--log-dir", default="./monitoring_logs", help="Directory for log files")
    parser.add_argument("--api-port", type=int, default=8050, help="Base API port")
    
    args = parser.parse_args()
    
    # Create and start monitor
    monitor = BlockchainMonitor(num_nodes=args.nodes, base_api_port=args.api_port)
    monitor.start_monitoring(
        interval=args.interval,
        save_logs=args.save_logs,
        log_dir=args.log_dir
    )


if __name__ == "__main__":
    main()
