#!/usr/bin/env python3

import sys
import os
import time
from datetime import datetime
sys.path.insert(0, '/Users/shubham/Documents/proofwithquantumannealing/blockchain')

import requests
import json

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

def get_node_status(node_port=11000):
    """Get basic node status"""
    try:
        url = f'http://localhost:{node_port}/api/v1/blockchain/'
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            return {
                'active': True,
                'blocks': len(data.get('blocks', [])),
                'pool_size': data.get('transaction_pool_size', 0),
                'response_time': response.elapsed.total_seconds()
            }
        else:
            return {'active': False, 'error': f'HTTP {response.status_code}'}
    except Exception as e:
        return {'active': False, 'error': str(e)[:50]}

def analyze_forgers_and_metrics(api_ports):
    """Analyze which nodes forged blocks and their quantum metrics"""
    print(f"\n🔍 DETAILED FORGER AND METRICS ANALYSIS")
    print("=" * 80)
    
    forger_stats = {}
    node_metrics = {}
    all_blocks = []
    node_statuses = {}
    
    # First, collect node status information
    print(f"\n📡 NODE STATUS CHECK:")
    print("-" * 50)
    
    active_nodes = []
    for port in api_ports:
        node_num = port - 11000 + 1
        status = get_node_status(port)
        node_statuses[port] = status
        
        if status['active']:
            active_nodes.append(port)
            print(f"   ✅ Node {node_num:2d} (Port {port}): {status['blocks']} blocks, "
                  f"{status['pool_size']} pool, {status['response_time']*1000:.1f}ms response")
        else:
            print(f"   ❌ Node {node_num:2d} (Port {port}): {status['error']}")
    
    if not active_nodes:
        print("\n❌ No active nodes found!")
        return {}, {}, {}
    
    print(f"\n🌐 Active Nodes: {len(active_nodes)}/{len(api_ports)}")
    
    # Collect detailed data from active nodes
    for port in active_nodes:
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
        # Remove duplicates and sort blocks by block_count
        unique_blocks = {}
        for block, source_node, source_port in all_blocks:
            block_num = block.get('block_count', 0)
            if block_num not in unique_blocks:
                unique_blocks[block_num] = (block, source_node, source_port)
        
        sorted_blocks = sorted(unique_blocks.items())
        
        print(f"   📊 Found {len(sorted_blocks)} unique blocks across {len(active_nodes)} nodes")
        
        for block_num, (block, source_node, source_port) in sorted_blocks:
            forger = block.get('forger', 'Unknown')
            timestamp = block.get('timestamp', 0)
            tx_count = len(block.get('transactions', []))
            prev_hash = block.get('previous_hash', 'N/A')[:16] + "..."
            
            # Track forger statistics
            if forger not in forger_stats:
                forger_stats[forger] = {
                    'blocks_forged': 0,
                    'total_transactions': 0,
                    'first_block': None,
                    'last_block': None,
                    'block_numbers': [],
                    'timestamps': []
                }
            
            forger_stats[forger]['blocks_forged'] += 1
            forger_stats[forger]['total_transactions'] += tx_count
            forger_stats[forger]['block_numbers'].append(block_num)
            forger_stats[forger]['timestamps'].append(timestamp)
            
            if forger_stats[forger]['first_block'] is None:
                forger_stats[forger]['first_block'] = block_num
            forger_stats[forger]['last_block'] = block_num
            
            # Show block details
            forger_short = forger[:40] + "..." if len(forger) > 40 else forger
            formatted_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S") if timestamp > 0 else "N/A"
            
            print(f"\n   📦 Block {block_num:2d}:")
            print(f"      👨‍💼 Forger: {forger_short}")
            print(f"      ⏰ Time: {formatted_time}")
            print(f"      💳 Transactions: {tx_count}")
            print(f"      📍 Source: Node {source_node}")
            print(f"      🔗 Prev Hash: {prev_hash}")
    
    # Display forger summary
    print(f"\n👨‍💼 FORGER SUMMARY:")
    print("-" * 50)
    
    if forger_stats:
        sorted_forgers = sorted(forger_stats.items(), key=lambda x: x[1]['blocks_forged'], reverse=True)
        
        for i, (forger, stats) in enumerate(sorted_forgers, 1):
            forger_short = forger[:60] + "..." if len(forger) > 60 else forger
            block_range = f"{stats['first_block']}-{stats['last_block']}" if stats['first_block'] != stats['last_block'] else str(stats['first_block'])
            
            # Calculate time span
            if len(stats['timestamps']) > 1:
                time_span = max(stats['timestamps']) - min(stats['timestamps'])
                time_span_str = f"{time_span:.1f}s"
            else:
                time_span_str = "Single block"
            
            print(f"\n   🏆 Rank {i}: {forger_short}")
            print(f"      📦 Blocks Forged: {stats['blocks_forged']}")
            print(f"      💳 Total Transactions: {stats['total_transactions']}")
            print(f"      📊 Block Range: {block_range}")
            print(f"      📋 Block Numbers: {stats['block_numbers']}")
            print(f"      ⏱️  Time Span: {time_span_str}")
            
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
                print(f"      🌐 Total Nodes: {metrics['total_nodes']}")
                print(f"      ✅ Active Nodes: {metrics.get('active_nodes', 'N/A')}")
            
            if 'probe_count' in metrics:
                print(f"      🔍 Total Probes: {metrics['probe_count']}")
            
            # Node performance scores
            if 'node_scores' in metrics and metrics['node_scores']:
                print(f"      📊 Node Performance Scores:")
                
                # Sort nodes by suitability score
                sorted_nodes = sorted(
                    metrics['node_scores'].items(), 
                    key=lambda x: x[1].get('suitability_score', 0), 
                    reverse=True
                )
                
                print(f"         {'Node':<35} {'Uptime':<8} {'Latency':<10} {'Throughput':<12} {'Suitability':<12} {'S/F':<8}")
                print(f"         {'-'*35} {'-'*8} {'-'*10} {'-'*12} {'-'*12} {'-'*8}")
                
                for node_id, scores in sorted_nodes[:10]:  # Show top 10 nodes
                    node_short = node_id[:33] + ".." if len(node_id) > 33 else node_id
                    
                    uptime = scores.get('uptime', 0)
                    latency = scores.get('latency', float('inf'))
                    throughput = scores.get('throughput', 0)
                    suitability = scores.get('suitability_score', 0)
                    success = scores.get('proposals_success', 0)
                    failed = scores.get('proposals_failed', 0)
                    
                    # Format latency display
                    latency_str = f"{latency*1000:.1f}ms" if latency != float('inf') and latency < 999 else "∞"
                    success_fail = f"{success}/{failed}"
                    
                    print(f"         {node_short:<35} {uptime:.3f}    {latency_str:<10} "
                          f"{throughput:<12.2f} {suitability:<12.4f} {success_fail:<8}")
            
            # Protocol parameters
            if 'protocol_parameters' in metrics:
                params = metrics['protocol_parameters']
                print(f"      ⚙️  Protocol Parameters:")
                print(f"         ⏱️  Max Delay: {params.get('max_delay_tolerance', 'N/A')}s")
                print(f"         ⌛ Block Timeout: {params.get('block_proposal_timeout', 'N/A')}s")
                print(f"         👥 Witness Quorum: {params.get('witness_quorum_size', 'N/A')}")
                print(f"         💰 Penalty Coeff: {params.get('penalty_coefficient', 'N/A')}")
            
            # Quantum annealing configuration
            if 'quantum_annealing_config' in metrics:
                quantum = metrics['quantum_annealing_config']
                print(f"      🔮 Quantum Config:")
                print(f"         ⏰ Annealing Time: {quantum.get('annealing_time_microseconds', 'N/A')}μs")
                print(f"         🔄 Num Reads: {quantum.get('num_reads', 'N/A')}")
                print(f"         🖥️  Simulator: {quantum.get('simulator_enabled', 'N/A')}")
    else:
        print("   ❌ No quantum metrics available from any node")
    
    return forger_stats, node_metrics, node_statuses

