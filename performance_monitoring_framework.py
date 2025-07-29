#!/usr/bin/env python3
"""
Built-in Performance Monitoring Framework for Quantum Blockchain Core

This module provides high-precision, intrinsic timing and logging framework
that continuously tracks the lifecycle of transactions and blocks within the
blockchain core methods.

Features:
- Nanosecond-precision timestamping
- Structured JSON logging
- Automated KPI derivation
- Zero-overhead when disabled
- Thread-safe operation
"""

import time
import json
import threading
import logging
import uuid
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict, deque
from enum import Enum
import statistics
import hashlib


class ProtocolEvent(Enum):
    """Core protocol events for performance monitoring"""
    # Consensus Events
    LEADER_SELECTION = "leader_selection"
    LEADER_DESIGNATION = "leader_designation"
    
    # Transaction Lifecycle
    TRANSACTION_INGRESS = "transaction_ingress"
    TRANSACTION_VALIDATION = "transaction_validation"
    TRANSACTION_VALIDATION_COMPLETE = "transaction_validation_complete"
    TRANSACTION_POOL_ADD = "transaction_pool_add"
    
    # Block Lifecycle
    BLOCK_PACKING_START = "block_packing_start"
    BLOCK_PACKING_COMPLETE = "block_packing_complete"
    BLOCK_PROPOSAL_START = "block_proposal_start"
    BLOCK_PROPOSAL_BROADCAST = "block_proposal_broadcast"
    BLOCK_RECEIVED = "block_received"
    BLOCK_VALIDATION_START = "block_validation_start"
    BLOCK_VALIDATION_COMPLETE = "block_validation_complete"
    BLOCK_FINALIZATION = "block_finalization"
    BLOCK_APPENDED = "block_appended"
    
    # Consensus Specific
    QUANTUM_ANNEALING_START = "quantum_annealing_start"
    QUANTUM_ANNEALING_COMPLETE = "quantum_annealing_complete"
    WITNESS_SELECTION = "witness_selection"
    
    # Network Events
    BLOCK_PROPAGATION_START = "block_propagation_start"
    BLOCK_PROPAGATION_RECEIVED = "block_propagation_received"
    NETWORK_SYNC_START = "network_sync_start"
    NETWORK_SYNC_COMPLETE = "network_sync_complete"


@dataclass
class PerformanceEvent:
    """Structured performance event with high-precision timing"""
    event_id: str
    event_type: ProtocolEvent
    timestamp_ns: int
    node_id: str
    block_hash: Optional[str] = None
    transaction_id: Optional[str] = None
    slot_number: Optional[int] = None
    metadata: Dict[str, Any] = None
    
    def to_json(self) -> str:
        """Convert event to structured JSON log entry"""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['timestamp_iso'] = time.strftime(
            '%Y-%m-%dT%H:%M:%S.%fZ', 
            time.gmtime(self.timestamp_ns / 1_000_000_000)
        )
        return json.dumps(data, separators=(',', ':'))
    
    @property
    def timestamp_ms(self) -> float:
        """Get timestamp in milliseconds"""
        return self.timestamp_ns / 1_000_000
    
    @property
    def timestamp_s(self) -> float:
        """Get timestamp in seconds"""
        return self.timestamp_ns / 1_000_000_000


