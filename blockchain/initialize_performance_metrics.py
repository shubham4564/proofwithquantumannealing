#!/usr/bin/env python3
"""
Performance Metrics Initialization Module

This module provides utilities to initialize performance metrics collection
for the quantum blockchain node during startup.
"""

import logging
from performance_metrics_integration import (
    PerformanceMetricsCollector,
    BlockchainMetricsIntegrator
)

logger = logging.getLogger(__name__)


def initialize_performance_metrics(node):
    """
    Initialize performance metrics collection for a blockchain node.
    
    Args:
        node: The blockchain node instance
        
    Returns:
        bool: True if initialization successful, False otherwise
    """
    try:
        logger.info("Initializing performance metrics collection...")
        
        # Give the node a moment to fully initialize if needed
        import time
        time.sleep(0.5)
        
        # Create metrics collector
        metrics_collector = PerformanceMetricsCollector()
        
        # Create integrator for blockchain methods
        integrator = BlockchainMetricsIntegrator(metrics_collector)
        
        # Integrate with blockchain
        if hasattr(node, 'blockchain') and node.blockchain:
            integrator.integrate_blockchain_methods(node.blockchain)
            node.blockchain.metrics_collector = metrics_collector
            logger.info("✓ Blockchain metrics integration completed")
        else:
            logger.warning("Node does not have blockchain attribute or blockchain is None")
            
        # Integrate with transaction pool
        if hasattr(node, 'transaction_pool') and node.transaction_pool:
            integrator.integrate_transaction_pool_methods(node.transaction_pool)
            node.transaction_pool.metrics_collector = metrics_collector
            logger.info("✓ Transaction pool metrics integration completed")
        else:
            logger.warning("Node does not have transaction_pool attribute or transaction_pool is None")
            
        # Start background metrics collection
        integrator.start_background_collection()
        
        # Store integrator reference for later cleanup
        node.metrics_integrator = integrator
        
        logger.info("🚀 Performance metrics initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize performance metrics: {e}")
        return False


def cleanup_performance_metrics(node):
    """
    Clean up performance metrics collection when shutting down.
    
    Args:
        node: The blockchain node instance
    """
    try:
        if hasattr(node, 'metrics_integrator'):
            node.metrics_integrator.stop_background_collection()
            logger.info("Performance metrics collection stopped")
    except Exception as e:
        logger.error(f"Error during metrics cleanup: {e}")


def get_node_performance_summary(node):
    """
    Get a comprehensive performance summary for the node.
    
    Args:
        node: The blockchain node instance
        
    Returns:
        dict: Performance summary data
    """
    try:
        if not hasattr(node, 'blockchain') or not hasattr(node.blockchain, 'metrics_collector'):
            return {
                "status": "metrics_not_initialized",
                "message": "Performance metrics not initialized. Call initialize_performance_metrics() first.",
                "basic_info": {
                    "node_type": type(node).__name__,
                    "has_blockchain": hasattr(node, 'blockchain'),
                    "has_transaction_pool": hasattr(node, 'transaction_pool')
                }
            }
            
        collector = node.blockchain.metrics_collector
        comprehensive_metrics = collector.get_comprehensive_metrics()
        
        # Add node-specific information
        node_info = {
            "node_id": getattr(node, 'node_id', 'unknown'),
            "startup_time": getattr(node, 'startup_time', None),
            "node_type": type(node).__name__
        }
        
        blockchain_info = {}
        if hasattr(node, 'blockchain'):
            blockchain_info = {
                "total_blocks": len(node.blockchain.blocks),
                "blockchain_type": type(node.blockchain).__name__,
                "consensus_type": "quantum_annealing"
            }
            
        transaction_pool_info = {}
        if hasattr(node, 'transaction_pool'):
            transaction_pool_info = {
                "pending_transactions": len(node.transaction_pool.transactions),
                "forge_interval_ms": node.transaction_pool.forge_interval * 1000,
                "pool_type": type(node.transaction_pool).__name__
            }
        
        return {
            "status": "active",
            "timestamp": comprehensive_metrics.get("timestamp"),
            "node_info": node_info,
            "blockchain_info": blockchain_info,
            "transaction_pool_info": transaction_pool_info,
            "performance_metrics": comprehensive_metrics,
            "quantum_consensus_data": node.blockchain.get_quantum_metrics() if hasattr(node.blockchain, 'get_quantum_metrics') else {}
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to get performance summary"
        }


def validate_metrics_integration(node):
    """
    Validate that performance metrics are properly integrated.
    
    Args:
        node: The blockchain node instance
        
    Returns:
        dict: Validation results
    """
    results = {
        "overall_status": "unknown",
        "blockchain_integration": False,
        "transaction_pool_integration": False,
        "metrics_collector_present": False,
        "background_collection_active": False,
        "api_endpoints_enhanced": False,
        "details": []
    }
    
    try:
        # Check blockchain integration
        if hasattr(node, 'blockchain') and hasattr(node.blockchain, 'metrics_collector'):
            results["blockchain_integration"] = True
            results["metrics_collector_present"] = True
            results["details"].append("✓ Blockchain metrics collector attached")
        else:
            results["details"].append("❌ Blockchain metrics collector missing")
            
        # Check transaction pool integration
        if hasattr(node, 'transaction_pool') and hasattr(node.transaction_pool, 'metrics_collector'):
            results["transaction_pool_integration"] = True
            results["details"].append("✓ Transaction pool metrics collector attached")
        else:
            results["details"].append("❌ Transaction pool metrics collector missing")
            
        # Check background collection
        if hasattr(node, 'metrics_integrator'):
            integrator = node.metrics_integrator
            if hasattr(integrator, 'collection_thread') and integrator.collection_thread and integrator.collection_thread.is_alive():
                results["background_collection_active"] = True
                results["details"].append("✓ Background metrics collection active")
            else:
                results["details"].append("❌ Background metrics collection not active")
        else:
            results["details"].append("❌ Metrics integrator not found")
            
        # Determine overall status
        if results["blockchain_integration"] and results["transaction_pool_integration"] and results["background_collection_active"]:
            results["overall_status"] = "fully_integrated"
        elif results["metrics_collector_present"]:
            results["overall_status"] = "partially_integrated"
        else:
            results["overall_status"] = "not_integrated"
            
    except Exception as e:
        results["details"].append(f"❌ Validation error: {e}")
        results["overall_status"] = "error"
        
    return results


# Example usage and integration guide
if __name__ == "__main__":
    print("Performance Metrics Integration Guide")
    print("=" * 50)
    print()
    print("To integrate performance metrics into your blockchain node:")
    print()
    print("1. Import this module in your node startup script:")
    print("   from initialize_performance_metrics import initialize_performance_metrics")
    print()
    print("2. After creating your node instance, call:")
    print("   success = initialize_performance_metrics(node)")
    print()
    print("3. Validate integration:")
    print("   validation = validate_metrics_integration(node)")
    print("   print(validation)")
    print()
    print("4. Get performance summary:")
    print("   summary = get_node_performance_summary(node)")
    print()
    print("5. Access enhanced API endpoints:")
    print("   GET /api/v1/blockchain/performance-metrics/")
    print("   GET /api/v1/blockchain/transaction-pool/")
    print()
    print("6. During shutdown, clean up:")
    print("   cleanup_performance_metrics(node)")
