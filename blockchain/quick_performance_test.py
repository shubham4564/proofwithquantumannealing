#!/usr/bin/env python3
"""
Quick Performance Test

A simplified version of the flexible performance test for quick automated testing.
"""

import sys
import os
sys.path.insert(0, '/Users/shubham/Documents/proofwithquantumannealing/blockchain')

from flexible_performance_test import FlexiblePerformanceTest

def quick_test(num_transactions=50, batch_size=5, monitor_duration=20):
    """Run a quick performance test with specified parameters"""
    print(f"🚀 QUICK PERFORMANCE TEST")
    print(f"💳 {num_transactions} transactions, batch size {batch_size}, {monitor_duration}s monitoring")
    print("=" * 50)
    
    tester = FlexiblePerformanceTest()
    results = tester.run_performance_test(
        num_transactions=num_transactions,
        batch_size=batch_size,
        monitor_duration=monitor_duration
    )
    
    if results:
        summary = results['summary']
        print(f"\n🎯 QUICK SUMMARY:")
        print(f"   ✅ Success Rate: {summary['transaction_metrics']['success_rate_percent']:.1f}%")
        print(f"   ⚡ Overall TPS: {summary['throughput_metrics']['overall_tps']:.2f}")
        print(f"   📦 Blocks Created: {summary['consensus_metrics']['total_blocks_created']}")
        print(f"   ⏱️  Avg Transaction Time: {summary['transaction_metrics']['timing']['avg_total_transaction_time_ms']:.2f}ms")
        print(f"   🔗 Avg Consensus Time: {summary['consensus_metrics']['avg_consensus_time_seconds']:.3f}s")
        
        return summary
    else:
        print("❌ Test failed")
        return None

if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    num_tx = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    monitor_duration = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    
    quick_test(num_tx, batch_size, monitor_duration)
