#!/usr/bin/env python3
"""
Enhanced Performance Metrics Integration

This module integrates comprehensive performance metrics into the blockchain core,
extracting real-time data from existing APIs, logs, and blockchain operations.
"""

import time
import json
import logging
from typing import Dict, List, Optional, Tuple
from collections import deque, defaultdict
from dataclasses import dataclass, asdict
import threading


@dataclass
class PerformanceMetric:
    """Individual performance metric data point"""
    timestamp: float
    metric_name: str
    value: float
    metadata: Dict = None


@dataclass
class BlockCreationMetrics:
    """Metrics for block creation process"""
    block_height: int
    creation_start_time: float
    creation_end_time: float
    transaction_count: int
    block_size_bytes: int
    consensus_time_ms: float
    validation_time_ms: float
    leader_public_key: str
    slot_number: int


@dataclass
class TransactionPoolMetrics:
    """Real-time transaction pool metrics"""
    timestamp: float
    pending_count: int
    total_size_bytes: int
    average_transaction_size: int
    time_since_last_block: float
    throughput_tps: float
    forge_interval: float


class PerformanceMetricsCollector:
    """Collects and manages real-time performance metrics from blockchain operations"""
    
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        
        # Metric storage
        self.block_metrics: deque = deque(maxlen=max_history_size)
        self.transaction_metrics: deque = deque(maxlen=max_history_size)
        self.consensus_metrics: deque = deque(maxlen=max_history_size)
        self.pool_metrics: deque = deque(maxlen=max_history_size)
        
        # Performance counters
        self.total_blocks_processed = 0
        self.total_transactions_processed = 0
        self.start_time = time.time()
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Current measurements
        self.current_block_creation_start = None
        self.consensus_timing_stack = []
        
    def record_block_creation_start(self, leader_key: str, slot_number: int, transaction_count: int):
        """Record the start of block creation process"""
        with self.lock:
            self.current_block_creation_start = {
                'start_time': time.time(),
                'leader_key': leader_key,
                'slot_number': slot_number,
                'transaction_count': transaction_count
            }
    
    def record_block_creation_complete(self, block_height: int, block_size_bytes: int, 
                                     consensus_time_ms: float = None, validation_time_ms: float = None):
        """Record completed block creation"""
        with self.lock:
            if self.current_block_creation_start:
                end_time = time.time()
                start_data = self.current_block_creation_start
                
                metrics = BlockCreationMetrics(
                    block_height=block_height,
                    creation_start_time=start_data['start_time'],
                    creation_end_time=end_time,
                    transaction_count=start_data['transaction_count'],
                    block_size_bytes=block_size_bytes,
                    consensus_time_ms=consensus_time_ms or ((end_time - start_data['start_time']) * 1000),
                    validation_time_ms=validation_time_ms or 0,
                    leader_public_key=start_data['leader_key'],
                    slot_number=start_data['slot_number']
                )
                
                self.block_metrics.append(metrics)
                self.total_blocks_processed += 1
                self.total_transactions_processed += start_data['transaction_count']
                self.current_block_creation_start = None
    
    def record_transaction_pool_state(self, transaction_pool):
        """Record current transaction pool metrics"""
        with self.lock:
            try:
                current_time = time.time()
                pool_size_bytes = transaction_pool.get_pool_size_estimate()
                
                # Calculate TPS based on recent block history
                recent_tps = self.calculate_recent_tps(window_seconds=30)
                
                metrics = TransactionPoolMetrics(
                    timestamp=current_time,
                    pending_count=len(transaction_pool.transactions),
                    total_size_bytes=pool_size_bytes,
                    average_transaction_size=pool_size_bytes // max(1, len(transaction_pool.transactions)),
                    time_since_last_block=transaction_pool.get_time_since_last_forge(),
                    throughput_tps=recent_tps,
                    forge_interval=transaction_pool.forge_interval
                )
                
                self.pool_metrics.append(metrics)
                
            except Exception as e:
                logging.warning(f"Failed to record transaction pool metrics: {e}")
    
    def record_consensus_timing(self, operation: str, duration_ms: float, metadata: Dict = None):
        """Record consensus operation timing"""
        with self.lock:
            metric = PerformanceMetric(
                timestamp=time.time(),
                metric_name=f"consensus_{operation}",
                value=duration_ms,
                metadata=metadata or {}
            )
            self.consensus_metrics.append(metric)
    
    def calculate_recent_tps(self, window_seconds: int = 60) -> float:
        """Calculate TPS over recent time window"""
        with self.lock:
            current_time = time.time()
            cutoff_time = current_time - window_seconds
            
            recent_blocks = [b for b in self.block_metrics if b.creation_end_time >= cutoff_time]
            
            if not recent_blocks:
                return 0.0
            
            total_transactions = sum(b.transaction_count for b in recent_blocks)
            time_span = current_time - recent_blocks[0].creation_start_time
            
            return total_transactions / max(time_span, 1.0)
    
    def calculate_average_consensus_time(self, window_seconds: int = 300) -> float:
        """Calculate average consensus time over recent window"""
        with self.lock:
            current_time = time.time()
            cutoff_time = current_time - window_seconds
            
            recent_blocks = [b for b in self.block_metrics if b.creation_end_time >= cutoff_time]
            
            if not recent_blocks:
                return 0.0
            
            total_consensus_time = sum(b.consensus_time_ms for b in recent_blocks)
            return total_consensus_time / len(recent_blocks) / 1000.0  # Convert to seconds
    
    def get_comprehensive_metrics(self) -> Dict:
        """Get comprehensive performance metrics"""
        with self.lock:
            current_time = time.time()
            uptime = current_time - self.start_time
            
            # Calculate various performance indicators
            recent_tps = self.calculate_recent_tps(60)
            avg_consensus_time = self.calculate_average_consensus_time(300)
            
            # Block creation statistics
            block_stats = {}
            if self.block_metrics:
                recent_blocks = list(self.block_metrics)[-10:]  # Last 10 blocks
                block_stats = {
                    'recent_block_times': [b.consensus_time_ms / 1000.0 for b in recent_blocks],
                    'average_block_time': sum(b.consensus_time_ms for b in recent_blocks) / len(recent_blocks) / 1000.0,
                    'average_transactions_per_block': sum(b.transaction_count for b in recent_blocks) / len(recent_blocks),
                    'average_block_size_mb': sum(b.block_size_bytes for b in recent_blocks) / len(recent_blocks) / (1024 * 1024)
                }
            
            # Transaction pool statistics
            pool_stats = {}
            if self.pool_metrics:
                latest_pool = self.pool_metrics[-1]
                pool_stats = {
                    'current_pending_transactions': latest_pool.pending_count,
                    'pool_size_mb': latest_pool.total_size_bytes / (1024 * 1024),
                    'time_until_next_block': latest_pool.forge_interval - latest_pool.time_since_last_block
                }
            
            return {
                'system_metrics': {
                    'uptime_seconds': uptime,
                    'total_blocks_processed': self.total_blocks_processed,
                    'total_transactions_processed': self.total_transactions_processed,
                    'blocks_per_hour': (self.total_blocks_processed / uptime) * 3600 if uptime > 0 else 0
                },
                'performance_metrics': {
                    'current_tps': recent_tps,
                    'average_consensus_time_seconds': avg_consensus_time,
                    'theoretical_max_tps': 1.0 / avg_consensus_time if avg_consensus_time > 0 else 0,
                    'efficiency_percentage': (recent_tps / (1.0 / avg_consensus_time)) * 100 if avg_consensus_time > 0 else 0
                },
                'block_statistics': block_stats,
                'transaction_pool_statistics': pool_stats,
                'data_points': {
                    'block_metrics_count': len(self.block_metrics),
                    'consensus_metrics_count': len(self.consensus_metrics),
                    'pool_metrics_count': len(self.pool_metrics)
                }
            }


