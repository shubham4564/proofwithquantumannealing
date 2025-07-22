#!/usr/bin/env python3
"""
Batch Performance Test Runner

Runs multiple performance tests with different configurations to analyze
blockchain performance under various loads and conditions.
"""

import sys
import os
import time
from datetime import datetime
import json

sys.path.insert(0, '/Users/shubham/Documents/proofwithquantumannealing/blockchain')

from flexible_performance_test import FlexiblePerformanceTest

class BatchTestRunner:
    """Run multiple performance tests with different configurations"""
    
    def __init__(self):
        self.test_results = []
    
    def run_test_scenario(self, name, num_transactions, batch_size, monitor_duration):
        """Run a single test scenario"""
        print(f"\n🧪 SCENARIO: {name}")
        print(f"   💳 Transactions: {num_transactions}")
        print(f"   📦 Batch Size: {batch_size}")
        print(f"   ⏱️  Monitor: {monitor_duration}s")
        print("-" * 50)
        
        tester = FlexiblePerformanceTest()
        start_time = time.time()
        
        results = tester.run_performance_test(
            num_transactions=num_transactions,
            batch_size=batch_size,
            monitor_duration=monitor_duration
        )
        
        test_duration = time.time() - start_time
        
        if results:
            summary = results['summary']
            scenario_result = {
                'scenario_name': name,
                'config': {
                    'num_transactions': num_transactions,
                    'batch_size': batch_size,
                    'monitor_duration': monitor_duration
                },
                'test_duration_seconds': test_duration,
                'summary': summary,
                'key_metrics': {
                    'success_rate': summary['transaction_metrics']['success_rate_percent'],
                    'overall_tps': summary['throughput_metrics']['overall_tps'],
                    'blocks_created': summary['consensus_metrics']['total_blocks_created'],
                    'avg_transaction_time_ms': summary['transaction_metrics']['timing']['avg_total_transaction_time_ms'],
                    'avg_consensus_time_s': summary['consensus_metrics']['avg_consensus_time_seconds']
                }
            }
            
            self.test_results.append(scenario_result)
            
            print(f"\n✅ SCENARIO COMPLETE: {name}")
            print(f"   🎯 Success Rate: {scenario_result['key_metrics']['success_rate']:.1f}%")
            print(f"   ⚡ TPS: {scenario_result['key_metrics']['overall_tps']:.2f}")
            print(f"   📦 Blocks: {scenario_result['key_metrics']['blocks_created']}")
            
            return scenario_result
        else:
            print(f"\n❌ SCENARIO FAILED: {name}")
            return None
    
    def run_all_scenarios(self):
        """Run all predefined test scenarios"""
        print("🚀 BATCH PERFORMANCE TEST RUNNER")
        print("🧪 Running multiple scenarios to analyze blockchain performance")
        print("=" * 70)
        
        scenarios = [
            # Small load tests
            ("Light Load", 25, 5, 15),
            ("Medium Load", 50, 10, 20),
            ("Heavy Load", 100, 20, 30),
            
            # Batch size comparison
            ("Small Batches", 60, 3, 20),
            ("Large Batches", 60, 30, 20),
            
            # Sustained load test
            ("Sustained Load", 150, 15, 45),
            
            # Stress test
            ("Stress Test", 200, 25, 60),
        ]
        
        for name, num_tx, batch_size, monitor_duration in scenarios:
            try:
                self.run_test_scenario(name, num_tx, batch_size, monitor_duration)
                
                # Cool-down period between tests
                print("   😴 Cooling down for 5 seconds...")
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ Scenario '{name}' failed with error: {e}")
                continue
    
    def generate_comparative_report(self):
        """Generate a comparative report across all test scenarios"""
        if not self.test_results:
            print("❌ No test results to analyze")
            return
        
        print(f"\n📊 COMPARATIVE PERFORMANCE ANALYSIS")
        print("=" * 70)
        
        # Summary table
        print(f"\n📈 Scenario Comparison:")
        print(f"{'Scenario':<20} {'TPS':<8} {'Success%':<9} {'Blocks':<7} {'TxTime(ms)':<11} {'ConsTime(s)':<11}")
        print("-" * 70)
        
        for result in self.test_results:
            metrics = result['key_metrics']
            print(f"{result['scenario_name']:<20} "
                  f"{metrics['overall_tps']:<8.2f} "
                  f"{metrics['success_rate']:<9.1f} "
                  f"{metrics['blocks_created']:<7} "
                  f"{metrics['avg_transaction_time_ms']:<11.2f} "
                  f"{metrics['avg_consensus_time_s']:<11.3f}")
        
        # Best performance analysis
        print(f"\n🏆 Best Performance Analysis:")
        
        best_tps = max(self.test_results, key=lambda x: x['key_metrics']['overall_tps'])
        best_success = max(self.test_results, key=lambda x: x['key_metrics']['success_rate'])
        best_blocks = max(self.test_results, key=lambda x: x['key_metrics']['blocks_created'])
        fastest_tx = min(self.test_results, key=lambda x: x['key_metrics']['avg_transaction_time_ms'])
        fastest_consensus = min(self.test_results, key=lambda x: x['key_metrics']['avg_consensus_time_s'])
        
        print(f"   ⚡ Highest TPS: {best_tps['scenario_name']} ({best_tps['key_metrics']['overall_tps']:.2f} TPS)")
        print(f"   ✅ Best Success Rate: {best_success['scenario_name']} ({best_success['key_metrics']['success_rate']:.1f}%)")
        print(f"   📦 Most Blocks: {best_blocks['scenario_name']} ({best_blocks['key_metrics']['blocks_created']} blocks)")
        print(f"   🏃 Fastest Transactions: {fastest_tx['scenario_name']} ({fastest_tx['key_metrics']['avg_transaction_time_ms']:.2f}ms)")
        print(f"   ⚡ Fastest Consensus: {fastest_consensus['scenario_name']} ({fastest_consensus['key_metrics']['avg_consensus_time_s']:.3f}s)")
        
        # Performance recommendations
        print(f"\n💡 Performance Recommendations:")
        
        avg_tps = sum(r['key_metrics']['overall_tps'] for r in self.test_results) / len(self.test_results)
        avg_success = sum(r['key_metrics']['success_rate'] for r in self.test_results) / len(self.test_results)
        
        if avg_tps >= 10:
            print(f"   ✅ Excellent throughput: Average {avg_tps:.2f} TPS across all scenarios")
        elif avg_tps >= 5:
            print(f"   🟡 Good throughput: Average {avg_tps:.2f} TPS - consider optimization for higher loads")
        else:
            print(f"   🔴 Limited throughput: Average {avg_tps:.2f} TPS - performance optimization needed")
        
        if avg_success >= 95:
            print(f"   ✅ Excellent reliability: {avg_success:.1f}% average success rate")
        elif avg_success >= 85:
            print(f"   🟡 Good reliability: {avg_success:.1f}% average success rate")
        else:
            print(f"   🔴 Reliability issues: {avg_success:.1f}% average success rate - investigate network issues")
        
        # Optimal configuration
        balanced_scores = []
        for result in self.test_results:
            metrics = result['key_metrics']
            # Balanced score considering TPS, success rate, and consistency
            score = (metrics['overall_tps'] * 0.4 + 
                    metrics['success_rate'] * 0.4 + 
                    (100 - metrics['avg_transaction_time_ms']) * 0.2)
            balanced_scores.append((score, result))
        
        best_balanced = max(balanced_scores, key=lambda x: x[0])[1]
        print(f"\n🎯 Recommended Configuration:")
        print(f"   📋 Scenario: {best_balanced['scenario_name']}")
        print(f"   💳 Transactions: {best_balanced['config']['num_transactions']}")
        print(f"   📦 Batch Size: {best_balanced['config']['batch_size']}")
        print(f"   ⚡ Performance: {best_balanced['key_metrics']['overall_tps']:.2f} TPS, {best_balanced['key_metrics']['success_rate']:.1f}% success")
    
    def save_results(self):
        """Save all test results to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"batch_performance_results_{timestamp}.json"
        
        report_data = {
            'timestamp': timestamp,
            'total_scenarios': len(self.test_results),
            'test_results': self.test_results
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Complete results saved to: {filename}")
        return filename

def main():
    """Main batch test execution"""
    print("🧪 BATCH PERFORMANCE TEST SUITE")
    print("📊 Comprehensive blockchain performance analysis across multiple scenarios")
    print("=" * 80)
    
    runner = BatchTestRunner()
    
    # Run all scenarios
    runner.run_all_scenarios()
    
    # Generate comparative analysis
    runner.generate_comparative_report()
    
    # Save results
    runner.save_results()
    
    print(f"\n🏁 BATCH TESTING COMPLETE!")
    print(f"   🧪 Scenarios Run: {len(runner.test_results)}")
    print(f"   📊 Full analysis and recommendations provided above")

if __name__ == "__main__":
    main()