def get_forger_performance_correlation(forger_stats, node_metrics):
    """Correlate forger performance with quantum metrics"""
    print(f"\n🔗 FORGER PERFORMANCE CORRELATION:")
    print("-" * 50)
    
    if not forger_stats or not node_metrics:
        print("   ❌ Insufficient data for correlation analysis")
        return []
    
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
                'effective_score': matching_metrics.get('effective_score', 0),
                'proposals_success': matching_metrics.get('proposals_success', 0),
                'proposals_failed': matching_metrics.get('proposals_failed', 0)
            })
    
    if correlations:
        # Sort by blocks forged
        correlations.sort(key=lambda x: x['blocks_forged'], reverse=True)
        
        print(f"   📊 Forger Performance vs Quantum Metrics:")
        print(f"   {'Rank':<4} {'Forger':<25} {'Blks':<4} {'Uptime':<7} {'Latency':<9} {'Thput':<7} {'Suit':<8} {'S/F':<7}")
        print(f"   {'-'*4} {'-'*25} {'-'*4} {'-'*7} {'-'*9} {'-'*7} {'-'*8} {'-'*7}")
        
        for i, corr in enumerate(correlations, 1):
            forger_short = corr['forger'][:23] + ".." if len(corr['forger']) > 23 else corr['forger']
            latency_str = f"{corr['latency']*1000:.0f}ms" if corr['latency'] != float('inf') and corr['latency'] < 999 else "∞"
            success_fail = f"{corr['proposals_success']}/{corr['proposals_failed']}"
            
            print(f"   {i:<4} {forger_short:<25} {corr['blocks_forged']:<4} {corr['uptime']:.3f}   "
                  f"{latency_str:<9} {corr['throughput']:<7.2f} {corr['suitability_score']:<8.4f} {success_fail:<7}")
        
        # Calculate statistics
        total_blocks = sum(c['blocks_forged'] for c in correlations)
        avg_uptime = sum(c['uptime'] for c in correlations) / len(correlations)
        valid_latencies = [c['latency'] for c in correlations if c['latency'] != float('inf')]
        avg_latency = sum(valid_latencies) / len(valid_latencies) if valid_latencies else float('inf')
        avg_throughput = sum(c['throughput'] for c in correlations) / len(correlations)
        active_forgers = sum(1 for c in correlations if c['blocks_forged'] > 0)
        
        print(f"\n   📈 Network Performance Summary:")
        print(f"      🏆 Active Forgers: {active_forgers}")
        print(f"      📦 Total Blocks: {total_blocks}")
        print(f"      ⬆️  Average Uptime: {avg_uptime:.3f}")
        if avg_latency != float('inf'):
            print(f"      🚀 Average Latency: {avg_latency*1000:.1f}ms")
        print(f"      📈 Average Throughput: {avg_throughput:.2f}")
        
        # Success rate
        total_success = sum(c['proposals_success'] for c in correlations)
        total_failed = sum(c['proposals_failed'] for c in correlations)
        total_proposals = total_success + total_failed
        
        if total_proposals > 0:
            success_rate = total_success / total_proposals * 100
            print(f"      ✅ Proposal Success Rate: {success_rate:.1f}% ({total_success}/{total_proposals})")
        
        # Find the most efficient forger
        if correlations:
            best_forger = max(correlations, key=lambda x: x['suitability_score'])
            most_productive = max(correlations, key=lambda x: x['blocks_forged'])
            
            print(f"\n   🏅 Top Performers:")
            print(f"      🥇 Highest Suitability: {best_forger['suitability_score']:.4f} score")
            print(f"      🔥 Most Productive: {most_productive['blocks_forged']} blocks forged")
    else:
        print("   ❌ No correlations found between forgers and quantum metrics")
    
    return correlations