class BlockchainMetricsIntegrator:
    """Integrates performance metrics collection into existing blockchain methods"""
    
    def __init__(self, blockchain, node):
        self.blockchain = blockchain
        self.node = node
        self.metrics_collector = PerformanceMetricsCollector()
        
        # Add metrics endpoints to API
        self._add_metrics_endpoints()
        
        # Start background metrics collection
        self._start_metrics_collection()
    
    def _add_metrics_endpoints(self):
        """Add new metrics endpoints to existing API"""
        # This would integrate with the existing FastAPI router
        # For now, we'll enhance the existing get_quantum_metrics method
        pass
    
    def _start_metrics_collection(self):
        """Start background thread for continuous metrics collection"""
        def collect_metrics():
            while True:
                try:
                    # Record transaction pool state every 5 seconds
                    self.metrics_collector.record_transaction_pool_state(self.node.transaction_pool)
                    time.sleep(5)
                except Exception as e:
                    logging.warning(f"Metrics collection error: {e}")
                    time.sleep(10)
        
        metrics_thread = threading.Thread(target=collect_metrics, daemon=True)
        metrics_thread.start()
    
    def enhance_existing_methods(self):
        """Enhance existing blockchain methods with metrics collection"""
        
        # Wrap block creation method
        original_create_block = self.blockchain.create_block
        def enhanced_create_block(*args, **kwargs):
            # Extract leader info
            proposer_wallet = args[0] if args else kwargs.get('proposer_wallet')
            leader_key = proposer_wallet.public_key_string() if hasattr(proposer_wallet, 'public_key_string') else 'unknown'
            
            # Get current slot and transaction count
            current_slot = self.blockchain.leader_schedule.get_current_slot()
            tx_count = len(self.node.transaction_pool.transactions)
            
            # Record block creation start
            self.metrics_collector.record_block_creation_start(leader_key, current_slot, tx_count)
            
            # Call original method
            result = original_create_block(*args, **kwargs)
            
            # Record block creation complete
            if result:
                block_height = len(self.blockchain.blocks)
                block_size = len(json.dumps(result.to_dict()).encode('utf-8'))
                self.metrics_collector.record_block_creation_complete(block_height, block_size)
            
            return result
        
        self.blockchain.create_block = enhanced_create_block
        
        # Wrap quantum consensus operations
        if hasattr(self.blockchain, 'quantum_consensus'):
            self._wrap_consensus_methods()
    
    def _wrap_consensus_methods(self):
        """Wrap quantum consensus methods with timing metrics"""
        quantum_consensus = self.blockchain.quantum_consensus
        
        # Wrap solve_qubo method if it exists
        if hasattr(quantum_consensus, 'solve_qubo'):
            original_solve_qubo = quantum_consensus.solve_qubo
            def timed_solve_qubo(*args, **kwargs):
                start_time = time.time()
                result = original_solve_qubo(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                self.metrics_collector.record_consensus_timing('qubo_solve', duration_ms)
                return result
            quantum_consensus.solve_qubo = timed_solve_qubo
    
    def get_enhanced_quantum_metrics(self):
        """Enhanced version of get_quantum_metrics with performance data"""
        # Get original quantum metrics
        original_metrics = self.blockchain.get_quantum_metrics()
        
        # Add enhanced performance metrics
        performance_metrics = self.metrics_collector.get_comprehensive_metrics()
        
        # Merge the data
        enhanced_metrics = {
            **original_metrics,
            'performance_analytics': performance_metrics,
            'real_time_measurements': {
                'measurement_active': True,
                'collection_uptime': time.time() - self.metrics_collector.start_time,
                'last_updated': time.time()
            }
        }
        
        return enhanced_metrics


def integrate_performance_metrics(blockchain, node):
    """
    Main integration function to add comprehensive performance metrics
    to an existing blockchain and node instance.
    """
    integrator = BlockchainMetricsIntegrator(blockchain, node)
    integrator.enhance_existing_methods()
    
    # Replace the original get_quantum_metrics method
    blockchain.get_quantum_metrics = integrator.get_enhanced_quantum_metrics
    
    # Add metrics collector to blockchain for direct access
    blockchain.metrics_collector = integrator.metrics_collector
    
    logging.info("Enhanced performance metrics integration complete")
    return integrator
