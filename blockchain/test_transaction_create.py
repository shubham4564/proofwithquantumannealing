#!/usr/bin/env python3
"""
Test script to create a valid transaction for testing the API
"""
import sys
import json
import requests
sys.path.append('.')

from blockchain.transaction.transaction import Transaction
from blockchain.utils.helpers import BlockchainUtils
from blockchain.transaction.wallet import Wallet

def create_test_transaction():
    """Create a properly encoded transaction for testing"""
    # Create a simple transaction
    wallet = Wallet()
    transaction = Transaction(
        sender_public_key=wallet.public_key_string(),
        receiver_public_key='test_recipient',
        amount=100.0,
        type='transfer'
    )
    
    # Sign the transaction properly using the wallet's sign method
    payload = transaction.payload()  # This returns a dict, not bytes
    proper_signature = wallet.sign(payload)
    transaction.sign(proper_signature)
    
    # Encode it properly using jsonpickle (same as BlockchainUtils.encode)
    import jsonpickle
    encoded_transaction = jsonpickle.encode(transaction, unpicklable=True)
    payload = {'transaction': encoded_transaction}
    
    print("Testing transaction creation API...")
    print(f"Transaction payload size: {len(json.dumps(payload))} bytes")
    
    # Test the API
    try:
        response = requests.post(
            'http://localhost:11000/api/v1/transaction/create/',
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Transaction submitted successfully!")
        else:
            print(f"❌ Transaction submission failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error submitting transaction: {e}")

if __name__ == "__main__":
    create_test_transaction()
