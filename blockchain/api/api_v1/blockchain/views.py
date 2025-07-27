from fastapi import APIRouter, Request
from pydantic import BaseModel

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


@router.post("/gossip/add_peer/", name="Add gossip peer")
async def add_gossip_peer(request: Request, peer_data: dict):
    """Add a peer to the gossip network"""
    node = request.app.state.node
    
    try:
        # Extract peer information from request
        peer_public_key = peer_data.get('peer_public_key')
        ip_address = peer_data.get('ip_address', 'localhost')
        gossip_port = peer_data.get('gossip_port')
        tpu_port = peer_data.get('tpu_port')
        tvu_port = peer_data.get('tvu_port')
        
        # Validate required fields
        if not all([peer_public_key, gossip_port, tpu_port, tvu_port]):
            return {
                "success": False,
                "error": "Missing required fields: peer_public_key, gossip_port, tpu_port, tvu_port"
            }
        
        # Add peer to gossip network
        node.blockchain.add_gossip_peer(
            peer_public_key=peer_public_key,
            ip_address=ip_address,
            gossip_port=gossip_port,
            tpu_port=tpu_port,
            tvu_port=tvu_port
        )
        
        return {
            "success": True,
            "message": f"Added gossip peer {peer_public_key[:20]}... at {ip_address}:{gossip_port}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to add gossip peer: {str(e)}"
        }


@router.get("/gossip/status/", name="Get gossip protocol status")
async def gossip_status(request: Request):
    """Get detailed gossip protocol status"""
    node = request.app.state.node
    
    if not node.blockchain.gossip_node:
        return {
            "gossip_enabled": False,
            "error": "Gossip protocol not initialized"
        }
    
    gossip_node = node.blockchain.gossip_node
    
    return {
        "gossip_enabled": True,
        "node_public_key": gossip_node.public_key[:20] + "..." if gossip_node.public_key else "unknown",
        "gossip_port": gossip_node.gossip_port,
        "tpu_port": gossip_node.tpu_port,
        "tvu_port": gossip_node.tvu_port,
        "active_peers": len(gossip_node.active_peers),
        "known_peers": len(gossip_node.known_peers),
        "pruned_peers": len(gossip_node.pruned_peers),
        "crds_size": gossip_node.crds.get_size(),
        "message_stats": gossip_node.get_stats(),
        "peer_list": [
            {
                "public_key": peer_key[:20] + "...",
                "contact_info": {
                    "ip": contact.ip_address,
                    "gossip_port": contact.gossip_port,
                    "tpu_port": contact.tpu_port,
                    "tvu_port": contact.tvu_port
                }
            }
            for peer_key, contact in list(gossip_node.known_peers.items())[:10]  # Show max 10 peers
        ]
    }
