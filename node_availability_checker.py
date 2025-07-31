#!/usr/bin/env python3
"""
Node Availability Checker for Transaction Processing
===================================================

This script checks the availability and readiness of blockchain nodes for transaction processing.
It provides comprehensive metrics including:
- Node health and API responsiveness  
- Transaction endpoint availability
- Leader schedule status
- Network connectivity
- TPU (Transaction Processing Unit) availability
- Gossip protocol status
- Performance metrics for transaction handling

Usage:
    python node_availability_checker.py
    python node_availability_checker.py --detailed
    python node_availability_checker.py --test-transactions
    python node_availability_checker.py --export-json availability_report.json
"""

import argparse
import requests
import json
import time
import threading
import concurrent.futures
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import socket


@dataclass
class NodeAvailability:
    """Comprehensive node availability information"""
    node_id: int
    api_port: int
    p2p_port: int
    gossip_port: int
    tpu_port: int
    tvu_port: int
    
    # Basic Health
    process_running: bool
    api_responding: bool
    api_response_time: float
    
    # Transaction Capabilities
    transaction_endpoint_available: bool
    transaction_response_time: float
    accepts_transactions: bool
    mempool_size: int
    
    # Leadership & Consensus
    is_current_leader: bool
    is_upcoming_leader: bool
    leader_schedule_available: bool
    quantum_consensus_healthy: bool
    quantum_active_nodes: int
    quantum_total_nodes: int
    
    # Network Status
    gossip_active_peers: int
    p2p_connected_peers: int
    network_latency: float
    
    # Performance Metrics
    blocks_produced: int
    transactions_processed: int
    average_transaction_time: float
    
    # Overall Status
    status: str  # 'available', 'limited', 'degraded', 'offline'
    availability_score: float  # 0-100
    transaction_readiness: str  # 'ready', 'limited', 'not_ready'


