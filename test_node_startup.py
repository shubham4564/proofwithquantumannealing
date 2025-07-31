#!/usr/bin/env python3
"""
Test script to validate node startup components
"""

import os
import sys
import subprocess

def test_wallet_import():
    """Test that we can import and use the Wallet class"""
    print("🧪 Testing Wallet class import...")
    
    # Add blockchain path
    sys.path.insert(0, os.path.join(os.getcwd(), 'blockchain'))
    
    try:
        from blockchain.transaction.wallet import Wallet
        print("✅ Wallet class imported successfully")
        
        # Test creating a wallet
        wallet = Wallet()
        print("✅ Wallet instance created successfully")
        
        # Test that save_to_file method exists
        if hasattr(wallet, 'save_to_file'):
            print("✅ save_to_file method exists")
        else:
            print("❌ save_to_file method missing")
            return False
            
        # Test key generation without actually saving
        pem_data = wallet.get_private_key_pem()
        if pem_data and pem_data.startswith('-----BEGIN PRIVATE KEY-----'):
            print("✅ Private key generation working")
        else:
            print("❌ Private key generation failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Wallet test failed: {e}")
        return False

def test_existing_keys():
    """Test that required key files exist"""
    print("\n🔑 Testing existing key files...")
    
    key_dir = "blockchain/keys"
    if not os.path.exists(key_dir):
        print(f"❌ Key directory not found: {key_dir}")
        return False
        
    required_keys = [
        "genesis_private_key.pem",
        "node2_private_key.pem", 
        "node3_private_key.pem",
        "node4_private_key.pem",
        "node5_private_key.pem",
        "node6_private_key.pem"
    ]
    
    missing_keys = []
    for key_file in required_keys:
        key_path = os.path.join(key_dir, key_file)
        if os.path.exists(key_path):
            print(f"✅ Found: {key_file}")
        else:
            print(f"❌ Missing: {key_file}")
            missing_keys.append(key_file)
    
    if missing_keys:
        print(f"\n⚠️ Missing {len(missing_keys)} key files")
        return False
    else:
        print("✅ All required key files found")
        return True

def test_key_format():
    """Test that key files are in correct format"""
    print("\n🔍 Testing key file formats...")
    
    test_key = "blockchain/keys/genesis_private_key.pem"
    if not os.path.exists(test_key):
        print(f"❌ Test key not found: {test_key}")
        return False
        
    try:
        with open(test_key, 'r') as f:
            content = f.read()
            
        if content.startswith('-----BEGIN PRIVATE KEY-----'):
            print("✅ Key file format is correct (PKCS#8 PEM)")
            return True
        elif content.startswith('-----BEGIN EC PRIVATE KEY-----'):
            print("⚠️ Key file is in EC format, may need conversion")
            return True
        else:
            print("❌ Unknown key format")
            return False
            
    except Exception as e:
        print(f"❌ Error reading key file: {e}")
        return False

def test_network_detection():
    """Test network IP detection"""
    print("\n🌐 Testing network detection...")
    
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        if result.returncode == 0:
            ip = result.stdout.strip().split()[0]
            print(f"✅ Detected IP: {ip}")
            
            # Extract subnet
            if '.' in ip:
                subnet = '.'.join(ip.split('.')[:-1])
                print(f"✅ Detected subnet: {subnet}.x")
                return True
            else:
                print("❌ Invalid IP format")
                return False
        else:
            print("❌ Could not detect IP address")
            return False
            
    except Exception as e:
        print(f"❌ Network detection failed: {e}")
        return False

def main():
    print("🚀 Node Startup Component Tests")
    print("===============================\n")
    
    tests = [
        ("Wallet Import", test_wallet_import),
        ("Existing Keys", test_existing_keys), 
        ("Key Format", test_key_format),
        ("Network Detection", test_network_detection)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running: {test_name}")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Node startup should work correctly.")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues before starting nodes.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
