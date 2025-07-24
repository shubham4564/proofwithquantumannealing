#!/usr/bin/env python3

import sys
import os
import random
import time
import threading
from datetime import datetime
sys.path.insert(0, '/Users/shubham/Documents/proofwithquantumannealing/blockchain')

from blockchain.transaction.wallet import Wallet
from blockchain.transaction.transaction import Transaction
from blockchain.utils.helpers import BlockchainUtils
import requests
import json

def create_transaction_with_timing(sender_wallet, receiver_public_key, amount, transaction_type='TRANSFER'):
    """Create and return an encoded transaction with timing measurements"""
    timings = {}
    
    # Time transaction creation and signing
    start_time = time.time()
    transaction = sender_wallet.create_transaction(receiver_public_key, amount, transaction_type)
    timings['transaction_creation_signing'] = time.time() - start_time
    
    # Time encoding
    start_time = time.time()
    encoded_transaction = BlockchainUtils.encode(transaction)
    timings['transaction_encoding'] = time.time() - start_time
    
    return encoded_transaction, timings

def submit_transaction_with_timing(encoded_transaction, node_port=11001):
    """Submit transaction to the specified node with timing"""
    url = f'http://localhost:{node_port}/api/v1/transaction/create/'
    
    # Time network submission
    start_time = time.time()
    try:
        response = requests.post(url, json={'transaction': encoded_transaction}, timeout=10)
        submission_time = time.time() - start_time
        return response.status_code, response.text, submission_time
    except Exception as e:
        submission_time = time.time() - start_time
        return 0, str(e), submission_time

def monitor_blockchain_changes(api_ports, initial_blocks, monitoring_results, stop_event):
    """Monitor blockchain changes across all nodes and record timing"""
    monitoring_results['first_block_detected'] = None
    monitoring_results['all_nodes_synced'] = None
    monitoring_results['block_propagation_times'] = []
    
    start_monitoring = time.time()
    
    while not stop_event.is_set():
        current_blocks = []
        check_time = time.time()
        
        for port in api_ports:
            blocks, _ = get_blockchain_status(port)
            current_blocks.append(blocks)
        
        max_blocks = max(current_blocks)
        min_blocks = min(current_blocks)
        
        # Detect first new block
        if max_blocks > initial_blocks and monitoring_results['first_block_detected'] is None:
            monitoring_results['first_block_detected'] = check_time - start_monitoring
            print(f"   🎯 First new block detected at {monitoring_results['first_block_detected']:.3f}s")
        
        # Detect when all nodes are synced
        if max_blocks > initial_blocks and max_blocks == min_blocks and monitoring_results['all_nodes_synced'] is None:
            monitoring_results['all_nodes_synced'] = check_time - start_monitoring
            print(f"   🔄 All nodes synchronized at {monitoring_results['all_nodes_synced']:.3f}s")
        
        # Record propagation progress
        if max_blocks > initial_blocks:
            nodes_with_new_blocks = sum(1 for blocks in current_blocks if blocks > initial_blocks)
            monitoring_results['block_propagation_times'].append({
                'time': check_time - start_monitoring,
                'nodes_synced': nodes_with_new_blocks,
                'total_nodes': len(api_ports)
            })
        
        time.sleep(0.1)  # Check every 100ms

def get_blockchain_status(node_port=11000):
    """Get blockchain status from a node"""
    try:
        url = f'http://localhost:{node_port}/api/v1/blockchain/'
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return len(data['blocks']), data.get('transaction_pool_size', 0)
        return 0, 0
    except:
        return 0, 0

def get_detailed_blockchain_data(node_port=11000):
    """Get detailed blockchain data including blocks and metrics"""
    try:
        url = f'http://localhost:{node_port}/api/v1/blockchain/'
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_quantum_metrics(node_port=11000):
    """Get quantum consensus metrics from a node"""
    try:
        url = f'http://localhost:{node_port}/api/v1/blockchain/quantum-metrics/'
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_active_nodes(api_ports):
    """Get list of active nodes by checking their API endpoints"""
    active_nodes = []
    for port in api_ports:
        try:
            url = f'http://localhost:{port}/api/v1/blockchain/'
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                active_nodes.append(port)
        except:
            continue
    return active_nodes

