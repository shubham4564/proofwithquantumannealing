from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/", name="View blockchain")
async def blockchain(request: Request):
    node = request.app.state.node
    return node.blockchain.to_dict()


@router.get("/quantum-metrics/", name="View quantum annealing metrics")
async def quantum_metrics(request: Request):
    """Get quantum annealing consensus metrics"""
    node = request.app.state.node
    return node.blockchain.get_quantum_metrics()


@router.get("/node-stats/", name="View enhanced node statistics")
async def node_stats(request: Request):
    """Get comprehensive node statistics including mempool and P2P metrics"""
    node = request.app.state.node
    
    # Check if node has enhanced statistics method
    if hasattr(node, 'get_enhanced_node_stats'):
        return node.get_enhanced_node_stats()
    else:
        # Fallback to basic stats for backward compatibility
        return {
            "node_info": {
                "ip": getattr(node, 'ip', 'unknown'),
                "port": getattr(node, 'port', 'unknown')
            },
            "blockchain": {
                "total_blocks": len(node.blockchain.blocks),
            },
            "transaction_pool": {
                "size": len(node.transaction_pool.transactions)
            },
            "note": "Enhanced statistics not available - using legacy node"
        }


@router.get("/mempool/", name="View transaction mempool")
async def mempool_stats(request: Request):
    """Get detailed transaction mempool statistics (Bitcoin-style)"""
    node = request.app.state.node
    
    # Check if node has enhanced mempool
    if hasattr(node, 'mempool'):
        mempool_stats = node.mempool.get_mempool_stats()
        
        # Add sample transactions for debugging
        sample_transactions = []
        for i, (tx_hash, tx) in enumerate(node.mempool.transactions.items()):
            if i >= 5:  # Show max 5 samples
                break
            sample_transactions.append({
                "hash": tx_hash[:16] + "...",
                "type": getattr(tx, 'type', 'unknown'),
                "sender": getattr(tx, 'sender_public_key', 'unknown')[:20] + "..." if hasattr(tx, 'sender_public_key') else 'unknown'
            })
        
        mempool_stats["sample_transactions"] = sample_transactions
        return mempool_stats
    else:
        # Fallback for legacy transaction pool
        return {
            "legacy_pool_size": len(node.transaction_pool.transactions),
            "note": "Enhanced mempool not available - showing legacy transaction pool"
        }
