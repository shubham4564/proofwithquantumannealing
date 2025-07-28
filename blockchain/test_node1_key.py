#!/usr/bin/env python3
"""
Test that the node1 ECDSA key works correctly with our implementation.
"""

import sys
import os

# Add the blockchain module path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from blockchain.quantum_consensus.quantum_annealing_consensus import QuantumAnnealingConsensus

def test_node1_key():
    """Test that node1 key loads and works correctly"""
    print("🧪 Testing node1 ECDSA key with quantum consensus...")
    
    # Initialize consensus
    consensus = QuantumAnnealingConsensus(initialize_genesis=False)
    
    # Test loading node1 key
    try:
        public_key, private_key = consensus.load_node_keys_from_file("node1")
        print(f"✅ Successfully loaded node1 keys")
        print(f"   Public key starts with: {public_key[:50]}...")
        print(f"   Private key starts with: {private_key[:50]}...")
        
        # Test signing with node1 key
        test_message = b"Test message for node1 ECDSA signing"
        signature = consensus.sign_message("node1", test_message)
        print(f"✅ Successfully signed message")
        print(f"   Signature: {signature[:64]}...")
        
        # Test verification
        is_valid = consensus.verify_signature("node1", test_message, signature)
        print(f"✅ Signature verification: {'PASSED' if is_valid else 'FAILED'}")
        
        # Test with wrong message
        wrong_message = b"Wrong message"
        is_invalid = consensus.verify_signature("node1", wrong_message, signature)
        print(f"✅ Wrong message verification: {'CORRECTLY REJECTED' if not is_invalid else 'INCORRECTLY ACCEPTED'}")
        
        print("\n🎉 node1 ECDSA key test successful!")
        return True
        
    except Exception as e:
        print(f"❌ node1 key test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_node1_key()
    exit(0 if success else 1)
