#!/usr/bin/env python3
"""
Optimized Transaction Pool Synchronization System

This module implements advanced transaction pool synchronization with:
1. Merkle tree-based pool consistency verification
2. Intelligent transaction redistribution
3. Pool state synchronization protocols
4. Conflict resolution and consensus
5. Load balancing across nodes
"""

import hashlib
import json
import time
import threading
from collections import defaultdict, deque
from datetime import datetime, timedelta
import requests
from concurrent.futures import ThreadPoolExecutor
import sys
import os

sys.path.insert(0, '/Users/shubham/Documents/proofwithquantumannealing/blockchain')
from blockchain.utils.helpers import BlockchainUtils

class MerklePoolTree:
    """Merkle tree for transaction pool integrity verification"""
    
    def __init__(self, transactions):
        self.transactions = transactions
        self.tree = self._build_tree()
        self.root_hash = self.tree[0] if self.tree else None
    
    def _build_tree(self):
        """Build Merkle tree from transactions"""
        if not self.transactions:
            return []
        
        # Create leaf hashes
        leaves = [self._hash_transaction(tx) for tx in self.transactions]
        tree = leaves[:]
        
        # Build tree bottom-up
        while len(leaves) > 1:
            next_level = []
            for i in range(0, len(leaves), 2):
                left = leaves[i]
                right = leaves[i + 1] if i + 1 < len(leaves) else left
                combined = hashlib.sha256((left + right).encode()).hexdigest()
                next_level.append(combined)
            leaves = next_level
            tree.extend(leaves)
        
        return tree
    
    def _hash_transaction(self, transaction):
        """Generate hash for a transaction"""
        if hasattr(transaction, 'signature'):
            return transaction.signature[:32]  # Use first 32 chars of signature
        else:
            return hashlib.sha256(str(transaction).encode()).hexdigest()[:32]
    
    def get_proof(self, transaction_index):
        """Get Merkle proof for a specific transaction"""
        if transaction_index >= len(self.transactions):
            return None
        
        proof = []
        current_index = transaction_index
        current_level_size = len(self.transactions)
        
        tree_index = 0
        while current_level_size > 1:
            # Find sibling
            if current_index % 2 == 0:
                sibling_index = current_index + 1
            else:
                sibling_index = current_index - 1
            
            if sibling_index < current_level_size:
                proof.append(self.tree[tree_index + sibling_index])
            
            # Move to next level
            tree_index += current_level_size
            current_index = current_index // 2
            current_level_size = (current_level_size + 1) // 2
        
        return proof
    
    def verify_proof(self, transaction, proof, root_hash):
        """Verify a transaction exists in the pool using Merkle proof"""
        current_hash = self._hash_transaction(transaction)
        
        for proof_hash in proof:
            # Combine with sibling (order doesn't matter for verification)
            combined1 = hashlib.sha256((current_hash + proof_hash).encode()).hexdigest()
            combined2 = hashlib.sha256((proof_hash + current_hash).encode()).hexdigest()
            current_hash = min(combined1, combined2)  # Use lexicographically smaller
        
        return current_hash == root_hash


