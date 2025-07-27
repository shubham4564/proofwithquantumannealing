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


@router.get("/leader/current/", name="Get current leader information")
async def current_leader_info(request: Request):
    """Get detailed information about the current leader and slot timing"""
    node = request.app.state.node
    
    try:
        # Get current leader info from blockchain
        leader_info = node.blockchain.get_current_leader_info()
        
        # Get additional blockchain state for context
        quantum_metrics = node.blockchain.get_quantum_metrics()
        
        return {
            "current_leader_info": leader_info,
            "consensus_context": {
                "total_nodes": quantum_metrics.get("total_nodes", 0),
                "active_nodes": quantum_metrics.get("active_nodes", 0),
                "gossip_peers": quantum_metrics.get("gossip_protocol", {}).get("active_peers", 0)
            },
            "node_public_key": node.wallet.public_key_string()[:30] + "..." if hasattr(node, 'wallet') else "unknown",
            "am_i_current_leader": node.blockchain.am_i_current_leader(node.wallet.public_key_string()) if hasattr(node, 'wallet') else False,
            "timestamp": leader_info.get("slot_start_time", 0)
        }
        
    except Exception as e:
        return {
            "error": f"Failed to get current leader info: {str(e)}",
            "fallback_proposer": node.blockchain.next_block_proposer() if hasattr(node.blockchain, 'next_block_proposer') else None
        }


@router.get("/leader/upcoming/", name="Get upcoming leaders schedule")
async def upcoming_leaders(request: Request):
    """Get information about upcoming leaders for Gulf Stream and transaction forwarding"""
    node = request.app.state.node
    
    try:
        # Get current leader info which includes upcoming leaders
        leader_info = node.blockchain.get_current_leader_info()
        upcoming_targets = leader_info.get("upcoming_leaders", [])
        
        # Check if this node is an upcoming leader
        my_public_key = getattr(node, 'public_key', '')
        upcoming_leadership = None
        if my_public_key:
            upcoming_leadership = node.blockchain.am_i_upcoming_leader(my_public_key, within_seconds=300)  # Next 5 minutes
        
        return {
            "upcoming_leaders": upcoming_targets,
            "schedule_size": len(upcoming_targets),
            "my_upcoming_leadership": upcoming_leadership,
            "leader_schedule_epoch": node.blockchain.leader_schedule.current_epoch,
            "slot_duration_seconds": node.blockchain.leader_schedule.slot_duration_seconds,
            "current_slot": node.blockchain.leader_schedule.get_current_slot(),
            "schedule_advance_time": 120  # Leaders known 2 minutes in advance
        }
        
    except Exception as e:
        return {
            "error": f"Failed to get upcoming leaders: {str(e)}",
            "upcoming_leaders": [],
            "schedule_size": 0
        }


@router.get("/leader/schedule/", name="Get full leader schedule")
async def leader_schedule(request: Request):
    """Get the complete leader schedule for the current and next epoch"""
    node = request.app.state.node
    
    try:
        leader_schedule = node.blockchain.leader_schedule
        
        # Get schedules in a readable format
        current_schedule_readable = {}
        for slot, leader in leader_schedule.current_schedule.items():
            current_schedule_readable[str(slot)] = leader[:30] + "..." if leader else "None"
        
        next_schedule_readable = {}
        for slot, leader in leader_schedule.next_schedule.items():
            next_schedule_readable[str(slot)] = leader[:30] + "..." if leader else "None"
        
        return {
            "current_epoch": leader_schedule.current_epoch,
            "current_schedule": current_schedule_readable,
            "current_schedule_size": len(leader_schedule.current_schedule),
            "next_epoch": leader_schedule.current_epoch + 1,
            "next_schedule": next_schedule_readable,
            "next_schedule_size": len(leader_schedule.next_schedule),
            "slot_duration_seconds": leader_schedule.slot_duration_seconds,
            "epoch_start_time": leader_schedule.epoch_start_time,
            "current_slot": leader_schedule.get_current_slot(),
            "slots_per_epoch": leader_schedule.slots_per_epoch
        }
        
    except Exception as e:
        return {
            "error": f"Failed to get leader schedule: {str(e)}",
            "current_epoch": 0,
            "current_schedule": {},
            "next_schedule": {}
        }


@router.get("/leader/quantum-selection/", name="Get quantum consensus leader selection details")
async def quantum_leader_selection(request: Request):
    """Get detailed quantum annealing consensus leader selection information"""
    node = request.app.state.node
    
    try:
        quantum_metrics = node.blockchain.get_quantum_metrics()
        
        # Try to get the next block proposer using quantum consensus
        next_proposer = None
        if node.blockchain.quantum_consensus:
            try:
                last_block_hash = node.blockchain.blocks[-1].payload() if node.blockchain.blocks else "genesis"
                next_proposer = node.blockchain.quantum_consensus.select_representative_node(
                    str(last_block_hash)
                )
            except Exception as e:
                next_proposer = f"Selection failed: {str(e)}"
        
        return {
            "quantum_consensus_enabled": bool(node.blockchain.quantum_consensus),
            "next_quantum_proposer": next_proposer[:30] + "..." if next_proposer and len(str(next_proposer)) > 30 else next_proposer,
            "node_scores": quantum_metrics.get("node_scores", {}),
            "probe_statistics": quantum_metrics.get("probe_statistics", {}),
            "protocol_parameters": quantum_metrics.get("protocol_parameters", {}),
            "scoring_weights": quantum_metrics.get("scoring_weights", {}),
            "total_registered_nodes": quantum_metrics.get("total_nodes", 0),
            "active_nodes": quantum_metrics.get("active_nodes", 0)
        }
        
    except Exception as e:
        return {
            "error": f"Failed to get quantum leader selection details: {str(e)}",
            "quantum_consensus_enabled": False
        }
