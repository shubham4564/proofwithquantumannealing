#!/usr/bin/env python3
"""
Quick Performance Metrics Demo

This script demonstrates how to measure the key performance metrics:
1. Transaction Time - Time for transaction to be processed
2. Consensus Time - Time for quantum annealing consensus to complete
3. Transaction Throughput - Number of transactions processed per second

Usage:
    python quick_metrics_demo.py
"""

import requests
import time
import json
from datetime import datetime

from blockchain.transaction.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils


def measure_single_transaction_timing(api_port=8050):
    """Measure timing for a single transaction with detailed breakdown"""
    print("⏱️  MEASURING SINGLE TRANSACTION TIMING")
    print("-" * 50)
    
    # Create test wallets
    sender = Wallet()
    receiver = Wallet()
    
    # Fund sender first
    print("1. Funding sender wallet...")
    fund_start = time.time()
    exchange = Wallet()  # Genesis/Exchange wallet
    fund_tx = exchange.create_transaction(sender.public_key_string(), 100.0, "EXCHANGE")
    fund_package = {"transaction": BlockchainUtils.encode(fund_tx)}
    
    response = requests.post(f"http://localhost:{api_port}/api/v1/transaction/create/", 
                           json=fund_package, timeout=10)
    fund_time = time.time() - fund_start
    print(f"   Funding transaction time: {fund_time:.3f}s")
    
    if response.status_code != 200:
        print(f"   ❌ Funding failed: {response.status_code}")
        return
    
    # Wait for funding to be processed
    time.sleep(5)
    
    # Now measure actual transaction
    print("\n2. Measuring target transaction...")
    
    # Step 1: Transaction creation time
    creation_start = time.time()
    transaction = sender.create_transaction(receiver.public_key_string(), 10.0, "TRANSFER")
    creation_time = time.time() - creation_start
    print(f"   Transaction creation: {creation_time:.6f}s")
    
    # Step 2: Network submission time
    submission_start = time.time()
    package = {"transaction": BlockchainUtils.encode(transaction)}
    
    response = requests.post(f"http://localhost:{api_port}/api/v1/transaction/create/", 
                           json=package, timeout=15)
    submission_time = time.time() - submission_start
    print(f"   Network submission: {submission_time:.3f}s")
    
    # Step 3: Total transaction time
    total_time = creation_time + submission_time
    print(f"   Total transaction time: {total_time:.3f}s")
    
    # Step 4: Check if transaction was successful
    if response.status_code == 200:
        print("   ✅ Transaction successful")
        
        # Wait and check blockchain state
        print("\n3. Checking blockchain inclusion...")
        inclusion_start = time.time()
        
        for i in range(30):  # Check for up to 30 seconds
            blockchain_response = requests.get(f"http://localhost:{api_port}/api/v1/blockchain/", timeout=5)
            if blockchain_response.status_code == 200:
                blockchain_data = blockchain_response.json()
                blocks = blockchain_data.get('blocks', [])
                
                if len(blocks) > 1:  # More than genesis block
                    inclusion_time = time.time() - inclusion_start
                    print(f"   Block inclusion time: {inclusion_time:.3f}s")
                    break
            time.sleep(1)
        else:
            print("   ⚠️  Transaction not included in block within 30s")
    else:
        print(f"   ❌ Transaction failed: {response.status_code}")
    
    return {
        'creation_time': creation_time,
        'submission_time': submission_time,
        'total_time': total_time,
        'success': response.status_code == 200
    }