class KPICalculator:
    """Automated KPI calculation from performance events"""
    
    def __init__(self):
        self.events = deque(maxlen=10000)  # Keep last 10k events
        self.event_index = defaultdict(list)  # Index by event type
        self._lock = threading.Lock()
    
    def add_event(self, event: PerformanceEvent):
        """Add event to KPI calculator"""
        with self._lock:
            self.events.append(event)
            self.event_index[event.event_type].append(event)
            
            # Maintain index size
            if len(self.event_index[event.event_type]) > 1000:
                self.event_index[event.event_type] = self.event_index[event.event_type][-1000:]
    
    def calculate_transaction_latency(self, time_window_s: int = 60) -> Dict[str, float]:
        """Calculate transaction latency from ingress to finalization"""
        cutoff_time = time.time_ns() - (time_window_s * 1_000_000_000)
        latencies = []
        
        # Group events by transaction ID
        tx_events = defaultdict(list)
        for event in self.events:
            if (event.transaction_id and 
                event.timestamp_ns > cutoff_time and
                event.event_type in [ProtocolEvent.TRANSACTION_INGRESS, ProtocolEvent.BLOCK_FINALIZATION]):
                tx_events[event.transaction_id].append(event)
        
        # Calculate latencies for complete transaction lifecycles
        for tx_id, events in tx_events.items():
            ingress_events = [e for e in events if e.event_type == ProtocolEvent.TRANSACTION_INGRESS]
            finalization_events = [e for e in events if e.event_type == ProtocolEvent.BLOCK_FINALIZATION]
            
            if ingress_events and finalization_events:
                ingress_time = min(e.timestamp_ns for e in ingress_events)
                finalization_time = max(e.timestamp_ns for e in finalization_events)
                latency_ms = (finalization_time - ingress_time) / 1_000_000
                latencies.append(latency_ms)
        
        if not latencies:
            return {"count": 0, "avg_ms": 0, "min_ms": 0, "max_ms": 0, "p95_ms": 0}
        
        return {
            "count": len(latencies),
            "avg_ms": statistics.mean(latencies),
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "p95_ms": statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
        }
    
    def calculate_block_creation_time(self, time_window_s: int = 60) -> Dict[str, float]:
        """Calculate time from block packing start to proposal broadcast"""
        cutoff_time = time.time_ns() - (time_window_s * 1_000_000_000)
        creation_times = []
        
        # Group events by block hash
        block_events = defaultdict(list)
        for event in self.events:
            if (event.block_hash and 
                event.timestamp_ns > cutoff_time and
                event.event_type in [ProtocolEvent.BLOCK_PACKING_START, ProtocolEvent.BLOCK_PROPOSAL_BROADCAST]):
                block_events[event.block_hash].append(event)
        
        # Calculate creation times
        for block_hash, events in block_events.items():
            start_events = [e for e in events if e.event_type == ProtocolEvent.BLOCK_PACKING_START]
            broadcast_events = [e for e in events if e.event_type == ProtocolEvent.BLOCK_PROPOSAL_BROADCAST]
            
            if start_events and broadcast_events:
                start_time = min(e.timestamp_ns for e in start_events)
                broadcast_time = max(e.timestamp_ns for e in broadcast_events)
                creation_time_ms = (broadcast_time - start_time) / 1_000_000
                creation_times.append(creation_time_ms)
        
        if not creation_times:
            return {"count": 0, "avg_ms": 0, "min_ms": 0, "max_ms": 0, "target_ms": 450}
        
        return {
            "count": len(creation_times),
            "avg_ms": statistics.mean(creation_times),
            "min_ms": min(creation_times),
            "max_ms": max(creation_times),
            "target_ms": 450,  # Quantum annealing target
            "within_target_pct": len([t for t in creation_times if t <= 450]) / len(creation_times) * 100
        }
    
    def calculate_consensus_latency(self, time_window_s: int = 60) -> Dict[str, float]:
        """Calculate consensus latency from proposal to finalization"""
        cutoff_time = time.time_ns() - (time_window_s * 1_000_000_000)
        consensus_times = []
        
        # Group events by block hash
        block_events = defaultdict(list)
        for event in self.events:
            if (event.block_hash and 
                event.timestamp_ns > cutoff_time and
                event.event_type in [ProtocolEvent.BLOCK_PROPOSAL_BROADCAST, ProtocolEvent.BLOCK_FINALIZATION]):
                block_events[event.block_hash].append(event)
        
        # Calculate consensus times
        for block_hash, events in block_events.items():
            proposal_events = [e for e in events if e.event_type == ProtocolEvent.BLOCK_PROPOSAL_BROADCAST]
            finalization_events = [e for e in events if e.event_type == ProtocolEvent.BLOCK_FINALIZATION]
            
            if proposal_events and finalization_events:
                proposal_time = min(e.timestamp_ns for e in proposal_events)
                finalization_time = max(e.timestamp_ns for e in finalization_events)
                consensus_time_ms = (finalization_time - proposal_time) / 1_000_000
                consensus_times.append(consensus_time_ms)
        
        if not consensus_times:
            return {"count": 0, "avg_ms": 0, "min_ms": 0, "max_ms": 0}
        
        return {
            "count": len(consensus_times),
            "avg_ms": statistics.mean(consensus_times),
            "min_ms": min(consensus_times),
            "max_ms": max(consensus_times),
            "p95_ms": statistics.quantiles(consensus_times, n=20)[18] if len(consensus_times) >= 20 else max(consensus_times)
        }
    
    def calculate_throughput_tps(self, time_window_s: int = 60) -> Dict[str, float]:
        """Calculate transactions per second (TPS)"""
        cutoff_time = time.time_ns() - (time_window_s * 1_000_000_000)
        
        # Count finalized transactions in time window
        finalized_transactions = len([
            e for e in self.events 
            if (e.event_type == ProtocolEvent.BLOCK_FINALIZATION and 
                e.transaction_id and 
                e.timestamp_ns > cutoff_time)
        ])
        
        actual_window_s = min(time_window_s, len(self.events) / 100 if self.events else 1)
        tps = finalized_transactions / actual_window_s if actual_window_s > 0 else 0
        
        return {
            "transactions_finalized": finalized_transactions,
            "time_window_s": actual_window_s,
            "tps": tps,
            "theoretical_max_tps": 2.22  # 450ms slots
        }
    
    def calculate_block_propagation_time(self, time_window_s: int = 60) -> Dict[str, float]:
        """Calculate block propagation time across network"""
        cutoff_time = time.time_ns() - (time_window_s * 1_000_000_000)
        propagation_times = []
        
        # Group events by block hash
        block_events = defaultdict(list)
        for event in self.events:
            if (event.block_hash and 
                event.timestamp_ns > cutoff_time and
                event.event_type in [ProtocolEvent.BLOCK_PROPOSAL_BROADCAST, ProtocolEvent.BLOCK_RECEIVED]):
                block_events[event.block_hash].append(event)
        
        # Calculate propagation times
        for block_hash, events in block_events.items():
            broadcast_events = [e for e in events if e.event_type == ProtocolEvent.BLOCK_PROPOSAL_BROADCAST]
            received_events = [e for e in events if e.event_type == ProtocolEvent.BLOCK_RECEIVED]
            
            if broadcast_events and received_events:
                broadcast_time = min(e.timestamp_ns for e in broadcast_events)
                
                # Calculate propagation time to each receiving node
                for received_event in received_events:
                    if received_event.timestamp_ns > broadcast_time:
                        propagation_time_ms = (received_event.timestamp_ns - broadcast_time) / 1_000_000
                        propagation_times.append(propagation_time_ms)
        
        if not propagation_times:
            return {"count": 0, "avg_ms": 0, "min_ms": 0, "max_ms": 0}
        
        return {
            "count": len(propagation_times),
            "avg_ms": statistics.mean(propagation_times),
            "min_ms": min(propagation_times),
            "max_ms": max(propagation_times),
            "p95_ms": statistics.quantiles(propagation_times, n=20)[18] if len(propagation_times) >= 20 else max(propagation_times)
        }
    
    def get_comprehensive_kpis(self, time_window_s: int = 60) -> Dict[str, Any]:
        """Get all KPIs in a comprehensive report"""
        return {
            "timestamp": time.time_ns(),
            "time_window_seconds": time_window_s,
            "transaction_latency": self.calculate_transaction_latency(time_window_s),
            "block_creation_time": self.calculate_block_creation_time(time_window_s),
            "consensus_latency": self.calculate_consensus_latency(time_window_s),
            "throughput": self.calculate_throughput_tps(time_window_s),
            "block_propagation": self.calculate_block_propagation_time(time_window_s),
            "total_events_tracked": len(self.events),
            "unique_transactions": len(set(e.transaction_id for e in self.events if e.transaction_id)),
            "unique_blocks": len(set(e.block_hash for e in self.events if e.block_hash))
        }


