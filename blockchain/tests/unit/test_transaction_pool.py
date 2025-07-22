import os
import sys

# Add the parent directory to Python path to find blockchain modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from blockchain.transaction.transaction_pool import TransactionPool


def test_transaction_pool(transaction):
    pool = TransactionPool()
    assert not pool.transaction_exists(transaction)
    pool.add_transaction(transaction)
    assert pool.transaction_exists(transaction)