def analyze_forgers_and_metrics(api_ports):
    """Analyze which nodes forged blocks and their quantum metrics"""
    print(f"\n🔍 DETAILED FORGER AND METRICS ANALYSIS")
    print("=" * 80)
    
    forger_stats = {}
    node_metrics = {}
    all_blocks = []
    
    # Collect data from all nodes
    for port in api_ports:
        node_num = port - 11000 + 1
        
        # Get blockchain data
        blockchain_data = get_detailed_blockchain_data(port)
        if blockchain_data and 'blocks' in blockchain_data:
            blocks = blockchain_data['blocks']
            all_blocks.extend([(block, node_num, port) for block in blocks])
        
        # Get quantum metrics
        metrics = get_quantum_metrics(port)
        if metrics:
            node_metrics[port] = metrics
    
    # Analyze forgers from blocks
    print(f"\n📦 BLOCK FORGING ANALYSIS:")
    print("-" * 50)
    
    if all_blocks:
        # Sort blocks by block_count to get chronological order
        all_blocks.sort(key=lambda x: x[0].get('block_count', 0))
        
        for block, source_node, source_port in all_blocks:
            block_num = block.get('block_count', 0)
            forger = block.get('forger', 'Unknown')
            timestamp = block.get('timestamp', 0)
            tx_count = len(block.get('transactions', []))
            
            # Track forger statistics
            if forger not in forger_stats:
                forger_stats[forger] = {
                    'blocks_forged': 0,
                    'total_transactions': 0,
                    'first_block': None,
                    'last_block': None,
                    'block_numbers': []
                }
            
            forger_stats[forger]['blocks_forged'] += 1
            forger_stats[forger]['total_transactions'] += tx_count
            forger_stats[forger]['block_numbers'].append(block_num)
            
            if forger_stats[forger]['first_block'] is None:
                forger_stats[forger]['first_block'] = block_num
            forger_stats[forger]['last_block'] = block_num
            
            # Show block details
            forger_short = forger[:40] + "..." if len(forger) > 40 else forger
            formatted_time = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S") if timestamp > 0 else "N/A"
            print(f"   Block {block_num:2d}: Forger={forger_short}")
            print(f"            Time={formatted_time}, Transactions={tx_count}, Source=Node{source_node}")
    
    # Display forger summary
    print(f"\n👨‍💼 FORGER SUMMARY:")
    print("-" * 50)
    
    if forger_stats:
        sorted_forgers = sorted(forger_stats.items(), key=lambda x: x[1]['blocks_forged'], reverse=True)
        
        for i, (forger, stats) in enumerate(sorted_forgers, 1):
            forger_short = forger[:40] + "..." if len(forger) > 40 else forger
            block_range = f"{stats['first_block']}-{stats['last_block']}" if stats['first_block'] != stats['last_block'] else str(stats['first_block'])
            
            print(f"\n   🏆 Rank {i}: {forger_short}")
            print(f"      📦 Blocks Forged: {stats['blocks_forged']}")
            print(f"      💳 Total Transactions: {stats['total_transactions']}")
            print(f"      📊 Block Range: {block_range}")
            print(f"      📋 Block Numbers: {stats['block_numbers']}")
            
            if stats['blocks_forged'] > 0:
                avg_tx_per_block = stats['total_transactions'] / stats['blocks_forged']
                print(f"      ⚡ Avg Transactions/Block: {avg_tx_per_block:.1f}")
    else:
        print("   ❌ No blocks found or no forging activity detected")
    
    # Display quantum consensus metrics
    print(f"\n🔮 QUANTUM CONSENSUS METRICS:")
    print("-" * 50)
    
    if node_metrics:
        for port, metrics in node_metrics.items():
            node_num = port - 11000 + 1
            print(f"\n   🖥️  Node {node_num} (Port {port}):")
            
            # Basic consensus info
            if 'consensus_type' in metrics:
                print(f"      🎯 Consensus Type: {metrics['consensus_type']}")
            
            if 'total_nodes' in metrics:
                print(f"      🌐 Total Nodes in Network: {metrics['total_nodes']}")
                print(f"      ✅ Active Nodes: {metrics.get('active_nodes', 'N/A')}")
            
            if 'probe_count' in metrics:
                print(f"      🔍 Total Probes: {metrics['probe_count']}")
            
            # Node-specific scores and metrics
            if 'node_scores' in metrics and metrics['node_scores']:
                print(f"      📊 Node Performance Scores:")
                
                # Sort nodes by suitability score
                sorted_nodes = sorted(
                    metrics['node_scores'].items(), 
                    key=lambda x: x[1].get('suitability_score', 0), 
                    reverse=True
                )
                
                probe_stats = metrics.get('probe_statistics', {})
                
                for node_id, scores in sorted_nodes[:5]:  # Show top 5 nodes
                    node_short = node_id[:30] + "..." if len(node_id) > 30 else node_id
                    
                    uptime = scores.get('uptime', 0)
                    latency = scores.get('latency', float('inf'))
                    throughput = scores.get('throughput', 0)
                    suitability = scores.get('suitability_score', 0)
                    effective = scores.get('effective_score', 0)
                    success = scores.get('proposals_success', 0)
                    failed = scores.get('proposals_failed', 0)
                    
                    # Get probe counts from probe_statistics
                    node_probe_stats = probe_stats.get(node_id, {})
                    probes_sent = node_probe_stats.get('probes_sent', 0)
                    probes_received = node_probe_stats.get('probes_received', 0)
                    witness_count = node_probe_stats.get('witness_count', 0)
                    
                    # Format latency display
                    latency_str = f"{latency*1000:.1f}ms" if latency != float('inf') and latency < 999 else "∞"
                    
                    print(f"         🔹 {node_short}")
                    print(f"            ⬆️  Uptime: {uptime:.3f} | 🚀 Latency: {latency_str} | 📈 Throughput: {throughput:.2f}")
                    print(f"            🎯 Suitability: {suitability:.4f} | ⚡ Effective: {effective:.4f}")
                    print(f"            ✅ Success: {success} | ❌ Failed: {failed}")
                    print(f"            📡 Probes: ↗️{probes_sent} sent | ↙️{probes_received} recv | 👁️{witness_count} witness")
            
            # Protocol parameters
            if 'protocol_parameters' in metrics:
                params = metrics['protocol_parameters']
                print(f"      ⚙️  Protocol Parameters:")
                print(f"         ⏱️  Max Delay Tolerance: {params.get('max_delay_tolerance', 'N/A')}s")
                print(f"         ⌛ Block Proposal Timeout: {params.get('block_proposal_timeout', 'N/A')}s")
                print(f"         👥 Witness Quorum Size: {params.get('witness_quorum_size', 'N/A')}")
                print(f"         💰 Penalty Coefficient: {params.get('penalty_coefficient', 'N/A')}")
            
            # Quantum annealing configuration
            if 'quantum_annealing_config' in metrics:
                quantum = metrics['quantum_annealing_config']
                print(f"      🔮 Quantum Annealing Config:")
                print(f"         ⏰ Annealing Time: {quantum.get('annealing_time_microseconds', 'N/A')}μs")
                print(f"         🔄 Num Reads: {quantum.get('num_reads', 'N/A')}")
                print(f"         🖥️  Simulator Enabled: {quantum.get('simulator_enabled', 'N/A')}")
                print(f"         🎲 Perturbation Epsilon: {quantum.get('perturbation_epsilon', 'N/A')}")
            
            # Scoring weights
            if 'scoring_weights' in metrics:
                weights = metrics['scoring_weights']
                print(f"      ⚖️  Scoring Weights:")
                print(f"         ⬆️  Uptime: {weights.get('uptime', 'N/A')}")
                print(f"         🚀 Latency: {weights.get('latency', 'N/A')}")
                print(f"         📈 Throughput: {weights.get('throughput', 'N/A')}")
                print(f"         📊 Past Performance: {weights.get('past_performance', 'N/A')}")
            
            # Probe statistics summary
            if 'probe_statistics' in metrics and metrics['probe_statistics']:
                print(f"      📡 Probe Statistics Summary:")
                probe_stats = metrics['probe_statistics']
                total_sent = sum(stats.get('probes_sent', 0) for stats in probe_stats.values())
                total_received = sum(stats.get('probes_received', 0) for stats in probe_stats.values())
                total_witness = sum(stats.get('witness_count', 0) for stats in probe_stats.values())
                active_probe_nodes = len([node for node, stats in probe_stats.items() 
                                        if stats.get('probes_sent', 0) > 0 or stats.get('probes_received', 0) > 0])
                
                print(f"         📤 Total Probes Sent: {total_sent}")
                print(f"         📥 Total Probes Received: {total_received}")
                print(f"         👁️  Total Witness Events: {total_witness}")
                print(f"         🔄 Active Probe Nodes: {active_probe_nodes}")
                
                if active_probe_nodes > 0:
                    avg_sent = total_sent / active_probe_nodes
                    avg_received = total_received / active_probe_nodes
                    print(f"         📊 Avg Probes/Node: ↗️{avg_sent:.1f} sent | ↙️{avg_received:.1f} recv")
    else:
        print("   ❌ No quantum metrics available from any node")
    
    return forger_stats, node_metrics

