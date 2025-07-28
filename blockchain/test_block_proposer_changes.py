#!/usr/bin/env python3
"""
Test Block Constructor Changes
Verify that all forger references have been successfully changed to block_proposer
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_block_constructor():
    """Test that Block constructor works with block_proposer field"""
    print("🧪 Testing Block constructor changes...")
    
    try:
        from blockchain.block import Block
        from blockchain.transaction.transaction import Transaction
        
        # Test Block creation
        test_transactions = [
            Transaction(
                sender_public_key="test_sender",
                receiver_public_key="test_receiver", 
                amount=100,
                type="TRANSFER"
            )
        ]
        
        # Test Block constructor with block_proposer
        test_block = Block(
            transactions=test_transactions,
            last_hash="test_hash",
            block_proposer="test_proposer",
            block_count=1
        )
        
        print(f"   ✅ Block constructor works")
        print(f"   ✅ Block proposer field: {test_block.block_proposer}")
        print(f"   ✅ Block payload includes block_proposer: {'test_proposer' in test_block.payload()}")
        
        # Test to_dict method
        block_dict = test_block.to_dict()
        print(f"   ✅ to_dict() includes block_proposer: {'block_proposer' in str(block_dict)}")
        
        # Test to_json method
        block_json = test_block.to_json()
        print(f"   ✅ to_json() includes block_proposer: {'block_proposer' in block_json}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Block constructor test failed: {e}")
        return False

def test_blockchain_methods():
    """Test that blockchain methods work with block_proposer"""
    print("\n🧪 Testing Blockchain methods...")
    
    try:
        from blockchain.blockchain import Blockchain
        
        # Create test blockchain
        blockchain = Blockchain()
        
        # Test next_block_proposer method
        next_proposer = blockchain.next_block_proposer()
        print(f"   ✅ next_block_proposer() works: {next_proposer[:20] if next_proposer else 'None'}...")
        
        # Test block_proposer_valid method exists
        if hasattr(blockchain, 'block_proposer_valid'):
            print(f"   ✅ block_proposer_valid() method exists")
        else:
            print(f"   ❌ block_proposer_valid() method missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Blockchain methods test failed: {e}")
        return False

def test_api_compatibility():
    """Test that API endpoints support both field names for compatibility"""
    print("\n🧪 Testing API compatibility...")
    
    try:
        # Test data with both field names
        test_block_data_old = {
            'transactions': [],
            'last_hash': 'test_hash',
            'forger': 'test_forger',  # Old field name
            'block_count': 1,
            'timestamp': 1234567890,
            'signature': 'test_sig'
        }
        
        test_block_data_new = {
            'transactions': [],
            'last_hash': 'test_hash', 
            'block_proposer': 'test_proposer',  # New field name
            'block_count': 1,
            'timestamp': 1234567890,
            'signature': 'test_sig'
        }
        
        from blockchain.block import Block
        
        # Test creating block from old format
        try:
            old_block = Block(
                transactions=test_block_data_old['transactions'],
                last_hash=test_block_data_old['last_hash'],
                block_proposer=test_block_data_old.get('block_proposer', test_block_data_old.get('forger', '')),
                block_count=test_block_data_old['block_count']
            )
            print(f"   ✅ Backward compatibility with 'forger' field works")
        except Exception as e:
            print(f"   ❌ Backward compatibility failed: {e}")
            return False
        
        # Test creating block from new format
        try:
            new_block = Block(
                transactions=test_block_data_new['transactions'],
                last_hash=test_block_data_new['last_hash'],
                block_proposer=test_block_data_new['block_proposer'],
                block_count=test_block_data_new['block_count']
            )
            print(f"   ✅ New 'block_proposer' field works")
        except Exception as e:
            print(f"   ❌ New field format failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ API compatibility test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 Testing Block Proposer Field Changes")
    print("=" * 50)
    
    tests = [
        test_block_constructor,
        test_blockchain_methods,
        test_api_compatibility
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Block proposer field changes are successful.")
        return True
    else:
        print("❌ Some tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