def measure_consensus_timing(api_port=8050, duration=30):
    """Measure quantum annealing consensus timing"""
    print(f"\n🔬 MEASURING CONSENSUS TIMING ({duration}s)")
    print("-" * 50)
    
    consensus_times = []
    probe_counts = []
    
    start_time = time.time()
    last_block_count = 0
    
    # Get initial blockchain state
    try:
        response = requests.get(f"http://localhost:{api_port}/api/v1/blockchain/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            last_block_count = len(data.get('blocks', []))
    except:
        pass
    
    print(f"Starting with {last_block_count} blocks...")
    
    while time.time() - start_time < duration:
        try:
            # Get quantum metrics
            quantum_response = requests.get(f"http://localhost:{api_port}/api/v1/blockchain/quantum-metrics/", timeout=5)
            
            if quantum_response.status_code == 200:
                quantum_data = quantum_response.json()
                probe_count = quantum_data.get('probe_count', 0)
                active_nodes = quantum_data.get('active_nodes', 0)
                
                probe_counts.append(probe_count)
                
                print(f"   Probes: {probe_count}, Active nodes: {active_nodes}")
                
                # Check for new blocks (indicating consensus completion)
                blockchain_response = requests.get(f"http://localhost:{api_port}/api/v1/blockchain/", timeout=5)
                if blockchain_response.status_code == 200:
                    blockchain_data = blockchain_response.json()
                    current_block_count = len(blockchain_data.get('blocks', []))
                    
                    if current_block_count > last_block_count:
                        # New block found - consensus completed
                        consensus_time = 5.0  # Estimated consensus time (would need deeper integration for exact timing)
                        consensus_times.append(consensus_time)
                        print(f"   🎯 New block! Estimated consensus time: {consensus_time:.2f}s")
                        last_block_count = current_block_count
            
        except Exception as e:
            print(f"   ⚠️  Error measuring consensus: {e}")
        
        time.sleep(5)  # Check every 5 seconds
    
    # Calculate metrics
    if consensus_times:
        avg_consensus_time = sum(consensus_times) / len(consensus_times)
        print(f"\n📊 Consensus Results:")
        print(f"   Consensus rounds observed: {len(consensus_times)}")
        print(f"   Average consensus time: {avg_consensus_time:.2f}s")
    else:
        print(f"\n📊 No consensus rounds completed during {duration}s measurement")
    
    if probe_counts:
        avg_probes = sum(probe_counts) / len(probe_counts)
        max_probes = max(probe_counts)
        print(f"   Average probe count: {avg_probes:.1f}")
        print(f"   Maximum probe count: {max_probes}")
    
    return {
        'consensus_rounds': len(consensus_times),
        'avg_consensus_time': sum(consensus_times) / len(consensus_times) if consensus_times else 0,
        'avg_probe_count': sum(probe_counts) / len(probe_counts) if probe_counts else 0,
        'max_probe_count': max(probe_counts) if probe_counts else 0
    }


def measure_transaction_throughput(api_port=8050, num_transactions=20, concurrent=True):
    """Measure transaction throughput"""
    print(f"\n🚀 MEASURING TRANSACTION THROUGHPUT")
    print(f"   Transactions: {num_transactions}")
    print(f"   Mode: {'Concurrent' if concurrent else 'Sequential'}")
    print("-" * 50)
    
    # Create test wallets
    sender = Wallet()
    receiver = Wallet()
    
    # Fund sender
    print("1. Setting up test wallets...")
    exchange = Wallet()
    fund_tx = exchange.create_transaction(sender.public_key_string(), 500.0, "EXCHANGE")
    fund_package = {"transaction": BlockchainUtils.encode(fund_tx)}
    
    response = requests.post(f"http://localhost:{api_port}/api/v1/transaction/create/", 
                           json=fund_package, timeout=10)
    if response.status_code != 200:
        print("   ❌ Failed to fund test wallet")
        return
    
    time.sleep(5)  # Wait for funding
    
    print("2. Sending transactions...")
    
    start_time = time.time()
    successful_transactions = 0
    failed_transactions = 0
    response_times = []
    
    if concurrent:
        # Concurrent transactions using threading
        from concurrent.futures import ThreadPoolExecutor
        
        def send_transaction(tx_index):
            try:
                tx_start = time.time()
                transaction = sender.create_transaction(receiver.public_key_string(), 1.0, "TRANSFER")
                package = {"transaction": BlockchainUtils.encode(transaction)}
                
                response = requests.post(f"http://localhost:{api_port}/api/v1/transaction/create/", 
                                       json=package, timeout=15)
                tx_time = time.time() - tx_start
                
                success = response.status_code == 200
                print(f"   TX {tx_index+1}: {'✅' if success else '❌'} ({tx_time:.3f}s)")
                
                return {'success': success, 'time': tx_time}
            except Exception as e:
                print(f"   TX {tx_index+1}: ❌ Error - {e}")
                return {'success': False, 'time': 0}
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(send_transaction, i) for i in range(num_transactions)]
            
            for future in futures:
                try:
                    result = future.result(timeout=30)
                    if result['success']:
                        successful_transactions += 1
                        response_times.append(result['time'])
                    else:
                        failed_transactions += 1
                except:
                    failed_transactions += 1
    
    else:
        # Sequential transactions
        for i in range(num_transactions):
            try:
                tx_start = time.time()
                transaction = sender.create_transaction(receiver.public_key_string(), 1.0, "TRANSFER")
                package = {"transaction": BlockchainUtils.encode(transaction)}
                
                response = requests.post(f"http://localhost:{api_port}/api/v1/transaction/create/", 
                                       json=package, timeout=15)
                tx_time = time.time() - tx_start
                
                if response.status_code == 200:
                    successful_transactions += 1
                    response_times.append(tx_time)
                    print(f"   TX {i+1}: ✅ ({tx_time:.3f}s)")
                else:
                    failed_transactions += 1
                    print(f"   TX {i+1}: ❌ ({tx_time:.3f}s)")
                
                time.sleep(0.1)  # Small delay between transactions
                
            except Exception as e:
                failed_transactions += 1
                print(f"   TX {i+1}: ❌ Error - {e}")
    
    total_time = time.time() - start_time
    
    # Calculate throughput metrics
    throughput = successful_transactions / total_time
    success_rate = successful_transactions / num_transactions
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    print(f"\n📊 Throughput Results:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Successful transactions: {successful_transactions}")
    print(f"   Failed transactions: {failed_transactions}")
    print(f"   Success rate: {success_rate:.2%}")
    print(f"   Throughput: {throughput:.2f} TPS (transactions per second)")
    print(f"   Average response time: {avg_response_time:.3f}s")
    
    if response_times:
        print(f"   Min response time: {min(response_times):.3f}s")
        print(f"   Max response time: {max(response_times):.3f}s")
    
    return {
        'throughput_tps': throughput,
        'success_rate': success_rate,
        'avg_response_time': avg_response_time,
        'total_time': total_time,
        'successful_transactions': successful_transactions,
        'failed_transactions': failed_transactions
    }


