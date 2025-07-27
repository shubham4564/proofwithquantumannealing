import copy
import time
from threading import Timer

from api.main import NodeAPI
from blockchain.blockchain import Blockchain
from blockchain.consensus.gulf_stream import GulfStreamProcessor
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fast_gulf_stream import FastGulfStreamForwarder
from blockchain.slot_producer import SlotBasedBlockProducer
from blockchain.p2p.message import Message, MessageType, InventoryItem, InventoryMessage, GetDataMessage
from blockchain.p2p.socket_communication import SocketCommunication
from blockchain.p2p.transaction_mempool import TransactionMempool
from blockchain.transaction.transaction_pool import TransactionPool
from blockchain.transaction.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils
from blockchain.utils.logger import logger


class Node:
    def __init__(self, ip, port, key=None):
        self.p2p = None
        self.ip = ip
        self.port = port
        
        # Calculate gossip protocol ports based on P2P port
        # P2P: 10000-10099, Gossip: 12000-12999, TPU: 13000-13999, TVU: 14000-14999
        self.gossip_port = 12000 + (port - 10000) if port >= 10000 else 12000
        self.tpu_port = 13000 + (port - 10000) if port >= 10000 else 13000
        self.tvu_port = 14000 + (port - 10000) if port >= 10000 else 14000
        
        # Legacy transaction pool for backward compatibility
        self.transaction_pool = TransactionPool()
        
        # New Bitcoin-style mempool for efficient P2P propagation
        self.mempool = TransactionMempool()
        
        self.wallet = Wallet()
        if key is not None:
            self.wallet.from_key(key)
            
        # Initialize blockchain with this node's public key for gossip integration
        self.blockchain = Blockchain(genesis_public_key=self.wallet.public_key_string())
        
        # ENHANCED: Register this node with quantum consensus immediately at startup
        if self.blockchain.quantum_consensus:
            try:
                self.blockchain.quantum_consensus.register_node(
                    self.wallet.public_key_string(), 
                    self.wallet.public_key_string()
                )
                logger.info(f"Node registered with quantum consensus: {self.wallet.public_key_string()[:20]}...")
            except Exception as e:
                logger.warning(f"Failed to register node with quantum consensus: {e}")
        
        # Initialize gossip node with this node's specific ports (after blockchain creation)
        if self.blockchain.gossip_node:
            # Update gossip node with node-specific IP and ports
            try:
                self.blockchain.initialize_gossip_node(
                    public_key=self.wallet.public_key_string(),
                    ip_address=self.ip,
                    gossip_port=self.gossip_port,
                    tpu_port=self.tpu_port,
                    tvu_port=self.tvu_port
                )
                logger.info(f"Gossip node reconfigured for node-specific ports: gossip={self.gossip_port}, tpu={self.tpu_port}, tvu={self.tvu_port}")
            except Exception as e:
                logger.warning(f"Failed to reconfigure gossip node ports: {e}")
        
        # Initialize Gulf Stream for transaction forwarding
        self.gulf_stream = GulfStreamProcessor(self.blockchain.leader_schedule)
        
        # Initialize Fast Gulf Stream for UDP forwarding to current/next leaders
        self.fast_gulf_stream = FastGulfStreamForwarder(
            node_public_key=self.wallet.public_key_string(),
            leader_schedule=self.blockchain.leader_schedule,
            port_base=15000  # Use ports 15000-15999 for Gulf Stream UDP
        )
        logger.info("Gulf Stream processor initialized")
        
        # Initialize slot-based block production
        self.slot_producer = SlotBasedBlockProducer(self)
        
        # Track seen blocks to prevent rebroadcast loops
        self.seen_blocks = set()
        
        # Connection health tracking
        self.peer_health = {}  # peer_id -> last_ping_time
        self.ping_interval = 60  # Ping peers every 60 seconds

    def start_p2p(self, enhanced=True):
        """
        Start P2P communication system with integrated gossip protocol.
        
        Args:
            enhanced (bool): If True, use Bitcoin-style enhanced P2P with INV/GETDATA/TX.
                           If False, use legacy direct broadcast system.
        """
        if enhanced:
            logger.info("Starting enhanced Bitcoin-style P2P system with gossip protocol")
            self.start_p2p_enhanced()
        else:
            logger.info("Starting legacy P2P system with gossip protocol")
            self.start_p2p_legacy()
        
        # Start gossip protocol for leader schedule distribution
        self.start_gossip_protocol()
    
    def start_gossip_protocol(self):
        """Start the gossip protocol for leader schedule distribution"""
        try:
            if not self.blockchain.gossip_node:
                logger.warning("Gossip node not initialized, cannot start")
                return
            
            # Start gossip node asynchronously
            import asyncio
            import threading
            
            def start_gossip_async():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.blockchain.start_gossip_node())
                except Exception as e:
                    logger.error(f"Failed to start gossip node: {e}")
            
            self.gossip_thread = threading.Thread(target=start_gossip_async, daemon=True)
            self.gossip_thread.start()
            
            logger.info({
                "message": "Gossip protocol started",
                "gossip_port": self.gossip_port,
                "tpu_port": self.tpu_port,
                "tvu_port": self.tvu_port,
                "public_key": self.wallet.public_key_string()[:20] + "..."
            })
            
        except Exception as e:
            logger.error(f"Failed to start gossip protocol: {e}")
    
    def start_p2p_legacy(self):
        """Start the legacy P2P communication system (direct broadcast)"""
        self.p2p = SocketCommunication(self.ip, self.port)
        self.p2p.start_socket_communication(self)
        
        # Start periodic heartbeat to stay active in quantum consensus
        import threading
        self.heartbeat_active = True
        self.heartbeat_thread = threading.Thread(target=self._quantum_heartbeat, daemon=True)
        self.heartbeat_thread.start()
        
        logger.info("Legacy P2P system started")
        
    def _quantum_heartbeat(self):
        """Periodically update node activity in quantum consensus"""
        import time
        while self.heartbeat_active:
            try:
                # Re-register to update last_seen time (reduced frequency for CPU optimization)
                self.blockchain.quantum_consensus.register_node(
                    self.wallet.public_key_string(), 
                    self.wallet.public_key_string()
                )
                time.sleep(60)  # Reduced from 15s to 60s to lower CPU usage
            except Exception as e:
                logger.error({"message": "Heartbeat error", "error": str(e)})
                time.sleep(10)  # Increased error recovery time

    def start_slot_production(self):
        """Start Solana-style slot-based block production"""
        self.slot_producer.start_slot_production()
        logger.info("Slot-based block production enabled")
    
    def stop_slot_production(self):
        """Stop slot-based block production"""
        self.slot_producer.stop_slot_production()
        logger.info("Slot-based block production disabled")
    
    def get_slot_info(self):
        """Get current slot timing and production information"""
        return self.slot_producer.get_slot_info()
    
    def get_node_status(self):
        """Get comprehensive node status including gossip protocol"""
        status = {
            'node_info': {
                'ip': self.ip,
                'p2p_port': self.port,
                'gossip_port': self.gossip_port,
                'tpu_port': self.tpu_port,
                'tvu_port': self.tvu_port,
                'public_key': self.wallet.public_key_string()[:30] + "..."
            },
            'p2p_status': {
                'active': bool(self.p2p),
                'connected_peers': len(self.p2p.all_nodes) if self.p2p else 0,
                'peer_health': len([p for p in self.peer_health.values() if time.time() - p < 300])  # Active in last 5 min
            },
            'blockchain_status': self.blockchain.get_integration_status(),
            'transaction_pools': {
                'legacy_pool': len(self.transaction_pool.transactions),
                'mempool': len(self.mempool.transactions),
                'gulf_stream': self.blockchain.gulf_stream_node.get_gulf_stream_status() if self.blockchain.gulf_stream_node else None,
                'fast_gulf_stream': self.fast_gulf_stream.get_metrics() if self.fast_gulf_stream else None
            },
            'gossip_protocol': self.blockchain.get_gossip_stats(),
            'slot_production': {
                'enabled': hasattr(self, 'slot_producer') and self.slot_producer.is_running if hasattr(self.slot_producer, 'is_running') else False,
                'slot_info': self.get_slot_info()
            }
        }
        return status

    def start_node_api(self, api_port):
        self.api = NodeAPI()
        self.api.inject_node(self)
        self.api.start(self.ip, api_port)

    def handle_transaction(self, transaction, from_api=False, source_peer=None):
        """
        Handle incoming transaction with Gulf Stream integration.
        
        Args:
            transaction: Transaction object to process
            from_api: True if transaction came from API, False if from P2P
            source_peer: Peer ID that sent the transaction (for P2P tracking)
        """
        # Register node in quantum consensus if available
        if self.blockchain and self.blockchain.quantum_consensus:
            self.blockchain.quantum_consensus.register_node(
                self.wallet.public_key_string(), 
                self.wallet.public_key_string()
            )
        
        # 1. Verification: Check transaction legitimacy
        data = transaction.payload()
        signature = transaction.signature
        signer_public_key = transaction.sender_public_key
        signature_valid = Wallet.signature_valid(data, signature, signer_public_key)
        
        # Check for duplicates in both pools
        transaction_in_legacy_pool = self.transaction_pool.transaction_exists(transaction)
        transaction_in_blockchain = self.blockchain.transaction_exists(transaction)
        
        # Calculate transaction hash for mempool
        tx_hash = self.mempool.calculate_transaction_hash(transaction)
        transaction_in_mempool = self.mempool.has_transaction(tx_hash)

        if not signature_valid:
            logger.warning({
                "message": "Transaction rejected - invalid signature",
                "tx_hash": tx_hash[:16] + "...",
                "sender": transaction.sender_public_key[:20] + "...",
                "source": "API" if from_api else f"P2P({source_peer[:10]}...)" if source_peer else "P2P"
            })
            return

        if transaction_in_legacy_pool or transaction_in_blockchain or transaction_in_mempool:
            logger.debug({
                "message": "Transaction already known - not propagating",
                "tx_hash": tx_hash[:16] + "...",
                "in_legacy_pool": transaction_in_legacy_pool,
                "in_blockchain": transaction_in_blockchain,
                "in_mempool": transaction_in_mempool,
                "source": "API" if from_api else f"P2P({source_peer[:10]}...)" if source_peer else "P2P"
            })
            return

        # 2. Submit to blockchain's Gulf Stream system
        try:
            if not self.blockchain:
                raise Exception("Blockchain not initialized")
                
            result = self.blockchain.submit_transaction(transaction)
            
            # 3. FAST FORWARD: Immediately forward to current and next leaders via UDP
            # Convert transaction object to dictionary format for Fast Gulf Stream
            transaction_dict = {
                'sender_public_key': transaction.sender_public_key,
                'receiver_public_key': transaction.receiver_public_key,
                'amount': transaction.amount,
                'transaction_type': transaction.type,  # Use .type instead of .transaction_type
                'timestamp': transaction.timestamp,    # Use .timestamp directly
                'transaction_id': transaction.id       # Use .id instead of .transaction_id
            }
            
            # Check if Fast Gulf Stream is available before using it
            fast_forward_result = {}
            if hasattr(self, 'fast_gulf_stream') and self.fast_gulf_stream:
                fast_forward_result = self.fast_gulf_stream.forward_transaction_fast(transaction_dict)
                # Ensure result is a dictionary (handle legacy boolean returns)
                if not isinstance(fast_forward_result, dict):
                    fast_forward_result = {
                        'current_leader_sent': bool(fast_forward_result),
                        'next_leader_sent': False,
                        'forward_time_ms': 0,
                        'success': bool(fast_forward_result)
                    }
            else:
                logger.warning({"message": "Fast Gulf Stream not available, skipping fast forward"})
            
            logger.info({
                "message": "Transaction submitted via Gulf Stream",
                "tx_hash": tx_hash[:16] + "...",
                "transaction_id": result.get('transaction_id', tx_hash[:8]),
                "transaction_type": transaction.type,
                "sender": transaction.sender_public_key[:20] + "...",
                "receiver": transaction.receiver_public_key[:20] + "...",
                "source": "API" if from_api else f"P2P({source_peer[:10]}...)" if source_peer else "P2P",
                "fast_forward": {
                    "current_leader_sent": fast_forward_result.get('current_leader_sent', False),
                    "next_leader_sent": fast_forward_result.get('next_leader_sent', False),
                    "forward_time_ms": fast_forward_result.get('forward_time_ms', 0)
                },
                "gulf_stream_stats": result.get('gulf_stream_status', {}).get('forwarding_stats', {})
            })
            
        except Exception as e:
            logger.error({
                "message": "Gulf Stream submission failed - transaction rejected",
                "error": str(e),
                "tx_hash": tx_hash[:16] + "..."
            })
            
            # No fallback - Gulf Stream only
            # Transaction is rejected if Gulf Stream fails
            return

        # Check if block proposal is needed
        block_proposal_required = self.transaction_pool.forging_required()  # Method name kept for compatibility
        
        # ENHANCED: Current leader should create blocks more frequently if they have transactions
        current_leader = self.blockchain.leader_schedule.get_current_leader()
        am_current_leader = (current_leader == self.wallet.public_key_string())
        
        # Get available transactions for block creation (Fast Gulf Stream + regular Gulf Stream + local)
        available_transactions = []
        gulf_stream_transactions = []
        fast_gulf_stream_transactions = []
        
        if am_current_leader:
            # PRIORITY 1: Get Fast Gulf Stream transactions (UDP forwarded)
            fast_gulf_stream_transactions = self.fast_gulf_stream.get_transactions_for_leader(self.wallet.public_key_string())
            available_transactions.extend(fast_gulf_stream_transactions)
            
            # PRIORITY 2: Get regular Gulf Stream transactions (in-memory forwarded)
            gulf_stream_transactions = self.blockchain.gulf_stream_node.get_transactions_for_leader(self.wallet.public_key_string())
            available_transactions.extend(gulf_stream_transactions)
        
        # PRIORITY 3: Add local transaction pool
        available_transactions.extend(self.transaction_pool.transactions)
        
        # ENHANCED: Immediate block creation if I'm leader with transactions
        should_create_block = (
            am_current_leader and len(available_transactions) > 0
        ) or block_proposal_required
        
        if should_create_block:
            logger.info({
                "message": "Triggering block creation as current leader",
                "am_current_leader": am_current_leader,
                "fast_gulf_stream_transactions": len(fast_gulf_stream_transactions) if am_current_leader else 0,
                "gulf_stream_transactions": len(gulf_stream_transactions) if am_current_leader else 0,
                "legacy_pool_size": len(self.transaction_pool.transactions),
                "total_available_transactions": len(available_transactions),
                "mempool_size": len(self.mempool.transactions),
                "reason": "Current leader with transactions" if am_current_leader and len(available_transactions) > 0 else "4-second interval reached"
            })
            self.propose_block()
        
        # OLD CODE: More frequent block proposal checks - every 5 transactions or when interval is reached
        elif len(self.transaction_pool.transactions) % 5 == 0 and len(self.transaction_pool.transactions) > 0:
            logger.info({
                "message": "Fallback: Legacy block proposal check (every 5 transactions)",
                "legacy_pool_size": len(self.transaction_pool.transactions),
                "mempool_size": len(self.mempool.transactions),
                "node_public_key": self.wallet.public_key_string()[:20] + "...",
                "am_current_leader": am_current_leader
            })
            self.propose_block()
            logger.info({
                "message": "Checking 4-second block proposal interval",
                "block_proposal_required": block_proposal_required,
                "legacy_pool_size": len(self.transaction_pool.transactions),
                "mempool_size": len(self.mempool.transactions),
                "node_public_key": self.wallet.public_key_string()[:20] + "...",
                "source": "API" if from_api else "P2P"
            })
        
        if block_proposal_required:
            if from_api:
                time.sleep(0.1)  # Brief delay to allow quantum consensus calculations
                
            logger.info({
                "message": "4-second interval reached, attempting quantum consensus block proposal",
                "source": "API" if from_api else "P2P"
            })
            self.propose_block()

    def handle_inventory(self, connected_node, inv_data):
        """
        Handle Bitcoin-style INV message - announcements of available transactions/blocks.
        Responds with GETDATA for items we don't have.
        """
        try:
            inv_message = InventoryMessage.from_dict(inv_data)
            peer_id = f"{connected_node.host}:{connected_node.port}"
            
            # Separate transaction and block inventories
            tx_hashes = []
            block_hashes = []
            
            for item in inv_message.inventory:
                if item.type == InventoryItem.TYPE_TX:
                    tx_hashes.append(item.hash)
                elif item.type == InventoryItem.TYPE_BLOCK:
                    block_hashes.append(item.hash)
            
            # Find missing transactions we want to request
            missing_tx_hashes = self.mempool.get_missing_transactions(tx_hashes, peer_id)
            
            # For blocks, check against our blockchain (simplified)
            missing_block_hashes = []
            for block_hash in block_hashes:
                if block_hash not in self.seen_blocks:
                    missing_block_hashes.append(block_hash)
            
            # Send GETDATA request for missing items
            if missing_tx_hashes or missing_block_hashes:
                requested_items = []
                
                for tx_hash in missing_tx_hashes:
                    requested_items.append(InventoryItem(InventoryItem.TYPE_TX, tx_hash))
                
                for block_hash in missing_block_hashes:
                    requested_items.append(InventoryItem(InventoryItem.TYPE_BLOCK, block_hash))
                
                getdata_message = GetDataMessage(requested_items)
                message = Message(self.p2p.socket_connector, MessageType.GETDATA, getdata_message.to_dict())
                encoded_message = BlockchainUtils.encode(message)
                
                self.p2p.send_to_node(connected_node, encoded_message)
                
                logger.info({
                    "message": "Requested missing items via GETDATA",
                    "peer": peer_id,
                    "requested_transactions": len(missing_tx_hashes),
                    "requested_blocks": len(missing_block_hashes),
                    "sample_tx_hashes": [h[:8] + "..." for h in missing_tx_hashes[:3]]
                })
            
        except Exception as e:
            logger.error(f"Error handling INV message from {connected_node.host}:{connected_node.port}: {e}")

    def handle_getdata(self, connected_node, getdata_data):
        """
        Handle Bitcoin-style GETDATA message - requests for specific transactions/blocks.
        Responds with TX or BLOCK_DATA messages.
        """
        try:
            getdata_message = GetDataMessage.from_dict(getdata_data)
            peer_id = f"{connected_node.host}:{connected_node.port}"
            
            served_count = 0
            
            for item in getdata_message.inventory:
                if item.type == InventoryItem.TYPE_TX:
                    # Send transaction data
                    transaction = self.mempool.get_transaction(item.hash)
                    if transaction:
                        message = Message(self.p2p.socket_connector, MessageType.TX, transaction)
                        encoded_message = BlockchainUtils.encode(message)
                        self.p2p.send_to_node(connected_node, encoded_message)
                        served_count += 1
                        
                        # Update statistics
                        self.mempool.stats['total_served'] += 1
                
                elif item.type == InventoryItem.TYPE_BLOCK:
                    # Send block data (simplified - would need block lookup by hash)
                    # For now, use the last block as a placeholder
                    if self.blockchain.blocks:
                        last_block = self.blockchain.blocks[-1]
                        message = Message(self.p2p.socket_connector, MessageType.BLOCK_DATA, last_block)
                        encoded_message = BlockchainUtils.encode(message)
                        self.p2p.send_to_node(connected_node, encoded_message)
                        served_count += 1
            
            if served_count > 0:
                logger.info({
                    "message": "Served data requests via TX/BLOCK_DATA",
                    "peer": peer_id,
                    "served_items": served_count,
                    "total_requested": len(getdata_message.inventory)
                })
                
        except Exception as e:
            logger.error(f"Error handling GETDATA message from {connected_node.host}:{connected_node.port}: {e}")

    def handle_transaction_data(self, transaction):
        """
        Handle TX message - transaction data received in response to our GETDATA request.
        """
        # Calculate peer that sent this (would need better peer tracking in production)
        source_peer = "response_peer"  # Simplified
        
        # Process the transaction normally
        self.handle_transaction(transaction, from_api=False, source_peer=source_peer)

    def handle_block_data(self, block):
        """
        Handle BLOCK_DATA message - block data received in response to our GETDATA request.
        """
        # Process the block normally
        self.handle_block(block)

    def handle_ping(self, connected_node, ping_data):
        """Handle PING message and respond with PONG"""
        try:
            # Extract nonce from ping data
            nonce = ping_data.get('nonce', int(time.time()))
            
            # Respond with PONG containing the same nonce
            pong_data = {'nonce': nonce, 'timestamp': time.time()}
            message = Message(self.p2p.socket_connector, MessageType.PONG, pong_data)
            encoded_message = BlockchainUtils.encode(message)
            self.p2p.send_to_node(connected_node, encoded_message)
            
            peer_id = f"{connected_node.host}:{connected_node.port}"
            logger.debug(f"Responded to PING from {peer_id} with PONG")
            
        except Exception as e:
            logger.error(f"Error handling PING from {connected_node.host}:{connected_node.port}: {e}")

    def handle_pong(self, connected_node, pong_data):
        """Handle PONG message - response to our PING"""
        try:
            peer_id = f"{connected_node.host}:{connected_node.port}"
            current_time = time.time()
            
            # Update peer health tracking
            self.peer_health[peer_id] = current_time
            
            # Calculate latency if we have the original ping timestamp
            if 'timestamp' in pong_data:
                ping_time = pong_data['timestamp']
                latency = current_time - ping_time
                logger.debug(f"PONG received from {peer_id}, latency: {latency*1000:.1f}ms")
            
        except Exception as e:
            logger.error(f"Error handling PONG from {connected_node.host}:{connected_node.port}: {e}")

    def start_peer_health_monitoring(self):
        """Start periodic ping to maintain connection health (Bitcoin-style)"""
        def ping_peers():
            if not self.p2p or not hasattr(self.p2p, 'all_nodes'):
                return
            
            for peer in self.p2p.all_nodes:
                try:
                    ping_data = {'nonce': int(time.time()), 'timestamp': time.time()}
                    message = Message(self.p2p.socket_connector, MessageType.PING, ping_data)
                    encoded_message = BlockchainUtils.encode(message)
                    self.p2p.send_to_node(peer, encoded_message)
                except Exception as e:
                    logger.debug(f"Failed to ping peer {peer.host}:{peer.port}: {e}")
        
        # Schedule periodic pings
        def schedule_next_ping():
            ping_peers()
            timer = Timer(self.ping_interval, schedule_next_ping)
            timer.daemon = True
            timer.start()
        
        # Start the ping cycle
        timer = Timer(self.ping_interval, schedule_next_ping)
        timer.daemon = True
        timer.start()
        
        logger.info("Started peer health monitoring with periodic pings")

    def start_p2p_enhanced(self):
        """Start the enhanced Bitcoin-style P2P communication system"""
        logger.info({
            "message": "Starting enhanced P2P system with Bitcoin-style transaction propagation",
            "node_ip": self.ip,
            "node_port": self.port,
            "features": ["INV/GETDATA/TX", "Gossip Protocol", "Peer Health Monitoring", "Transaction Mempool"]
        })
        
        # Start the standard P2P system
        self.p2p = SocketCommunication(self.ip, self.port)
        self.p2p.start_socket_communication(self)
        
        # Start enhanced features
        self.start_peer_health_monitoring()
        
        # Log initial mempool state
        logger.info({
            "message": "Enhanced P2P system initialized",
            "mempool_config": {
                "max_size": self.mempool.max_mempool_size,
                "max_peer_connections": self.mempool.max_peer_connections,
                "announcement_timeout": self.mempool.announcement_timeout
            }
        })

    def get_enhanced_node_stats(self):
        """Get comprehensive node statistics including mempool and P2P metrics"""
        base_stats = {
            "node_info": {
                "ip": self.ip,
                "port": self.port,
                "public_key_prefix": self.wallet.public_key_string()[:20] + "..."
            },
            "blockchain": {
                "total_blocks": len(self.blockchain.blocks),
                "last_block_hash": BlockchainUtils.hash(self.blockchain.blocks[-1].payload()).hex()[:16] + "..." if self.blockchain.blocks else None
            },
            "legacy_transaction_pool": {
                "size": len(self.transaction_pool.transactions)
            }
        }
        
        # Add mempool statistics
        base_stats["mempool"] = self.mempool.get_mempool_stats()
        
        # Add P2P statistics
        if self.p2p and hasattr(self.p2p, 'all_nodes'):
            base_stats["p2p"] = {
                "connected_peers": len(self.p2p.all_nodes),
                "peer_health_tracked": len(self.peer_health),
                "seen_blocks": len(self.seen_blocks)
            }
        
        return base_stats

    def _announce_transaction_to_peers(self, tx_hash):
        """
        Announce transaction using Bitcoin-style INV message to all connected peers.
        Used for transactions received via API.
        """
        if not self.p2p or not hasattr(self.p2p, 'all_nodes') or not self.p2p.all_nodes:
            return
        
        # Create inventory item for the transaction
        inv_item = InventoryItem(InventoryItem.TYPE_TX, tx_hash)
        inv_message = InventoryMessage([inv_item])
        
        # Send INV message to all connected peers
        message = Message(self.p2p.socket_connector, MessageType.INV, inv_message.to_dict())
        encoded_message = BlockchainUtils.encode(message)
        
        announced_to = 0
        for peer in self.p2p.all_nodes:
            try:
                self.p2p.send_to_node(peer, encoded_message)
                announced_to += 1
                
                # Track that we announced this transaction to this peer
                peer_id = f"{peer.host}:{peer.port}"
                self.mempool.mark_announced_to_peer(peer_id, [tx_hash])
                
            except Exception as e:
                logger.debug(f"Failed to announce transaction to peer {peer.host}:{peer.port}: {e}")
        
        logger.info({
            "message": "Transaction announced to network via INV",
            "tx_hash": tx_hash[:16] + "...",
            "announced_to_peers": announced_to,
            "total_peers": len(self.p2p.all_nodes)
        })

    def _gossip_transaction_to_peers(self, tx_hash, exclude_peer=None):
        """
        Gossip transaction to subset of peers using Bitcoin-style flood algorithm.
        Excludes the peer that sent us the transaction to prevent echo.
        """
        if not self.p2p or not hasattr(self.p2p, 'all_nodes') or not self.p2p.all_nodes:
            return
        
        # Bitcoin typically forwards to 8-10 peers, excluding the source
        max_forwards = min(8, len(self.p2p.all_nodes))
        forwarded_to = 0
        
        # Create inventory item for the transaction
        inv_item = InventoryItem(InventoryItem.TYPE_TX, tx_hash)
        inv_message = InventoryMessage([inv_item])
        message = Message(self.p2p.socket_connector, MessageType.INV, inv_message.to_dict())
        encoded_message = BlockchainUtils.encode(message)
        
        for peer in self.p2p.all_nodes:
            if forwarded_to >= max_forwards:
                break
                
            peer_id = f"{peer.host}:{peer.port}"
            
            # Skip the peer that sent us this transaction
            if exclude_peer and peer_id == exclude_peer:
                continue
            
            # Check if this peer likely already has this transaction
            if not self.mempool.get_transactions_for_announcement(peer_id):
                continue
            
            try:
                self.p2p.send_to_node(peer, encoded_message)
                self.mempool.mark_announced_to_peer(peer_id, [tx_hash])
                forwarded_to += 1
                
            except Exception as e:
                logger.debug(f"Failed to gossip transaction to peer {peer_id}: {e}")
        
        logger.info({
            "message": "Transaction gossiped to network subset",
            "tx_hash": tx_hash[:16] + "...",
            "forwarded_to_peers": forwarded_to,
            "excluded_peer": exclude_peer[:20] + "..." if exclude_peer else None
        })

    def _forward_transaction_to_leaders(self, transaction, leaders):
        """
        Forward transaction directly to current and upcoming leaders using Gulf Stream protocol.
        """
        if not self.p2p or not hasattr(self.p2p, 'all_nodes') or not self.p2p.all_nodes:
            logger.warning("No P2P connection available for Gulf Stream forwarding")
            return
        
        if not leaders:
            logger.warning("No leaders available for Gulf Stream forwarding")
            return
        
        # Create transaction message for direct forwarding
        message = Message(self.p2p.socket_connector, MessageType.TRANSACTION, transaction.to_dict())
        encoded_message = BlockchainUtils.encode(message)
        
        forwarded_count = 0
        
        for leader_public_key in leaders:
            # Find peer that matches this leader
            leader_peer = None
            for peer in self.p2p.all_nodes:
                # In a real implementation, you'd have a mapping of public keys to peers
                # For now, we'll forward to all peers as we don't have the peer-to-public-key mapping
                try:
                    self.p2p.send_to_node(peer, encoded_message)
                    forwarded_count += 1
                    break  # Forward to first available peer for each leader
                except Exception as e:
                    logger.debug(f"Failed to forward to peer {peer.host}:{peer.port}: {e}")
        
        logger.info({
            "message": "Transaction forwarded via Gulf Stream",
            "leaders_count": len(leaders),
            "forwarded_to_peers": forwarded_count,
            "tx_type": transaction.type,
            "sender": transaction.sender_public_key[:20] + "..."
        })

    def handle_block(self, block):
        block_proposer = block.forger  # Note: block.forger field name kept for compatibility
        block_hash = block.payload()
        signature = block.signature
        
        # Calculate block hash for duplicate detection
        block_hash_hex = BlockchainUtils.hash(block_hash).hex()

        logger.info({
            "message": "Received block from network",
            "block_number": block.block_count,
            "block_proposer": block_proposer[:30] + "..." if block_proposer else "None",
            "transactions_count": len(block.transactions),
            "current_blockchain_length": len(self.blockchain.blocks),
            "block_hash": block_hash_hex[:16] + "..."
        })

        # Check if we've already seen this block (prevent rebroadcast loops)
        if block_hash_hex in self.seen_blocks:
            logger.info({
                "message": "Block already seen, ignoring to prevent loops",
                "block_hash": block_hash_hex[:16] + "..."
            })
            return
        
        # Mark this block as seen
        self.seen_blocks.add(block_hash_hex)
        
        # Limit seen blocks cache size to prevent memory issues
        if len(self.seen_blocks) > 1000:
            # Remove oldest 200 entries (simplified - could use LRU)
            old_blocks = list(self.seen_blocks)[:200]
            for old_block in old_blocks:
                self.seen_blocks.discard(old_block)

        # Check if we already have a block with this block_count (prevent duplicates)
        if block.block_count < len(self.blockchain.blocks):
            logger.info({
                "message": "Block already exists, ignoring",
                "block_number": block.block_count,
                "current_length": len(self.blockchain.blocks)
            })
            return

        # Fast validation path: check lightweight validations first
        # Order optimized for fail-fast: cheapest checks first
        block_count_valid = self.blockchain.block_count_valid(block)
        if not block_count_valid:
            logger.info({
                "message": "Block validation failed: invalid block count",
                "block_number": block.block_count,
                "expected": len(self.blockchain.blocks),
                "fast_reject": True
            })
            logger.info({"message": "Block count invalid, requesting full chain"})
            self.request_chain()
            return

        # Quick hash validation (relatively fast)
        last_block_hash_valid = self.blockchain.last_block_hash_valid(block)
        if not last_block_hash_valid:
            logger.info({
                "message": "Block validation failed: invalid last block hash",
                "block_number": block.block_count,
                "fast_reject": True
            })
            return

        # Expensive validations only if lightweight ones pass
        signature_valid = Wallet.signature_valid(block_hash, signature, block_proposer)
        block_proposer_valid = self.blockchain.block_proposer_valid(block, signature_pre_validated=signature_valid)
        transactions_valid = self.blockchain.transactions_valid(block.transactions)

        # Enhanced logging with block proposer mismatch details (only if all validations performed)
        if signature_valid and block_proposer_valid and transactions_valid:
            logger.info({
                "message": "Block validation results - all passed",
                "block_count_valid": True,
                "last_block_hash_valid": True,
                "block_proposer_valid": True,
                "transactions_valid": True,
                "signature_valid": True,
                "optimization": "fast_path_success"
            })
        else:
            logger.info({
                "message": "Block validation results - some failed",
                "block_count_valid": True,  # Already validated above
                "last_block_hash_valid": True,  # Already validated above
                "block_proposer_valid": block_proposer_valid,
                "transactions_valid": transactions_valid,
                "signature_valid": signature_valid
            })

        if not block_count_valid:
            logger.info({"message": "Block count invalid, requesting full chain"})
            self.request_chain()

        # Use proper Leader-Based Consensus validation (now implemented in blockchain.py)
        # This includes the new block proposer validation that trusts quantum consensus selection
        if (
            last_block_hash_valid
            and block_proposer_valid
            and transactions_valid
            and signature_valid
        ):
            logger.info({
                "message": "Block validated successfully via Leader-Based Consensus",
                "block_number": block.block_count,
                "new_blockchain_length": len(self.blockchain.blocks) + 1,
                "validations": {
                    "last_block_hash": last_block_hash_valid,
                    "block_proposer": block_proposer_valid,
                    "transactions": transactions_valid,
                    "signature": signature_valid
                }
            })
            self.blockchain.add_block(block)
            self.transaction_pool.remove_from_pool(block.transactions)
            
            # Rebroadcast to ensure all nodes receive the valid block
            logger.info({
                "message": "Rebroadcasting validated block to network",
                "block_number": block.block_count
            })
            message = Message(self.p2p.socket_connector, "BLOCK", block)
            self.p2p.broadcast(BlockchainUtils.encode(message))
        else:
            logger.warning({
                "message": "Block rejected due to core validation failures",
                "block_number": block.block_count,
                "block_proposer": block_proposer[:30] + "..." if block_proposer else "None",
                "failed_validations": {
                    "last_block_hash": not last_block_hash_valid,
                    "transactions": not transactions_valid,
                    "signature": not signature_valid
                },
                "note": "Block rejected due to fundamental validation failures (not block proposer mismatch)"
            })

    def request_chain(self):
        message = Message(self.p2p.socket_connector, "BLOCKCHAINREQUEST", None)
        encoded_message = BlockchainUtils.encode(message)
        self.p2p.broadcast(encoded_message)

    def handle_blockchain_request(self, requesting_node):
        message = Message(self.p2p.socket_connector, "BLOCKCHAIN", self.blockchain)
        encoded_message = BlockchainUtils.encode(message)
        self.p2p.send(requesting_node, encoded_message)

    def handle_blockchain(self, blockchain):
        local_blockchain_copy = copy.deepcopy(self.blockchain)
        local_block_count = len(local_blockchain_copy.blocks)
        received_chain_block_count = len(blockchain.blocks)
        if local_block_count < received_chain_block_count:
            for block_number, block in enumerate(blockchain.blocks):
                if block_number >= local_block_count:
                    local_blockchain_copy.add_block(block)
                    self.transaction_pool.remove_from_pool(block.transactions)
            self.blockchain = local_blockchain_copy

    def propose_block(self):
        # FIXED: Check if we should propose a block using LEADER SCHEDULE (not quantum consensus directly)
        current_leader = self.blockchain.leader_schedule.get_current_leader()
        my_public_key = self.wallet.public_key_string()
        
        logger.info({
            "message": "Block proposal attempt",
            "current_leader_from_schedule": current_leader[:50] + "..." if current_leader else "None",
            "my_public_key": my_public_key[:50] + "...",
            "am_i_current_leader": current_leader == my_public_key,
            "transactions_in_pool": len(self.transaction_pool.transactions),
            "current_blockchain_length": len(self.blockchain.blocks),
            "current_slot": self.blockchain.leader_schedule.get_current_slot()
        })
        
        # ENHANCED: Check if I'm the current leader according to the leader schedule
        if current_leader == my_public_key:
            try:
                # CRITICAL: Check if a block was already received for this round
                # This prevents race conditions where multiple nodes try to propose blocks simultaneously
                expected_block_count = len(self.blockchain.blocks)
                
                logger.info({
                    "message": "I am selected as block proposer, proceeding with block creation",
                    "expected_block_count": expected_block_count,
                    "current_time": time.time(),
                    "transactions_available": len(self.transaction_pool.transactions)
                })
                
                # Get transactions for this block using Fast Gulf Stream + Gulf Stream + PoH ordering
                
                # PRIORITY 1: Get Fast Gulf Stream transactions (UDP forwarded)
                fast_gulf_stream_transactions = self.fast_gulf_stream.get_transactions_for_leader(my_public_key)
                
                # PRIORITY 2: Get regular Gulf Stream transactions (in-memory forwarded)
                gulf_stream_transactions = self.blockchain.gulf_stream_node.get_transactions_for_leader(my_public_key)
                
                # PRIORITY 3: Combine with local transaction pool 
                all_available_transactions = fast_gulf_stream_transactions + gulf_stream_transactions + self.transaction_pool.transactions
                
                # PoH ordering: Let blockchain order transactions with Proof of History
                if all_available_transactions:
                    transactions_for_block = all_available_transactions  # Blockchain will apply PoH ordering
                    logger.info({
                        "message": "Using Fast Gulf Stream + Gulf Stream + local transactions for block with PoH ordering",
                        "fast_gulf_stream_count": len(fast_gulf_stream_transactions),
                        "gulf_stream_count": len(gulf_stream_transactions),
                        "local_pool_count": len(self.transaction_pool.transactions),
                        "total_transactions": len(all_available_transactions),
                        "will_apply_poh_ordering": True
                    })
                else:
                    # Create empty block for slot (Solana-style: every slot gets a block)
                    transactions_for_block = []
                    logger.info({
                        "message": "Creating empty block for slot (no transactions available)",
                        "gulf_stream_count": 0,
                        "local_pool_count": 0,
                        "slot_based_creation": True
                    })
                
                # Allow block proposal with any number of transactions (including zero)
                # Every slot, create a block regardless of transaction count or size
                logger.info({
                    "message": "Creating block for slot interval",
                    "pool_size": len(self.transaction_pool.transactions),
                    "transactions_for_block": len(transactions_for_block),
                    "size_limit": "none"
                })
                
                # Update last block creation time before creating block
                self.transaction_pool.update_last_forge_time()  # Method name kept for compatibility
                
                # Debug: Check wallet type before calling create_block
                logger.debug({
                    "message": "Debug: About to call create_block with Solana-style parallel execution",
                    "wallet_type": type(self.wallet).__name__,
                    "wallet_has_public_key_string": hasattr(self.wallet, 'public_key_string'),
                    "my_public_key": my_public_key[:20] + "...",
                    "solana_features": ["PoH Sequencing", "Parallel Execution (Sealevel)", "State Root Hash", "Gulf Stream"]
                })
                
                block = self.blockchain.create_block(
                    self.wallet, use_gulf_stream=True
                )
                
                # Double-check that no block was added while we were creating this one
                if block.block_count != expected_block_count:
                    logger.warning({
                        "message": "Block race condition detected, another block was added during creation",
                        "expected_block_count": expected_block_count,
                        "actual_block_count": block.block_count,
                        "current_blockchain_length": len(self.blockchain.blocks)
                    })
                    return  # Abort block proposal, another node was faster
                
                logger.info({
                    "message": "SOLANA-STYLE BLOCK PROPOSED SUCCESSFULLY",
                    "block_number": block.block_count,
                    "transactions_included": len(block.transactions),
                    "block_proposer": my_public_key[:20] + "...",
                    "block_timestamp": block.timestamp,
                    "block_hash": BlockchainUtils.hash(block.payload()).hex()[:16] + "...",
                    "remaining_in_pool": len(self.transaction_pool.transactions) - len(block.transactions),
                    "solana_features": {
                        "poh_entries": len(getattr(block, 'poh_sequence', [])),
                        "parallel_execution": bool(hasattr(block, 'parallel_execution_results')),
                        "state_root_hash": getattr(block, 'state_root_hash', 'none')[:16] + "..." if hasattr(block, 'state_root_hash') else "none",
                        "execution_time_ms": getattr(block, 'execution_time_ms', 0),
                        "parallel_efficiency": f"{getattr(block, 'parallel_efficiency', 100):.1f}%"
                    }
                })
                
                # Remove only the transactions that were included in the block
                self.transaction_pool.remove_from_pool(block.transactions)
                self.gulf_stream.remove_transactions(block.transactions)  # Clean up Gulf Stream too
                
                # Mark our own block as seen to prevent rebroadcast loops
                proposed_block_hash = BlockchainUtils.hash(block.payload()).hex()
                self.seen_blocks.add(proposed_block_hash)
                
                # Broadcast the new block to all peers
                message = Message(self.p2p.socket_connector, "BLOCK", block)
                self.p2p.broadcast(BlockchainUtils.encode(message))
                
                logger.info({
                    "message": "Block broadcast to network",
                    "block_number": block.block_count,
                    "remaining_transactions": len(self.transaction_pool.transactions),
                    "peers_notified": len(self.p2p.peers)
                })
                
                # Update quantum consensus with successful proposal
                self.blockchain.quantum_consensus.record_proposal_result(my_public_key, True)
                
            except Exception as e:
                logger.error({
                    "message": "Block proposal failed",
                    "error": str(e),
                    "block_proposer": my_public_key[:20] + "..."
                })
                # Update quantum consensus with failed proposal
                self.blockchain.quantum_consensus.record_proposal_result(my_public_key, False)
                
        else:
            logger.info({
                "message": "Not selected as current leader",
                "current_leader_from_schedule": current_leader[:20] + "..." if current_leader else "None",
                "my_key": my_public_key[:20] + "...",
                "current_slot": self.blockchain.leader_schedule.get_current_slot()
            })
    
    def shutdown(self):
        """Gracefully shutdown the node and all its components"""
        logger.info("Shutting down blockchain node...")
        
        # Shutdown Fast Gulf Stream
        if hasattr(self, 'fast_gulf_stream') and self.fast_gulf_stream:
            try:
                self.fast_gulf_stream.shutdown()
                logger.info("Fast Gulf Stream shutdown completed")
            except Exception as e:
                logger.error(f"Error shutting down Fast Gulf Stream: {e}")
        
        # Shutdown slot producer
        if hasattr(self, 'slot_producer') and self.slot_producer:
            try:
                if hasattr(self.slot_producer, 'stop'):
                    self.slot_producer.stop()
                logger.info("Slot producer shutdown completed")
            except Exception as e:
                logger.error(f"Error shutting down slot producer: {e}")
        
        # Shutdown P2P
        if self.p2p:
            try:
                self.p2p.stop()
                logger.info("P2P communication shutdown completed")
            except Exception as e:
                logger.error(f"Error shutting down P2P: {e}")
        
        logger.info("Node shutdown completed")
