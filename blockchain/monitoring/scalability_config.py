#!/usr/bin/env python3
"""
Scalability Configuration for Quantum Annealing Consensus
Optimized parameters for handling 1000+ nodes efficiently.
"""

class ScalabilityConfig:
    """Configuration parameters optimized for large-scale networks"""
    
    # Core scalability parameters
    MAX_CANDIDATE_NODES = 50  # Limit quantum optimization problem size
    PROBE_SAMPLE_SIZE = 20    # O(sqrt(n)) probe sampling
    WITNESS_SAMPLE_SIZE = 10  # Witness pool size for large networks
    
    # Performance caching
    PERFORMANCE_CACHE_TTL = 60  # Cache performance scores for 1 minute
    PERFORMANCE_HISTORY_WINDOW = 100  # Keep last N performance records
    
    # Node management
    NODE_INACTIVE_THRESHOLD = 3600  # Remove nodes after 1 hour of inactivity
    NODE_ACTIVE_THRESHOLD = 300     # Consider nodes active if seen within 5 minutes
    
    # Quantum annealing optimization
    QUANTUM_READS_SCALING = {
        'small': (1, 50, 50),      # (min_nodes, max_nodes, num_reads)
        'medium': (51, 200, 75),   # Scale reads with problem complexity
        'large': (201, 500, 100),
        'xlarge': (501, 1000, 125),
        'xxlarge': (1001, float('inf'), 150)
    }
    
    # Network clustering (for geographic/performance-based optimization)
    ENABLE_NODE_CLUSTERING = True
    CLUSTER_COUNT = 10  # Number of geographic/performance clusters
    CLUSTER_REPRESENTATIVES = 5  # Representatives per cluster for selection
    
    # Probe protocol optimization
    PROBE_PARALLEL_LIMIT = 10  # Maximum parallel probe operations
    PROBE_TIMEOUT = 1.0        # Probe timeout in seconds
    PROBE_BATCH_SIZE = 50      # Process probes in batches
    
    # Memory management
    MEMORY_CLEANUP_INTERVAL = 300  # Cleanup every 5 minutes
    MAX_PROBE_HISTORY = 1000       # Keep last N probe records
    MAX_CACHE_ENTRIES = 5000       # Maximum cached performance scores
    
    @classmethod
    def get_quantum_reads_for_size(cls, node_count: int) -> int:
        """Get optimal number of quantum reads based on network size"""
        for size_class, (min_nodes, max_nodes, num_reads) in cls.QUANTUM_READS_SCALING.items():
            if min_nodes <= node_count <= max_nodes:
                return num_reads
        return 150  # Default for very large networks
    
    @classmethod
    def get_probe_sample_size(cls, node_count: int) -> int:
        """Calculate optimal probe sample size for given network size"""
        if node_count <= 10:
            return node_count  # Probe all nodes for small networks
        elif node_count <= 100:
            return min(cls.PROBE_SAMPLE_SIZE, node_count // 2)
        else:
            # O(sqrt(n)) scaling for large networks
            import math
            return min(cls.PROBE_SAMPLE_SIZE, int(math.sqrt(node_count) * 2))
    
    @classmethod
    def get_candidate_limit(cls, node_count: int) -> int:
        """Get candidate node limit based on network size"""
        if node_count <= cls.MAX_CANDIDATE_NODES:
            return node_count
        else:
            # Logarithmic scaling for very large networks
            import math
            return min(cls.MAX_CANDIDATE_NODES, int(cls.MAX_CANDIDATE_NODES * math.log10(node_count / 10)))


class PerformanceMonitor:
    """Monitor and track performance metrics for scalability analysis"""
    
    def __init__(self):
        self.metrics = {
            'selection_times': [],
            'probe_times': [],
            'cache_hit_rates': [],
            'memory_usage': [],
            'node_counts': []
        }
        self.start_time = None
    
    def start_monitoring(self):
        """Start performance monitoring"""
        import time
        self.start_time = time.time()
    
    def record_selection_time(self, duration: float, node_count: int):
        """Record node selection time"""
        self.metrics['selection_times'].append(duration)
        self.metrics['node_counts'].append(node_count)
    
    def record_probe_time(self, duration: float):
        """Record probe protocol execution time"""
        self.metrics['probe_times'].append(duration)
    
    def record_cache_hit_rate(self, hit_rate: float):
        """Record cache hit rate"""
        self.metrics['cache_hit_rates'].append(hit_rate)
    
    def get_performance_summary(self) -> dict:
        """Get performance summary statistics"""
        import statistics
        
        summary = {}
        
        if self.metrics['selection_times']:
            summary['avg_selection_time'] = statistics.mean(self.metrics['selection_times'])
            summary['max_selection_time'] = max(self.metrics['selection_times'])
            summary['selection_time_std'] = statistics.stdev(self.metrics['selection_times']) if len(self.metrics['selection_times']) > 1 else 0
        
        if self.metrics['probe_times']:
            summary['avg_probe_time'] = statistics.mean(self.metrics['probe_times'])
            summary['max_probe_time'] = max(self.metrics['probe_times'])
        
        if self.metrics['cache_hit_rates']:
            summary['avg_cache_hit_rate'] = statistics.mean(self.metrics['cache_hit_rates'])
        
        if self.metrics['node_counts']:
            summary['max_nodes_tested'] = max(self.metrics['node_counts'])
            summary['total_selections'] = len(self.metrics['node_counts'])
        
        if self.start_time:
            import time
            summary['total_monitoring_time'] = time.time() - self.start_time
        
        return summary
    
    def is_performance_acceptable(self, max_selection_time: float = 5.0) -> bool:
        """Check if performance meets scalability requirements"""
        if not self.metrics['selection_times']:
            return False
        
        max_time = max(self.metrics['selection_times'])
        return max_time <= max_selection_time


# Export configuration for use in quantum consensus
SCALABILITY_CONFIG = ScalabilityConfig()
PERFORMANCE_MONITOR = PerformanceMonitor()
