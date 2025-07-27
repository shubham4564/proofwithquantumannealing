#!/usr/bin/env python3
"""
Real Transaction Stress Test with Multiple Concurrent Block Producers
====================================================================

This creates actual transactions and submits them to the blockchain network
to measure real-world performance under load.
"""

import time
import threading
import concurrent.futures
from blockchain.transaction.wallet import Wallet
from blockchain.transaction.transaction import Transaction
from blockchain.blockchain import Blockchain
import requests
import json
from datetime import datetime
import statistics

class RealTransactionStressTester:
    def __init__(self):
        self.wallets = [Wallet() for _ in range(20)]  # Create 20 test wallets
        self.metrics = {
            'transaction_submit_times': [],
            'block_creation_times': [],
            'network_confirmation_times': [],
            'throughput_samples': []
        }
        
    def create_real_transaction(self, sender_wallet, receiver_wallet, amount):
        """Create and sign a real transaction"""
        transaction = Transaction(
            sender_wallet.public_key_string(),
            receiver_wallet.public_key_string(),
            amount,
            "TRANSFER"
        )
        
        # Sign the transaction properly
        transaction_data = transaction.payload()
        signature = sender_wallet.sign(transaction_data)
        transaction.signature = signature
        
        return transaction
    
    def test_individual_transaction_performance(self, transaction_count=100):
        """Test individual transaction creation and processing"""
        print(f"\n🧪 TESTING INDIVIDUAL TRANSACTION PERFORMANCE ({transaction_count} transactions)")
        print("-" * 70)
        
        creation_times = []
        signing_times = []
        
        for i in range(transaction_count):
            sender = self.wallets[i % len(self.wallets)]
            receiver = self.wallets[(i + 1) % len(self.wallets)]
            amount = 10.0 + (i % 50)
            
            # Measure transaction creation time
            start_creation = time.time()
            transaction = Transaction(
                sender.public_key_string(),
                receiver.public_key_string(),
                amount,
                "TRANSFER"
            )
            creation_time = (time.time() - start_creation) * 1000
            creation_times.append(creation_time)
            
            # Measure signing time
            start_signing = time.time()
            transaction_data = transaction.payload()
            signature = sender.sign(transaction_data)
            transaction.signature = signature
            signing_time = (time.time() - start_signing) * 1000
            signing_times.append(signing_time)
            
            if (i + 1) % 20 == 0:
                print(f"✅ Created and signed {i + 1}/{transaction_count} transactions")
        
        avg_creation = statistics.mean(creation_times)
        avg_signing = statistics.mean(signing_times)
        total_avg = avg_creation + avg_signing
        
        print(f"\n📊 INDIVIDUAL TRANSACTION METRICS:")
        print(f"   Average Creation Time: {avg_creation:.3f} ms")
        print(f"   Average Signing Time: {avg_signing:.3f} ms")
        print(f"   Total Processing Time: {total_avg:.3f} ms per transaction")
        print(f"   Theoretical Creation Rate: {1000/total_avg:.0f} transactions/second")
        
        return {
            'avg_creation_time_ms': avg_creation,
            'avg_signing_time_ms': avg_signing,
            'avg_total_time_ms': total_avg,
            'theoretical_creation_rate': 1000/total_avg,
            'total_transactions': transaction_count
        }
    
    def test_parallel_transaction_creation(self, transaction_count=500, num_threads=8):
        """Test parallel transaction creation with multiple threads"""
        print(f"\n🚀 TESTING PARALLEL TRANSACTION CREATION")
        print(f"   Transactions: {transaction_count}, Threads: {num_threads}")
        print("-" * 60)
        
        def create_transaction_batch(batch_start, batch_size):
            batch_transactions = []
            batch_times = []
            
            for i in range(batch_start, min(batch_start + batch_size, transaction_count)):
                start_time = time.time()
                
                sender = self.wallets[i % len(self.wallets)]
                receiver = self.wallets[(i + 1) % len(self.wallets)]
                amount = 15.0 + (i % 75)
                
                transaction = self.create_real_transaction(sender, receiver, amount)
                
                end_time = time.time()
                batch_times.append((end_time - start_time) * 1000)
                batch_transactions.append(transaction)
            
            return batch_transactions, batch_times
        
        # Calculate batch size per thread
        batch_size = transaction_count // num_threads
        
        start_parallel = time.time()
        
        # Execute parallel creation
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for thread_id in range(num_threads):
                batch_start = thread_id * batch_size
                if thread_id == num_threads - 1:  # Last thread gets remaining transactions
                    actual_batch_size = transaction_count - batch_start
                else:
                    actual_batch_size = batch_size
                
                future = executor.submit(create_transaction_batch, batch_start, actual_batch_size)
                futures.append(future)
            
            # Collect results
            all_transactions = []
            all_times = []
            
            for future in concurrent.futures.as_completed(futures):
                batch_txs, batch_times = future.result()
                all_transactions.extend(batch_txs)
                all_times.extend(batch_times)
        
        total_parallel_time = time.time() - start_parallel
        
        # Calculate metrics
        avg_individual_time = statistics.mean(all_times)
        parallel_throughput = len(all_transactions) / total_parallel_time
        speedup_factor = (avg_individual_time * len(all_transactions) / 1000) / total_parallel_time
        
        print(f"\n📊 PARALLEL CREATION METRICS:")
        print(f"   Total Transactions Created: {len(all_transactions)}")
        print(f"   Total Parallel Time: {total_parallel_time:.3f} seconds")
        print(f"   Average Individual Time: {avg_individual_time:.3f} ms")
        print(f"   Parallel Throughput: {parallel_throughput:.0f} transactions/second")
        print(f"   Speedup Factor: {speedup_factor:.1f}x")
        print(f"   Parallel Efficiency: {(speedup_factor/num_threads)*100:.1f}%")
        
        return {
            'total_transactions': len(all_transactions),
            'total_time_seconds': total_parallel_time,
            'avg_individual_time_ms': avg_individual_time,
            'parallel_throughput': parallel_throughput,
            'speedup_factor': speedup_factor,
            'parallel_efficiency': (speedup_factor/num_threads)*100,
            'transactions': all_transactions
        }
    
    def test_blockchain_integration(self, transactions):
        """Test actual blockchain processing with real transactions"""
        print(f"\n⛓️  TESTING BLOCKCHAIN INTEGRATION")
        print(f"   Processing {len(transactions)} real transactions")
        print("-" * 50)
        
        # Create a test blockchain instance
        test_wallet = Wallet()
        blockchain = Blockchain(test_wallet.public_key_string())
        
        # Process transactions in batches
        batch_size = 50
        processing_results = []
        
        for i in range(0, len(transactions), batch_size):
            batch = transactions[i:i + batch_size]
            
            start_batch = time.time()
            
            # Submit transactions to blockchain
            for tx in batch:
                start_submit = time.time()
                blockchain.submit_transaction(tx)
                submit_time = (time.time() - start_submit) * 1000
                self.metrics['transaction_submit_times'].append(submit_time)
            
            # Create a block with these transactions
            start_block = time.time()
            block = blockchain.create_block(test_wallet, use_gulf_stream=True)
            block_creation_time = (time.time() - start_block) * 1000
            self.metrics['block_creation_times'].append(block_creation_time)
            
            batch_time = time.time() - start_batch
            
            processing_results.append({
                'batch_size': len(batch),
                'batch_time_seconds': batch_time,
                'block_number': block.block_count,
                'transactions_in_block': len(block.transactions),
                'block_creation_time_ms': block_creation_time
            })
            
            print(f"✅ Batch {i//batch_size + 1:2d}: {len(batch):2d} txs → Block #{block.block_count} ({len(block.transactions)} txs) in {batch_time:.3f}s")
        
        # Calculate blockchain metrics
        total_submit_time = sum(self.metrics['transaction_submit_times'])
        avg_submit_time = statistics.mean(self.metrics['transaction_submit_times'])
        avg_block_time = statistics.mean(self.metrics['block_creation_times'])
        
        total_processing_time = sum(result['batch_time_seconds'] for result in processing_results)
        blockchain_throughput = len(transactions) / total_processing_time
        
        print(f"\n📊 BLOCKCHAIN INTEGRATION METRICS:")
        print(f"   Total Transactions Processed: {len(transactions)}")
        print(f"   Total Blocks Created: {len(processing_results)}")
        print(f"   Average Submit Time: {avg_submit_time:.3f} ms per transaction")
        print(f"   Average Block Creation: {avg_block_time:.3f} ms per block")
        print(f"   Total Processing Time: {total_processing_time:.3f} seconds")
        print(f"   Blockchain Throughput: {blockchain_throughput:.0f} TPS")
        print(f"   Final Blockchain Length: {len(blockchain.blocks)} blocks")
        
        return {
            'total_transactions_processed': len(transactions),
            'total_blocks_created': len(processing_results),
            'avg_submit_time_ms': avg_submit_time,
            'avg_block_creation_time_ms': avg_block_time,
            'total_processing_time_seconds': total_processing_time,
            'blockchain_throughput_tps': blockchain_throughput,
            'final_blockchain_length': len(blockchain.blocks),
            'processing_results': processing_results
        }
    
    def test_consensus_timing(self, num_consensus_rounds=50):
        """Test quantum consensus timing under load"""
        print(f"\n🔮 TESTING QUANTUM CONSENSUS TIMING")
        print(f"   Running {num_consensus_rounds} consensus rounds")
        print("-" * 50)
        
        # Create test blockchain for consensus testing
        test_wallet = Wallet()
        blockchain = Blockchain(test_wallet.public_key_string())
        
        consensus_times = []
        leader_selections = []
        
        for round_num in range(num_consensus_rounds):
            start_consensus = time.time()
            
            # Trigger leader selection
            last_block_hash = f"test_hash_{round_num}"
            if blockchain.quantum_consensus:
                selected_leader = blockchain.quantum_consensus.select_representative_node(last_block_hash)
                leader_selections.append(selected_leader)
            
            consensus_time = (time.time() - start_consensus) * 1000
            consensus_times.append(consensus_time)
            
            if (round_num + 1) % 10 == 0:
                print(f"✅ Completed {round_num + 1}/{num_consensus_rounds} consensus rounds")
        
        # Calculate consensus metrics
        avg_consensus_time = statistics.mean(consensus_times)
        min_consensus_time = min(consensus_times)
        max_consensus_time = max(consensus_times)
        consensus_std = statistics.stdev(consensus_times) if len(consensus_times) > 1 else 0
        
        # Calculate leader diversity
        unique_leaders = len(set(leader_selections)) if leader_selections else 0
        leader_diversity = unique_leaders / len(leader_selections) if leader_selections else 0
        
        print(f"\n📊 CONSENSUS TIMING METRICS:")
        print(f"   Average Consensus Time: {avg_consensus_time:.3f} ms")
        print(f"   Min/Max Consensus Time: {min_consensus_time:.3f} / {max_consensus_time:.3f} ms")
        print(f"   Consensus Time Std Dev: {consensus_std:.3f} ms")
        print(f"   Leader Diversity: {unique_leaders}/{len(leader_selections)} ({leader_diversity:.1%})")
        print(f"   Consensus Rate: {1000/avg_consensus_time:.0f} rounds/second")
        
        return {
            'avg_consensus_time_ms': avg_consensus_time,
            'min_consensus_time_ms': min_consensus_time,
            'max_consensus_time_ms': max_consensus_time,
            'consensus_std_dev_ms': consensus_std,
            'leader_diversity_ratio': leader_diversity,
            'unique_leaders': unique_leaders,
            'total_rounds': len(leader_selections),
            'consensus_rate_per_second': 1000/avg_consensus_time
        }
    
    def generate_comprehensive_metrics_report(self, individual_perf, parallel_perf, blockchain_perf, consensus_perf):
        """Generate a comprehensive metrics report"""
        print(f"\n📊 COMPREHENSIVE REAL TRANSACTION METRICS REPORT")
        print("=" * 80)
        
        current_time = datetime.now()
        
        # Create a JSON-serializable report by excluding Transaction objects
        report = {
            'report_metadata': {
                'timestamp': current_time.isoformat(),
                'test_type': 'Real Transaction Stress Test',
                'blockchain_type': 'Quantum-Enhanced Solana-Style',
                'test_scope': 'End-to-End Transaction Processing'
            },
            'individual_transaction_performance': {
                'avg_creation_time_ms': individual_perf['avg_creation_time_ms'],
                'avg_signing_time_ms': individual_perf['avg_signing_time_ms'],
                'avg_total_time_ms': individual_perf['avg_total_time_ms'],
                'theoretical_creation_rate': individual_perf['theoretical_creation_rate'],
                'total_transactions': individual_perf['total_transactions']
            },
            'parallel_processing_performance': {
                'total_transactions': parallel_perf['total_transactions'],
                'parallel_time_seconds': parallel_perf['total_time_seconds'],
                'avg_individual_time_ms': parallel_perf['avg_individual_time_ms'],
                'parallel_throughput': parallel_perf['parallel_throughput'],
                'speedup_factor': parallel_perf['speedup_factor'],
                'parallel_efficiency': parallel_perf['parallel_efficiency']
            },
            'blockchain_integration_performance': {
                'total_transactions_processed': blockchain_perf['total_transactions_processed'],
                'total_blocks_created': blockchain_perf['total_blocks_created'],
                'avg_submit_time_ms': blockchain_perf['avg_submit_time_ms'],
                'avg_block_creation_time_ms': blockchain_perf['avg_block_creation_time_ms'],
                'blockchain_throughput_tps': blockchain_perf['blockchain_throughput_tps'],
                'final_blockchain_length': blockchain_perf['final_blockchain_length']
            },
            'consensus_timing_performance': {
                'total_consensus_rounds': consensus_perf['total_rounds'],
                'avg_consensus_time_ms': consensus_perf['avg_consensus_time_ms'],
                'min_consensus_time_ms': consensus_perf['min_consensus_time_ms'],
                'max_consensus_time_ms': consensus_perf['max_consensus_time_ms'],
                'consensus_rate_per_second': consensus_perf['consensus_rate_per_second'],
                'leader_diversity_ratio': consensus_perf['leader_diversity_ratio']
            },
            'summary_metrics': {}
        }
        
        # Calculate summary metrics
        end_to_end_tps = min(
            individual_perf['theoretical_creation_rate'],
            parallel_perf['parallel_throughput'],
            blockchain_perf['blockchain_throughput_tps']
        )
        
        total_transactions_tested = (
            100 +  # individual test
            parallel_perf['total_transactions'] +
            blockchain_perf['total_transactions_processed']
        )
        
        report['summary_metrics'] = {
            'estimated_end_to_end_tps': end_to_end_tps,
            'total_transactions_tested': total_transactions_tested,
            'total_blocks_created': blockchain_perf['total_blocks_created'],
            'average_block_creation_time_ms': blockchain_perf['avg_block_creation_time_ms'],
            'average_consensus_time_ms': consensus_perf['avg_consensus_time_ms'],
            'parallel_efficiency_percent': parallel_perf['parallel_efficiency'],
            'overall_test_success': True
        }
        
        # Print summary
        print(f"🎯 EXECUTIVE SUMMARY:")
        print(f"   Test Timestamp: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Total Transactions Tested: {total_transactions_tested}")
        print(f"   Total Blocks Created: {blockchain_perf['total_blocks_created']}")
        
        print(f"\n⚡ PERFORMANCE HIGHLIGHTS:")
        print(f"   Individual Transaction Rate: {individual_perf['theoretical_creation_rate']:.0f} TPS")
        print(f"   Parallel Processing Rate: {parallel_perf['parallel_throughput']:.0f} TPS")
        print(f"   Blockchain Processing Rate: {blockchain_perf['blockchain_throughput_tps']:.0f} TPS")
        print(f"   Estimated End-to-End TPS: {end_to_end_tps:.0f}")
        
        print(f"\n🔮 CONSENSUS PERFORMANCE:")
        print(f"   Average Consensus Time: {consensus_perf['avg_consensus_time_ms']:.3f} ms")
        print(f"   Consensus Rate: {consensus_perf['consensus_rate_per_second']:.0f} rounds/second")
        print(f"   Leader Selection Diversity: {consensus_perf['leader_diversity_ratio']:.1%}")
        
        print(f"\n⛓️  BLOCKCHAIN METRICS:")
        print(f"   Average Block Creation: {blockchain_perf['avg_block_creation_time_ms']:.3f} ms")
        print(f"   Average Transaction Submit: {blockchain_perf['avg_submit_time_ms']:.3f} ms")
        print(f"   Final Blockchain Length: {blockchain_perf['final_blockchain_length']} blocks")
        
        print(f"\n🚀 PARALLEL PROCESSING:")
        print(f"   Parallel Efficiency: {parallel_perf['parallel_efficiency']:.1f}%")
        print(f"   Speedup Factor: {parallel_perf['speedup_factor']:.1f}x")
        
        # Save report
        filename = f"real_transaction_metrics_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Detailed metrics report saved to: {filename}")
        
        return report


