#!/usr/bin/env python3
"""
Consensus Timing Measurement Tool
Measures how long it takes to select a representative node
"""

import time
import requests
import statistics
from datetime import datetime
import sys
import os

# Add blockchain modules to path
sys.path.append('/Users/shubham/Documents/fromgithub/proofwithquantumannealing/blockchain')

from blockchain.transaction.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils

def create_and_submit_transaction(node_port=11000):
    """Create and submit a transaction to trigger consensus"""
    try:
        # Create sender wallet
        sender_wallet = Wallet()
        receiver_public_key = "receiver_test_key"
        
        # Create transaction
        transaction = sender_wallet.create_transaction(receiver_public_key, 1.0, 'TRANSFER')
        encoded_transaction = BlockchainUtils.encode(transaction)
        
        # Submit to node
        url = f'http://localhost:{node_port}/api/v1/transaction/create/'
        start_time = time.time()
        
        response = requests.post(url, json={'transaction': encoded_transaction}, timeout=10)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return total_time, response.status_code, response.text[:100] if response.text else ""
        
    except Exception as e:
        return None, 0, str(e)

def trigger_consensus_rounds(num_rounds=5):
    """Trigger multiple consensus rounds and measure timing"""
    print("🕒 CONSENSUS TIMING MEASUREMENT")
    print("=" * 60)
    
    timing_results = []
    
    for round_num in range(1, num_rounds + 1):
        print(f"\n🔄 Round {round_num}/{num_rounds}")
        print("-" * 30)
        
        try:
            # Create and submit transaction to trigger consensus
            total_time, status_code, response_text = create_and_submit_transaction()
            
            if total_time is not None:
                print(f"   ⏱️  Total Response Time: {total_time:.3f}s")
                print(f"   📊 HTTP Status: {status_code}")
                
                if status_code == 200:
                    timing_results.append(total_time)
                    print(f"   ✅ Round {round_num} completed successfully")
                else:
                    print(f"   ❌ Round {round_num} failed: {response_text}")
            else:
                print(f"   ❌ Round {round_num} error: {response_text}")
            
            # Wait between rounds to allow consensus to complete
            if round_num < num_rounds:
                print(f"   ⏳ Waiting 3 seconds before next round...")
                time.sleep(3)
                
        except Exception as e:
            print(f"   ❌ Round {round_num} exception: {e}")
            
    return timing_results

def analyze_timing_results(timing_results):
    """Analyze timing statistics"""
    print(f"\n📊 TIMING ANALYSIS")
    print("=" * 60)
    
    if not timing_results:
        print("❌ No successful timing measurements")
        return
    
    print(f"🔢 Successful Measurements: {len(timing_results)}")
    print(f"⏱️  Average Time: {statistics.mean(timing_results):.3f}s")
    print(f"📏 Median Time: {statistics.median(timing_results):.3f}s")
    print(f"📊 Min Time: {min(timing_results):.3f}s")
    print(f"📊 Max Time: {max(timing_results):.3f}s")
    
    if len(timing_results) > 1:
        print(f"📈 Standard Deviation: {statistics.stdev(timing_results):.3f}s")
    
    print(f"\n📋 Individual Measurements:")
    for i, timing in enumerate(timing_results, 1):
        print(f"   Round {i}: {timing:.3f}s")

def check_consensus_activity():
    """Check current consensus activity"""
    print(f"\n🔍 CONSENSUS ACTIVITY CHECK")
    print("=" * 60)
    
    try:
        # Check multiple nodes for probe activity
        for port in [11000, 11001, 11002]:
            response = requests.get(f"http://localhost:{port}/api/v1/blockchain/quantum-metrics/", 
                                  timeout=5)
            if response.status_code == 200:
                data = response.json()
                node_num = port - 10999
                total_probes = data.get('probe_count', 0)
                total_nodes = data.get('total_nodes', 0)
                
                print(f"   🖥️  Node {node_num}: {total_probes} probes, {total_nodes} total nodes")
            else:
                print(f"   ❌ Node {port - 10999}: API error")
                
    except Exception as e:
        print(f"   ❌ Error checking consensus activity: {e}")

def main():
    print(f"🚀 QUANTUM CONSENSUS TIMING MEASUREMENT")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Check initial consensus state
    check_consensus_activity()
    
    # Measure consensus timing
    print(f"\n🎯 Triggering consensus rounds to measure timing...")
    timing_results = trigger_consensus_rounds(5)
    
    # Analyze results
    analyze_timing_results(timing_results)
    
    # Final consensus state
    check_consensus_activity()
    
    print(f"\n💡 INTERPRETATION:")
    print("=" * 60)
    print("The timing includes:")
    print("   1. 🌐 Network request time (HTTP POST)")
    print("   2. 🔍 Transaction validation")
    print("   3. 🧮 Quantum consensus node selection")
    print("   4. 📦 Block creation (if selected as forger)")
    print("   5. 🌍 P2P block propagation")
    print("   6. 📨 HTTP response generation")
    print()
    print("For pure consensus timing, subtract network/validation overhead")
    print("Typical consensus selection: ~0.1-0.5s of total time")

if __name__ == "__main__":
    main()