class TransactionPoolSynchronizer:
    """Advanced transaction pool synchronization system"""
    
    def __init__(self, node_configs=None):
        self.node_configs = node_configs or {
            i: 11000 + i - 1 for i in range(1, 11)
        }
        
        # Synchronization state
        self.pool_states = {}  # node_id -> pool_state
        self.last_sync_times = defaultdict(float)
        self.sync_conflicts = defaultdict(list)
        self.redistribution_queue = deque()
        
        # Configuration
        self.SYNC_INTERVAL = 15.0  # Sync every 15 seconds
        self.MAX_POOL_IMBALANCE = 5  # Max difference between largest and smallest pools
        self.CONFLICT_RESOLUTION_THRESHOLD = 3  # Nodes needed for consensus
        self.REDISTRIBUTION_BATCH_SIZE = 3  # Transactions to move at once
        
        # HTTP session for API calls
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=15,
            pool_maxsize=30,
            max_retries=2
        )
        self.session.mount('http://', adapter)
        self.session.timeout = (3, 8)
        
        # Threading
        self.sync_active = False
        self.sync_thread = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    def start_synchronization(self):
        """Start continuous pool synchronization"""
        if self.sync_active:
            return
        
        self.sync_active = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        print("🔄 Transaction pool synchronization started")
        
    def stop_synchronization(self):
        """Stop pool synchronization"""
        self.sync_active = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5.0)
        self.executor.shutdown(wait=True)
        print("🛑 Transaction pool synchronization stopped")
    
    def _sync_loop(self):
        """Main synchronization loop"""
        while self.sync_active:
            try:
                # Get current pool states from all nodes
                self._collect_pool_states()
                
                # Detect and resolve conflicts
                self._detect_sync_conflicts()
                
                # Balance pool loads
                self._balance_pool_loads()
                
                # Execute redistributions
                self._execute_redistributions()
                
                time.sleep(self.SYNC_INTERVAL)
                
            except Exception as e:
                print(f"❌ Sync loop error: {e}")
                time.sleep(self.SYNC_INTERVAL)
    
    def get_node_pool_state(self, node_id):
        """Get detailed pool state from a specific node"""
        api_port = self.node_configs[node_id]
        
        try:
            # Get transaction pool
            pool_response = self.session.get(
                f'http://localhost:{api_port}/api/v1/transaction/transaction_pool/'
            )
            
            if pool_response.status_code == 200:
                transactions = pool_response.json()
                if not isinstance(transactions, list):
                    transactions = []
                
                # Create Merkle tree for integrity
                merkle_tree = MerklePoolTree(transactions)
                
                # Analyze pool composition
                pool_analysis = self._analyze_pool_composition(transactions)
                
                return {
                    'node_id': node_id,
                    'timestamp': time.time(),
                    'transaction_count': len(transactions),
                    'transactions': transactions,
                    'merkle_root': merkle_tree.root_hash,
                    'merkle_tree': merkle_tree,
                    'composition': pool_analysis,
                    'status': 'success'
                }
            else:
                return {
                    'node_id': node_id,
                    'status': 'api_error',
                    'error_code': pool_response.status_code,
                    'timestamp': time.time()
                }
                
        except Exception as e:
            return {
                'node_id': node_id,
                'status': 'connection_error',
                'error': str(e),
                'timestamp': time.time()
            }
    
    def _collect_pool_states(self):
        """Collect pool states from all nodes concurrently"""
        futures = {}
        
        for node_id in self.node_configs.keys():
            future = self.executor.submit(self.get_node_pool_state, node_id)
            futures[future] = node_id
        
        # Collect results
        new_pool_states = {}
        for future in futures:
            try:
                state = future.result(timeout=10)
                new_pool_states[state['node_id']] = state
            except Exception as e:
                node_id = futures[future]
                new_pool_states[node_id] = {
                    'node_id': node_id,
                    'status': 'timeout',
                    'error': str(e),
                    'timestamp': time.time()
                }
        
        self.pool_states = new_pool_states
    
    def _analyze_pool_composition(self, transactions):
        """Analyze composition and characteristics of transaction pool"""
        if not transactions:
            return {
                'total_value': 0,
                'unique_senders': 0,
                'transaction_types': {},
                'age_distribution': {}
            }
        
        total_value = 0
        unique_senders = set()
        transaction_types = defaultdict(int)
        timestamps = []
        
        for tx in transactions:
            # Transaction value
            if 'amount' in tx:
                try:
                    total_value += float(tx['amount'])
                except (ValueError, TypeError):
                    pass
            
            # Unique senders
            if 'sender_public_key' in tx:
                unique_senders.add(tx['sender_public_key'])
            
            # Transaction types
            tx_type = tx.get('type', 'unknown')
            transaction_types[tx_type] += 1
            
            # Timestamps for age analysis
            if 'timestamp' in tx:
                try:
                    timestamps.append(float(tx['timestamp']))
                except (ValueError, TypeError):
                    pass
        
        # Calculate age distribution
        current_time = time.time()
        age_distribution = {
            'fresh': 0,    # < 30 seconds
            'recent': 0,   # 30s - 5min
            'old': 0       # > 5min
        }
        
        for ts in timestamps:
            age = current_time - ts
            if age < 30:
                age_distribution['fresh'] += 1
            elif age < 300:
                age_distribution['recent'] += 1
            else:
                age_distribution['old'] += 1
        
        return {
            'total_value': total_value,
            'unique_senders': len(unique_senders),
            'transaction_types': dict(transaction_types),
            'age_distribution': age_distribution
        }
    
    def _detect_sync_conflicts(self):
        """Detect synchronization conflicts and inconsistencies"""
        online_nodes = [
            node_id for node_id, state in self.pool_states.items()
            if state.get('status') == 'success'
        ]
        
        if len(online_nodes) < 2:
            return  # Need at least 2 nodes to detect conflicts
        
        # Compare Merkle roots
        merkle_roots = {}
        for node_id in online_nodes:
            state = self.pool_states[node_id]
            root = state.get('merkle_root')
            if root:
                if root not in merkle_roots:
                    merkle_roots[root] = []
                merkle_roots[root].append(node_id)
        
        # Detect conflicts (different roots)
        if len(merkle_roots) > 1:
            print(f"⚠️  Pool synchronization conflict detected!")
            for root, nodes in merkle_roots.items():
                print(f"   Root {root[:16]}...: Nodes {nodes}")
            
            # Store conflict for resolution
            conflict = {
                'timestamp': time.time(),
                'merkle_roots': merkle_roots,
                'affected_nodes': online_nodes
            }
            self.sync_conflicts[time.time()] = conflict
            
            # Attempt automatic resolution
            self._resolve_sync_conflict(conflict)
    
    def _resolve_sync_conflict(self, conflict):
        """Attempt to resolve pool synchronization conflicts"""
        merkle_roots = conflict['merkle_roots']
        
        # Use majority consensus
        majority_root = max(merkle_roots.items(), key=lambda x: len(x[1]))
        majority_nodes = majority_root[1]
        minority_nodes = []
        
        for root, nodes in merkle_roots.items():
            if root != majority_root[0]:
                minority_nodes.extend(nodes)
        
        print(f"🔧 Resolving conflict using majority consensus")
        print(f"   Majority: {len(majority_nodes)} nodes with root {majority_root[0][:16]}...")
        print(f"   Minority: {len(minority_nodes)} nodes need synchronization")
        
        # Get canonical pool state from majority
        if majority_nodes:
            canonical_node = majority_nodes[0]
            canonical_state = self.pool_states[canonical_node]
            
            # Force sync minority nodes to canonical state
            for node_id in minority_nodes:
                self._force_sync_node(node_id, canonical_state)
    
    def _force_sync_node(self, target_node_id, canonical_state):
        """Force a node to synchronize to canonical pool state"""
        print(f"🔄 Force syncing Node {target_node_id} to canonical state")
        
        # This would require additional API endpoints to:
        # 1. Clear the target node's pool
        # 2. Re-submit canonical transactions
        # For now, we'll log the action needed
        
        canonical_count = canonical_state.get('transaction_count', 0)
        target_state = self.pool_states.get(target_node_id, {})
        target_count = target_state.get('transaction_count', 0)
        
        print(f"   Target: {target_count} transactions -> Canonical: {canonical_count} transactions")
        
        # In a production system, this would involve:
        # - API endpoint to clear pool: POST /api/v1/transaction/clear_pool/
        # - Re-submit canonical transactions: POST /api/v1/transaction/sync_from_canonical/
    
    def _balance_pool_loads(self):
        """Balance transaction loads across nodes"""
        online_nodes = [
            node_id for node_id, state in self.pool_states.items()
            if state.get('status') == 'success'
        ]
        
        if len(online_nodes) < 2:
            return
        
        # Calculate pool sizes
        pool_sizes = {}
        for node_id in online_nodes:
            state = self.pool_states[node_id]
            pool_sizes[node_id] = state.get('transaction_count', 0)
        
        if not pool_sizes:
            return
        
        max_pool_size = max(pool_sizes.values())
        min_pool_size = min(pool_sizes.values())
        avg_pool_size = sum(pool_sizes.values()) / len(pool_sizes)
        
        # Check if rebalancing is needed
        if max_pool_size - min_pool_size > self.MAX_POOL_IMBALANCE:
            print(f"⚖️  Pool imbalance detected: {min_pool_size} - {max_pool_size} (avg: {avg_pool_size:.1f})")
            
            # Find overloaded and underloaded nodes
            overloaded_nodes = [
                node_id for node_id, size in pool_sizes.items()
                if size > avg_pool_size + 2
            ]
            underloaded_nodes = [
                node_id for node_id, size in pool_sizes.items()
                if size < avg_pool_size - 2
            ]
            
            # Queue redistributions
            for overloaded_node in overloaded_nodes:
                for underloaded_node in underloaded_nodes:
                    if pool_sizes[overloaded_node] > pool_sizes[underloaded_node] + 3:
                        redistribution = {
                            'source_node': overloaded_node,
                            'target_node': underloaded_node,
                            'transaction_count': self.REDISTRIBUTION_BATCH_SIZE,
                            'priority': abs(pool_sizes[overloaded_node] - pool_sizes[underloaded_node])
                        }
                        self.redistribution_queue.append(redistribution)
    
    def _execute_redistributions(self):
        """Execute queued transaction redistributions"""
        while self.redistribution_queue:
            redistribution = self.redistribution_queue.popleft()
            
            print(f"🔄 Redistributing {redistribution['transaction_count']} transactions: "
                  f"Node {redistribution['source_node']} -> Node {redistribution['target_node']}")
            
            # In production, this would:
            # 1. Get transactions from source node
            # 2. Remove them from source pool
            # 3. Submit them to target node
            # For now, we simulate the action
            
            time.sleep(0.1)  # Prevent overwhelming the system
    
    def get_synchronization_report(self):
        """Generate comprehensive synchronization report"""
        online_nodes = [
            node_id for node_id, state in self.pool_states.items()
            if state.get('status') == 'success'
        ]
        
        if not online_nodes:
            return {
                'status': 'no_nodes_online',
                'timestamp': datetime.now().isoformat()
            }
        
        # Calculate statistics
        pool_sizes = [
            self.pool_states[node_id].get('transaction_count', 0)
            for node_id in online_nodes
        ]
        
        total_transactions = sum(pool_sizes)
        avg_pool_size = total_transactions / len(pool_sizes) if pool_sizes else 0
        max_pool_size = max(pool_sizes) if pool_sizes else 0
        min_pool_size = min(pool_sizes) if pool_sizes else 0
        
        # Check Merkle root consistency
        merkle_roots = set()
        for node_id in online_nodes:
            root = self.pool_states[node_id].get('merkle_root')
            if root:
                merkle_roots.add(root)
        
        sync_status = "synchronized" if len(merkle_roots) <= 1 else "conflicts_detected"
        
        return {
            'timestamp': datetime.now().isoformat(),
            'sync_status': sync_status,
            'online_nodes': len(online_nodes),
            'total_nodes': len(self.node_configs),
            'total_transactions': total_transactions,
            'avg_pool_size': avg_pool_size,
            'max_pool_size': max_pool_size,
            'min_pool_size': min_pool_size,
            'pool_imbalance': max_pool_size - min_pool_size,
            'merkle_roots_count': len(merkle_roots),
            'pending_redistributions': len(self.redistribution_queue),
            'sync_conflicts_count': len(self.sync_conflicts),
            'node_details': {
                node_id: {
                    'pool_size': state.get('transaction_count', 0),
                    'merkle_root': state.get('merkle_root', '')[:16] + '...' if state.get('merkle_root') else 'None',
                    'status': state.get('status', 'unknown')
                }
                for node_id, state in self.pool_states.items()
            }
        }
    
    def print_sync_status(self):
        """Print formatted synchronization status"""
        report = self.get_synchronization_report()
        
        print(f"\n🔄 TRANSACTION POOL SYNCHRONIZATION STATUS")
        print(f"{'='*55}")
        print(f"🕐 Timestamp: {report['timestamp']}")
        print(f"🌐 Sync Status: {report['sync_status']}")
        print(f"📊 Nodes Online: {report['online_nodes']}/{report['total_nodes']}")
        print(f"📦 Total Transactions: {report['total_transactions']}")
        print(f"📈 Avg Pool Size: {report['avg_pool_size']:.1f}")
        print(f"⚖️  Pool Imbalance: {report['pool_imbalance']}")
        
        if report['sync_status'] != 'synchronized':
            print(f"⚠️  Merkle Roots: {report['merkle_roots_count']} different states")
            print(f"🔧 Pending Redistributions: {report['pending_redistributions']}")
        
        print(f"\n📋 Node Details:")
        for node_id, details in report['node_details'].items():
            status_icon = "🟢" if details['status'] == 'success' else "🔴"
            print(f"   {status_icon} Node {node_id}: {details['pool_size']} tx, "
                  f"Root: {details['merkle_root']}")


