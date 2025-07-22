# Flexible Block Size Configuration

This document explains how to configure and manage block size limits in the quantum annealing blockchain.

## Overview

The blockchain now supports flexible block size configuration with a default limit of 1KB. This limit can be easily adjusted based on network requirements, performance needs, and storage constraints.

## Features

### 1. Configurable Block Size Limits
- **Default**: 1KB (1024 bytes)
- **Minimum**: 200 bytes (prevents tiny blocks)
- **Maximum**: 10MB (prevents abuse)
- **Flexible**: Can be changed at runtime

### 2. Preset Configurations
Common block size presets are available:

| Preset   | Size     | Est. Transactions |
|----------|----------|-------------------|
| tiny     | 512B     | ~1-2              |
| small    | 1KB      | ~2-3              |
| medium   | 4KB      | ~8-12             |
| large    | 16KB     | ~32-48            |
| xlarge   | 64KB     | ~128-192          |
| xxlarge  | 256KB    | ~512-768          |

### 3. Automatic Size Management
- Transactions are automatically selected to fit within size limits
- Block size is calculated in real-time
- Size validation is performed during block creation and validation

## Usage Examples

### Basic Configuration

```python
from blockchain.blockchain import Blockchain

# Create blockchain with default 1KB block size
blockchain = Blockchain()

# Create blockchain with custom size (2KB)
blockchain = Blockchain(max_block_size=2048)
```

### Changing Block Size

```python
# Set custom block size (4KB)
blockchain.set_max_block_size(4096)

# Use preset configuration
blockchain.set_block_size_preset('medium')  # 4KB

# Get current configuration
size_info = blockchain.get_block_size_info()
print(f"Max size: {size_info['max_size_formatted']}")
print(f"Estimated transactions: {size_info['estimated_transactions_per_block']}")
```

### Block Size Validation

```python
from blockchain.config.block_config import BlockConfig

# Check if a size is valid
is_valid = BlockConfig.validate_block_size(2048)  # True

# Format size for display
formatted = BlockConfig.format_size(2048)  # "2.0 KB"

# Estimate transaction capacity
tx_count = BlockConfig.estimate_transactions_per_block(2048)  # ~6
```

## Implementation Details

### Block Size Calculation
Block size is calculated using JSON serialization of the block data:
- Block headers and metadata (~200 bytes overhead)
- Transaction data (variable size)
- Signatures and cryptographic proofs

### Transaction Selection Algorithm
When creating blocks, transactions are selected using a greedy approach:
1. Start with an empty block
2. Add transactions one by one
3. Check if the resulting block exceeds the size limit
4. Stop when the limit would be exceeded

### Size-Aware Transaction Pool
The transaction pool can estimate:
- Individual transaction sizes
- Total pool size
- How many transactions fit in a block
- Whether the current pool can fit in one block

## Configuration Files

### BlockConfig Class
Located in `blockchain/config/block_config.py`:
- Defines size limits and presets
- Provides validation and formatting utilities
- Estimates transaction capacity

### Transaction Pool
Enhanced in `blockchain/transaction/transaction_pool.py`:
- Size-aware transaction selection
- Pool size estimation
- Block capacity checking

## Performance Considerations

### Small Blocks (≤1KB)
- **Pros**: Fast propagation, low storage overhead, good for IoT
- **Cons**: Lower transaction throughput, more blocks needed

### Medium Blocks (1KB-16KB)
- **Pros**: Balanced performance, good general purpose
- **Cons**: Moderate storage and bandwidth requirements

### Large Blocks (≥16KB)
- **Pros**: High transaction throughput, fewer blocks
- **Cons**: Slower propagation, higher bandwidth/storage needs

## Best Practices

1. **Start Small**: Begin with small blocks (1KB) and increase as needed
2. **Monitor Performance**: Watch network propagation times and storage growth
3. **Consider Network**: Adjust based on network capacity and node resources
4. **Test Changes**: Use the demo script to test different configurations
5. **Document Changes**: Keep track of block size changes for network coordination

## Demo and Testing

Run the block size demonstration script:

```bash
cd blockchain/scripts
python block_size_demo.py
```

This script shows:
- Available presets
- Size validation
- Transaction capacity estimation
- Configuration examples

## API Reference

### Blockchain Methods
- `blockchain.set_max_block_size(size_bytes)` - Set custom size
- `blockchain.set_block_size_preset(preset_name)` - Use preset
- `blockchain.get_max_block_size()` - Get current size limit
- `blockchain.get_block_size_info()` - Get detailed configuration
- `blockchain.block_valid(block)` - Validate block including size

### Block Methods
- `block.calculate_size()` - Get block size in bytes
- `block.is_within_size_limit(max_size)` - Check size compliance

### Configuration Utilities
- `BlockConfig.validate_block_size(size)` - Validate size
- `BlockConfig.format_size(size)` - Format for display
- `BlockConfig.get_preset_size(preset)` - Get preset size
- `BlockConfig.estimate_transactions_per_block(size)` - Estimate capacity

## Migration Guide

If upgrading from a version without flexible block sizes:

1. **Existing blockchains**: Will use the default 1KB limit
2. **Configuration**: Update any hardcoded size assumptions
3. **Testing**: Verify block creation and validation still work
4. **Monitoring**: Watch for blocks that might exceed new limits

## Troubleshooting

### Common Issues

**Block size too small**:
- Increase the block size limit
- Check if transactions are unusually large
- Verify minimum size requirements

**Transactions not fitting**:
- Check individual transaction sizes
- Increase block size limit
- Optimize transaction data structures

**Performance issues**:
- Monitor block propagation times
- Consider reducing block size for faster networks
- Check storage growth rates

### Logging
Block size information is logged during:
- Blockchain initialization
- Block size changes
- Block creation and validation
- Size limit violations
