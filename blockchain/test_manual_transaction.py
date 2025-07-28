#!/usr/bin/env python3
"""Quick transaction test script"""

import requests
import json
import time
from blockchain.transaction.transaction import Transaction
from blockchain.transaction.wallet import Wallet
from blockchain.utils.helpers import BlockchainUtils

def main():
    print("Creating test transaction...")
    
    # Load genesis keys
    try:
        with open('keys/genesis_private_key.pem', 'r') as f:
            private_key = f.read()
        with open('keys/genesis_public_key.pem', 'r') as f:
            genesis_public_key = f.read()
    except FileNotFoundError:
        print("Error: Genesis key files not found")
        return
    
    # Create receiver keys (using node2 for testing)
    try:
        with open('keys/node2_public_key.pem', 'r') as f:
            receiver_public_key = f.read()
    except FileNotFoundError:
        print("Error: Node2 key file not found")
        return
    
    # Create wallet from genesis private key
    wallet = Wallet()
    wallet.from_key(private_key)
    
    # Create transaction
    transaction = Transaction(
        sender_public_key=genesis_public_key,
        receiver_public_key=receiver_public_key,
        amount=25.0,
        type="TRANSFER"
    )
    
    # Sign the transaction
    signature = wallet.sign(transaction.payload())
    transaction.sign(signature)
    
    print(f"Transaction created: {transaction.id}")
    
    # Encode and submit
    encoded_transaction = BlockchainUtils.encode(transaction)
    payload = {"transaction": encoded_transaction}
    
    try:
        response = requests.post(
            "http://localhost:11000/api/v1/transaction/create/",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Transaction submitted successfully!")
            print(f"Response: {response.json()}")
            
            # Check transaction pool
            time.sleep(1)
            pool_response = requests.get("http://localhost:11000/api/v1/transaction/transaction_pool/")
            if pool_response.status_code == 200:
                pool_data = pool_response.json()
                print(f"Transaction pool size: {len(pool_data)}")
            
        else:
            print(f"❌ Failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error submitting transaction: {e}")

if __name__ == "__main__":
    main()