class PerformanceMonitor:
    """Main performance monitoring framework"""
    
    def __init__(self, node_id: str, enabled: bool = True, log_to_file: bool = True):
        self.node_id = node_id
        self.enabled = enabled
        self.log_to_file = log_to_file
        self.events = []  # List to store performance events
        self.kpi_calculator = KPICalculator()
        self._lock = threading.Lock()
        
        # Set up structured logging
        self.logger = logging.getLogger(f"performance_monitor_{node_id}")
        self.logger.setLevel(logging.INFO)
        
        if log_to_file:
            handler = logging.FileHandler(f"performance_logs_{node_id}.jsonl")
            handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(handler)
        
        # Console handler for critical events
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(logging.Formatter('PERF: %(message)s'))
        self.logger.addHandler(console_handler)
    
    def record_event(self, 
                    event_type: ProtocolEvent,
                    block_hash: Optional[str] = None,
                    transaction_id: Optional[str] = None,
                    slot_number: Optional[int] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> str:
        """Record a performance event with high-precision timing"""
        if not self.enabled:
            return ""
        
        event_id = str(uuid.uuid4())
        timestamp_ns = time.time_ns()
        
        event = PerformanceEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp_ns=timestamp_ns,
            node_id=self.node_id,
            block_hash=block_hash,
            transaction_id=transaction_id,
            slot_number=slot_number,
            metadata=metadata or {}
        )
        
        # Log structured event
        self.logger.info(event.to_json())
        
        # Store event for retrieval
        with self._lock:
            self.events.append(event)
            # Keep only the last 10000 events to prevent memory issues
            if len(self.events) > 10000:
                self.events = self.events[-5000:]  # Keep last 5000 events
        
        # Add to KPI calculator
        self.kpi_calculator.add_event(event)
        
        return event
    
    def get_kpis(self, time_window_s: int = 60) -> Dict[str, Any]:
        """Get current KPIs"""
        return self.kpi_calculator.get_comprehensive_kpis(time_window_s)
    
    def get_recent_events(self, limit: int = 100) -> List[PerformanceEvent]:
        """Get recent performance events"""
        with self._lock:
            # Return the most recent events, up to the specified limit
            return list(self.events[-limit:]) if self.events else []
    
    def get_events_by_type(self, event_type: ProtocolEvent, limit: int = 50) -> List[PerformanceEvent]:
        """Get recent events of a specific type"""
        with self._lock:
            filtered_events = [e for e in self.events if e.event_type == event_type]
            return filtered_events[-limit:] if filtered_events else []
    
    def clear_events(self):
        """Clear all stored events"""
        with self._lock:
            self.events.clear()
    
    def enable(self):
        """Enable performance monitoring"""
        self.enabled = True
    
    def disable(self):
        """Disable performance monitoring"""
        self.enabled = False


