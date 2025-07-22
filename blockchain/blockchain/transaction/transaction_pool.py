import time
import json

class TransactionPool:
    def __init__(self):
        self.transactions = []
        self.last_forge_time = 0
        self.min_forge_interval = 8.0   # Reduced from 15 to 8 seconds - balance between CPU and responsiveness
        self.max_forge_interval = 45.0  # Reduced from 60 to 45 seconds 
        self.min_transactions_for_forging = 3  # Keep at 3 for batching
        self.max_transactions_per_block = 15  # Keep larger blocks
        
        # Block size considerations
        self.estimated_transaction_size = 300  # Bytes per transaction (rough estimate)

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def transaction_exists(self, transaction):
        for pool_transaction in self.transactions:
            if pool_transaction.equals(transaction):
                return True
        return False

    def remove_from_pool(self, transactions):
        new_pool_transactions = []
        for pool_transaction in self.transactions:
            insert = True
            for transaction in transactions:
                if pool_transaction.equals(transaction):
                    insert = False
            if insert:
                new_pool_transactions.append(pool_transaction)
        self.transactions = new_pool_transactions

    def forging_required(self):
        """
        Determine if forging is required based on:
        1. Minimum transaction count (≥2)
        2. Time-based constraints to prevent over-forging
        3. Maximum wait time to ensure progress
        """
        current_time = time.time()
        time_since_last_forge = current_time - self.last_forge_time
        transaction_count = len(self.transactions)
        
        # Must have minimum transactions
        if transaction_count < self.min_transactions_for_forging:
            return False
        
        # Respect minimum forging interval to prevent spam blocks
        if time_since_last_forge < self.min_forge_interval:
            return False
            
        # Force forging if we have transactions and max interval passed
        if transaction_count >= self.min_transactions_for_forging and time_since_last_forge >= self.max_forge_interval:
            return True
            
        # Allow forging if we have sufficient transactions and some time has passed
        if transaction_count >= 6 and time_since_last_forge >= self.min_forge_interval:
            return True
            
        # Allow forging if pool is getting full
        if transaction_count >= self.max_transactions_per_block:
            return True
            return True
            
        return False
    
    def get_transactions_for_block(self, max_block_size_bytes=None):
        """
        Get transactions to include in the next block.
        
        Args:
            max_block_size_bytes (int, optional): Maximum block size in bytes.
                                                 If provided, will estimate transaction count.
        
        Returns:
            List of transactions for the block
        """
        if max_block_size_bytes is not None:
            # Estimate how many transactions can fit in the block
            # Account for block overhead (headers, metadata, etc.)
            block_overhead = 200  # bytes
            available_space = max_block_size_bytes - block_overhead
            estimated_max_transactions = max(1, available_space // self.estimated_transaction_size)
            
            # Use the smaller of: estimated max transactions, configured max, or available transactions
            max_transactions = min(estimated_max_transactions, self.max_transactions_per_block, len(self.transactions))
        else:
            max_transactions = min(self.max_transactions_per_block, len(self.transactions))
        
        return self.transactions[:max_transactions]
    
    def estimate_transaction_size(self, transaction):
        """
        Estimate the size of a transaction in bytes.
        
        Args:
            transaction: Transaction object
            
        Returns:
            int: Estimated size in bytes
        """
        try:
            transaction_dict = transaction.to_dict()
            transaction_json = json.dumps(transaction_dict, separators=(',', ':'))
            return len(transaction_json.encode('utf-8'))
        except Exception:
            # Fallback estimate if serialization fails
            return self.estimated_transaction_size
    
    def get_pool_size_estimate(self):
        """
        Get an estimate of the total size of all transactions in the pool.
        
        Returns:
            int: Estimated size in bytes
        """
        if not self.transactions:
            return 0
        
        # Sample a few transactions to get better size estimate
        sample_size = min(5, len(self.transactions))
        total_sample_size = sum(self.estimate_transaction_size(tx) for tx in self.transactions[:sample_size])
        avg_transaction_size = total_sample_size / sample_size
        
        return int(avg_transaction_size * len(self.transactions))
    
    def can_fit_in_block(self, max_block_size_bytes):
        """
        Check if the current pool can fit in a block of the given size.
        
        Args:
            max_block_size_bytes (int): Maximum block size in bytes
            
        Returns:
            bool: True if transactions can fit, False otherwise
        """
        estimated_pool_size = self.get_pool_size_estimate()
        block_overhead = 200  # bytes for block headers and metadata
        return (estimated_pool_size + block_overhead) <= max_block_size_bytes
    
    def update_last_forge_time(self):
        """Update the last forge time - should be called when a block is successfully created"""
        self.last_forge_time = time.time()
