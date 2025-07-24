#!/usr/bin/env python3
"""
Quantum Consensus Simulation Script

This script simulates a complete quantum blockchain consensus process with:
1. Realistic uptime, latency, throughput, and performance metrics
2. Representative node selection using actual quantum annealing consensus
3. Block creation and network propagation simulation
4. Complete blockchain integration with transaction processing

The simulation demonstrates the full lifecycle from metrics collection
through consensus to block creation and network synchronization.
"""

import sys
import os
import time
import random
import json
import hashlib
import math
import secrets
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import threading

# Cryptographic imports
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Add blockchain path for imports
sys.path.insert(0, '/Users/shubham/Documents/fromgithub/proofwithquantumannealing/blockchain')

from blockchain.transaction.wallet import Wallet
from blockchain.transaction.transaction import Transaction
from blockchain.utils.helpers import BlockchainUtils
from blockchain.block import Block
from blockchain.blockchain import Blockchain
from blockchain.quantum_consensus.quantum_annealing_consensus import QuantumAnnealingConsensus

class QuantumConsensusSimulator:
    """
    Comprehensive simulator for quantum blockchain consensus with realistic network conditions.
    """
    
    def __init__(self, num_nodes: int = 10):
        """Initialize the quantum consensus simulator"""
        self.num_nodes = num_nodes
        self.consensus = QuantumAnnealingConsensus()
        self.simulated_network = {}
        self.blockchain = Blockchain()
        self.transaction_pool = []
        self.simulation_start_time = time.time()
        
        # Pre-create wallet pool for high-performance transaction creation
        self.wallet_pool = []
        print("🔮 Pre-generating wallet pool for high performance...")
        for i in range(200):  # Pre-create 200 wallets
            self.wallet_pool.append(Wallet())
        
        # Transaction metrics tracking
        self.transaction_metrics = {
            'creation_times': {},      # tx_id -> creation_timestamp
            'processing_times': {},    # tx_id -> processing_duration (includes wallet selection)
            'pure_tx_times': {},       # tx_id -> pure transaction creation time (wallet already available)
            'confirmation_times': {},  # tx_id -> confirmation_timestamp
            'total_transactions': 0,
            'successful_transactions': 0,
            'failed_transactions': 0,
            'throughput_history': []   # (timestamp, tx_count, duration)
        }
        
        # Network simulation parameters
        self.base_latency = 0.020  # 20ms base network latency
        self.latency_variance = 0.030  # 30ms variance
        self.throughput_base = 10.0  # Base 10 probes/minute
        self.throughput_variance = 15.0  # Up to 15 probes/minute variance
        
        print("🔮 Quantum Consensus Simulator Initialized")
        print(f"   🌐 Network Size: {num_nodes} nodes")
        print(f"   ⚡ Base Latency: {self.base_latency*1000:.0f}ms ± {self.latency_variance*1000:.0f}ms")
        print(f"   📈 Throughput Range: {self.throughput_base:.1f} - {self.throughput_base + self.throughput_variance:.1f} probes/min")
        
    def generate_node_identity(self, node_index: int) -> tuple[str, str]:
        """Generate a unique node identity with public key"""
        node_id = f"node_{node_index:02d}_{secrets.token_hex(8)}"
        
        # Generate cryptographic keys for this node
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        
        # Serialize public key to PEM format
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return node_id, public_pem
        
    def simulate_network_conditions(self, node_id: str) -> Dict:
        """Generate realistic network conditions for a node"""
        runtime = time.time() - self.simulation_start_time
        
        # Define node performance patterns
        patterns = ['stable', 'unstable', 'failing', 'good', 'average']
        pattern = random.choice(patterns)
        
        # Base conditions based on pattern
        if pattern == 'stable':
            base_uptime = 0.98
            base_latency = self.base_latency + random.uniform(0, 0.01)
            success_base = 0.95
        elif pattern == 'good':
            base_uptime = 0.92
            base_latency = self.base_latency + random.uniform(0, 0.015)
            success_base = 0.85
        elif pattern == 'average':
            base_uptime = 0.85
            base_latency = self.base_latency + random.uniform(0.015, 0.025)
            success_base = 0.75
        elif pattern == 'unstable':
            base_uptime = 0.70
            base_latency = self.base_latency + random.uniform(0.015, 0.025)
            success_base = 0.65
        else:  # failing
            base_uptime = 0.45
            base_latency = self.base_latency + random.uniform(0.02, 0.04)
            success_base = 0.45
            
        # Add time-based variations (network congestion, maintenance windows)
        time_factor = 1.0 + 0.1 * math.sin(runtime / 300)  # 5-minute cycles
        daily_factor = 1.0 + 0.05 * math.sin(runtime / 86400)  # Daily patterns
        
        # Calculate final metrics
        uptime = max(0.1, min(1.0, base_uptime * time_factor))
        latency = base_latency * time_factor * daily_factor
        throughput = self.throughput_base + random.uniform(0, self.throughput_variance)
        
        # Proposal success/failure counts (simulated historical data)
        total_proposals = random.randint(5, 20)
        successful_proposals = int(total_proposals * success_base * random.uniform(0.8, 1.2))
        failed_proposals = total_proposals - successful_proposals
        
        node_hash = hashlib.sha256(node_id.encode()).hexdigest()[:8]
        
        return {
            'uptime': uptime,
            'latency': latency,
            'throughput': throughput,
            'proposals_success': max(0, successful_proposals),
            'proposals_failed': max(0, failed_proposals),
            'pattern': pattern,
            'node_hash': node_hash,
            'runtime_seconds': runtime
        }
    
    def setup_simulated_network(self):
        """Set up the simulated network with realistic nodes and metrics"""
        print(f"\n🌐 Setting up simulated {self.num_nodes}-node network...")
        
        for i in range(self.num_nodes):
            node_id, public_key = self.generate_node_identity(i)
            conditions = self.simulate_network_conditions(node_id)
            
            # Register node with quantum consensus
            self.consensus.register_node(node_id, public_key)
            
            # Set simulated metrics directly
            self.consensus.nodes[node_id]['uptime'] = conditions['uptime']
            self.consensus.nodes[node_id]['latency'] = conditions['latency']
            self.consensus.nodes[node_id]['throughput'] = conditions['throughput']
            self.consensus.nodes[node_id]['proposal_success_count'] = conditions['proposals_success']
            self.consensus.nodes[node_id]['proposal_failure_count'] = conditions['proposals_failed']
            self.consensus.nodes[node_id]['last_seen'] = time.time() - random.uniform(0, 30)
            
            # Store for reference
            self.simulated_network[node_id] = {
                'public_key': public_key,
                'conditions': conditions,
                'metrics': {
                    'uptime': conditions['uptime'],
                    'latency_ms': conditions['latency'] * 1000,
                    'throughput': conditions['throughput'],
                    'success_rate': conditions['proposals_success'] / max(1, conditions['proposals_success'] + conditions['proposals_failed']) * 100
                }
            }
            
            print(f"   ✅ Node {i+1:2d}: {node_id[:20]}... ({conditions['pattern']:8s} | Up:{conditions['uptime']*100:.1f}% | Lat:{conditions['latency']*1000:.0f}ms | Thr:{conditions['throughput']:.1f} | Succ:{conditions['proposals_success']:2d}/{conditions['proposals_success'] + conditions['proposals_failed']:2d})")
    
    def simulate_consensus_round(self) -> Optional[tuple[str, str]]:
        """
        Run a complete consensus round to select the representative node.
        Returns tuple of (public_key, node_id) if successful, None if failed.
        """
        print(f"\n🔮 QUANTUM CONSENSUS SIMULATION")
        print("=" * 60)
        
        # Get last block hash (or genesis hash if first block)
        if len(self.blockchain.blocks) > 1:
            last_block_hash = BlockchainUtils.hash(self.blockchain.blocks[-1].payload()).hex()
            block_number = len(self.blockchain.blocks)
        else:
            last_block_hash = "0" * 64
            block_number = 0
            
        print(f"   📦 Block Number: {block_number}")
        print(f"   🔗 Previous Hash: {last_block_hash[:16]}...")
        print(f"   🌐 Active Nodes: {len([n for n in self.consensus.nodes.keys() if self.consensus.calculate_uptime(n) > 0.5])}/{len(self.consensus.nodes)}")
        
        print(f"\n   🎯 Running Quantum Annealing Consensus...")
        consensus_start = time.time()
        
        selected_node = self.consensus.select_representative_node(last_block_hash)
        
        consensus_time = time.time() - consensus_start
        
        if selected_node:
            # Find the node_id that corresponds to this public key
            corresponding_node_id = None
            mock_metrics = None
            
            for node_id, data in self.simulated_network.items():
                if data['public_key'] == selected_node:
                    corresponding_node_id = node_id
                    break
            
            # Check if it might be the genesis node
            if not corresponding_node_id:
                # Check if it's a genesis or existing node
                for node_id in self.consensus.nodes.keys():
                    if self.consensus.nodes[node_id].get('public_key') == selected_node:
                        corresponding_node_id = node_id
                        # Create mock metrics for existing nodes
                        mock_metrics = {
                            'uptime': 0.95,
                            'latency_ms': 25.0,
                            'throughput': 15.0,
                            'success_rate': 90.0
                        }
                        break
                        
            if corresponding_node_id:
                # Get metrics from simulated network or use mock metrics
                if corresponding_node_id in self.simulated_network:
                    node_metrics = self.simulated_network[corresponding_node_id]['metrics']
                else:
                    node_metrics = mock_metrics
                    
                print(f"   ✅ Representative Node Selected: {corresponding_node_id[:20]}...")
                print(f"   ⏱️  Consensus Time: {consensus_time:.3f}s")
                print(f"   📊 Node Metrics:")
                print(f"      ⬆️  Uptime: {node_metrics['uptime']:.1%}")
                print(f"      🚀 Latency: {node_metrics['latency_ms']:.0f}ms")
                print(f"      📈 Throughput: {node_metrics['throughput']:.1f} probes/min")
                print(f"      🎯 Success Rate: {node_metrics['success_rate']:.1f}%")
                
                return (selected_node, corresponding_node_id)
            else:
                print(f"   ❌ Could not find node_id for selected public key")
                return None
        else:
            print(f"   ❌ No representative node selected")
            return None
    
    def simulate_block_creation(self, consensus_result: tuple[str, str], tx_type: str = "random") -> Block:
        """
        Simulate block creation by the selected representative node.
        """
        print(f"\n📦 BLOCK CREATION SIMULATION")
        print("=" * 60)
        
        rep_public_key, rep_node_id = consensus_result
        
        # Track block creation timing
        block_creation_start = time.time()
        
        # Don't create new transactions - use existing ones from pool
        print(f"   🔨 Representative Node: {rep_node_id[:20]}...")
        print(f"   💳 Transactions in Pool: {len(self.transaction_pool)}")
        
        # Simulate block creation time based on node performance
        if rep_node_id in self.simulated_network:
            node_conditions = self.simulated_network[rep_node_id]['conditions']
        else:
            # Use default conditions for genesis or other nodes
            node_conditions = {
                'uptime': 0.95,
                'latency': self.base_latency
            }
        
        # Better nodes create blocks faster - optimized for high throughput
        base_creation_time = 0.5  # 500ms base (reduced from 2s for higher throughput)
        uptime_factor = node_conditions['uptime']  # Higher uptime = faster
        latency_factor = 1.0 + (node_conditions['latency'] - self.base_latency) * 5  # Reduced impact for speed
        
        creation_time = base_creation_time * latency_factor / uptime_factor
        
        print(f"   ⏱️  Block Creation Time: {creation_time:.2f}s")
        time.sleep(min(creation_time, 0.3))  # Reduced sleep time for faster simulation
        
        # Get previous block hash
        previous_hash = BlockchainUtils.hash(self.blockchain.blocks[-1].payload()).hex() if len(self.blockchain.blocks) > 1 else "0" * 64
        block_count = len(self.blockchain.blocks)
        
        # Track transaction processing - use all available transactions (blockchain will select optimal amount)
        transactions_to_include = self.transaction_pool[:]  # Take all available transactions
        processing_start = time.time()
        
        # Create the block
        try:
            new_block = Block(
                transactions=transactions_to_include,
                last_hash=previous_hash,
                forger=rep_public_key,
                block_count=block_count
            )
            
            processing_end = time.time()
            total_block_time = processing_end - block_creation_start
            processing_time = processing_end - processing_start
            
            # Update transaction confirmation times - REMOVE this as it will be done later
            # for tx in transactions_to_include:
            #     if hasattr(tx, 'tx_id'):
            #         self.transaction_metrics['confirmation_times'][tx.tx_id] = processing_end
            
            # Calculate transaction throughput for this block
            if total_block_time > 0:
                block_throughput = len(transactions_to_include) / total_block_time
                
            print(f"   ✅ Block Created Successfully!")
            print(f"      📦 Block Hash: {BlockchainUtils.hash(new_block.payload()).hex()[:24]}...")
            print(f"      💳 Transactions: {len(new_block.transactions)}")
            print(f"      🔢 Block Count: {new_block.block_count}")
            print(f"      ⏱️  Total Block Time: {total_block_time:.3f}s")
            print(f"      🚀 Block TX Throughput: {block_throughput:.1f} tx/s")
            print(f"      📊 Processing Time: {processing_time:.3f}s")
            
            # Remove processed transactions from pool
            for tx in new_block.transactions:
                if tx in self.transaction_pool:
                    self.transaction_pool.remove(tx)
            
            return new_block
            
        except Exception as e:
            print(f"   ❌ Block Creation Failed: {e}")
            raise e
    
    def create_sample_transactions(self, count: int = 5, tx_type: str = "random") -> List[Transaction]:
        """
        Create sample transactions for the block with flexible options
        
        Args:
            count: Number of transactions to create
            tx_type: Type of transactions ('random', 'micro', 'large', 'mixed', 'stress')
        """
        transactions = []
        transaction_start_time = time.time()
        
        print(f"   🔄 Creating {count} {tx_type} transactions...")
        
        for i in range(count):
            # Track total timing (including wallet selection)
            tx_total_start = time.time()
            
            # Use pre-created wallets for high performance (no key generation overhead)
            sender = random.choice(self.wallet_pool)
            receiver = random.choice(self.wallet_pool)
            
            # Determine transaction amount based on type
            if tx_type == "micro":
                amount = random.uniform(0.001, 0.1)  # Micro transactions
            elif tx_type == "large":
                amount = random.uniform(50.0, 500.0)  # Large transactions
            elif tx_type == "mixed":
                # Mix of small, medium, and large
                weights = [0.5, 0.3, 0.2]  # 50% small, 30% medium, 20% large
                tx_size = random.choices(['small', 'medium', 'large'], weights=weights)[0]
                if tx_size == 'small':
                    amount = random.uniform(0.1, 5.0)
                elif tx_size == 'medium':
                    amount = random.uniform(5.0, 50.0)
                else:  # large
                    amount = random.uniform(50.0, 200.0)
            elif tx_type == "stress":
                # High-frequency small transactions for stress testing
                amount = random.uniform(0.01, 1.0)
            else:  # random (default)
                amount = random.uniform(0.1, 10.0)
            
            # Track pure transaction creation timing (after wallet is available)
            tx_creation_start = time.time()
            
            # Create transaction
            transaction = sender.create_transaction(receiver.public_key_string(), amount, "MINING")
            
            tx_creation_end = time.time()
            tx_total_end = time.time()
            
            # Calculate both timing metrics
            total_duration = tx_total_end - tx_total_start  # Includes wallet selection
            pure_creation_duration = tx_creation_end - tx_creation_start  # Pure transaction creation
            
            if transaction:
                # Generate unique transaction ID
                tx_id = f"tx_{int(tx_creation_start * 1000000)}_{i}"
                
                # Store both timing metrics
                self.transaction_metrics['creation_times'][tx_id] = tx_creation_start
                self.transaction_metrics['processing_times'][tx_id] = total_duration  # Total time including wallet selection
                self.transaction_metrics['pure_tx_times'][tx_id] = pure_creation_duration  # Pure transaction creation only
                self.transaction_metrics['total_transactions'] += 1
                
                # Add custom metadata to track transaction
                transaction.tx_id = tx_id
                transaction.tx_type = tx_type
                transaction.creation_time = tx_creation_start
                
                transactions.append(transaction)
                self.transaction_metrics['successful_transactions'] += 1
            else:
                self.transaction_metrics['failed_transactions'] += 1
        
        total_creation_time = time.time() - transaction_start_time
        
        # Calculate throughput
        if total_creation_time > 0:
            throughput = len(transactions) / total_creation_time
            self.transaction_metrics['throughput_history'].append(
                (time.time(), len(transactions), total_creation_time)
            )
            
            print(f"   📊 Transaction Creation Metrics:")
            print(f"      ✅ Created: {len(transactions)}/{count} transactions")
            print(f"      ⏱️  Total Time: {total_creation_time:.3f}s")
            print(f"      🚀 Throughput: {throughput:.1f} tx/s")
            print(f"      📈 Avg per TX: {total_creation_time/count*1000:.2f}ms")
                
        return transactions
    
    def simulate_network_propagation(self, block: Block, forger_node_id: str) -> Dict:
        """Simulate block propagation across the network"""
        print(f"\n📡 NETWORK PROPAGATION SIMULATION")
        print("=" * 60)
        
        propagation_results = {
            'propagation_start': time.time(),
            'successful_nodes': [],
            'failed_nodes': [],
            'propagation_times': {}
        }
        
        # Simulate propagation to each node
        for node_id, node_data in self.simulated_network.items():
            if node_id == forger_node_id or node_id.startswith('-----BEGIN'):
                continue  # Skip the forger node or genesis nodes
                
            node_conditions = node_data['conditions']
            
            # Calculate propagation time based on network conditions
            base_prop_time = 0.1  # 100ms base
            latency_factor = node_conditions['latency'] / self.base_latency
            uptime_factor = node_conditions['uptime']
            
            # Random network jitter
            jitter = random.uniform(0.05, 0.3)
            
            propagation_time = (base_prop_time * latency_factor + jitter) / uptime_factor
            
            # Simulate success/failure based on node reliability
            success_probability = node_conditions['uptime'] * 0.9  # 90% of uptime reliability
            
            if random.random() < success_probability:
                propagation_results['successful_nodes'].append(node_id)
                propagation_results['propagation_times'][node_id] = propagation_time
                time.sleep(0.01)  # Small delay for realism
            else:
                propagation_results['failed_nodes'].append(node_id)
        
        # Calculate statistics
        successful_count = len(propagation_results['successful_nodes'])
        total_nodes = len(self.simulated_network) - 1  # Exclude forger
        success_rate = successful_count / total_nodes * 100
        
        if propagation_results['propagation_times']:
            avg_propagation = sum(propagation_results['propagation_times'].values()) / len(propagation_results['propagation_times'])
            max_propagation = max(propagation_results['propagation_times'].values())
        else:
            avg_propagation = 0
            max_propagation = 0
        
        print(f"   📊 Propagation Results:")
        print(f"      ✅ Successful: {successful_count}/{total_nodes} nodes ({success_rate:.1f}%)")
        print(f"      ❌ Failed: {len(propagation_results['failed_nodes'])} nodes")
        print(f"      ⏱️  Average Time: {avg_propagation:.3f}s")
        print(f"      🐌 Max Time: {max_propagation:.3f}s")
        
        return propagation_results
    
    def add_block_to_blockchain(self, block: Block):
        """Add the validated block to the blockchain"""
        self.blockchain.add_block(block)
        
        print(f"\n⛓️  BLOCKCHAIN UPDATE")
        print("=" * 60)
        print(f"   📦 Block {block.block_count} added to blockchain")
        print(f"   📏 Blockchain Length: {len(self.blockchain.blocks)} blocks")
        print(f"   🔗 Latest Hash: {BlockchainUtils.hash(block.payload()).hex()[:24]}...")
        
    def display_network_status(self):
        """Display final network status and statistics"""
        print(f"\n📈 NETWORK STATUS SUMMARY")
        print("=" * 60)
        
        total_nodes = len(self.simulated_network)
        active_nodes = len([n for n in self.consensus.nodes.keys() if self.consensus.calculate_uptime(n) > 0.7])
        
        print(f"   🌐 Total Nodes: {total_nodes}")
        print(f"   ✅ Active Nodes: {active_nodes} ({active_nodes/total_nodes*100:.1f}%)")
        print(f"   ⛓️  Blockchain Length: {len(self.blockchain.blocks)} blocks")
        print(f"   💳 Transaction Pool: {len(self.transaction_pool)} pending")
        
        # Calculate network averages
        avg_uptime = sum(n['conditions']['uptime'] for n in self.simulated_network.values()) / total_nodes
        avg_latency = sum(n['conditions']['latency'] for n in self.simulated_network.values()) / total_nodes * 1000
        
        print(f"   📊 Network Averages:")
        print(f"      ⬆️  Uptime: {avg_uptime:.1%}")
        print(f"      🚀 Latency: {avg_latency:.1f}ms")
        
        # Display transaction metrics
        self.display_transaction_metrics()
        
    def display_transaction_metrics(self):
        """Display comprehensive transaction timing and throughput metrics"""
        print(f"\n💳 TRANSACTION PERFORMANCE METRICS")
        print("=" * 60)
        
        metrics = self.transaction_metrics
        
        print(f"   📊 Transaction Summary:")
        print(f"      ✅ Successful: {metrics['successful_transactions']}")
        print(f"      ❌ Failed: {metrics['failed_transactions']}")
        print(f"      📦 Total: {metrics['total_transactions']}")
        
        if metrics['successful_transactions'] > 0:
            success_rate = (metrics['successful_transactions'] / metrics['total_transactions']) * 100
            print(f"      🎯 Success Rate: {success_rate:.1f}%")
        
        # Calculate timing statistics
        if metrics['processing_times']:
            processing_times = list(metrics['processing_times'].values())
            avg_processing = sum(processing_times) / len(processing_times)
            min_processing = min(processing_times)
            max_processing = max(processing_times)
            
            print(f"\n   ⏱️  Total Transaction Times (includes wallet selection):")
            print(f"      📈 Average: {avg_processing*1000:.2f}ms")
            print(f"      ⚡ Fastest: {min_processing*1000:.2f}ms")
            print(f"      🐌 Slowest: {max_processing*1000:.2f}ms")
        
        # Calculate pure transaction creation timing (after wallet is available)
        if metrics['pure_tx_times']:
            pure_times = list(metrics['pure_tx_times'].values())
            avg_pure = sum(pure_times) / len(pure_times)
            min_pure = min(pure_times)
            max_pure = max(pure_times)
            
            print(f"\n   🔥 Pure Transaction Creation Times (wallet already available):")
            print(f"      📈 Average: {avg_pure*1000:.2f}ms")
            print(f"      ⚡ Fastest: {min_pure*1000:.2f}ms")
            print(f"      🐌 Slowest: {max_pure*1000:.2f}ms")
        
        # Calculate end-to-end transaction times (creation to confirmation)
        if metrics['creation_times'] and metrics['confirmation_times']:
            end_to_end_times = []
            for tx_id in metrics['creation_times']:
                if tx_id in metrics['confirmation_times']:
                    e2e_time = metrics['confirmation_times'][tx_id] - metrics['creation_times'][tx_id]
                    end_to_end_times.append(e2e_time)
            
            if end_to_end_times:
                avg_e2e = sum(end_to_end_times) / len(end_to_end_times)
                min_e2e = min(end_to_end_times)
                max_e2e = max(end_to_end_times)
                
                print(f"\n   🔄 End-to-End Transaction Times:")
                print(f"      📈 Average: {avg_e2e:.3f}s")
                print(f"      ⚡ Fastest: {min_e2e:.3f}s")
                print(f"      🐌 Slowest: {max_e2e:.3f}s")
        
        # Calculate overall throughput
        if metrics['throughput_history']:
            total_tx = sum(entry[1] for entry in metrics['throughput_history'])
            total_time = sum(entry[2] for entry in metrics['throughput_history'])
            
            if total_time > 0:
                overall_throughput = total_tx / total_time
                print(f"\n   🚀 Overall Throughput: {overall_throughput:.1f} tx/s")
                
                # Display throughput history
                print(f"   📊 Throughput History:")
                for i, (timestamp, tx_count, duration) in enumerate(metrics['throughput_history']):
                    batch_throughput = tx_count / duration if duration > 0 else 0
                    print(f"      Batch {i+1}: {tx_count} tx in {duration:.3f}s = {batch_throughput:.1f} tx/s")
        
    def run_complete_simulation(self, tx_type: str = "random"):
        """Run the complete simulation from setup to block creation"""
        print("🚀 QUANTUM BLOCKCHAIN CONSENSUS SIMULATION")
        print("=" * 80)
        print(f"   📅 Simulation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   🔮 Quantum Annealing Consensus Protocol")
        print(f"   🌐 Distributed Network Simulation")
        print(f"   💳 Transaction Type: {tx_type.upper()}")
        
        # Step 1: Setup network
        self.setup_simulated_network()
        
        # Step 2: Blockchain already initialized with genesis block
        print(f"\n   🏗️  Using existing genesis block: {BlockchainUtils.hash(self.blockchain.blocks[0].payload()).hex()[:24]}...")
        
        # Step 3: Create transactions FIRST (simulate users creating transactions)
        initial_transactions = self.create_sample_transactions(random.randint(3, 7), tx_type)
        self.transaction_pool.extend(initial_transactions)
        print(f"\n   💳 Transaction Pool: {len(self.transaction_pool)} pending transactions")
        
        # Step 4: Run consensus simulation
        consensus_result = self.simulate_consensus_round()
        
        if not consensus_result:
            print(f"\n❌ Simulation failed: No representative node selected")
            return False
        
        rep_public_key, rep_node_id = consensus_result
        
        # Step 5: Create block with existing transactions
        new_block = self.simulate_block_creation((rep_public_key, rep_node_id), tx_type)
        
        # Step 6: Simulate network propagation
        propagation_results = self.simulate_network_propagation(new_block, rep_node_id)
        
        # Step 7: Add to blockchain
        self.add_block_to_blockchain(new_block)
        
        # Step 8: Update transaction confirmation times AFTER full consensus+block process
        final_confirmation_time = time.time()
        for tx in new_block.transactions:
            if hasattr(tx, 'tx_id'):
                self.transaction_metrics['confirmation_times'][tx.tx_id] = final_confirmation_time
        
        # Step 9: Update performance metrics
        self.consensus.record_proposal_result(rep_public_key, True)
        
        # Step 10: Display final status
        self.display_network_status()
        
        return True
    
    def run_transaction_stress_test(self, rounds: int = 3, transactions_per_round: int = 20, tx_type: str = "stress"):
        """Run a stress test with high transaction volume"""
        print(f"\n🔥 TRANSACTION STRESS TEST")
        print("=" * 80)
        print(f"   🎯 Rounds: {rounds}")
        print(f"   💳 Transactions per Round: {transactions_per_round}")
        print(f"   📊 Transaction Type: {tx_type.upper()}")
        
        stress_start_time = time.time()
        
        # Setup network first
        if not self.simulated_network:
            self.setup_simulated_network()
        
        total_transactions_processed = 0
        
        for round_num in range(1, rounds + 1):
            print(f"\n🔄 === STRESS TEST ROUND {round_num}/{rounds} ===")
            
            round_start = time.time()
            
            # Create high volume of transactions FIRST (before consensus)
            stress_transactions = self.create_sample_transactions(transactions_per_round, tx_type)
            self.transaction_pool.extend(stress_transactions)
            
            # Run consensus
            consensus_result = self.simulate_consensus_round()
            if consensus_result:
                rep_public_key, rep_node_id = consensus_result
                
                # Process multiple blocks if needed
                blocks_created = 0
                while len(self.transaction_pool) > 0 and blocks_created < 5:  # Max 5 blocks per round
                    new_block = self.simulate_block_creation((rep_public_key, rep_node_id), tx_type)
                    
                    # Simulate network propagation for each block
                    propagation_results = self.simulate_network_propagation(new_block, rep_node_id)
                    
                    # Add to blockchain
                    self.add_block_to_blockchain(new_block)
                    
                    # Update transaction confirmation times AFTER full process
                    final_confirmation_time = time.time()
                    for tx in new_block.transactions:
                        if hasattr(tx, 'tx_id'):
                            self.transaction_metrics['confirmation_times'][tx.tx_id] = final_confirmation_time
                    
                    total_transactions_processed += len(new_block.transactions)
                    blocks_created += 1
                    
                    if len(self.transaction_pool) == 0:
                        break
            
            round_time = time.time() - round_start
            round_throughput = transactions_per_round / round_time if round_time > 0 else 0
            
            print(f"   ⏱️  Round {round_num} Time: {round_time:.3f}s")
            print(f"   🚀 Round {round_num} Throughput: {round_throughput:.1f} tx/s")
            
            # Brief pause between rounds
            time.sleep(0.5)
        
        # Calculate overall stress test metrics
        total_stress_time = time.time() - stress_start_time
        overall_throughput = total_transactions_processed / total_stress_time if total_stress_time > 0 else 0
        
        print(f"\n🎉 STRESS TEST COMPLETED")
        print("=" * 60)
        print(f"   📊 Total Transactions Processed: {total_transactions_processed}")
        print(f"   ⏱️  Total Time: {total_stress_time:.3f}s")
        print(f"   🚀 Overall Throughput: {overall_throughput:.1f} tx/s")
        print(f"   ⛓️  Final Blockchain Length: {len(self.blockchain.blocks)} blocks")
        
        # Display detailed metrics
        self.display_transaction_metrics()
        
        return True


