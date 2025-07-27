#!/usr/bin/env python3
"""
Debug script to test block creation and identify the wallet parameter issue
"""

import sys
sys.path.append('.')

from blockchain.transaction.wallet import Wallet
from blockchain.blockchain import Blockchain

def test_block_creation():
    """Test block creation with proper wallet object"""
    print("🔍 Testing block creation...")
    
    # Create a wallet
    wallet = Wallet()
    print(f"✅ Wallet created: {type(wallet)}")
    print(f"✅ Wallet has public_key_string: {hasattr(wallet, 'public_key_string')}")
    
    # Create blockchain
    blockchain = Blockchain(genesis_public_key=wallet.public_key_string())
    print(f"✅ Blockchain created with {len(blockchain.blocks)} blocks")
    
    # Try to create a block
    try:
        print("🏗️ Attempting to create block...")
        block = blockchain.create_block(wallet, use_gulf_stream=True)
        print(f"✅ Block created successfully: {block.block_count}")
        
    except Exception as e:
        print(f"❌ Block creation failed: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_block_creation()