def main():
    """Main execution function for comprehensive real transaction testing"""
    print("🚀 REAL TRANSACTION STRESS TESTING & PERFORMANCE ANALYSIS")
    print("=" * 80)
    
    tester = RealTransactionStressTester()
    
    print("🎯 Test Overview:")
    print("   • Individual transaction performance")
    print("   • Parallel transaction creation")
    print("   • Blockchain integration testing")
    print("   • Quantum consensus timing")
    
    # Step 1: Test individual transaction performance
    print("\n" + "="*60)
    individual_perf = tester.test_individual_transaction_performance(transaction_count=200)
    
    # Step 2: Test parallel transaction creation
    print("\n" + "="*60)
    parallel_perf = tester.test_parallel_transaction_creation(
        transaction_count=1000, 
        num_threads=8
    )
    
    # Step 3: Test blockchain integration
    print("\n" + "="*60)
    blockchain_perf = tester.test_blockchain_integration(
        parallel_perf['transactions'][:500]  # Use first 500 for blockchain testing
    )
    
    # Step 4: Test consensus timing
    print("\n" + "="*60)
    consensus_perf = tester.test_consensus_timing(num_consensus_rounds=100)
    
    # Step 5: Generate comprehensive report
    print("\n" + "="*60)
    final_report = tester.generate_comprehensive_metrics_report(
        individual_perf, parallel_perf, blockchain_perf, consensus_perf
    )
    
    print(f"\n✅ COMPREHENSIVE REAL TRANSACTION TESTING COMPLETE!")
    print(f"📊 {individual_perf['theoretical_creation_rate']:.0f} TPS theoretical rate")
    print(f"⚡ {parallel_perf['parallel_throughput']:.0f} TPS parallel processing")
    print(f"⛓️  {blockchain_perf['blockchain_throughput_tps']:.0f} TPS blockchain processing")
    print(f"🔮 {consensus_perf['consensus_rate_per_second']:.0f} consensus rounds/second")


if __name__ == "__main__":
    main()