def main():
    """Main simulation entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Quantum Blockchain Consensus Simulator')
    parser.add_argument('--nodes', type=int, default=10, help='Number of nodes in the network')
    parser.add_argument('--rounds', type=int, default=1, help='Number of consensus rounds to run')
    parser.add_argument('--tx-type', choices=['random', 'micro', 'large', 'mixed', 'stress'], 
                       default='random', help='Type of transactions to generate')
    parser.add_argument('--stress-test', action='store_true', 
                       help='Run transaction stress test')
    parser.add_argument('--tx-per-round', type=int, default=20,
                       help='Transactions per round in stress test')
    
    args = parser.parse_args()
    
    try:
        # Create and run simulator
        simulator = QuantumConsensusSimulator(num_nodes=args.nodes)
        
        if args.stress_test:
            simulator.run_transaction_stress_test(
                rounds=args.rounds, 
                transactions_per_round=args.tx_per_round,
                tx_type=args.tx_type
            )
        else:
            simulator.run_complete_simulation(tx_type=args.tx_type)
        
        print(f"\n🎉 Simulation completed successfully!")
        print(f"   ⛓️  Final blockchain length: {len(simulator.blockchain.blocks)} blocks")
        print(f"   🌐 Network nodes: {len(simulator.simulated_network)}")
        print(f"   💳 Total transactions processed: {simulator.transaction_metrics['successful_transactions']}")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Simulation interrupted by user")
    except Exception as e:
        print(f"\n❌ Simulation error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
