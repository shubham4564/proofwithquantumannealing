import copy
import time

from api.main import NodeAPI
from blockchain.blockchain import Blockchain
from blockchain.p2p.message import Message
from blockchain.p2p.socket_communication import SocketCommunication
from blockchain.transaction.transaction_pool import TransactionPool
from blockchain.transaction.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils
from blockchain.utils.logger import logger


class Node:
    def __init__(self, ip, port, key=None):
        self.p2p = None
        self.ip = ip
        self.port = port
        self.transaction_pool = TransactionPool()
        self.wallet = Wallet()
        self.blockchain = Blockchain()
        self.seen_blocks = set()  # Track block hashes to prevent rebroadcast loops
        
        # Handle key initialization and quantum consensus registration
        if key:
            self.wallet.from_key(key)
        else:
            # Generate unique keys for this node instance
            node_id = f"node_{ip}_{port}_{int(__import__('time').time())}"
            public_key, private_key = self.blockchain.quantum_consensus.generate_node_keys(node_id)
            
            # Use generated keys for wallet
            self.wallet.from_key(private_key)
        
        # Register this node in quantum consensus for forging eligibility
        self.blockchain.quantum_consensus.register_node(
            self.wallet.public_key_string(), 
            self.wallet.public_key_string()
        )
        
        logger.info({
            "message": "Node registered in quantum consensus",
            "node_public_key": self.wallet.public_key_string()[:50] + "...",
            "ip": ip,
            "port": port
        })

    def start_p2p(self):
        self.p2p = SocketCommunication(self.ip, self.port)
        self.p2p.start_socket_communication(self)
        
        # Start periodic heartbeat to stay active in quantum consensus
        import threading
        self.heartbeat_active = True
        self.heartbeat_thread = threading.Thread(target=self._quantum_heartbeat, daemon=True)
        self.heartbeat_thread.start()
        
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

    def start_node_api(self, api_port):
        self.api = NodeAPI()
        self.api.inject_node(self)
        self.api.start(self.ip, api_port)

    def handle_transaction(self, transaction, from_api=False):
        # Update this node's activity in quantum consensus
        self.blockchain.quantum_consensus.register_node(
            self.wallet.public_key_string(), 
            self.wallet.public_key_string()
        )
        
        data = transaction.payload()
        signature = transaction.signature
        signer_public_key = transaction.sender_public_key
        signature_valid = Wallet.signature_valid(data, signature, signer_public_key)
        transaction_exists = self.transaction_pool.transaction_exists(transaction)
        transaction_in_block = self.blockchain.transaction_exists(transaction)

        if not transaction_exists and not transaction_in_block and signature_valid:
            self.transaction_pool.add_transaction(transaction)
            
            logger.info({
                "message": "Transaction added to pool",
                "pool_size": len(self.transaction_pool.transactions),
                "transaction_type": transaction.type,
                "sender": transaction.sender_public_key[:20] + "...",
                "receiver": transaction.receiver_public_key[:20] + "...",
                "source": "API" if from_api else "P2P"
            })
            
            # Only broadcast if this transaction came from API (not P2P)
            if from_api:
                message = Message(self.p2p.socket_connector, "TRANSACTION", transaction)
                self.p2p.broadcast(BlockchainUtils.encode(message))

            forging_required = self.transaction_pool.forging_required()
            
            # Only log forging checks occasionally to reduce log spam
            if forging_required or len(self.transaction_pool.transactions) % 5 == 0:
                logger.info({
                    "message": "Checking forging requirement",
                    "forging_required": forging_required,
                    "pool_size": len(self.transaction_pool.transactions),
                    "node_public_key": self.wallet.public_key_string()[:20] + "...",
                    "source": "API" if from_api else "P2P"
                })
            
            if forging_required:
                # Add a small delay to prevent thundering herd of forge attempts
                if from_api:
                    time.sleep(0.5)  # Brief delay for API transactions to reduce CPU spikes
                    
                logger.info({
                    "message": "Attempting to forge block",
                    "source": "API" if from_api else "P2P"
                })
                self.forge()

    def handle_block(self, block):
        forger = block.forger
        block_hash = block.payload()
        signature = block.signature
        
        # Calculate block hash for duplicate detection
        block_hash_hex = BlockchainUtils.hash(block_hash).hex()

        logger.info({
            "message": "Received block from network",
            "block_number": block.block_count,
            "forger": forger[:30] + "..." if forger else "None",
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

        block_count_valid = self.blockchain.block_count_valid(block)
        last_block_hash_valid = self.blockchain.last_block_hash_valid(block)
        forger_valid = self.blockchain.forger_valid(block)
        transactions_valid = self.blockchain.transactions_valid(block.transactions)
        signature_valid = Wallet.signature_valid(block_hash, signature, forger)

        # Enhanced logging with forger mismatch details
        logger.info({
            "message": "Block validation results",
            "block_count_valid": block_count_valid,
            "last_block_hash_valid": last_block_hash_valid,
            "forger_valid": forger_valid,
            "transactions_valid": transactions_valid,
            "signature_valid": signature_valid
        })

        if not block_count_valid:
            logger.info({"message": "Block count invalid, requesting full chain"})
            self.request_chain()

        # Use proper Leader-Based Consensus validation (now implemented in blockchain.py)
        # This includes the new forger validation that trusts quantum consensus selection
        if (
            last_block_hash_valid
            and forger_valid
            and transactions_valid
            and signature_valid
        ):
            logger.info({
                "message": "Block validated successfully via Leader-Based Consensus",
                "block_number": block.block_count,
                "new_blockchain_length": len(self.blockchain.blocks) + 1,
                "validations": {
                    "last_block_hash": last_block_hash_valid,
                    "forger": forger_valid,
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
                "forger": forger[:30] + "..." if forger else "None",
                "failed_validations": {
                    "last_block_hash": not last_block_hash_valid,
                    "transactions": not transactions_valid,
                    "signature": not signature_valid
                },
                "note": "Block rejected due to fundamental validation failures (not forger mismatch)"
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

    def forge(self):
        # Check if we should forge (quantum consensus selection)
        forger = self.blockchain.next_forger()
        my_public_key = self.wallet.public_key_string()
        
        logger.info({
            "message": "Forging attempt",
            "selected_forger": forger[:50] + "..." if forger else "None",
            "my_public_key": my_public_key[:50] + "...",
            "am_i_forger": forger == my_public_key,
            "transactions_in_pool": len(self.transaction_pool.transactions),
            "current_blockchain_length": len(self.blockchain.blocks)
        })
        
        if forger == my_public_key:
            try:
                # CRITICAL: Check if a block was already received for this round
                # This prevents race conditions where multiple nodes try to forge simultaneously
                expected_block_count = len(self.blockchain.blocks)
                
                logger.info({
                    "message": "I am selected as forger, proceeding with block creation",
                    "expected_block_count": expected_block_count,
                    "current_time": time.time(),
                    "transactions_available": len(self.transaction_pool.transactions)
                })
                
                # Get transactions for this block (respecting size limits)
                max_block_size = self.blockchain.get_max_block_size()
                transactions_for_block = self.transaction_pool.get_transactions_for_block(max_block_size)
                
                if not transactions_for_block:
                    logger.warning({
                        "message": "No transactions available for block creation, aborting forge",
                        "pool_size": len(self.transaction_pool.transactions),
                        "max_block_size": max_block_size
                    })
                    return
                
                # Update forge time before creating block
                self.transaction_pool.update_last_forge_time()
                
                block = self.blockchain.create_block(
                    transactions_for_block, self.wallet
                )
                
                # Double-check that no block was added while we were creating this one
                if block.block_count != expected_block_count:
                    logger.warning({
                        "message": "Block race condition detected, another block was added during creation",
                        "expected_block_count": expected_block_count,
                        "actual_block_count": block.block_count,
                        "current_blockchain_length": len(self.blockchain.blocks)
                    })
                    return  # Abort forging, another node was faster
                
                logger.info({
                    "message": "Block forged successfully",
                    "block_number": block.block_count,
                    "transactions_included": len(block.transactions),
                    "forger": my_public_key[:20] + "...",
                    "block_timestamp": block.timestamp,
                    "block_hash": BlockchainUtils.hash(block.payload()).hex()[:16] + "...",
                    "remaining_in_pool": len(self.transaction_pool.transactions) - len(block.transactions)
                })
                
                # Remove only the transactions that were included in the block
                self.transaction_pool.remove_from_pool(block.transactions)
                
                # Mark our own block as seen to prevent rebroadcast loops
                forged_block_hash = BlockchainUtils.hash(block.payload()).hex()
                self.seen_blocks.add(forged_block_hash)
                
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
                    "message": "Block forging failed",
                    "error": str(e),
                    "forger": my_public_key[:20] + "..."
                })
                # Update quantum consensus with failed proposal
                self.blockchain.quantum_consensus.record_proposal_result(my_public_key, False)
                
        else:
            logger.info({
                "message": "Not selected as forger",
                "selected_forger": forger[:20] + "..." if forger else "None",
                "my_key": my_public_key[:20] + "..."
            })
