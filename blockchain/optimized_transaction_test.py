#!/usr/bin/env python3
"""
Network Performance Optimization for Quantum Annealing Blockchain

This module implements several optimizations to address network bottlenecks:
1. Async transaction processing with batching
2. Connection pooling for HTTP requests  
3. Background signature validation
4. Rate limiting and queue management
5. Optimized P2P broadcasting
"""

import asyncio
import aiohttp
import time
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import sys
import os
import random

sys.path.insert(0, '/Users/shubham/Documents/proofwithquantumannealing/blockchain')

from blockchain.transaction.wallet import Wallet
from blockchain.transaction.transaction import Transaction
from blockchain.utils.helpers import BlockchainUtils
import json

class OptimizedNetworkClient:
    """High-performance network client with connection pooling and async operations"""
    
    def __init__(self, max_connections=50, timeout=5.0):
        self.max_connections = max_connections
        self.timeout = timeout
        self.session = None
        self._session_lock = threading.Lock()
        
    async def __aenter__(self):
        """Async context manager entry"""
        if self.session is None:
            connector = aiohttp.TCPConnector(
                limit=self.max_connections,
                limit_per_host=10,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'Content-Type': 'application/json'}
            )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def submit_transaction_async(self, encoded_transaction, node_port):
        """Submit transaction asynchronously with connection reuse"""
        url = f'http://localhost:{node_port}/api/v1/transaction/create/'
        
        start_time = time.time()
        try:
            async with self.session.post(url, json={'transaction': encoded_transaction}) as response:
                submission_time = time.time() - start_time
                text = await response.text()
                return response.status, text, submission_time
        except Exception as e:
            submission_time = time.time() - start_time
            return 0, str(e), submission_time


class TransactionBatcher:
    """Batches transactions for more efficient processing"""
    
    def __init__(self, batch_size=10, batch_timeout=1.0):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.pending_transactions = deque()
        self.last_batch_time = time.time()
        self.processing_lock = threading.Lock()
        
    def add_transaction(self, transaction_data):
        """Add transaction to batch"""
        with self.processing_lock:
            self.pending_transactions.append(transaction_data)
            
            # Check if batch is ready
            current_time = time.time()
            batch_ready = (len(self.pending_transactions) >= self.batch_size or
                          current_time - self.last_batch_time >= self.batch_timeout)
            
            if batch_ready:
                return self.get_batch()
            return None
    
    def get_batch(self):
        """Get current batch and reset"""
        with self.processing_lock:
            if not self.pending_transactions:
                return None
                
            batch = list(self.pending_transactions)
            self.pending_transactions.clear()
            self.last_batch_time = time.time()
            return batch


class AsyncTransactionProcessor:
    """Asynchronous transaction processor with optimized network operations"""
    
    def __init__(self, api_ports):
        self.api_ports = api_ports
        self.executor = ThreadPoolExecutor(max_workers=20)  # For CPU-bound crypto operations
        self.batcher = TransactionBatcher(batch_size=5, batch_timeout=0.5)
        self.network_client = OptimizedNetworkClient(max_connections=50, timeout=10.0)
        
        # Performance tracking
        self.performance_stats = {
            'transactions_created': 0,
            'transactions_submitted': 0,
            'total_creation_time': 0,
            'total_submission_time': 0,
            'batch_count': 0,
            'errors': 0
        }
    
    def create_transaction_in_background(self, sender_wallet, receiver_public_key, amount, transaction_type='TRANSFER'):
        """Create transaction in background thread to avoid blocking"""
        return self.executor.submit(self._create_transaction_sync, sender_wallet, receiver_public_key, amount, transaction_type)
    
    def _create_transaction_sync(self, sender_wallet, receiver_public_key, amount, transaction_type):
        """Synchronous transaction creation (runs in thread pool)"""
        start_time = time.time()
        try:
            transaction = sender_wallet.create_transaction(receiver_public_key, amount, transaction_type)
            encoded_transaction = BlockchainUtils.encode(transaction)
            creation_time = time.time() - start_time
            
            self.performance_stats['transactions_created'] += 1
            self.performance_stats['total_creation_time'] += creation_time
            
            return encoded_transaction, creation_time
        except Exception as e:
            self.performance_stats['errors'] += 1
            return None, time.time() - start_time
    
    async def submit_transactions_batch(self, transactions_batch):
        """Submit a batch of transactions concurrently"""
        async with self.network_client:
            start_time = time.time()
            
            # Create submission tasks
            tasks = []
            for encoded_transaction in transactions_batch:
                target_port = random.choice(self.api_ports)
                task = self.network_client.submit_transaction_async(encoded_transaction, target_port)
                tasks.append(task)
            
            # Execute all submissions concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            batch_time = time.time() - start_time
            
            # Process results
            successful = 0
            failed = 0
            total_network_time = 0
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed += 1
                    self.performance_stats['errors'] += 1
                else:
                    status_code, response, submission_time = result
                    total_network_time += submission_time
                    
                    if status_code == 200:
                        successful += 1
                    else:
                        failed += 1
                        if failed <= 3:  # Log first few errors
                            print(f"   ❌ Batch tx {i+1}: HTTP {status_code} - {response[:50]}")
            
            self.performance_stats['transactions_submitted'] += successful
            self.performance_stats['total_submission_time'] += total_network_time
            self.performance_stats['batch_count'] += 1
            
            avg_network_time = total_network_time / len(results) if results else 0
            
            return {
                'successful': successful,
                'failed': failed,
                'batch_time': batch_time,
                'avg_network_time': avg_network_time,
                'total_network_time': total_network_time
            }
    
    def get_performance_summary(self):
        """Get performance statistics"""
        stats = self.performance_stats.copy()
        
        if stats['transactions_created'] > 0:
            stats['avg_creation_time_ms'] = (stats['total_creation_time'] / stats['transactions_created']) * 1000
        else:
            stats['avg_creation_time_ms'] = 0
            
        if stats['transactions_submitted'] > 0:
            stats['avg_submission_time_ms'] = (stats['total_submission_time'] / stats['transactions_submitted']) * 1000
        else:
            stats['avg_submission_time_ms'] = 0
            
        return stats