def get_forger_performance_correlation(forger_stats, node_metrics):
    """Correlate forger performance with quantum metrics"""
    print(f"\n🔗 FORGER PERFORMANCE CORRELATION:")
    print("-" * 50)
    
    if not forger_stats or not node_metrics:
        print("   ❌ Insufficient data for correlation analysis")
        return
    
    # Try to match forgers with their quantum metrics
    correlations = []
    
    for forger, stats in forger_stats.items():
        # Find this forger in node metrics
        matching_metrics = None
        for port, metrics in node_metrics.items():
            if 'node_scores' in metrics:
                for node_id, scores in metrics['node_scores'].items():
                    if node_id == forger:
                        matching_metrics = scores
                        break
        
        if matching_metrics:
            correlations.append({
                'forger': forger,
                'blocks_forged': stats['blocks_forged'],
                'total_transactions': stats['total_transactions'],
                'uptime': matching_metrics.get('uptime', 0),
                'latency': matching_metrics.get('latency', float('inf')),
                'throughput': matching_metrics.get('throughput', 0),
                'suitability_score': matching_metrics.get('suitability_score', 0),
                'proposals_success': matching_metrics.get('proposals_success', 0),
                'proposals_failed': matching_metrics.get('proposals_failed', 0),
                'probes_sent': matching_metrics.get('probes_sent', 0),
                'probes_received': matching_metrics.get('probes_received', 0),
                'witness_count': matching_metrics.get('witness_count', 0)
            })
    
    if correlations:
        # Sort by blocks forged
        correlations.sort(key=lambda x: x['blocks_forged'], reverse=True)
        
        print(f"   📊 Forger Performance vs Quantum Metrics:")
        print(f"   {'Rank':<4} {'Forger':<25} {'Blks':<4} {'Uptime':<7} {'Latency':<9} {'Thput':<7} {'Suit':<8} {'S/F':<8} {'Probes S/R/W':<12}")
        print(f"   {'-'*4} {'-'*25} {'-'*4} {'-'*7} {'-'*9} {'-'*7} {'-'*8} {'-'*8} {'-'*12}")
        
        for i, corr in enumerate(correlations, 1):
            forger_short = corr['forger'][:20] + "..." if len(corr['forger']) > 23 else corr['forger'][:23]
            latency_str = f"{corr['latency']*1000:.1f}ms" if corr['latency'] != float('inf') else "∞"
            success_fail = f"{corr['proposals_success']}/{corr['proposals_failed']}"
            probe_stats = f"{corr['probes_sent']}/{corr['probes_received']}/{corr['witness_count']}"
            
            print(f"   {i:<4} {forger_short:<25} {corr['blocks_forged']:<4} {corr['uptime']:.3f}   "
                  f"{latency_str:<9} {corr['throughput']:<7.2f} {corr['suitability_score']:<8.4f} {success_fail:<8} {probe_stats:<12}")
        
        # Calculate some basic statistics
        total_blocks = sum(c['blocks_forged'] for c in correlations)
        avg_uptime = sum(c['uptime'] for c in correlations) / len(correlations)
        active_forgers = sum(1 for c in correlations if c['blocks_forged'] > 0)
        total_probes_sent = sum(c['probes_sent'] for c in correlations)
        total_probes_received = sum(c['probes_received'] for c in correlations)
        total_witness_events = sum(c['witness_count'] for c in correlations)
        
        print(f"\n   📈 Network Performance Summary:")
        print(f"      🏆 Active Forgers: {active_forgers}")
        print(f"      📦 Total Blocks: {total_blocks}")
        print(f"      ⬆️  Average Uptime: {avg_uptime:.3f}")
        print(f"      📤 Total Probes Sent: {total_probes_sent}")
        print(f"      📥 Total Probes Received: {total_probes_received}")
        print(f"      👁️  Total Witness Events: {total_witness_events}")
        
        # Find the most efficient forger
        if correlations:
            best_forger = max(correlations, key=lambda x: x['suitability_score'])
            print(f"      🥇 Highest Suitability: {best_forger['suitability_score']:.4f} score")
            
            most_productive = max(correlations, key=lambda x: x['blocks_forged'])
            print(f"      🔥 Most Productive: {most_productive['blocks_forged']} blocks forged")
            
            most_probing = max(correlations, key=lambda x: x['probes_sent'])
            print(f"      📡 Most Active Prober: {most_probing['probes_sent']} probes sent")
            
            best_witness = max(correlations, key=lambda x: x['witness_count'])
            print(f"      👁️  Best Witness: {best_witness['witness_count']} witness events")
    else:
        print("   ❌ No correlations found between forgers and quantum metrics")
    
    return correlations