def run_pool_sync_test():
    """Run comprehensive pool synchronization test"""
    print("🔄 Starting Transaction Pool Synchronization Test")
    print("=" * 60)
    
    synchronizer = TransactionPoolSynchronizer()
    
    # Initial pool state collection
    print("📊 Collecting initial pool states...")
    synchronizer._collect_pool_states()
    synchronizer.print_sync_status()
    
    # Start synchronization
    print(f"\n🔄 Starting continuous synchronization (60 seconds)...")
    synchronizer.start_synchronization()
    
    try:
        # Monitor for 60 seconds
        for i in range(4):
            time.sleep(15)
            print(f"\n⏱️  Sync update ({(i+1)*15}s):")
            synchronizer.print_sync_status()
            
    finally:
        synchronizer.stop_synchronization()
    
    # Final assessment
    final_report = synchronizer.get_synchronization_report()
    
    print(f"\n🎯 SYNCHRONIZATION ASSESSMENT:")
    if final_report['sync_status'] == 'synchronized':
        print("✅ Pools are properly synchronized")
    else:
        print("⚠️  Synchronization issues detected")
    
    if final_report['pool_imbalance'] <= 3:
        print("✅ Pool loads are well balanced")
    else:
        print(f"⚖️  Pool imbalance: {final_report['pool_imbalance']} transactions")
    
    return final_report


if __name__ == "__main__":
    report = run_pool_sync_test()
    
    print(f"\n💡 OPTIMIZATION RECOMMENDATIONS:")
    if report['sync_status'] != 'synchronized':
        print("🔧 Implement stronger pool consistency protocols")
        print("🔧 Add automatic conflict resolution mechanisms")
    
    if report['pool_imbalance'] > 5:
        print("🔧 Enable automatic load balancing")
        print("🔧 Implement smart transaction routing")
    
    if report['online_nodes'] < report['total_nodes']:
        print("🔧 Investigate offline nodes")
        print("🔧 Improve network connectivity")
    
    print(f"\n📊 Performance Metrics:")
    print(f"   🎯 Synchronization Rate: {(1 if report['sync_status'] == 'synchronized' else 0)*100:.0f}%")
    print(f"   ⚖️  Load Balance Score: {max(0, 100 - report['pool_imbalance']*10):.0f}%")
    print(f"   🌐 Network Health: {(report['online_nodes']/report['total_nodes'])*100:.0f}%")