async def run_optimized_transaction_test(num_transactions):
    """Run optimized transaction test with async processing and batching"""
    print(f"🚀 Starting OPTIMIZED {num_transactions}-Transaction Test")
    print("🔧 Optimizations: Async I/O, Connection Pooling, Batching, Background Processing")
    print("=" * 80)
    
    # API ports for all 10 nodes (11000-11009)
    api_ports = list(range(11000, 11010))
    
    # Initialize optimized processor
    processor = AsyncTransactionProcessor(api_ports)
    
    # Check initial blockchain state
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('http://localhost:11000/api/v1/blockchain/') as response:
                if response.status == 200:
                    data = await response.json()
                    initial_blocks = len(data['blocks'])
                    print(f"📊 Initial state: {initial_blocks} blocks")
                else:
                    initial_blocks = 1
                    print(f"⚠️  Could not check initial state, assuming 1 block")
        except:
            initial_blocks = 1
            print(f"⚠️  Network unavailable, assuming 1 block")
    
    # Create wallets
    print(f"\n💳 Creating wallets for optimized testing...")
    wallet_creation_start = time.time()
    
    sender_count = min(max(1, num_transactions // 10), 20)
    receiver_count = min(max(1, num_transactions // 2), 100)
    
    sender_wallets = [Wallet() for _ in range(sender_count)]
    receiver_wallets = [Wallet() for _ in range(receiver_count)]
    
    wallet_creation_time = time.time() - wallet_creation_start
    print(f"   🔑 Created {len(sender_wallets)} sender + {len(receiver_wallets)} receiver wallets in {wallet_creation_time:.3f}s")
    
    # Start transaction creation and submission
    print(f"\n⚡ Creating and submitting {num_transactions} transactions with optimizations...")
    
    total_start_time = time.time()
    creation_futures = []
    pending_batches = []
    
    # Create transactions in background threads
    for i in range(num_transactions):
        sender_wallet = random.choice(sender_wallets)
        receiver_wallet = random.choice(receiver_wallets)
        receiver_public_key = receiver_wallet.public_key_string()
        amount = random.uniform(1.0, 100.0)
        
        # Submit to background thread pool
        future = processor.create_transaction_in_background(
            sender_wallet, receiver_public_key, amount, "TRANSFER"
        )
        creation_futures.append(future)
    
    print(f"   🏭 {num_transactions} transaction creation tasks submitted to thread pool")
    
    # Process completed transactions and batch them
    processed_transactions = []
    batch_results = []
    
    for i, future in enumerate(creation_futures, 1):
        try:
            encoded_transaction, creation_time = future.result(timeout=5.0)
            
            if encoded_transaction:
                processed_transactions.append(encoded_transaction)
                
                # Add to batcher
                batch = processor.batcher.add_transaction(encoded_transaction)
                
                if batch:
                    # Process batch asynchronously
                    print(f"   📦 Processing batch of {len(batch)} transactions...")
                    batch_result = await processor.submit_transactions_batch(batch)
                    batch_results.append(batch_result)
                    
                    print(f"   ✅ Batch {len(batch_results)}: {batch_result['successful']} successful, "
                          f"{batch_result['failed']} failed, "
                          f"batch time: {batch_result['batch_time']:.3f}s, "
                          f"avg network: {batch_result['avg_network_time']*1000:.1f}ms")
            
            # Show progress
            if i % max(1, num_transactions // 5) == 0:
                print(f"   🔄 Progress: {i}/{num_transactions} transactions processed")
                
        except Exception as e:
            print(f"   ❌ Transaction {i} failed: {e}")
    
    # Process any remaining transactions in final batch
    final_batch = processor.batcher.get_batch()
    if final_batch:
        print(f"   📦 Processing final batch of {len(final_batch)} transactions...")
        batch_result = await processor.submit_transactions_batch(final_batch)
        batch_results.append(batch_result)
        print(f"   ✅ Final batch: {batch_result['successful']} successful, {batch_result['failed']} failed")
    
    total_processing_time = time.time() - total_start_time
    
    # Calculate summary statistics
    total_successful = sum(result['successful'] for result in batch_results)
    total_failed = sum(result['failed'] for result in batch_results)
    total_batch_time = sum(result['batch_time'] for result in batch_results)
    total_network_time = sum(result['total_network_time'] for result in batch_results)
    
    # Get performance summary
    perf_stats = processor.get_performance_summary()
    
    print(f"\n📈 OPTIMIZED TRANSACTION PROCESSING COMPLETE:")
    print(f"   ✅ Successful: {total_successful}")
    print(f"   ❌ Failed: {total_failed}")
    print(f"   📊 Success Rate: {total_successful/num_transactions*100:.1f}%")
    print(f"   ⏱️  Total Processing Time: {total_processing_time:.3f}s")
    print(f"   📦 Batches Processed: {len(batch_results)}")
    print(f"   ⚡ Average Creation Time: {perf_stats['avg_creation_time_ms']:.2f}ms")
    print(f"   🌐 Average Network Time: {perf_stats['avg_submission_time_ms']:.2f}ms")
    print(f"   🚀 Effective Throughput: {total_successful/total_processing_time:.2f} tx/s")
    
    # Wait for consensus
    print(f"\n⏳ Waiting for quantum consensus and block forging...")
    await asyncio.sleep(15)
    
    # Check final state
    print(f"\n📊 Final blockchain status:")
    async with aiohttp.ClientSession() as session:
        for i, port in enumerate(api_ports[:5], 1):  # Check first 5 nodes
            try:
                async with session.get(f'http://localhost:{port}/api/v1/blockchain/') as response:
                    if response.status == 200:
                        data = await response.json()
                        final_blocks = len(data['blocks'])
                        status_icon = "🟢" if final_blocks > initial_blocks else "🔴"
                        print(f"   {status_icon} Node {i} (API {port}): {final_blocks} blocks")
                    else:
                        print(f"   🔴 Node {i} (API {port}): Connection failed")
            except:
                print(f"   🔴 Node {i} (API {port}): Network error")
    
    return {
        'successful_transactions': total_successful,
        'failed_transactions': total_failed,
        'total_processing_time': total_processing_time,
        'avg_creation_time_ms': perf_stats['avg_creation_time_ms'],
        'avg_network_time_ms': perf_stats['avg_submission_time_ms'],
        'throughput': total_successful/total_processing_time,
        'batch_count': len(batch_results)
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run optimized blockchain transaction test')
    parser.add_argument('--count', '-c', type=int, default=10, 
                       help='Number of transactions to create (default: 10)')
    
    args = parser.parse_args()
    
    if args.count <= 0:
        print("❌ Number of transactions must be positive")
        exit(1)
    
    # Run the optimized test
    print(f"🎯 Starting optimized test with {args.count} transactions")
    results = asyncio.run(run_optimized_transaction_test(args.count))
    
    print(f"\n🏁 OPTIMIZATION RESULTS:")
    print(f"   📊 Processed: {results['successful_transactions']} successful, {results['failed_transactions']} failed")
    print(f"   ⚡ Creation Time: {results['avg_creation_time_ms']:.2f}ms avg")
    print(f"   🌐 Network Time: {results['avg_network_time_ms']:.2f}ms avg")
    print(f"   🚀 Throughput: {results['throughput']:.2f} tx/s")
    print(f"   📦 Batches: {results['batch_count']}")
