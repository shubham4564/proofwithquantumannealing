#!/usr/bin/env python3
"""
Monitor quantum consensus in real-time during block proposals
"""
import requests
import time
import json
from datetime import datetime
import sys
import os

# Add blockchain module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from blockchain.transaction.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils

def get_node_status(port):
    """Get status from a specific node"""
    try:
        response = requests.get(f"http://localhost:{port}/api/v1/blockchain/", timeout=2)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def get_quantum_metrics(port):
    """Get quantum metrics from a node"""
    try:
        response = requests.get(f"http://localhost:{port}/api/v1/blockchain/quantum-metrics/", timeout=2)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def send_transaction(port, wallet, to_address, amount):
    """Send a transaction to trigger quantum consensus"""
    try:
        transaction_data = {
            "sender": wallet.public_key_string(),
            "receiver": to_address,
            "amount": amount,
            "type": "TRANSFER"
        }
        
        # Sign transaction
        encoded_data = BlockchainUtils.encode(transaction_data)
        signature = wallet.sign(encoded_data)
        
        payload = {
            "sender": wallet.public_key_string(),
            "receiver": to_address,
            "amount": amount,
            "type": "TRANSFER",
            "signature": signature
        }
        
        response = requests.post(f"http://localhost:{port}/api/v1/transaction/create/", 
                               json=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Transaction failed: {e}")
        return False

def main():
    print("🌌 QUANTUM CONSENSUS MONITORING")
    print("="*60)
    
    # Discover available nodes
    available_nodes = []
    for port in range(11000, 11100):
        if get_node_status(port):
            available_nodes.append(port)
    
    print(f"📊 Found {len(available_nodes)} active nodes: {available_nodes}")
    if len(available_nodes) < 2:
        print("❌ Need at least 2 nodes for meaningful testing")
        return
    
    # Create test wallets
    sender_wallet = Wallet()
    receiver_wallet = Wallet()
    
    print(f"👛 Created test wallets")
    print(f"   Sender: {sender_wallet.public_key_string()[:50]}...")
    print(f"   Receiver: {receiver_wallet.public_key_string()[:50]}...")
    
    print("\n🔄 Starting real-time quantum consensus monitoring...")
    print("   (Press Ctrl+C to stop)")
    
    transaction_count = 0
    
    try:
        while True:
            print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Monitoring cycle {transaction_count + 1}")
            print("-" * 50)
            
            # Send a transaction to trigger consensus
            target_node = available_nodes[transaction_count % len(available_nodes)]
            print(f"📤 Sending transaction to Node {target_node - 11000} (port {target_node})")
            
            success = send_transaction(target_node, sender_wallet, 
                                     receiver_wallet.public_key_string(), 
                                     10 + transaction_count)
            
            if success:
                print("✅ Transaction sent successfully")
                transaction_count += 1
            else:
                print("❌ Transaction failed")
            
            # Wait a moment for processing
            time.sleep(2)
            
            # Collect quantum metrics from all nodes
            quantum_data = {}
            for port in available_nodes:
                metrics = get_quantum_metrics(port)
                if metrics:
                    quantum_data[port] = metrics
            
            # Display quantum consensus activity
            print(f"🌌 QUANTUM CONSENSUS STATUS")
            for port, data in quantum_data.items():
                node_id = port - 11000
                consensus_type = data.get('consensus_type', 'Unknown')
                total_nodes = data.get('total_nodes', 0)
                active_nodes = data.get('active_nodes', 0)
                probe_count = data.get('probe_count', 0)
                
                print(f"   Node {node_id:2d}: {consensus_type}, "
                      f"Nodes: {active_nodes}/{total_nodes}, "
                      f"Probes: {probe_count}")
                
                # Show node scores if available
                node_scores = data.get('node_scores', {})
                if node_scores:
                    for pub_key, score_data in node_scores.items():
                        short_key = pub_key[:30] + "..."
                        suitability = score_data.get('suitability_score', 0)
                        proposals_success = score_data.get('proposals_success', 0)
                        proposals_failed = score_data.get('proposals_failed', 0)
                        print(f"      └─ {short_key}: Score={suitability:.4f}, "
                              f"Success={proposals_success}, Failed={proposals_failed}")
            
            # Wait before next cycle
            print(f"⏳ Waiting 10 seconds before next transaction...")
            time.sleep(8)  # Total 10 seconds with the 2 second wait above
            
    except KeyboardInterrupt:
        print(f"\n\n🏁 Monitoring stopped. Sent {transaction_count} transactions.")
        print("📊 Final quantum metrics summary:")
        
        # Final metrics collection
        for port in available_nodes:
            metrics = get_quantum_metrics(port)
            if metrics:
                node_id = port - 11000
                probe_count = metrics.get('probe_count', 0)
                consensus_type = metrics.get('consensus_type', 'Unknown')
                print(f"   Node {node_id}: {probe_count} probes, Type: {consensus_type}")

if __name__ == "__main__":
    main()
