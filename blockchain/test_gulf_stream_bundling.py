#!/usr/bin/env python3
"""
Test script to demonstrate Gulf Stream transaction bundling functionality.
Shows how multiple transactions are bundled into single UDP packets for efficiency.
"""

import time
import json
from typing import Dict, Any
from collections import defaultdict

# Mock classes for testing
class MockTransaction:
    def __init__(self, sender, receiver, amount, tx_id):
        self.sender_public_key = sender
        self.receiver_public_key = receiver
        self.amount = amount
        self.type = "transfer"
        self.timestamp = time.time()
        self.id = tx_id
        self.signature = f"sig_{tx_id}"

class MockLeaderSchedule:
    def __init__(self):
        self.leaders = ["leader1", "leader2", "leader3", "leader4", "leader5"]
        self.current_index = 0
    
    def get_current_leader(self):
        return self.leaders[self.current_index % len(self.leaders)]
    
    def get_upcoming_leaders(self, count):
        upcoming = []
        for i in range(1, count + 1):
            leader_index = (self.current_index + i) % len(self.leaders)
            upcoming.append((i, self.leaders[leader_index], time.time() + i * 0.45))
        return upcoming

def test_transaction_bundling():
    """
    Test the transaction bundling functionality of Gulf Stream.
    """
    print("🚀 Testing Gulf Stream Transaction Bundling")
    print("=" * 60)
    
    # Import the Gulf Stream processor
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from blockchain.consensus.gulf_stream import GulfStreamProcessor
    
    # Create mock leader schedule
    leader_schedule = MockLeaderSchedule()
    
    # Initialize Gulf Stream processor
    gulf_stream = GulfStreamProcessor(leader_schedule, "test_node_123")
    
    print(f"📊 Initial Stats:")
    stats = gulf_stream.get_stats()
    print(f"   - Max Bundle Size: {stats['max_bundle_size_bytes']} bytes")
    print(f"   - Bundle Timeout: {stats['bundle_timeout_ms']} ms")
    print(f"   - Transaction Lifetime: {stats['transaction_lifetime_seconds']} seconds")
    print()
    
    # Create multiple transactions to test bundling
    transactions = []
    for i in range(10):
        tx = MockTransaction(
            sender=f"sender_{i}",
            receiver=f"receiver_{i}",
            amount=100 + i,
            tx_id=f"tx_{i:03d}"
        )
        transactions.append(tx)
    
    print(f"📦 Processing {len(transactions)} transactions...")
    
    # Process transactions one by one (they should be bundled)
    results = []
    for i, tx in enumerate(transactions):
        result = gulf_stream.process_transaction(tx, f"rpc_node_{i % 3}")
        results.append(result)
        
        print(f"   ✅ Transaction {i+1}: {result['status']} - {result['tx_hash'][:16]}...")
        
        # Small delay to potentially trigger timeout-based bundling
        if i == 4:  # After 5 transactions, wait to trigger timeout
            print("   ⏱️  Waiting to trigger timeout-based bundling...")
            time.sleep(0.015)  # 15ms delay (longer than 10ms timeout)
    
    print()
    
    # Check stats after processing
    print(f"📈 Final Stats:")
    final_stats = gulf_stream.get_stats()
    gs_stats = final_stats['gulf_stream_stats']
    
    print(f"   - Transactions Forwarded: {gs_stats['transactions_forwarded']}")
    print(f"   - Bundles Sent: {gs_stats['bundles_sent']}")
    print(f"   - Avg Transactions per Bundle: {gs_stats['transactions_per_bundle_avg']:.2f}")
    print(f"   - Bundle Efficiency: {gs_stats['bundle_efficiency']:.2f}")
    print(f"   - Successful TPU Transmissions: {gs_stats['tpu_transmissions_successful']}")
    print(f"   - Failed TPU Transmissions: {gs_stats['tpu_transmissions_failed']}")
    print()
    
    # Show pending bundles
    print(f"🔄 Pending State:")
    print(f"   - Pending Transactions by Leader: {final_stats['total_pending_transactions']}")
    print(f"   - Pending Bundles: {final_stats['total_pending_bundles']}")
    
    for leader, count in final_stats['pending_bundles'].items():
        if count > 0:
            print(f"     - {leader}: {count} transactions in bundle")
    print()
    
    # Force flush remaining bundles
    print(f"💨 Flushing remaining bundles...")
    flushed = gulf_stream.flush_pending_bundles()
    print(f"   - Flushed {flushed} bundles")
    
    # Final stats after flush
    final_final_stats = gulf_stream.get_stats()
    gs_final_stats = final_final_stats['gulf_stream_stats']
    print(f"   - Total Bundles Sent: {gs_final_stats['bundles_sent']}")
    print(f"   - Final Avg Transactions per Bundle: {gs_final_stats['transactions_per_bundle_avg']:.2f}")
    
    print()
    print("✅ Transaction bundling test completed!")
    print()
    print("📋 Summary:")
    print(f"   - Processed {len(transactions)} transactions")
    print(f"   - Sent {gs_final_stats['bundles_sent']} UDP packets (bundles)")
    print(f"   - Efficiency: {gs_final_stats['transactions_per_bundle_avg']:.2f} transactions per packet")
    print(f"   - Network overhead reduced by ~{(1 - gs_final_stats['bundles_sent']/len(transactions))*100:.1f}%")

def test_bundle_timeout():
    """
    Test the bundle timeout functionality.
    """
    print("\n⏰ Testing Bundle Timeout Mechanism")
    print("=" * 60)
    
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from blockchain.consensus.gulf_stream import GulfStreamProcessor
    
    leader_schedule = MockLeaderSchedule()
    gulf_stream = GulfStreamProcessor(leader_schedule, "timeout_test_node")
    
    # Process a single transaction
    tx = MockTransaction("sender_timeout", "receiver_timeout", 500, "timeout_tx")
    result = gulf_stream.process_transaction(tx, "rpc_timeout")
    
    print(f"📦 Processed transaction: {result['tx_hash'][:16]}...")
    
    stats_before = gulf_stream.get_stats()
    print(f"📊 Bundles before timeout: {stats_before['gulf_stream_stats']['bundles_sent']}")
    
    # Wait for timeout
    print("⏱️  Waiting for bundle timeout (15ms)...")
    time.sleep(0.015)
    
    # Process bundle timeouts
    bundles_sent = gulf_stream.process_bundle_timeouts()
    print(f"💨 Timeout triggered: {bundles_sent} bundles sent")
    
    stats_after = gulf_stream.get_stats()
    print(f"📊 Bundles after timeout: {stats_after['gulf_stream_stats']['bundles_sent']}")
    
    print("✅ Bundle timeout test completed!")

if __name__ == "__main__":
    test_transaction_bundling()
    test_bundle_timeout()