def run_full_analysis(max_nodes=None):
    """Run comprehensive forger and metrics analysis"""
    print(f"🔍 BLOCKCHAIN FORGER & METRICS ANALYSIS")
    print(f"⏰ Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Auto-detect active nodes or use specified range
    if max_nodes is None:
        # Try to auto-detect by checking ports 11000-11099
        print("🔍 Auto-detecting active nodes...")
        api_ports = []
        for port in range(11000, 11100):
            try:
                response = requests.get(f'http://localhost:{port}/api/v1/blockchain/', timeout=1)
                if response.status_code == 200:
                    api_ports.append(port)
            except:
                pass
        
        if not api_ports:
            # Fallback to standard 10 nodes
            api_ports = list(range(11000, 11010))
    else:
        # Use specified number of nodes
        api_ports = list(range(11000, 11000 + max_nodes))
    
    print(f"🎯 Scanning ports: {api_ports[0]}-{api_ports[-1]} ({len(api_ports)} nodes)")
    
    # Run comprehensive analysis
    forger_stats, node_metrics, node_statuses = analyze_forgers_and_metrics(api_ports)
    
    # Get performance correlations
    correlations = get_forger_performance_correlation(forger_stats, node_metrics)
    
    # Overall network health summary
    print(f"\n🏥 NETWORK HEALTH SUMMARY:")
    print("-" * 50)
    
    active_nodes = len([s for s in node_statuses.values() if s['active']])
    total_blocks = sum(stats['blocks_forged'] for stats in forger_stats.values()) if forger_stats else 0
    active_forgers = len([f for f, stats in forger_stats.items() if stats['blocks_forged'] > 0]) if forger_stats else 0
    
    print(f"   🌐 Network Size: {len(api_ports)} nodes configured")
    print(f"   ✅ Active Nodes: {active_nodes}")
    print(f"   🔌 Node Availability: {active_nodes/len(api_ports)*100:.1f}%")
    print(f"   📦 Total Blocks: {total_blocks}")
    print(f"   👨‍💼 Active Forgers: {active_forgers}")
    print(f"   🎯 Quantum Consensus: {'✅ Active' if total_blocks > 1 else '⚠️  Limited' if total_blocks == 1 else '❌ Issue'}")
    
    # Network performance assessment
    if correlations:
        avg_uptime = sum(c['uptime'] for c in correlations) / len(correlations)
        valid_latencies = [c['latency'] for c in correlations if c['latency'] != float('inf')]
        avg_latency = sum(valid_latencies) / len(valid_latencies) if valid_latencies else float('inf')
        
        print(f"   ⬆️  Network Uptime: {avg_uptime:.3f}")
        if avg_latency != float('inf'):
            print(f"   🚀 Network Latency: {avg_latency*1000:.1f}ms")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print("-" * 50)
    
    if active_nodes < len(api_ports):
        inactive = len(api_ports) - active_nodes
        print(f"   ⚠️  Start {inactive} inactive nodes to improve network resilience")
    
    if total_blocks <= 1:
        print(f"   ⚠️  Low forging activity - check quantum consensus and stake distribution")
    
    if correlations and avg_latency != float('inf') and avg_latency > 0.1:
        print(f"   ⚠️  High network latency - optimize P2P communication")
    
    if active_forgers < active_nodes // 2:
        print(f"   ⚠️  Few nodes forging - verify stake distribution and consensus parameters")
    
    if not correlations:
        print(f"   ⚠️  No quantum metrics - ensure quantum consensus API endpoints are working")
    else:
        print(f"   ✅ Quantum consensus metrics available - system appears healthy")
    
    print(f"\n✨ Analysis Complete! Use '--help' for more options.")
    
    return {
        'active_nodes': active_nodes,
        'total_blocks': total_blocks,
        'active_forgers': active_forgers,
        'forger_stats': forger_stats,
        'node_metrics': node_metrics,
        'correlations': correlations,
        'node_statuses': node_statuses
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze blockchain forgers and node metrics')
    parser.add_argument('--json', '-j', action='store_true', help='Output results in JSON format')
    parser.add_argument('--summary', '-s', action='store_true', help='Show only summary information')
    parser.add_argument('--watch', '-w', type=int, metavar='SECONDS', help='Watch mode - repeat analysis every N seconds')
    parser.add_argument('--nodes', '-n', type=int, metavar='COUNT', help='Number of nodes to analyze (auto-detect if not specified)')
    
    args = parser.parse_args()
    
    if args.watch:
        try:
            while True:
                results = run_full_analysis(args.nodes)
                if args.watch > 0:
                    print(f"\n⏳ Waiting {args.watch} seconds for next analysis...")
                    time.sleep(args.watch)
                else:
                    break
        except KeyboardInterrupt:
            print(f"\n⏹️  Analysis stopped by user.")
    else:
        results = run_full_analysis(args.nodes)
        
        if args.json:
            # Convert to JSON-serializable format
            json_results = {
                'timestamp': datetime.now().isoformat(),
                'active_nodes': results['active_nodes'],
                'total_blocks': results['total_blocks'], 
                'active_forgers': results['active_forgers'],
                'forger_stats': results['forger_stats'],
                'correlations': results['correlations']
            }
            print(f"\n📄 JSON Output:")
            print(json.dumps(json_results, indent=2))