def run_transaction_test_with_detailed_timing(num_transactions):
    """Run transaction test with comprehensive timing measurements"""
    print(f"🚀 Starting {num_transactions}-Transaction Test with Detailed Timing")
    print("=" * 70)
    
    # API ports for all 10 nodes (11000-11009)
    api_ports = list(range(11000, 11010))
    
    # Check initial blockchain state
    initial_blocks, initial_pool = get_blockchain_status(11000)
    print(f"📊 Initial state: {initial_blocks} blocks, {initial_pool} transactions in pool")
    
    # Initialize timing collections
    timing_data = {
        'transaction_creation': [],
        'transaction_encoding': [],
        'network_submission': [],
        'total_submission_time': 0,
        'monitoring_start': 0,
        'first_pool_detection': None,
        'quantum_consensus_start': None,
        'first_block_forged': None,
        'block_propagation_complete': None
    }
    
    print(f"\n💳 Creating wallets and submitting {num_transactions} transactions with timing...")
    
    successful_transactions = 0
    failed_transactions = 0
    
    # Scale wallet count based on transaction count
    sender_count = min(max(1, num_transactions // 10), 20)
    receiver_count = min(max(1, num_transactions // 2), 100)
    
    # Create wallets
    wallet_creation_start = time.time()
    sender_wallets = [Wallet() for _ in range(sender_count)]
    receiver_wallets = [Wallet() for _ in range(receiver_count)]
    wallet_creation_time = time.time() - wallet_creation_start
    
    print(f"   🔑 Created {len(sender_wallets)} sender + {len(receiver_wallets)} receiver wallets in {wallet_creation_time:.3f}s")
    
    # Start monitoring thread
    monitoring_results = {}
    stop_monitoring = threading.Event()
    monitoring_thread = threading.Thread(
        target=monitor_blockchain_changes, 
        args=(api_ports, initial_blocks, monitoring_results, stop_monitoring)
    )
    
    # Track transaction submission timing
    submission_start = time.time()
    timing_data['monitoring_start'] = submission_start
    monitoring_thread.start()
    
    print(f"\n⏱️  Transaction Submission with Detailed Timing:")
    
    for i in range(1, num_transactions + 1):
        try:
            # Select random wallets and target
            sender_wallet = random.choice(sender_wallets)
            receiver_wallet = random.choice(receiver_wallets)
            target_port = random.choice(api_ports)
            
            # Create transaction with timing
            receiver_public_key = receiver_wallet.public_key_string()
            amount = random.uniform(1.0, 100.0)
            
            encoded_transaction, tx_timings = create_transaction_with_timing(
                sender_wallet, receiver_public_key, amount, "TRANSFER"
            )
            
            # Submit with timing
            status_code, response, submission_time = submit_transaction_with_timing(encoded_transaction, target_port)
            
            # Record timings
            timing_data['transaction_creation'].append(tx_timings['transaction_creation_signing'])
            timing_data['transaction_encoding'].append(tx_timings['transaction_encoding'])
            timing_data['network_submission'].append(submission_time)
            
            if status_code == 200:
                successful_transactions += 1
                node_num = target_port - 11000 + 1
                print(f"   ✅ Tx {i}: Node {node_num}, Creation: {tx_timings['transaction_creation_signing']*1000:.1f}ms, "
                      f"Encoding: {tx_timings['transaction_encoding']*1000:.1f}ms, Network: {submission_time*1000:.1f}ms")
            else:
                failed_transactions += 1
                if i <= 3:
                    print(f"   ❌ Tx {i}: Failed - {response[:50]}")
            
            # Small delay for monitoring
            time.sleep(0.1)
                
        except Exception as e:
            failed_transactions += 1
            if failed_transactions <= 3:
                print(f"   ❌ Tx {i} exception: {e}")
    
    timing_data['total_submission_time'] = time.time() - submission_start
    
    # Calculate submission statistics
    avg_creation = sum(timing_data['transaction_creation']) / len(timing_data['transaction_creation']) if timing_data['transaction_creation'] else 0
    avg_encoding = sum(timing_data['transaction_encoding']) / len(timing_data['transaction_encoding']) if timing_data['transaction_encoding'] else 0
    avg_network = sum(timing_data['network_submission']) / len(timing_data['network_submission']) if timing_data['network_submission'] else 0
    
    print(f"\n📈 Transaction Submission Timing Summary:")
    print(f"   ✅ Successful: {successful_transactions}")
    print(f"   ❌ Failed: {failed_transactions}")
    print(f"   ⏱️  Average Creation+Signing: {avg_creation*1000:.2f}ms")
    print(f"   ⏱️  Average Encoding: {avg_encoding*1000:.2f}ms")
    print(f"   ⏱️  Average Network Submission: {avg_network*1000:.2f}ms")
    print(f"   ⏱️  Total Submission Time: {timing_data['total_submission_time']:.3f}s")
    
    # Wait for consensus and block creation with monitoring
    wait_time = min(max(15, num_transactions // 3), 90)
    print(f"\n⏳ Monitoring quantum consensus and block forging for {wait_time} seconds...")
    print(f"   🔍 Real-time blockchain monitoring active...")
    
    time.sleep(wait_time)
    
    # Stop monitoring
    stop_monitoring.set()
    monitoring_thread.join()
    
    # Get active nodes only
    active_api_ports = get_active_nodes(api_ports)
    print(f"\n🌐 Detected {len(active_api_ports)} active nodes out of {len(api_ports)} configured")
    
    # Get final blockchain state from active nodes only
    print(f"\n📊 Final blockchain status with timing analysis:")
    max_blocks = 0
    min_blocks = float('inf')
    total_pool_size = 0
    
    for i, port in enumerate(active_api_ports, 1):
        blocks, pool_size = get_blockchain_status(port)
        max_blocks = max(max_blocks, blocks)
        min_blocks = min(min_blocks, blocks)
        total_pool_size += pool_size
        
        status_icon = "🟢" if blocks > initial_blocks else "🔴"
        print(f"   {status_icon} Node {i} (API {port}): {blocks} blocks, {pool_size} txs in pool")
    
    # Calculate timing analysis
    blocks_created = max_blocks - initial_blocks
    
    print(f"\n⏱️  DETAILED TIMING ANALYSIS:")
    print(f"=" * 50)
    
    if blocks_created > 0:
        print(f"   🎯 NEW BLOCKS CREATED: {blocks_created}")
        
        if monitoring_results.get('first_block_detected'):
            print(f"   ⚡ Time to First Block: {monitoring_results['first_block_detected']:.3f}s")
            print(f"   🔄 Time to Full Sync: {monitoring_results.get('all_nodes_synced', 'N/A'):.3f}s" if monitoring_results.get('all_nodes_synced') else "   🔄 Time to Full Sync: Not achieved")
            
            # Estimate quantum consensus time
            first_block_time = monitoring_results['first_block_detected']
            submission_time = timing_data['total_submission_time']
            
            if first_block_time > submission_time:
                estimated_consensus_time = first_block_time - submission_time
                print(f"   🔮 Estimated Quantum Consensus Time: {estimated_consensus_time:.3f}s")
            else:
                print(f"   🔮 Estimated Quantum Consensus Time: Concurrent with submission")
            
            # Block propagation analysis
            if monitoring_results.get('block_propagation_times'):
                propagation_data = monitoring_results['block_propagation_times']
                if len(propagation_data) > 1:
                    first_prop = propagation_data[0]['time']
                    last_prop = propagation_data[-1]['time']
                    block_propagation_time = last_prop - first_prop
                    print(f"   📡 Block Propagation Time: {block_propagation_time:.3f}s")
                    print(f"   🌐 Propagation to All Nodes: {last_prop:.3f}s total")
    else:
        print(f"   ❌ NO NEW BLOCKS CREATED")
    
    print(f"\n📊 PROCESS TIMING BREAKDOWN:")
    print(f"   1️⃣  Wallet Creation: {wallet_creation_time:.3f}s")
    print(f"   2️⃣  Transaction Creation (avg): {avg_creation*1000:.2f}ms per tx")
    print(f"   3️⃣  Transaction Signing (included in creation)")
    print(f"   4️⃣  Transaction Encoding (avg): {avg_encoding*1000:.2f}ms per tx")
    print(f"   5️⃣  Network Submission (avg): {avg_network*1000:.2f}ms per tx")
    print(f"   6️⃣  Total Submission Phase: {timing_data['total_submission_time']:.3f}s")
    print(f"        (Time to submit all transactions to network)")
    
    if blocks_created > 0 and monitoring_results.get('first_block_detected'):
        first_block_time = monitoring_results['first_block_detected']
        submission_time = timing_data['total_submission_time']
        
        # Calculate quantum consensus time correctly
        if first_block_time > submission_time:
            # Normal case: block appeared after transaction submission completed
            quantum_time = first_block_time - submission_time
            print(f"   7️⃣  Quantum Consensus + Block Forging: {quantum_time:.3f}s")
            print(f"        (Time from submission completion to first new block)")
        else:
            # Block appeared during or before transaction submission
            # This means consensus was very fast or block was pre-existing
            if first_block_time < 1.0:  # Block appeared very quickly (likely pre-existing)
                print(f"   7️⃣  Quantum Consensus + Block Forging: <0.001s (block likely pre-existing)")
            else:
                # Block appeared during submission - show overlap
                overlap = submission_time - first_block_time
                print(f"   7️⃣  Quantum Consensus + Block Forging: Concurrent with submission")
                print(f"        (Block appeared {overlap:.3f}s before submission completed)")
        
        if monitoring_results.get('all_nodes_synced'):
            sync_time = monitoring_results['all_nodes_synced'] - monitoring_results['first_block_detected']
            print(f"   8️⃣  Block Propagation + Sync: {sync_time:.3f}s")
            print(f"        (Time for all nodes to sync the new block)")
            print(f"   🏁 Total End-to-End Time: {monitoring_results['all_nodes_synced']:.3f}s")
            print(f"        (From start of test to complete network sync)")
    
    print(f"\n🎯 Performance Metrics:")
    transactions_processed = successful_transactions - total_pool_size
    if blocks_created > 0:
        print(f"   ⚡ Transactions per Block: {transactions_processed/blocks_created:.1f}")
        if monitoring_results.get('first_block_detected'):
            overall_throughput = transactions_processed / monitoring_results['first_block_detected']
            print(f"   📈 Overall Throughput: {overall_throughput:.2f} tx/s")
    
    print(f"   🔀 Blockchain Sync: {'✅ Perfect' if max_blocks == min_blocks else '❌ Inconsistent'}")
    print(f"   🎯 Quantum Consensus: {'✅ Active' if blocks_created > 0 else '❌ No blocks created'}")
    
    return {
        'successful_transactions': successful_transactions,
        'failed_transactions': failed_transactions,
        'blocks_created': blocks_created,
        'timing_data': timing_data,
        'monitoring_results': monitoring_results,
        'avg_creation_time_ms': avg_creation * 1000,
        'avg_encoding_time_ms': avg_encoding * 1000,
        'avg_network_time_ms': avg_network * 1000,
        'total_submission_time': timing_data['total_submission_time'],
        'time_to_first_block': monitoring_results.get('first_block_detected'),
        'time_to_full_sync': monitoring_results.get('all_nodes_synced')
    }

def run_forger_analysis():
    """Run comprehensive forger and metrics analysis"""
    print(f"🔍 BLOCKCHAIN FORGER & METRICS ANALYSIS")
    print("=" * 80)
    
    # API ports for all 10 nodes
    api_ports = list(range(11000, 11010))
    
    # Check if nodes are running
    print(f"📡 Checking node availability...")
    active_nodes = []
    for port in api_ports:
        try:
            response = requests.get(f'http://localhost:{port}/api/v1/blockchain/', timeout=2)
            if response.status_code == 200:
                active_nodes.append(port)
                print(f"   ✅ Node {port - 11000 + 1} (Port {port}): Active")
            else:
                print(f"   ❌ Node {port - 11000 + 1} (Port {port}): HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Node {port - 11000 + 1} (Port {port}): Unreachable - {str(e)[:50]}")
    
    if not active_nodes:
        print("\n❌ No active nodes found. Please start the blockchain network first.")
        return None
    
    print(f"\n🌐 Found {len(active_nodes)} active nodes out of {len(api_ports)} total")
    
    # Run comprehensive analysis
    forger_stats, node_metrics = analyze_forgers_and_metrics(active_nodes)
    
    # Get performance correlations
    correlations = get_forger_performance_correlation(forger_stats, node_metrics)
    
    # Overall network health summary
    print(f"\n🏥 NETWORK HEALTH SUMMARY:")
    print("-" * 50)
    
    total_blocks = sum(stats['blocks_forged'] for stats in forger_stats.values()) if forger_stats else 0
    active_forgers = len([f for f, stats in forger_stats.items() if stats['blocks_forged'] > 0]) if forger_stats else 0
    
    print(f"   🌐 Network Size: {len(api_ports)} nodes configured")
    print(f"   ✅ Active Nodes: {len(active_nodes)}")
    print(f"   🔌 Node Availability: {len(active_nodes)/len(api_ports)*100:.1f}%")
    print(f"   📦 Total Blocks in Network: {total_blocks}")
    print(f"   👨‍💼 Active Forgers: {active_forgers}")
    print(f"   🎯 Quantum Consensus: {'✅ Active' if total_blocks > 1 else '❌ Issue'}")
    
    if correlations:
        # Network performance metrics
        avg_uptime = sum(c['uptime'] for c in correlations) / len(correlations)
        valid_latencies = [c['latency'] for c in correlations if c['latency'] != float('inf')]
        avg_latency = sum(valid_latencies) / len(valid_latencies) if valid_latencies else float('inf')
        avg_throughput = sum(c['throughput'] for c in correlations) / len(correlations)
        
        print(f"   ⬆️  Network Avg Uptime: {avg_uptime:.3f}")
        if avg_latency != float('inf'):
            print(f"   🚀 Network Avg Latency: {avg_latency*1000:.1f}ms")
        else:
            print(f"   🚀 Network Avg Latency: ∞ (measurement issues)")
        print(f"   📈 Network Avg Throughput: {avg_throughput:.2f}")
        
        # Success rate
        total_success = sum(c['proposals_success'] for c in correlations)
        total_failed = sum(c['proposals_failed'] for c in correlations)
        total_proposals = total_success + total_failed
        
        if total_proposals > 0:
            success_rate = total_success / total_proposals * 100
            print(f"   📊 Proposal Success Rate: {success_rate:.1f}% ({total_success}/{total_proposals})")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    print("-" * 50)
    
    if len(active_nodes) < len(api_ports):
        print(f"   ⚠️  Start inactive nodes to improve network resilience")
    
    if total_blocks <= 1:
        print(f"   ⚠️  No forging activity detected - check quantum consensus configuration")
    
    if correlations and avg_latency != float('inf') and avg_latency > 0.1:
        print(f"   ⚠️  High network latency detected - optimize P2P communication")
    
    if active_forgers < len(active_nodes) // 2:
        print(f"   ⚠️  Few nodes participating in forging - check stake distribution")
    
    if not correlations:
        print(f"   ⚠️  No quantum metrics available - ensure quantum consensus API is working")
    
    print(f"\n✨ Analysis Complete!")
    
    return {
        'active_nodes': len(active_nodes),
        'total_blocks': total_blocks,
        'active_forgers': active_forgers,
        'forger_stats': forger_stats,
        'node_metrics': node_metrics,
        'correlations': correlations
    }
    """Run transaction test with specified number of transactions"""
    print(f"🚀 Starting {num_transactions}-Transaction Test")
    print("=" * 50)
    
    # API ports for all 10 nodes (11000-11009)
    api_ports = list(range(11000, 11010))
    
    # Check initial blockchain state
    initial_blocks, initial_pool = get_blockchain_status(11000)
    print(f"📊 Initial state: {initial_blocks} blocks, {initial_pool} transactions in pool")
    
    print(f"\n💳 Creating wallets and submitting {num_transactions} transactions with proper public keys...")
    
    successful_transactions = 0
    failed_transactions = 0
    
    # Scale wallet count based on transaction count
    sender_count = min(max(1, num_transactions // 10), 20)  # 1-20 senders
    receiver_count = min(max(1, num_transactions // 2), 100)  # 1-100 receivers
    
    # Create multiple sender wallets to simulate different users
    sender_wallets = [Wallet() for _ in range(sender_count)]
    
    # Create receiver wallets with proper public keys
    receiver_wallets = [Wallet() for _ in range(receiver_count)]
    
    print(f"   🔑 Created {len(sender_wallets)} sender wallets")
    print(f"   🎯 Created {len(receiver_wallets)} receiver wallets")
    
    # Track transaction timing
    start_time = time.time()
    
    for i in range(1, num_transactions + 1):
        try:
            # Select random sender wallet and receiver wallet
            sender_wallet = random.choice(sender_wallets)
            receiver_wallet = random.choice(receiver_wallets)
            target_port = random.choice(api_ports)
            node_num = target_port - 11000 + 1
            
            # Create transaction with proper receiver public key
            receiver_public_key = receiver_wallet.public_key_string()
            amount = random.uniform(1.0, 100.0)
            
            transaction = sender_wallet.create_transaction(receiver_public_key, amount, "TRANSFER")
            encoded_transaction = BlockchainUtils.encode(transaction)
            
            # Submit to random node
            status_code, response = submit_transaction(encoded_transaction, target_port)
            
            if status_code == 200:
                successful_transactions += 1
                # Show progress at intervals based on transaction count
                progress_interval = max(1, num_transactions // 10)
                if i % progress_interval == 0:
                    print(f"   ✅ Transactions 1-{i}: {successful_transactions} successful, {failed_transactions} failed")
            else:
                failed_transactions += 1
                if i <= 5:  # Show first few errors for debugging
                    print(f"   ❌ Transaction {i}: HTTP {status_code} - {response[:100]}")
            
            # Adaptive delay based on transaction count
            if num_transactions > 50 and i % 20 == 0:
                time.sleep(0.5)  # Brief pause for large batches
            elif num_transactions > 10 and i % 5 == 0:
                time.sleep(0.2)  # Short pause for medium batches
                
        except Exception as e:
            failed_transactions += 1
            if failed_transactions <= 3:
                print(f"   ❌ Transaction {i} exception: {e}")
    
    # Calculate timing metrics
    submission_time = time.time() - start_time
    throughput = successful_transactions / submission_time if submission_time > 0 else 0
    
    print(f"\n📈 Transaction Submission Complete:")
    print(f"   ✅ Successful: {successful_transactions}")
    print(f"   ❌ Failed: {failed_transactions}")
    print(f"   📊 Success Rate: {successful_transactions/num_transactions*100:.1f}%")
    print(f"   ⏱️  Submission Time: {submission_time:.2f}s")
    print(f"   📈 Throughput: {throughput:.2f} tx/s")
    
    # Adaptive wait time based on transaction count
    wait_time = min(max(10, num_transactions // 5), 60)  # 10-60 seconds
    print(f"\n⏳ Waiting {wait_time} seconds for quantum consensus and forging...")
    time.sleep(wait_time)
    
    # Get active nodes only for final status
    active_api_ports = get_active_nodes(api_ports)
    print(f"\n🌐 Detected {len(active_api_ports)} active nodes out of {len(api_ports)} configured")
    
    print(f"\n📊 Final blockchain status across active nodes:")
    max_blocks = 0
    min_blocks = float('inf')
    total_pool_size = 0
    
    for i, port in enumerate(active_api_ports, 1):
        blocks, pool_size = get_blockchain_status(port)
        max_blocks = max(max_blocks, blocks)
        min_blocks = min(min_blocks, blocks)
        total_pool_size += pool_size
        
        status_icon = "🟢" if blocks > initial_blocks else "🔴"
        print(f"   {status_icon} Node {i} (API {port}): {blocks} blocks, {pool_size} txs in pool")
    
    print(f"\n🎯 Stress Test Results:")
    print(f"   📤 Transactions submitted: {successful_transactions}")
    print(f"   📦 Initial blocks: {initial_blocks}")
    print(f"   📦 Final blocks (max): {max_blocks}")
    print(f"   📈 New blocks created: {max_blocks - initial_blocks}")
    print(f"   🔄 Remaining in pools: {total_pool_size}")
    print(f"   🔀 Blockchain sync: {'✅ Perfect' if max_blocks == min_blocks else '❌ Inconsistent'}")
    
    if max_blocks > initial_blocks:
        blocks_created = max_blocks - initial_blocks
        transactions_processed = successful_transactions - total_pool_size
        print(f"   ✅ SUCCESS: {blocks_created} blocks forged, ~{transactions_processed} transactions processed")
        if blocks_created > 0:
            print(f"   ⚡ Throughput: ~{transactions_processed/blocks_created:.1f} transactions per block")
    else:
        print(f"   ❌ NO BLOCKS CREATED: Check quantum consensus logs")
    
    print(f"\n🔍 Network Performance Summary:")
    print(f"   🌐 Network Size: 10 nodes")
    print(f"   ⚡ Transaction Load: {num_transactions} transactions")
    print(f"   🎯 Quantum Consensus: {'✅ Active' if max_blocks > initial_blocks else '❌ Issue'}")
    print(f"   🔗 P2P Synchronization: {'✅ Working' if max_blocks == min_blocks else '❌ Issue'}")
    
    return {
        'successful_transactions': successful_transactions,
        'failed_transactions': failed_transactions,
        'success_rate': successful_transactions/num_transactions*100,
        'throughput': throughput,
        'blocks_created': max_blocks - initial_blocks,
        'final_pool_size': total_pool_size
    }


if __name__ == "__main__":
    import argparse
    
    # Command line argument parsing
    parser = argparse.ArgumentParser(description='Run blockchain transaction test or analysis')
    parser.add_argument('--count', '-c', type=int, default=1, 
                       help='Number of transactions to create (default: 1)')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Interactive mode to input transaction count')
    parser.add_argument('--analyze', '-a', action='store_true',
                       help='Run forger and metrics analysis instead of transaction test')
    parser.add_argument('--full-test', '-f', action='store_true',
                       help='Run transaction test followed by forger analysis')
    
    args = parser.parse_args()
    
    if args.analyze:
        # Run only the forger analysis
        print("🔍 Running Forger and Metrics Analysis...")
        analysis_results = run_forger_analysis()
        exit(0)
    
    if args.interactive:
        # Interactive mode
        try:
            if args.full_test:
                num_transactions = int(input("Enter number of transactions for full test: "))
            else:
                print("Select mode:")
                print("1. Transaction test")
                print("2. Forger analysis")
                print("3. Full test (transactions + analysis)")
                choice = input("Enter choice (1-3): ").strip()
                
                if choice == "2":
                    print("🔍 Running Forger and Metrics Analysis...")
                    analysis_results = run_forger_analysis()
                    exit(0)
                elif choice == "3":
                    args.full_test = True
                    num_transactions = int(input("Enter number of transactions for full test: "))
                else:
                    num_transactions = int(input("Enter number of transactions to create: "))
            
            if num_transactions <= 0:
                print("❌ Number of transactions must be positive")
                exit(1)
        except ValueError:
            print("❌ Invalid input. Please enter a valid number.")
            exit(1)
    else:
        num_transactions = args.count
    
    if num_transactions <= 0:
        print("❌ Number of transactions must be positive")
        exit(1)
    
    # Run the transaction test with detailed timing
    results = run_transaction_test_with_detailed_timing(num_transactions)
    
    print(f"\n🏁 Test Summary:")
    print(f"   📊 Successful: {results['successful_transactions']}")
    print(f"   ❌ Failed: {results['failed_transactions']}")
    print(f"   📦 Blocks Created: {results['blocks_created']}")
    print(f"   ⚡ Avg Creation Time: {results['avg_creation_time_ms']:.2f}ms")
    print(f"   🔗 Avg Network Time: {results['avg_network_time_ms']:.2f}ms")
    
    if results.get('time_to_first_block'):
        print(f"   🎯 Time to First Block: {results['time_to_first_block']:.3f}s")
    if results.get('time_to_full_sync'):
        print(f"   🌐 Time to Full Sync: {results['time_to_full_sync']:.3f}s")
    
    # Run forger analysis if requested
    if args.full_test:
        print(f"\n" + "="*80)
        print(f"🔍 Running Post-Transaction Forger Analysis...")
        analysis_results = run_forger_analysis()