class PerformanceInstrumentation:
    """Decorator and context manager for automatic instrumentation"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
    
    def instrument_method(self, 
                         start_event: ProtocolEvent,
                         end_event: ProtocolEvent,
                         extract_metadata: Optional[Callable] = None):
        """Decorator to instrument method calls"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not self.monitor.enabled:
                    return func(*args, **kwargs)
                
                # Extract metadata from arguments
                metadata = {}
                if extract_metadata:
                    try:
                        metadata = extract_metadata(*args, **kwargs)
                    except Exception:
                        pass
                
                # Record start event
                start_event_id = self.monitor.record_event(
                    start_event,
                    metadata.get('block_hash'),
                    metadata.get('transaction_id'),
                    metadata.get('slot_number'),
                    {**metadata, 'method': func.__name__, 'start_event_id': None}
                )
                
                start_time = time.time_ns()
                try:
                    result = func(*args, **kwargs)
                    success = True
                    error_msg = None
                except Exception as e:
                    success = False
                    error_msg = str(e)
                    raise
                finally:
                    # Record end event
                    end_time = time.time_ns()
                    duration_ms = (end_time - start_time) / 1_000_000
                    
                    self.monitor.record_event(
                        end_event,
                        metadata.get('block_hash'),
                        metadata.get('transaction_id'),
                        metadata.get('slot_number'),
                        {
                            **metadata,
                            'method': func.__name__,
                            'start_event_id': start_event_id,
                            'duration_ms': duration_ms,
                            'success': success,
                            'error': error_msg
                        }
                    )
                
                return result
            return wrapper
        return decorator
    
    def event_context(self, 
                     event_type: ProtocolEvent,
                     block_hash: Optional[str] = None,
                     transaction_id: Optional[str] = None,
                     slot_number: Optional[int] = None,
                     metadata: Optional[Dict[str, Any]] = None):
        """Context manager for timing operations"""
        class EventContext:
            def __init__(self, monitor, event_type, block_hash, transaction_id, slot_number, metadata):
                self.monitor = monitor
                self.event_type = event_type
                self.block_hash = block_hash
                self.transaction_id = transaction_id
                self.slot_number = slot_number
                self.metadata = metadata or {}
                self.start_time = None
                self.event_id = None
            
            def __enter__(self):
                if self.monitor.enabled:
                    self.start_time = time.time_ns()
                    self.event_id = self.monitor.record_event(
                        self.event_type,
                        self.block_hash,
                        self.transaction_id,
                        self.slot_number,
                        self.metadata
                    )
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.monitor.enabled and self.start_time:
                    duration_ms = (time.time_ns() - self.start_time) / 1_000_000
                    success = exc_type is None
                    
                    # Record completion metadata
                    completion_metadata = {
                        **self.metadata,
                        'start_event_id': self.event_id,
                        'duration_ms': duration_ms,
                        'success': success
                    }
                    if exc_val:
                        completion_metadata['error'] = str(exc_val)
                    
                    # Don't record end event for instantaneous events
                    if self.event_type not in [ProtocolEvent.TRANSACTION_INGRESS, ProtocolEvent.BLOCK_RECEIVED]:
                        pass  # Could record completion event if needed
        
        return EventContext(self.monitor, event_type, block_hash, transaction_id, slot_number, metadata)