class NodeAvailabilityChecker:
    """Comprehensive node availability checker for transaction processing"""
    
    def __init__(self, base_port: int = 11000, max_nodes: int = 20):
        self.base_port = base_port
        self.max_nodes = max_nodes
        self.available_nodes: List[NodeAvailability] = []
        self.unavailable_nodes: List[NodeAvailability] = []
        self.timeout = 3  # seconds for API calls
        
    def calculate_ports(self, node_index: int) -> Tuple[int, int, int, int, int]:
        """Calculate all ports for a node based on index"""
        api_port = self.base_port + node_index
        p2p_port = 10000 + node_index
        gossip_port = 12000 + node_index
        tpu_port = 13000 + node_index
        tvu_port = 14000 + node_index
        return api_port, p2p_port, gossip_port, tpu_port, tvu_port
    
    def check_process_running(self, port: int) -> bool:
        """Check if a process is running on the given port"""
        try:
            result = subprocess.run(['lsof', '-i', f':{port}'], 
                                  capture_output=True, text=True, timeout=5)
            return len(result.stdout.strip()) > 0
        except:
            return False
    
    def check_api_health(self, api_port: int) -> Tuple[bool, float, Dict]:
        """Check API health and get basic blockchain info"""
        try:
            start_time = time.time()
            response = requests.get(f'http://localhost:{api_port}/api/v1/blockchain/', 
                                  timeout=self.timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return True, response_time, response.json()
            else:
                return False, response_time, {}
        except Exception:
            return False, float('inf'), {}
    
    def check_transaction_endpoint(self, api_port: int) -> Tuple[bool, float, bool]:
        """Check transaction creation endpoint availability"""
        try:
            start_time = time.time()
            
            # First check if the endpoint responds (with a simple GET which should fail gracefully)
            response = requests.get(f'http://localhost:{api_port}/api/v1/transaction/create/', 
                                  timeout=self.timeout)
            response_time = time.time() - start_time
            
            # Even if it returns 405 (Method Not Allowed), the endpoint is available
            endpoint_available = response.status_code in [200, 405, 400, 422]
            
            # Check if node accepts transactions (should be true if API is healthy)
            accepts_transactions = response.status_code != 503  # Service Unavailable
            
            return endpoint_available, response_time, accepts_transactions
            
        except Exception:
            return False, float('inf'), False
    
    def get_leader_info(self, api_port: int) -> Tuple[bool, bool, bool]:
        """Get leadership and leader schedule information"""
        try:
            # Check current leader
            response = requests.get(f'http://localhost:{api_port}/api/v1/blockchain/leader/current/', 
                                  timeout=self.timeout)
            
            is_current_leader = False
            if response.status_code == 200:
                data = response.json()
                current_leader = data.get('current_leader', '')
                # If this node responds with leader info, it knows about leadership
                is_current_leader = len(current_leader) > 0
            
            # Check leader schedule availability
            schedule_response = requests.get(f'http://localhost:{api_port}/api/v1/blockchain/leader/schedule/', 
                                           timeout=self.timeout)
            leader_schedule_available = schedule_response.status_code == 200
            
            # For upcoming leader, we'd need to analyze the schedule
            # For now, assume any node with a working schedule could be upcoming
            is_upcoming_leader = leader_schedule_available
            
            return is_current_leader, is_upcoming_leader, leader_schedule_available
            
        except Exception:
            return False, False, False
    
    def get_quantum_metrics(self, api_port: int) -> Tuple[bool, int, int]:
        """Get quantum consensus health metrics"""
        try:
            response = requests.get(f'http://localhost:{api_port}/api/v1/blockchain/quantum-metrics/', 
                                  timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                active_nodes = data.get('active_nodes', 0)
                total_nodes = data.get('total_nodes', 0)
                
                # Consider healthy if more than 50% of expected nodes are active
                is_healthy = active_nodes > 0 and (total_nodes == 0 or active_nodes / total_nodes >= 0.5)
                
                return is_healthy, active_nodes, total_nodes
            else:
                return False, 0, 0
                
        except Exception:
            return False, 0, 0
    
    def get_network_status(self, api_port: int) -> Tuple[int, int, float]:
        """Get network connectivity status"""
        try:
            response = requests.get(f'http://localhost:{api_port}/api/v1/node/status', 
                                  timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract gossip peers
                gossip_peers = 0
                gossip_info = data.get('gossip_protocol', {})
                if isinstance(gossip_info, dict):
                    gossip_peers = gossip_info.get('active_peers', 0)
                
                # Extract P2P peers
                p2p_peers = data.get('connected_peers', 0)
                
                # Estimate network latency based on API response time
                start_time = time.time()
                ping_response = requests.get(f'http://localhost:{api_port}/ping', timeout=1)
                latency = time.time() - start_time if ping_response.status_code == 200 else float('inf')
                
                return gossip_peers, p2p_peers, latency
            else:
                return 0, 0, float('inf')
                
        except Exception:
            return 0, 0, float('inf')
    
    def get_performance_metrics(self, api_port: int, blockchain_data: Dict) -> Tuple[int, int, float]:
        """Extract performance metrics from blockchain data"""
        try:
            blocks = blockchain_data.get('blocks', [])
            blocks_produced = len(blocks)
            
            # Count total transactions
            transactions_processed = 0
            total_tx_time = 0
            tx_count = 0
            
            for block in blocks:
                block_transactions = block.get('transactions', [])
                transactions_processed += len(block_transactions)
                
                # Estimate transaction processing time (simplified)
                block_time = block.get('timestamp', 0)
                if block_time > 0:
                    for tx in block_transactions:
                        tx_count += 1
                        total_tx_time += 1.0  # Placeholder - would need actual timing data
            
            avg_tx_time = total_tx_time / tx_count if tx_count > 0 else 0.0
            
            return blocks_produced, transactions_processed, avg_tx_time
            
        except Exception:
            return 0, 0, 0.0
    
    def calculate_availability_score(self, node: NodeAvailability) -> float:
        """Calculate overall availability score (0-100)"""
        score = 0.0
        
        # Basic health (40 points)
        if node.process_running:
            score += 10
        if node.api_responding:
            score += 15
        if node.api_response_time < 1.0:
            score += 10
        elif node.api_response_time < 3.0:
            score += 5
        
        # Transaction capabilities (30 points)
        if node.transaction_endpoint_available:
            score += 10
        if node.accepts_transactions:
            score += 10
        if node.transaction_response_time < 1.0:
            score += 10
        elif node.transaction_response_time < 3.0:
            score += 5
        
        # Consensus and leadership (20 points)
        if node.quantum_consensus_healthy:
            score += 10
        if node.leader_schedule_available:
            score += 5
        if node.is_current_leader or node.is_upcoming_leader:
            score += 5
        
        # Network connectivity (10 points)
        if node.gossip_active_peers > 0:
            score += 5
        if node.p2p_connected_peers > 0:
            score += 5
        
        return min(score, 100.0)
    
    def determine_transaction_readiness(self, node: NodeAvailability) -> str:
        """Determine if node is ready to handle transactions"""
        if not node.process_running or not node.api_responding:
            return 'not_ready'
        
        if not node.transaction_endpoint_available or not node.accepts_transactions:
            return 'not_ready'
        
        if node.availability_score >= 80:
            return 'ready'
        elif node.availability_score >= 50:
            return 'limited'
        else:
            return 'not_ready'
    
    def check_single_node(self, node_index: int) -> NodeAvailability:
        """Perform comprehensive availability check for a single node"""
        api_port, p2p_port, gossip_port, tpu_port, tvu_port = self.calculate_ports(node_index)
        
        # Basic health checks
        process_running = self.check_process_running(api_port)
        api_responding, api_response_time, blockchain_data = self.check_api_health(api_port)
        
        # Transaction capabilities
        tx_endpoint_available, tx_response_time, accepts_transactions = self.check_transaction_endpoint(api_port)
        mempool_size = 0  # Would need specific endpoint for this
        
        # Leadership and consensus
        is_current_leader, is_upcoming_leader, leader_schedule_available = self.get_leader_info(api_port)
        quantum_healthy, quantum_active, quantum_total = self.get_quantum_metrics(api_port)
        
        # Network status
        gossip_peers, p2p_peers, network_latency = self.get_network_status(api_port)
        
        # Performance metrics
        blocks_produced, transactions_processed, avg_tx_time = self.get_performance_metrics(api_port, blockchain_data)
        
        # Create node availability object
        node = NodeAvailability(
            node_id=node_index + 1,
            api_port=api_port,
            p2p_port=p2p_port,
            gossip_port=gossip_port,
            tpu_port=tpu_port,
            tvu_port=tvu_port,
            
            process_running=process_running,
            api_responding=api_responding,
            api_response_time=api_response_time,
            
            transaction_endpoint_available=tx_endpoint_available,
            transaction_response_time=tx_response_time,
            accepts_transactions=accepts_transactions,
            mempool_size=mempool_size,
            
            is_current_leader=is_current_leader,
            is_upcoming_leader=is_upcoming_leader,
            leader_schedule_available=leader_schedule_available,
            quantum_consensus_healthy=quantum_healthy,
            quantum_active_nodes=quantum_active,
            quantum_total_nodes=quantum_total,
            
            gossip_active_peers=gossip_peers,
            p2p_connected_peers=p2p_peers,
            network_latency=network_latency,
            
            blocks_produced=blocks_produced,
            transactions_processed=transactions_processed,
            average_transaction_time=avg_tx_time,
            
            status='unknown',
            availability_score=0.0,
            transaction_readiness='unknown'
        )
        
        # Calculate derived fields
        node.availability_score = self.calculate_availability_score(node)
        node.transaction_readiness = self.determine_transaction_readiness(node)
        
        # Determine overall status
        if node.availability_score >= 80:
            node.status = 'available'
        elif node.availability_score >= 50:
            node.status = 'limited'
        elif node.process_running:
            node.status = 'degraded'
        else:
            node.status = 'offline'
        
        return node
    
    def check_all_nodes(self, parallel: bool = True) -> Tuple[List[NodeAvailability], List[NodeAvailability]]:
        """Check availability of all nodes"""
        print(f"🔍 CHECKING NODE AVAILABILITY FOR TRANSACTIONS")
        print("=" * 60)
        print(f"Scanning {self.max_nodes} potential nodes...")
        print(f"Base API Port: {self.base_port}")
        print()
        
        if parallel:
            # Parallel checking for speed
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(self.check_single_node, i): i for i in range(self.max_nodes)}
                nodes = []
                
                for future in concurrent.futures.as_completed(futures):
                    node = future.result()
                    nodes.append(node)
        else:
            # Sequential checking
            nodes = []
            for i in range(self.max_nodes):
                node = self.check_single_node(i)
                nodes.append(node)
                print(f"  Checked Node {i+1}: {node.status}")
        
        # Separate available and unavailable nodes
        available_nodes = [n for n in nodes if n.status in ['available', 'limited']]
        unavailable_nodes = [n for n in nodes if n.status in ['degraded', 'offline']]
        
        # Sort by availability score
        available_nodes.sort(key=lambda x: x.availability_score, reverse=True)
        
        self.available_nodes = available_nodes
        self.unavailable_nodes = unavailable_nodes
        
        return available_nodes, unavailable_nodes
    
    def print_summary(self):
        """Print a summary of node availability"""
        total_nodes = len(self.available_nodes) + len(self.unavailable_nodes)
        
        print(f"\n📊 NODE AVAILABILITY SUMMARY")
        print("=" * 50)
        print(f"Total Nodes Scanned: {total_nodes}")
        print(f"✅ Available for Transactions: {len(self.available_nodes)}")
        print(f"❌ Unavailable: {len(self.unavailable_nodes)}")
        print()
        
        if self.available_nodes:
            ready_nodes = [n for n in self.available_nodes if n.transaction_readiness == 'ready']
            limited_nodes = [n for n in self.available_nodes if n.transaction_readiness == 'limited']
            
            print(f"🚀 TRANSACTION-READY NODES: {len(ready_nodes)}")
            print("─" * 30)
            for node in ready_nodes:
                leader_indicator = "👑" if node.is_current_leader else "⏳" if node.is_upcoming_leader else ""
                print(f"  Node {node.node_id:2d} (port {node.api_port}): {node.availability_score:.1f}% {leader_indicator}")
                print(f"       API: {node.api_response_time:.3f}s | TX: {node.transaction_response_time:.3f}s")
                print(f"       Gossip: {node.gossip_active_peers} peers | P2P: {node.p2p_connected_peers} peers")
            
            if limited_nodes:
                print(f"\n⚠️  LIMITED CAPACITY NODES: {len(limited_nodes)}")
                print("─" * 30)
                for node in limited_nodes:
                    print(f"  Node {node.node_id:2d} (port {node.api_port}): {node.availability_score:.1f}%")
                    print(f"       Status: {node.transaction_readiness}")
        
        if self.unavailable_nodes:
            print(f"\n❌ UNAVAILABLE NODES: {len(self.unavailable_nodes)}")
            print("─" * 20)
            offline_count = len([n for n in self.unavailable_nodes if n.status == 'offline'])
            degraded_count = len([n for n in self.unavailable_nodes if n.status == 'degraded'])
            print(f"  Offline: {offline_count}")
            print(f"  Degraded: {degraded_count}")
    
    def print_detailed_report(self):
        """Print detailed availability report"""
        print(f"\n🔬 DETAILED NODE AVAILABILITY REPORT")
        print("=" * 60)
        
        all_nodes = self.available_nodes + self.unavailable_nodes
        all_nodes.sort(key=lambda x: x.node_id)
        
        for node in all_nodes:
            status_icon = {
                'available': '✅',
                'limited': '⚠️ ',
                'degraded': '🔶',
                'offline': '❌'
            }.get(node.status, '❓')
            
            print(f"\n{status_icon} Node {node.node_id:2d} - {node.status.upper()} ({node.availability_score:.1f}%)")
            print(f"   Ports: API:{node.api_port} | P2P:{node.p2p_port} | TPU:{node.tpu_port}")
            print(f"   Process: {'✅' if node.process_running else '❌'} | API: {'✅' if node.api_responding else '❌'} ({node.api_response_time:.3f}s)")
            print(f"   Transactions: {'✅' if node.accepts_transactions else '❌'} ({node.transaction_response_time:.3f}s)")
            print(f"   Leadership: Current:{'✅' if node.is_current_leader else '❌'} | Schedule:{'✅' if node.leader_schedule_available else '❌'}")
            print(f"   Quantum: {'✅' if node.quantum_consensus_healthy else '❌'} ({node.quantum_active_nodes}/{node.quantum_total_nodes} nodes)")
            print(f"   Network: Gossip:{node.gossip_active_peers} | P2P:{node.p2p_connected_peers} | Latency:{node.network_latency:.3f}s")
            print(f"   Performance: {node.blocks_produced} blocks | {node.transactions_processed} transactions")
            print(f"   Transaction Readiness: {node.transaction_readiness.upper()}")
    
    def get_best_nodes_for_transactions(self, count: int = 3) -> List[NodeAvailability]:
        """Get the best nodes for sending transactions"""
        ready_nodes = [n for n in self.available_nodes if n.transaction_readiness == 'ready']
        
        # Sort by combination of availability score and response time
        ready_nodes.sort(key=lambda x: (x.availability_score, -x.transaction_response_time), reverse=True)
        
        return ready_nodes[:count]
    
    def test_transaction_submission(self, node_count: int = 3) -> Dict:
        """Test actual transaction submission to verify availability"""
        print(f"\n🧪 TESTING TRANSACTION SUBMISSION")
        print("=" * 40)
        
        best_nodes = self.get_best_nodes_for_transactions(node_count)
        
        if not best_nodes:
            print("❌ No nodes available for transaction testing")
            return {}
        
        results = {}
        
        for node in best_nodes:
            print(f"Testing Node {node.node_id} (port {node.api_port})...")
            
            try:
                # Create a minimal test transaction payload
                test_payload = {
                    "transaction": "test_transaction_data"
                }
                
                start_time = time.time()
                response = requests.post(
                    f'http://localhost:{node.api_port}/api/v1/transaction/create/',
                    json=test_payload,
                    timeout=5
                )
                response_time = time.time() - start_time
                
                results[node.node_id] = {
                    'success': response.status_code in [200, 400, 422],  # 400/422 might be validation errors, but endpoint works
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'can_accept_transactions': response.status_code != 503
                }
                
                status = "✅" if results[node.node_id]['success'] else "❌"
                print(f"  {status} Status: {response.status_code} | Time: {response_time:.3f}s")
                
            except Exception as e:
                results[node.node_id] = {
                    'success': False,
                    'error': str(e),
                    'response_time': float('inf'),
                    'can_accept_transactions': False
                }
                print(f"  ❌ Error: {e}")
        
        return results
    
    def export_to_json(self, filename: str):
        """Export availability data to JSON file"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_nodes': len(self.available_nodes) + len(self.unavailable_nodes),
                'available_nodes': len(self.available_nodes),
                'unavailable_nodes': len(self.unavailable_nodes),
                'transaction_ready_nodes': len([n for n in self.available_nodes if n.transaction_readiness == 'ready'])
            },
            'available_nodes': [asdict(node) for node in self.available_nodes],
            'unavailable_nodes': [asdict(node) for node in self.unavailable_nodes]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"📄 Availability data exported to {filename}")


def main():
    parser = argparse.ArgumentParser(description='Check Node Availability for Transaction Processing')
    parser.add_argument('--base-port', type=int, default=11000, help='Base API port (default: 11000)')
    parser.add_argument('--max-nodes', type=int, default=20, help='Maximum number of nodes to check (default: 20)')
    parser.add_argument('--detailed', action='store_true', help='Show detailed report for each node')
    parser.add_argument('--test-transactions', action='store_true', help='Test actual transaction submission')
    parser.add_argument('--export-json', type=str, help='Export results to JSON file')
    parser.add_argument('--sequential', action='store_true', help='Check nodes sequentially instead of parallel')
    
    args = parser.parse_args()
    
    # Create checker and run availability check
    checker = NodeAvailabilityChecker(args.base_port, args.max_nodes)
    available_nodes, unavailable_nodes = checker.check_all_nodes(parallel=not args.sequential)
    
    # Print results
    checker.print_summary()
    
    if args.detailed:
        checker.print_detailed_report()
    
    # Test transaction submission if requested
    if args.test_transactions:
        test_results = checker.test_transaction_submission()
    
    # Export to JSON if requested
    if args.export_json:
        checker.export_to_json(args.export_json)
    
    # Print quick usage recommendations
    if available_nodes:
        print(f"\n🚀 RECOMMENDATIONS FOR BATCH TRANSACTION TEST")
        print("=" * 50)
        
        best_nodes = checker.get_best_nodes_for_transactions(3)
        if best_nodes:
            print("Best nodes for sending transactions:")
            for i, node in enumerate(best_nodes, 1):
                leader_note = " (Current Leader)" if node.is_current_leader else ""
                print(f"  {i}. Node {node.node_id} (port {node.api_port}) - {node.availability_score:.1f}%{leader_note}")
            
            print(f"\nSuggested batch_transaction_test.py commands:")
            best_node = best_nodes[0]
            print(f"  python batch_transaction_test.py --node {best_node.api_port} --batch-size 100")
            print(f"  python batch_transaction_test.py --node {best_node.api_port} --batch-size 50 --workers 25")
            
            if len(best_nodes) > 1:
                print(f"\nFor distributed testing across multiple nodes:")
                for node in best_nodes[:3]:
                    print(f"  python batch_transaction_test.py --node {node.api_port} --batch-size 33 &")
    
    return len(available_nodes) > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
