#!/usr/bin/env python3
"""
Post-Test Analysis Script

Analyzes the quantum annealing blockchain after the 100-transaction stress test
to show which nodes proposed blocks and current network state.
"""

import requests
import json
from datetime import datetime

def analyze_network_post_test(num_nodes=20, base_api_port=8050):
    """Analyze the network state after the stress test"""
    
    print("🔬 POST-STRESS TEST NETWORK ANALYSIS")
    print("=" * 80)
    print(f"📅 Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Collect data from all nodes
    nodes_data = []
    total_blocks = 0
    total_probes = 0
    active_nodes = 0
    
    print("📊 SCANNING ALL NODES...")
    print("-" * 40)
    
    for node_id in range(num_nodes):
        api_port = base_api_port + node_id
        
        try:
            # Get blockchain info
            blockchain_response = requests.get(
                f"http://localhost:{api_port}/api/v1/blockchain/", 
                timeout=3
            )
            
            # Get quantum metrics
            quantum_response = requests.get(
                f"http://localhost:{api_port}/api/v1/blockchain/quantum-metrics/",
                timeout=3
            )
            
            if blockchain_response.status_code == 200 and quantum_response.status_code == 200:
                blockchain_data = blockchain_response.json()
                quantum_data = quantum_response.json()
                
                block_count = len(blockchain_data.get('blocks', []))
                probe_count = quantum_data.get('probe_count', 0)
                suitability_score = 0.0
                
                # Extract suitability score from node_scores
                node_scores = quantum_data.get('node_scores', {})
                if node_scores:
                    for key, score_data in node_scores.items():
                        suitability_score = score_data.get('suitability_score', 0.0)
                        break  # Take the first (and usually only) score
                
                successful_proposals = 0
                if node_scores:
                    for key, score_data in node_scores.items():
                        successful_proposals = score_data.get('proposals_success', 0)
                        break
                
                nodes_data.append({
                    'node_id': node_id,
                    'api_port': api_port,
                    'block_count': block_count,
                    'probe_count': probe_count,
                    'suitability_score': suitability_score,
                    'successful_proposals': successful_proposals,
                    'status': 'online'
                })
                
                total_blocks = max(total_blocks, block_count)
                total_probes += probe_count
                active_nodes += 1
                
                print(f"✅ Node {node_id:2}: {block_count} blocks, {probe_count} probes, score {suitability_score:.4f}")
                
            else:
                print(f"❌ Node {node_id:2}: Offline or error")
                
        except Exception as e:
            print(f"❌ Node {node_id:2}: Connection failed")
    
    print(f"\n📈 NETWORK SUMMARY")
    print("-" * 40)
    print(f"Online Nodes: {active_nodes}/{num_nodes}")
    print(f"Maximum Blocks: {total_blocks}")
    print(f"Total Probe Activity: {total_probes}")
    print()
    
    # Find block proposers
    print("🏗️  BLOCK PROPOSAL ANALYSIS")
    print("-" * 40)
    
    proposers = [node for node in nodes_data if node['successful_proposals'] > 0]
    if proposers:
        print("Nodes that successfully proposed blocks:")
        for node in sorted(proposers, key=lambda x: x['successful_proposals'], reverse=True):
            print(f"  🎯 Node {node['node_id']:2}: {node['successful_proposals']} successful proposal(s)")
            print(f"     Suitability Score: {node['suitability_score']:.4f}")
            print(f"     Total Blocks: {node['block_count']}")
    else:
        print("No nodes show successful proposals in their metrics")
    
    # Quantum Consensus Analysis
    print(f"\n🔬 QUANTUM CONSENSUS ANALYSIS")
    print("-" * 40)
    
    if total_probes > 0:
        active_consensus_nodes = [node for node in nodes_data if node['probe_count'] > 0]
        if active_consensus_nodes:
            print("Nodes participating in quantum consensus:")
            for node in sorted(active_consensus_nodes, key=lambda x: x['probe_count'], reverse=True):
                print(f"  🔬 Node {node['node_id']:2}: {node['probe_count']} probes")
        else:
            print("No probe activity detected across the network")
    else:
        print("Quantum consensus has not yet activated")
        print("(This is normal for newly started networks)")
    
    # Performance Summary
    print(f"\n⚡ PERFORMANCE SUMMARY")
    print("-" * 40)
    
    avg_score = sum(node['suitability_score'] for node in nodes_data) / len(nodes_data) if nodes_data else 0
    max_score_node = max(nodes_data, key=lambda x: x['suitability_score']) if nodes_data else None
    
    print(f"Average Suitability Score: {avg_score:.4f}")
    if max_score_node:
        print(f"Highest Scoring Node: Node {max_score_node['node_id']} (score: {max_score_node['suitability_score']:.4f})")
    
    # Block Details from the lead node
    if nodes_data:
        lead_node = max(nodes_data, key=lambda x: x['block_count'])
        if lead_node['block_count'] > 1:  # More than genesis block
            print(f"\n📋 BLOCKCHAIN DETAILS (from Node {lead_node['node_id']})")
            print("-" * 40)
            
            try:
                blockchain_response = requests.get(
                    f"http://localhost:{lead_node['api_port']}/api/v1/blockchain/", 
                    timeout=3
                )
                
                if blockchain_response.status_code == 200:
                    blockchain_data = blockchain_response.json()
                    blocks = blockchain_data.get('blocks', [])
                    
                    print(f"Total Blocks: {len(blocks)}")
                    
                    # Show non-genesis blocks
                    for i, block in enumerate(blocks[1:], 1):  # Skip genesis
                        forger_key = block.get('forger', 'Unknown')[:50] + "..." if len(block.get('forger', '')) > 50 else block.get('forger', 'Unknown')
                        timestamp = datetime.fromtimestamp(block.get('timestamp', 0)).strftime('%H:%M:%S')
                        print(f"  Block {i}: Forged at {timestamp}")
                        print(f"    Block Count: {block.get('block_count', 'N/A')}")
                        print(f"    Transactions: {len(block.get('transactions', []))}")
                
            except Exception as e:
                print(f"Could not retrieve blockchain details: {e}")
    
    print(f"\n✅ ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Post-Test Network Analysis")
    parser.add_argument("--nodes", type=int, default=20, help="Number of nodes to analyze")
    parser.add_argument("--api-port", type=int, default=8050, help="Base API port")
    
    args = parser.parse_args()
    
    analyze_network_post_test(num_nodes=args.nodes, base_api_port=args.api_port)