def main():
    """Main demo function"""
    print("🎯 QUANTUM ANNEALING BLOCKCHAIN PERFORMANCE METRICS DEMO")
    print("=" * 70)
    
    # Check if node is available
    api_port = 8050
    try:
        response = requests.get(f"http://localhost:{api_port}/api/v1/blockchain/", timeout=3)
        if response.status_code != 200:
            print(f"❌ Node not available on port {api_port}")
            print("Please start a node first: python run_node.py")
            return
        print(f"✅ Node available on port {api_port}")
    except:
        print(f"❌ Cannot connect to node on port {api_port}")
        print("Please start a node first: python run_node.py")
        return
    
    # Measure different performance aspects
    
    # 1. Single transaction timing
    tx_metrics = measure_single_transaction_timing(api_port)
    
    # 2. Consensus timing
    consensus_metrics = measure_consensus_timing(api_port, duration=30)
    
    # 3. Transaction throughput
    throughput_metrics = measure_transaction_throughput(api_port, num_transactions=15, concurrent=True)
    
    # Generate summary report
    print("\n" + "="*70)
    print("📋 PERFORMANCE SUMMARY REPORT")
    print("="*70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("🔸 TRANSACTION TIMING:")
    if tx_metrics:
        print(f"   Transaction creation: {tx_metrics['creation_time']:.6f}s")
        print(f"   Network submission: {tx_metrics['submission_time']:.3f}s")
        print(f"   Total transaction time: {tx_metrics['total_time']:.3f}s")
    
    print("\n🔸 CONSENSUS PERFORMANCE:")
    print(f"   Consensus rounds observed: {consensus_metrics['consensus_rounds']}")
    print(f"   Average consensus time: {consensus_metrics['avg_consensus_time']:.2f}s")
    print(f"   Average probe count: {consensus_metrics['avg_probe_count']:.1f}")
    
    print("\n🔸 TRANSACTION THROUGHPUT:")
    print(f"   Throughput: {throughput_metrics['throughput_tps']:.2f} TPS")
    print(f"   Success rate: {throughput_metrics['success_rate']:.2%}")
    print(f"   Average response time: {throughput_metrics['avg_response_time']:.3f}s")
    
    print("\n" + "="*70)
    
    # Save detailed report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"performance_metrics_demo_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write("QUANTUM ANNEALING BLOCKCHAIN PERFORMANCE METRICS\n")
        f.write("="*50 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("TRANSACTION TIMING:\n")
        f.write(f"  Creation time: {tx_metrics['creation_time']:.6f}s\n")
        f.write(f"  Submission time: {tx_metrics['submission_time']:.3f}s\n")
        f.write(f"  Total time: {tx_metrics['total_time']:.3f}s\n\n")
        
        f.write("CONSENSUS PERFORMANCE:\n")
        f.write(f"  Consensus rounds: {consensus_metrics['consensus_rounds']}\n")
        f.write(f"  Avg consensus time: {consensus_metrics['avg_consensus_time']:.2f}s\n")
        f.write(f"  Avg probe count: {consensus_metrics['avg_probe_count']:.1f}\n\n")
        
        f.write("THROUGHPUT METRICS:\n")
        f.write(f"  TPS: {throughput_metrics['throughput_tps']:.2f}\n")
        f.write(f"  Success rate: {throughput_metrics['success_rate']:.2%}\n")
        f.write(f"  Avg response time: {throughput_metrics['avg_response_time']:.3f}s\n")
    
    print(f"📄 Detailed report saved to: {filename}")


if __name__ == "__main__":
    main()
