#!/usr/bin/env python3
"""
Block size management utility for the quantum annealing blockchain.

This script demonstrates how to configure and manage block size limits.
"""

import sys
import os

# Add the parent directory to Python path so we can import blockchain modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blockchain.blockchain import Blockchain
from blockchain.config.block_config import BlockConfig


def main():
    """Demonstrate block size configuration capabilities."""
    
    print("=== Quantum Annealing Blockchain - Block Size Configuration ===\n")
    
    # Create blockchain with default settings
    blockchain = Blockchain()
    print(f"1. Default blockchain created:")
    print_block_info(blockchain)
    print()
    
    # Show available presets
    print("2. Available block size presets:")
    for name, size in BlockConfig.BLOCK_SIZE_PRESETS.items():
        estimated_tx = BlockConfig.estimate_transactions_per_block(size)
        print(f"   {name:8} - {BlockConfig.format_size(size):8} (~{estimated_tx} transactions)")
    print()
    
    # Try different preset sizes
    print("3. Testing different block size presets:")
    for preset in ['tiny', 'small', 'medium', 'large']:
        try:
            blockchain.set_block_size_preset(preset)
            print(f"   Set to '{preset}': {blockchain.get_block_size_info()['max_size_formatted']}")
        except Exception as e:
            print(f"   Error setting '{preset}': {e}")
    print()
    
    # Set custom block size
    print("4. Setting custom block sizes:")
    custom_sizes = [512, 1024, 2048, 4096]
    for size in custom_sizes:
        try:
            blockchain.set_max_block_size(size)
            info = blockchain.get_block_size_info()
            print(f"   {BlockConfig.format_size(size):8} - ~{info['estimated_transactions_per_block']} transactions")
        except Exception as e:
            print(f"   Error setting {size} bytes: {e}")
    print()
    
    # Demonstrate block size validation
    print("5. Block size validation:")
    test_sizes = [100, 200, 1024, 1000000, 20000000]  # Some valid, some invalid
    for size in test_sizes:
        is_valid = BlockConfig.validate_block_size(size)
        status = "✓ Valid" if is_valid else "✗ Invalid"
        print(f"   {BlockConfig.format_size(size):10} - {status}")
    print()
    
    # Show final configuration
    print("6. Final blockchain configuration:")
    print_block_info(blockchain)


def print_block_info(blockchain):
    """Print detailed information about blockchain block configuration."""
    info = blockchain.get_block_size_info()
    print(f"   Max block size: {info['max_size_formatted']} ({info['max_size_bytes']} bytes)")
    print(f"   Estimated transactions per block: {info['estimated_transactions_per_block']}")
    print(f"   Block overhead: {BlockConfig.format_size(info['block_header_overhead'])}")


if __name__ == "__main__":
    main()