# Global performance monitor instance (initialized by blockchain)
_global_monitor: Optional[PerformanceMonitor] = None


def initialize_performance_monitoring(node_id: str, enabled: bool = True) -> PerformanceMonitor:
    """Initialize global performance monitoring"""
    global _global_monitor
    _global_monitor = PerformanceMonitor(node_id, enabled)
    return _global_monitor


def get_performance_monitor() -> Optional[PerformanceMonitor]:
    """Get global performance monitor instance"""
    return _global_monitor


def record_event(event_type: ProtocolEvent, **kwargs) -> str:
    """Convenience function to record performance event"""
    if _global_monitor:
        return _global_monitor.record_event(event_type, **kwargs)
    return ""


def get_current_kpis(time_window_s: int = 60) -> Dict[str, Any]:
    """Convenience function to get current KPIs"""
    if _global_monitor:
        return _global_monitor.get_kpis(time_window_s)
    return {}


# Utility functions for common event recording patterns
def record_transaction_ingress(transaction_id: str, metadata: Optional[Dict] = None) -> str:
    """Record transaction ingress event"""
    return record_event(
        ProtocolEvent.TRANSACTION_INGRESS,
        transaction_id=transaction_id,
        metadata=metadata
    )


def record_block_creation_start(block_hash: str, slot_number: int, transaction_count: int) -> str:
    """Record start of block creation"""
    return record_event(
        ProtocolEvent.BLOCK_PACKING_START,
        block_hash=block_hash,
        slot_number=slot_number,
        metadata={'transaction_count': transaction_count}
    )


def record_block_proposal(block_hash: str, slot_number: int, transaction_count: int, leader_id: str) -> str:
    """Record block proposal broadcast"""
    return record_event(
        ProtocolEvent.BLOCK_PROPOSAL_BROADCAST,
        block_hash=block_hash,
        slot_number=slot_number,
        metadata={'transaction_count': transaction_count, 'leader_id': leader_id}
    )


def record_block_finalization(block_hash: str, transaction_ids: List[str]) -> str:
    """Record block finalization with all transaction IDs"""
    events = []
    for tx_id in transaction_ids:
        event_id = record_event(
            ProtocolEvent.BLOCK_FINALIZATION,
            block_hash=block_hash,
            transaction_id=tx_id,
            metadata={'finalized_with_block': block_hash}
        )
        events.append(event_id)
    return events[0] if events else ""


if __name__ == "__main__":
    # Example usage and testing
    monitor = initialize_performance_monitoring("test_node_1")
    
    # Simulate some events
    tx_id = "tx_123"
    block_hash = "block_456"
    
    # Transaction lifecycle
    record_transaction_ingress(tx_id, {'source': 'client_wallet'})
    time.sleep(0.001)  # 1ms
    
    # Block creation
    record_block_creation_start(block_hash, 100, 5)
    time.sleep(0.05)   # 50ms
    record_block_proposal(block_hash, 100, 5, "leader_node")
    time.sleep(0.02)   # 20ms
    
    # Block finalization
    record_block_finalization(block_hash, [tx_id])
    
    # Get KPIs
    kpis = get_current_kpis(60)
    print(json.dumps(kpis, indent=2))
