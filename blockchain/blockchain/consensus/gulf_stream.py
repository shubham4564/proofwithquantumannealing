import time
import hashlib
from typing import List, Dict, Optional, Set
from collections import defaultdict
from blockchain.utils.logger import logger


class GulfStreamProcessor:
    """
    Solana-style Gulf Stream protocol implementation.
    Forwards transactions directly to current and upcoming leaders instead of using mempool.
    """
    
    def __init__(self, leader_schedule):
        self.leader_schedule = leader_schedule
        self.transaction_lifetime_seconds = 150  # ~2.5 minutes like Solana
        self.max_forwarding_slots = 5  # Forward to next 5 leaders
        
        # Transaction tracking
        self.pending_transactions = defaultdict(list)  # leader_public_key -> [transactions]
        self.transaction_timestamps = {}  # tx_hash -> timestamp
        self.forwarded_transactions = defaultdict(set)  # leader_public_key -> {tx_hashes}
        
        # Performance metrics
        self.stats = {
            "transactions_forwarded": 0,
            "transactions_expired": 0,
            "leaders_contacted": 0,
            "cache_hits": 0
        }
        
        logger.info("Gulf Stream processor initialized")
    
    def process_transaction(self, transaction, source_node_id: str = None) -> Dict:
        """
        Process a transaction using Gulf Stream protocol.
        Returns forwarding results and next steps.
        """
        tx_hash = self._calculate_transaction_hash(transaction)
        current_time = time.time()
        
        # Check if transaction is already being processed
        if tx_hash in self.transaction_timestamps:
            self.stats["cache_hits"] += 1
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
        
        # Get current and upcoming leaders
        current_leader = self.leader_schedule.get_current_leader()
        upcoming_leaders = self.leader_schedule.get_upcoming_leaders(self.max_forwarding_slots)
        
        if not current_leader:
            return {
                "status": "no_leader",
                "tx_hash": tx_hash,
                "message": "No current leader available"
            }
        
        # Record transaction
        self.transaction_timestamps[tx_hash] = current_time
        
        # Forward to current leader and upcoming leaders
        forwarding_results = self._forward_to_leaders(transaction, tx_hash, current_leader, upcoming_leaders)
        
        self.stats["transactions_forwarded"] += 1
        
        logger.info({
            "message": "Transaction processed via Gulf Stream",
            "tx_hash": tx_hash[:16] + "...",
            "current_leader": current_leader[:20] + "..." if current_leader else None,
            "forwarded_to": len(forwarding_results["leaders_contacted"]),
            "source_node": source_node_id[:20] + "..." if source_node_id else "API"
        })
        
        return {
            "status": "forwarded",
            "tx_hash": tx_hash,
            "forwarding_results": forwarding_results,
            "current_leader": current_leader,
            "upcoming_leaders": len(upcoming_leaders)
        }
    
    def _forward_to_leaders(self, transaction, tx_hash: str, current_leader: str, upcoming_leaders: List) -> Dict:
        """Forward transaction to current and upcoming leaders"""
        leaders_contacted = []
        
        # Forward to current leader (priority)
        if current_leader and tx_hash not in self.forwarded_transactions[current_leader]:
            self.pending_transactions[current_leader].append(transaction)
            self.forwarded_transactions[current_leader].add(tx_hash)
            leaders_contacted.append({
                "leader": current_leader[:20] + "...",
                "slot": "current",
                "time_offset": 0
            })
        
        # Forward to upcoming leaders
        for slot, leader, abs_time in upcoming_leaders:
            if leader and tx_hash not in self.forwarded_transactions[leader]:
                self.pending_transactions[leader].append(transaction)
                self.forwarded_transactions[leader].add(tx_hash)
                leaders_contacted.append({
                    "leader": leader[:20] + "...",
                    "slot": slot,
                    "time_offset": abs_time - time.time()
                })
        
        self.stats["leaders_contacted"] += len(leaders_contacted)
        
        return {
            "leaders_contacted": leaders_contacted,
            "total_leaders": len(leaders_contacted),
            "current_leader_contacted": current_leader in [lc["leader"] for lc in leaders_contacted]
        }
    
    def get_transactions_for_leader(self, leader_public_key: str) -> List:
        """
        Get pending transactions for a specific leader.
        Called by the leader when it's their turn to create a block.
        """
        if leader_public_key not in self.pending_transactions:
            return []
        
        # Get transactions and clear the cache for this leader
        transactions = self.pending_transactions[leader_public_key].copy()
        
        # Clear processed transactions
        self.pending_transactions[leader_public_key].clear()
        self.forwarded_transactions[leader_public_key].clear()
        
        # Filter out expired transactions
        valid_transactions = []
        current_time = time.time()
        
        for tx in transactions:
            tx_hash = self._calculate_transaction_hash(tx)
            tx_time = self.transaction_timestamps.get(tx_hash, current_time)
            
            if current_time - tx_time < self.transaction_lifetime_seconds:
                valid_transactions.append(tx)
            else:
                self.stats["transactions_expired"] += 1
                # Clean up expired transaction
                if tx_hash in self.transaction_timestamps:
                    del self.transaction_timestamps[tx_hash]
        
        logger.info({
            "message": "Transactions retrieved for leader",
            "leader": leader_public_key[:20] + "...",
            "total_transactions": len(transactions),
            "valid_transactions": len(valid_transactions),
            "expired_transactions": len(transactions) - len(valid_transactions)
        })
        
        return valid_transactions
    
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
        
        for tx_hash, timestamp in self.transaction_timestamps.items():
            if current_time - timestamp > self.transaction_lifetime_seconds:
                expired_hashes.append(tx_hash)
        
        # Clean up expired transactions
        for tx_hash in expired_hashes:
            del self.transaction_timestamps[tx_hash]
            self.stats["transactions_expired"] += 1
            
            # Remove from forwarded transaction sets
            for leader_txs in self.forwarded_transactions.values():
                leader_txs.discard(tx_hash)
        
        if expired_hashes:
            logger.info({
                "message": "Cleaned up expired transactions",
                "expired_count": len(expired_hashes)
            })
    
    def get_stats(self) -> Dict:
        """Get Gulf Stream performance statistics"""
        return {
            "gulf_stream_stats": self.stats.copy(),
            "pending_transactions_by_leader": {
                leader[:20] + "...": len(txs) 
                for leader, txs in self.pending_transactions.items()
            },
            "total_pending_transactions": sum(len(txs) for txs in self.pending_transactions.values()),
            "tracked_transactions": len(self.transaction_timestamps),
            "transaction_lifetime_seconds": self.transaction_lifetime_seconds
        }
    
    def reset_stats(self):
        """Reset performance statistics"""
        self.stats = {
            "transactions_forwarded": 0,
            "transactions_expired": 0,
            "leaders_contacted": 0,
            "cache_hits": 0
        }
    
    def forward_transaction(self, transaction, upcoming_leaders: List[str]) -> bool:
        """
        Forward transaction to leaders - compatibility wrapper for process_transaction
        """
        result = self.process_transaction(transaction)
        return result.get("status") == "forwarded"
    
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
        No size limits - block proposer includes all valid transactions received during their slot.
        """
        # Get current leader
        current_leader = self.leader_schedule.get_current_leader()
        if not current_leader:
            return []
        
        # Get ALL transactions forwarded to current leader (no size filtering)
        leader_transactions = self.get_transactions_for_leader(current_leader)
        
        logger.debug(f"Gulf Stream returning {len(leader_transactions)} transactions for block (no size limit)")
        return leader_transactions
    
    def remove_transactions(self, transactions):
        """
        Remove transactions from Gulf Stream after they're included in a block
        """
        for transaction in transactions:
            tx_hash = self._calculate_transaction_hash(transaction)
            
            # Remove from timestamp tracking
            if tx_hash in self.transaction_timestamps:
                del self.transaction_timestamps[tx_hash]
            
            # Remove from all leader queues
            for leader_key in list(self.pending_transactions.keys()):
                self.pending_transactions[leader_key] = [
                    tx for tx in self.pending_transactions[leader_key] 
                    if self._calculate_transaction_hash(tx) != tx_hash
                ]
                
                # Remove from forwarded tracking
                self.forwarded_transactions[leader_key].discard(tx_hash)
    
    def get_forwarding_stats(self) -> Dict:
        """
        Get forwarding statistics - compatibility wrapper for get_stats
        """
        return self.get_stats()
