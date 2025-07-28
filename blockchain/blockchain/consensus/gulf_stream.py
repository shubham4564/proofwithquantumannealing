import time
import hashlib
import socket
import json
from typing import List, Dict, Optional, Set
from collections import defaultdict
from blockchain.utils.logger import logger


class GulfStreamProcessor:
    """
    Solana-style Gulf Stream protocol implementation with transaction bundling.
    
    This implementation follows Solana's approach where transactions are bundled together 
    into single UDP packets for maximum network efficiency. Key features:
    
    1. Transaction Bundling: Multiple transactions are packed into single UDP packets
       (up to 1280 bytes) to minimize network overhead and maximize throughput.
       
    2. Smart Bundling Strategy: Bundles are sent when they reach size limits OR 
       timeout thresholds (10ms) to balance efficiency with latency.
       
    3. Leader Targeting: Transactions are forwarded to current leader + next 3 upcoming 
       leaders to ensure processing even during leader transitions.
       
    4. UDP Protocol: Uses connectionless UDP for speed, with built-in retry mechanisms
       at higher layers of the protocol stack.
       
    This approach enables high-throughput transaction processing by reducing network
    overhead while maintaining low latency through intelligent timeout mechanisms.
    """
    
    def __init__(self, leader_schedule, node_public_key: str):
        self.leader_schedule = leader_schedule
        self.node_public_key = node_public_key
        
        # Gulf Stream Configuration - Updated for 200-slot minimum buffer
        self.max_forwarding_slots = 200  # Minimum 200 slots ahead for proper buffering
        self.min_slot_buffer = 200  # Must maintain at least 200 slots between current and first forwarded slot
        
        # Transaction tracking
        self.pending_transactions_by_block_proposer = {}
        self.tracked_transactions = {}
        self.transaction_lifetime_seconds = 90  # 200 slots * 0.45s = 90 seconds
        
        # Transaction bundling configuration
        self.max_bundle_size_bytes = 1280  # Standard UDP packet size for optimal network performance
        self.pending_transaction_bundles = defaultdict(list)  # Bundles waiting to be sent
        self.bundle_timeout_ms = 10  # Maximum time to wait before sending a partial bundle (10ms)
        self.last_bundle_time = defaultdict(float)  # Track last bundle send time per leader
        
        # Performance metrics
        self.gulf_stream_stats = {
            "transactions_forwarded": 0,
            "block_proposers_contacted": 0,
            "tpu_transmissions_successful": 0,
            "tpu_transmissions_failed": 0,
            "forwarding_errors": 0,
            "bundles_sent": 0,
            "transactions_per_bundle_avg": 0,
            "bundle_efficiency": 0
        }
        
        logger.info({
            "message": "Gulf Stream processor initialized with TPU integration and transaction bundling",
            "node": self.node_public_key[:20] + "...",
            "max_forwarding_slots": self.max_forwarding_slots,
            "min_slot_buffer": self.min_slot_buffer,
            "transaction_lifetime": self.transaction_lifetime_seconds,
            "max_bundle_size_bytes": self.max_bundle_size_bytes,
            "bundle_timeout_ms": self.bundle_timeout_ms
        })
    
    def process_transaction(self, transaction, source_node_id: str = None) -> Dict:
        """
        Process a transaction using Gulf Stream protocol with bundling.
        Transactions are bundled together for efficient UDP transmission.
        Returns forwarding results and next steps.
        """
        tx_hash = self._calculate_transaction_hash(transaction)
        current_time = time.time()
        
        # Check if transaction is already being processed
        if tx_hash in self.tracked_transactions:
            return {
                "status": "already_processed",
                "tx_hash": tx_hash,
                "message": "Transaction already in Gulf Stream pipeline"
            }
        
        # Validate transaction lifetime (Recent Blockhash equivalent)
        if not self._validate_transaction_freshness(transaction):
            return {
                "status": "expired",
                "tx_hash": tx_hash,
                "message": "Transaction blockhash expired"
            }
        
        # Get current and upcoming leaders (limit to only 3 upcoming leaders)
        current_leader = self.leader_schedule.get_current_leader()
        upcoming_leaders = self.leader_schedule.get_upcoming_leaders(3)
        
        if not current_leader:
            return {
                "status": "no_leader",
                "tx_hash": tx_hash,
                "message": "No current leader available"
            }
        
        # Record transaction
        self.tracked_transactions[tx_hash] = current_time
        
        # Add transaction to bundles for current and upcoming leaders
        forwarding_results = self._add_to_bundles(transaction, tx_hash, current_leader, upcoming_leaders, source_node_id)
        
        self.gulf_stream_stats["transactions_forwarded"] += 1
        
        logger.debug({
            "message": "Transaction added to Gulf Stream bundles",
            "tx_hash": tx_hash[:16] + "...",
            "current_block_proposer": current_leader[:20] + "..." if current_leader else None,
            "leaders_targeted": len(forwarding_results["leaders_targeted"]),
            "source_node": source_node_id[:20] + "..." if source_node_id else "API"
        })
        
        return {
            "status": "bundled",
            "tx_hash": tx_hash,
            "forwarding_results": forwarding_results,
            "current_block_proposer": current_leader,
            "upcoming_block_proposers": len(upcoming_leaders)
        }
    
    def _add_to_bundles(self, transaction, tx_hash: str, current_leader: str, upcoming_leaders: List, source_node: str):
        """
        Add transaction to bundles for current leader + next 3 upcoming leaders.
        Implements efficient UDP packet bundling as per Solana's Gulf Stream protocol.
        """
        try:
            # Prepare list of all target leaders (current + upcoming)
            target_leaders = [current_leader]
            
            # Add upcoming leaders (limited to next 3)
            for slot_num, leader_key, future_time in upcoming_leaders:
                if leader_key not in target_leaders:  # Avoid duplicates
                    target_leaders.append(leader_key)
            
            # Limit to maximum 4 leaders (current + 3 upcoming)
            target_leaders = target_leaders[:4]
            
            if not target_leaders:
                logger.warning({
                    "message": "No valid Gulf Stream targets found",
                    "tx_hash": tx_hash[:16] + "..."
                })
                return {
                    "leaders_targeted": [],
                    "bundles_queued": 0
                }
            
            # Serialize transaction for bundling
            transaction_data = self._serialize_transaction(transaction)
            
            # Add transaction to each target leader's bundle
            bundles_queued = 0
            for leader_key in target_leaders:
                # Add to pending bundle for this leader
                self.pending_transaction_bundles[leader_key].append({
                    'tx_data': transaction_data,
                    'tx_hash': tx_hash,
                    'timestamp': time.time(),
                    'source_node': source_node
                })
                bundles_queued += 1
                
                # Check if bundle should be sent (size or timeout threshold reached)
                self._check_and_send_bundle(leader_key)
            
            return {
                "leaders_targeted": target_leaders,
                "bundles_queued": bundles_queued
            }
            
        except Exception as e:
            logger.error({
                "message": "Failed to add transaction to bundles",
                "tx_hash": tx_hash[:16] + "...",
                "error": str(e)
            })
            return {
                "leaders_targeted": [],
                "bundles_queued": 0
            }
    
    def _check_and_send_bundle(self, leader_key: str):
        """
        Check if a bundle should be sent based on size or timeout thresholds.
        Implements the UDP packet optimization strategy.
        """
        current_time = time.time()
        bundle = self.pending_transaction_bundles[leader_key]
        
        if not bundle:
            return
        
        # Calculate current bundle size
        bundle_size = self._calculate_bundle_size(bundle)
        
        # Check if bundle should be sent
        time_since_last_bundle = (current_time - self.last_bundle_time[leader_key]) * 1000  # Convert to ms
        should_send = (
            bundle_size >= self.max_bundle_size_bytes or  # Bundle is full
            time_since_last_bundle >= self.bundle_timeout_ms  # Timeout reached
        )
        
        if should_send:
            self._send_transaction_bundle(leader_key, bundle)
            
    def _send_transaction_bundle(self, leader_key: str, bundle: List[Dict]):
        """
        Send a bundle of transactions to a leader via UDP.
        This is the core Gulf Stream bundling implementation.
        """
        try:
            if not bundle:
                return False
                
            # Calculate TPU port for this leader
            tpu_port = self._get_tpu_port_for_leader(leader_key)
            if not tpu_port:
                return False
            
            # Create bundled packet
            packet = {
                'bundle_id': f"{self.node_public_key[:8]}_{int(time.time() * 1000000)}",
                'transaction_count': len(bundle),
                'transactions': [tx['tx_data'] for tx in bundle],
                'source_node': self.node_public_key,
                'timestamp': time.time(),
                'gulf_stream_version': '1.0',
                'target_leader': leader_key
            }
            
            # Serialize the entire bundle
            packet_data = json.dumps(packet)
            packet_bytes = packet_data.encode()
            
            # Check if packet is within UDP limits
            if len(packet_bytes) > self.max_bundle_size_bytes:
                # Split into smaller bundles if too large
                return self._send_split_bundles(leader_key, bundle)
            
            # Send UDP packet to leader's TPU port
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(0.1)  # 100ms timeout for fast transmission
                sock.sendto(packet_bytes, ('localhost', tpu_port))
            
            # Update statistics
            self.gulf_stream_stats["bundles_sent"] += 1
            self.gulf_stream_stats["tpu_transmissions_successful"] += 1
            
            # Calculate efficiency metrics
            total_bundles = self.gulf_stream_stats["bundles_sent"]
            total_transactions = self.gulf_stream_stats["transactions_forwarded"]
            if total_bundles > 0:
                self.gulf_stream_stats["transactions_per_bundle_avg"] = total_transactions / total_bundles
                self.gulf_stream_stats["bundle_efficiency"] = len(packet_bytes) / self.max_bundle_size_bytes
            
            # Track pending transactions for this leader
            if leader_key not in self.pending_transactions_by_block_proposer:
                self.pending_transactions_by_block_proposer[leader_key] = []
            
            for tx in bundle:
                self.pending_transactions_by_block_proposer[leader_key].append({
                    'tx_hash': tx['tx_hash'],
                    'forwarded_time': time.time(),
                    'tpu_port': tpu_port,
                    'bundle_id': packet['bundle_id']
                })
            
            # Clear the bundle and update timestamp
            self.pending_transaction_bundles[leader_key].clear()
            self.last_bundle_time[leader_key] = time.time()
            
            logger.info({
                "message": "Transaction bundle sent via UDP",
                "target_leader": leader_key[:20] + "...",
                "tpu_port": tpu_port,
                "bundle_id": packet['bundle_id'],
                "transaction_count": len(bundle),
                "bundle_size_bytes": len(packet_bytes),
                "efficiency": f"{(len(packet_bytes) / self.max_bundle_size_bytes) * 100:.1f}%"
            })
            
            return True
            
        except Exception as e:
            logger.error({
                "message": "Failed to send transaction bundle",
                "target_leader": leader_key[:16] + "...",
                "bundle_size": len(bundle),
                "error": str(e)
            })
            self.gulf_stream_stats["tpu_transmissions_failed"] += 1
            return False
    
    def _send_split_bundles(self, leader_key: str, bundle: List[Dict]) -> bool:
        """
        Split oversized bundles into multiple UDP packets.
        """
        try:
            mid_point = len(bundle) // 2
            bundle1 = bundle[:mid_point]
            bundle2 = bundle[mid_point:]
            
            success1 = self._send_transaction_bundle(leader_key, bundle1)
            success2 = self._send_transaction_bundle(leader_key, bundle2)
            
            return success1 and success2
            
        except Exception as e:
            logger.error({
                "message": "Failed to split and send bundles",
                "leader": leader_key[:16] + "...",
                "error": str(e)
            })
            return False
    
    def _calculate_bundle_size(self, bundle: List[Dict]) -> int:
        """
        Calculate the approximate size of a bundle in bytes.
        """
        if not bundle:
            return 0
        
        # Estimate packet overhead + transaction data
        packet_overhead = 200  # JSON overhead, headers, etc.
        transaction_sizes = sum(len(json.dumps(tx['tx_data'])) for tx in bundle)
        return packet_overhead + transaction_sizes
    
    def _serialize_transaction(self, transaction) -> Dict:
        """
        Serialize transaction data for bundling.
        """
        return {
            'sender_public_key': transaction.sender_public_key,
            'receiver_public_key': transaction.receiver_public_key,
            'amount': transaction.amount,
            'transaction_type': transaction.type,
            'timestamp': transaction.timestamp,
            'transaction_id': transaction.id,
            'signature': transaction.signature
        }
    
    def flush_pending_bundles(self):
        """
        Force send all pending bundles regardless of size.
        Called periodically to ensure no transactions are stuck in bundles.
        """
        bundles_sent = 0
        for leader_key in list(self.pending_transaction_bundles.keys()):
            bundle = self.pending_transaction_bundles[leader_key]
            if bundle:
                if self._send_transaction_bundle(leader_key, bundle):
                    bundles_sent += 1
        
        if bundles_sent > 0:
            logger.info({
                "message": "Flushed pending transaction bundles",
                "bundles_sent": bundles_sent
            })
        
        return bundles_sent
    
    def get_transactions_for_leader(self, leader_public_key: str) -> List:
        """
        Get pending transactions for a specific block proposer.
        Called by the block proposer when it's their turn to create a block.
        """
        if leader_public_key not in self.pending_transactions_by_block_proposer:
            return []
        
        # Get transactions and clear the cache for this leader
        transactions = self.pending_transactions_by_block_proposer[leader_public_key].copy()
        
        # Clear processed transactions
        self.pending_transactions_by_block_proposer[leader_public_key].clear()
        
        # Filter out expired transactions  
        valid_transactions = []
        current_time = time.time()
        
        for tx_info in transactions:
            tx_hash = tx_info['tx_hash']
            tx_time = self.tracked_transactions.get(tx_hash, current_time)
            
            if current_time - tx_time < self.transaction_lifetime_seconds:
                valid_transactions.append(tx_info)
            else:
                # Clean up expired transaction
                if tx_hash in self.tracked_transactions:
                    del self.tracked_transactions[tx_hash]
        
        logger.info({
            "message": "Transactions retrieved for block proposer",
            "block_proposer": leader_public_key[:20] + "...",
            "total_transactions": len(transactions),
            "valid_transactions": len(valid_transactions),
            "expired_transactions": len(transactions) - len(valid_transactions)
        })
        
        return valid_transactions
    
    def _get_tpu_port_for_leader(self, leader_public_key: str) -> Optional[int]:
        """
        Calculate TPU port for a block proposer based on their public key.
        TPU ports follow pattern: 13000 + node_index
        """
        try:
            # Use hash of public key to determine consistent node index
            import hashlib
            key_hash = hashlib.sha256(leader_public_key.encode()).hexdigest()
            node_index = int(key_hash[:8], 16) % 100  # Limit to 100 nodes (ports 13000-13099)
            tpu_port = 13000 + node_index
            return tpu_port
        except Exception as e:
            logger.warning(f"Failed to calculate TPU port for leader {leader_public_key[:20]}...: {e}")
            return None
    
    def _validate_transaction_freshness(self, transaction) -> bool:
        """
        Validate transaction freshness (equivalent to Recent Blockhash check).
        In our system, we check if the transaction was created recently.
        """
        # For now, we'll assume all transactions are fresh
        # In a full implementation, you'd check against recent block hashes
        # stored in the transaction similar to Solana's Recent Blockhash
        return True
    
    def _calculate_transaction_hash(self, transaction) -> str:
        """Calculate unique hash for transaction"""
        # Create a unique identifier for the transaction
        tx_data = f"{transaction.sender_public_key}_{transaction.receiver_public_key}_{transaction.amount}_{transaction.timestamp}"
        return hashlib.sha256(tx_data.encode()).hexdigest()
    
    def cleanup_expired_transactions(self):
        """Remove expired transactions from memory"""
        current_time = time.time()
        expired_hashes = []
        
        for tx_hash, timestamp in self.tracked_transactions.items():
            if current_time - timestamp > self.transaction_lifetime_seconds:
                expired_hashes.append(tx_hash)
        
        # Clean up expired transactions
        for tx_hash in expired_hashes:
            del self.tracked_transactions[tx_hash]
            
            # Remove from pending transaction sets
            for leader_key in list(self.pending_transactions_by_block_proposer.keys()):
                self.pending_transactions_by_block_proposer[leader_key] = [
                    tx for tx in self.pending_transactions_by_block_proposer[leader_key]
                    if tx['tx_hash'] != tx_hash
                ]
                
            # Remove from pending bundles
            for leader_key in list(self.pending_transaction_bundles.keys()):
                self.pending_transaction_bundles[leader_key] = [
                    tx for tx in self.pending_transaction_bundles[leader_key]
                    if tx['tx_hash'] != tx_hash
                ]
        
        if expired_hashes:
            logger.info({
                "message": "Cleaned up expired transactions",
                "expired_count": len(expired_hashes)
            })
    
    def get_stats(self) -> Dict:
        """Get Gulf Stream performance statistics"""
        return {
            "gulf_stream_stats": self.gulf_stream_stats.copy(),
            "pending_transactions_by_block_proposer": {
                leader[:20] + "...": len(txs) 
                for leader, txs in self.pending_transactions_by_block_proposer.items()
            },
            "pending_bundles": {
                leader[:20] + "...": len(bundle)
                for leader, bundle in self.pending_transaction_bundles.items()
            },
            "total_pending_transactions": sum(len(txs) for txs in self.pending_transactions_by_block_proposer.values()),
            "total_pending_bundles": sum(len(bundle) for bundle in self.pending_transaction_bundles.values()),
            "tracked_transactions": len(self.tracked_transactions),
            "transaction_lifetime_seconds": self.transaction_lifetime_seconds,
            "max_forwarding_slots": self.max_forwarding_slots,
            "max_bundle_size_bytes": self.max_bundle_size_bytes,
            "bundle_timeout_ms": self.bundle_timeout_ms
        }
    
    def reset_stats(self):
        """Reset performance statistics"""
        self.gulf_stream_stats = {
            "transactions_forwarded": 0,
            "block_proposers_contacted": 0,
            "tpu_transmissions_successful": 0,
            "tpu_transmissions_failed": 0,
            "forwarding_errors": 0,
            "bundles_sent": 0,
            "transactions_per_bundle_avg": 0,
            "bundle_efficiency": 0
        }
    
    def forward_transaction(self, transaction, upcoming_leaders: List[str]) -> bool:
        """
        Forward transaction to block proposers - compatibility wrapper for process_transaction
        """
        result = self.process_transaction(transaction)
        return result.get("status") == "bundled"
    
    def update_forwarding_state(self, transaction):
        """
        Update forwarding state for a transaction - used for P2P transactions
        """
        tx_hash = self._calculate_transaction_hash(transaction)
        if tx_hash not in self.transaction_timestamps:
            # Process this P2P transaction through Gulf Stream
            self.process_transaction(transaction)
    
    def get_transactions_for_block(self, max_block_size_bytes: int = None) -> List:
        """
        Get all transactions ready for block creation from Gulf Stream pipeline.
        Block proposer includes all valid transactions received during their slot.
        """
        # Get current block proposer
        current_leader = self.leader_schedule.get_current_leader()
        if not current_leader:
            return []
        
        # Get ALL transactions forwarded to current block proposer
        leader_transactions = self.get_transactions_for_leader(current_leader)
        
        logger.debug(f"Gulf Stream returning {len(leader_transactions)} transactions for block proposer")
        return leader_transactions
    
    def remove_transactions(self, transactions):
        """
        Remove transactions from Gulf Stream after they're included in a block
        """
        for transaction in transactions:
            tx_hash = self._calculate_transaction_hash(transaction)
            
            # Remove from timestamp tracking
            if tx_hash in self.tracked_transactions:
                del self.tracked_transactions[tx_hash]
            
            # Remove from all block proposer queues
            for leader_key in list(self.pending_transactions_by_block_proposer.keys()):
                self.pending_transactions_by_block_proposer[leader_key] = [
                    tx for tx in self.pending_transactions_by_block_proposer[leader_key] 
                    if tx.get('tx_hash') != tx_hash
                ]
                
            # Remove from pending bundles  
            for leader_key in list(self.pending_transaction_bundles.keys()):
                self.pending_transaction_bundles[leader_key] = [
                    tx for tx in self.pending_transaction_bundles[leader_key]
                    if tx.get('tx_hash') != tx_hash
                ]
    
    def get_forwarding_stats(self) -> Dict:
        """
        Get forwarding statistics - compatibility wrapper for get_stats
        """
        return self.get_stats()
    
    def process_bundle_timeouts(self):
        """
        Process bundle timeouts - send bundles that have been waiting too long.
        Should be called periodically to ensure transactions don't get stuck.
        """
        current_time = time.time()
        bundles_sent = 0
        
        for leader_key in list(self.pending_transaction_bundles.keys()):
            if not self.pending_transaction_bundles[leader_key]:
                continue
                
            time_since_last = (current_time - self.last_bundle_time.get(leader_key, 0)) * 1000
            
            if time_since_last >= self.bundle_timeout_ms:
                bundle = self.pending_transaction_bundles[leader_key]
                if self._send_transaction_bundle(leader_key, bundle):
                    bundles_sent += 1
        
        return bundles_sent
