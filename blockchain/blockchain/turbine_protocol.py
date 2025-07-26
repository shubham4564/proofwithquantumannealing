import json
import hashlib
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Shred:
    """A single data packet for Turbine transmission"""
    index: int
    total_shreds: int
    data: bytes
    is_data_shred: bool  # True for data shreds, False for recovery shreds
    block_hash: str
    
    def to_bytes(self) -> bytes:
        """Serialize shred for network transmission"""
        header = {
            'index': self.index,
            'total_shreds': self.total_shreds,
            'is_data_shred': self.is_data_shred,
            'block_hash': self.block_hash
        }
        header_bytes = json.dumps(header).encode()
        header_len = len(header_bytes).to_bytes(4, 'big')
        return header_len + header_bytes + self.data
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'Shred':
        """Deserialize shred from network transmission"""
        header_len = int.from_bytes(data[:4], 'big')
        header_bytes = data[4:4+header_len]
        header = json.loads(header_bytes.decode())
        shred_data = data[4+header_len:]
        
        return cls(
            index=header['index'],
            total_shreds=header['total_shreds'],
            data=shred_data,
            is_data_shred=header['is_data_shred'],
            block_hash=header['block_hash']
        )

class BlockShredder:
    """Handles block shredding and erasure coding for Turbine protocol"""
    
    def __init__(self, shred_size: int = 1024, redundancy_ratio: float = 0.3):
        self.shred_size = shred_size
        self.redundancy_ratio = redundancy_ratio
    
    def shred_block(self, block) -> List[Shred]:
        """
        Shred a block into fixed-size packets with erasure coding.
        
        Args:
            block: Block to shred
            
        Returns:
            List of shreds (data + recovery shreds)
        """
        # Serialize block to bytes
        block_data = json.dumps(block.to_dict()).encode()
        block_hash = hashlib.sha256(block_data).hexdigest()
        
        # Split into data shreds
        data_shreds = []
        for i in range(0, len(block_data), self.shred_size):
            chunk = block_data[i:i + self.shred_size]
            # Pad last chunk if necessary
            if len(chunk) < self.shred_size:
                chunk += b'\x00' * (self.shred_size - len(chunk))
            
            shred = Shred(
                index=len(data_shreds),
                total_shreds=0,  # Will be set after calculating recovery shreds
                data=chunk,
                is_data_shred=True,
                block_hash=block_hash
            )
            data_shreds.append(shred)
        
        # Generate recovery shreds using simple XOR-based erasure coding
        recovery_shreds = self._generate_recovery_shreds(data_shreds, block_hash)
        
        # Update total shred count
        total_shreds = len(data_shreds) + len(recovery_shreds)
        for shred in data_shreds + recovery_shreds:
            shred.total_shreds = total_shreds
        
        return data_shreds + recovery_shreds
    
    def _generate_recovery_shreds(self, data_shreds: List[Shred], block_hash: str) -> List[Shred]:
        """Generate recovery shreds using simple XOR-based erasure coding"""
        num_recovery = max(1, int(len(data_shreds) * self.redundancy_ratio))
        recovery_shreds = []
        
        for i in range(num_recovery):
            # Simple XOR-based parity: XOR all data shreds together
            recovery_data = bytearray(self.shred_size)
            for data_shred in data_shreds:
                for j in range(len(data_shred.data)):
                    recovery_data[j] ^= data_shred.data[j]
            
            # Add some variation for each recovery shred
            seed = f"{block_hash}_{i}".encode()
            for j in range(min(len(seed), len(recovery_data))):
                recovery_data[j] ^= seed[j]
            
            recovery_shred = Shred(
                index=len(data_shreds) + i,
                total_shreds=0,  # Will be set later
                data=bytes(recovery_data),
                is_data_shred=False,
                block_hash=block_hash
            )
            recovery_shreds.append(recovery_shred)
        
        return recovery_shreds
    
    def reconstruct_block(self, shreds: List[Shred]):
        """
        Reconstruct a block from received shreds.
        
        Args:
            shreds: List of received shreds
            
        Returns:
            Reconstructed block data or None if insufficient shreds
        """
        if not shreds:
            return None
        
        # Separate data and recovery shreds
        data_shreds = [s for s in shreds if s.is_data_shred]
        recovery_shreds = [s for s in shreds if not s.is_data_shred]
        
        # Sort data shreds by index
        data_shreds.sort(key=lambda x: x.index)
        
        # Calculate expected number of data shreds
        total_shreds = shreds[0].total_shreds
        expected_data_shreds = int(total_shreds / (1 + self.redundancy_ratio))
        
        # Check if we have enough shreds to reconstruct
        if len(data_shreds) >= expected_data_shreds:
            # We have enough data shreds, reconstruct directly
            return self._reconstruct_from_data_shreds(data_shreds, expected_data_shreds)
        elif len(shreds) >= expected_data_shreds:
            # Use erasure coding to recover missing data shreds
            return self._reconstruct_with_erasure_coding(data_shreds, recovery_shreds, expected_data_shreds)
        else:
            return None
    
    def _reconstruct_from_data_shreds(self, data_shreds: List[Shred], expected_count: int):
        """Reconstruct block from data shreds only"""
        if len(data_shreds) < expected_count:
            return None
        
        # Concatenate data from shreds
        block_data = b''
        for i in range(expected_count):
            shred = next((s for s in data_shreds if s.index == i), None)
            if shred is None:
                return None
            block_data += shred.data
        
        # Remove padding and deserialize
        block_data = block_data.rstrip(b'\x00')
        try:
            block_dict = json.loads(block_data.decode())
            return block_dict
        except:
            return None
    
    def _reconstruct_with_erasure_coding(self, data_shreds: List[Shred], recovery_shreds: List[Shred], expected_count: int):
        """Reconstruct missing data shreds using recovery shreds"""
        # For simplicity, this is a placeholder for more sophisticated erasure coding
        # In production, you would use Reed-Solomon or similar algorithms
        
        # If we have enough total shreds, attempt reconstruction
        if len(data_shreds) + len(recovery_shreds) >= expected_count:
            # For now, just try direct reconstruction if possible
            return self._reconstruct_from_data_shreds(data_shreds, min(len(data_shreds), expected_count))
        
        return None

class TurbinePropagationTree:
    """Manages the tree structure for Turbine block propagation"""
    
    def __init__(self, fanout: int = 200):
        self.fanout = fanout
        self.nodes = {}  # node_id -> node_info
        self.tree_structure = {}  # node_id -> [child_node_ids]
    
    def register_node(self, node_id: str, stake_weight: float = 1.0, network_address: str = None):
        """Register a node in the propagation tree"""
        self.nodes[node_id] = {
            'stake_weight': stake_weight,
            'network_address': network_address,
            'children': []
        }
        self._rebuild_tree()
    
    def _rebuild_tree(self):
        """Rebuild the propagation tree based on stake weights"""
        if not self.nodes:
            return
        
        # Sort nodes by stake weight (descending)
        sorted_nodes = sorted(self.nodes.items(), key=lambda x: x[1]['stake_weight'], reverse=True)
        
        # Build tree structure
        self.tree_structure = {node_id: [] for node_id, _ in sorted_nodes}
        
        # Assign children based on fanout
        for i, (parent_id, _) in enumerate(sorted_nodes):
            start_child = i * self.fanout + 1
            end_child = min(start_child + self.fanout, len(sorted_nodes))
            
            for j in range(start_child, end_child):
                if j < len(sorted_nodes):
                    child_id = sorted_nodes[j][0]
                    self.tree_structure[parent_id].append(child_id)
                    self.nodes[parent_id]['children'].append(child_id)
    
    def get_children(self, node_id: str) -> List[str]:
        """Get the children of a node in the propagation tree"""
        return self.tree_structure.get(node_id, [])
    
    def get_propagation_path(self, from_node: str) -> List[str]:
        """Get the propagation path from a node to all its descendants"""
        path = []
        to_visit = [from_node]
        
        while to_visit:
            current = to_visit.pop(0)
            if current != from_node:
                path.append(current)
            children = self.get_children(current)
            to_visit.extend(children)
        
        return path

class TurbineProtocol:
    """Main Turbine protocol implementation for block propagation"""
    
    def __init__(self, fanout: int = 200, shred_size: int = 1024):
        self.shredder = BlockShredder(shred_size=shred_size)
        self.propagation_tree = TurbinePropagationTree(fanout=fanout)
        self.received_shreds = {}  # block_hash -> List[Shred]
        self.reconstructed_blocks = {}  # block_hash -> block_data
    
    def register_validator(self, validator_id: str, stake_weight: float = 1.0, network_address: str = None):
        """Register a validator in the Turbine network"""
        self.propagation_tree.register_node(validator_id, stake_weight, network_address)
    
    def broadcast_block(self, block, leader_id: str) -> List[Dict]:
        """
        Broadcast a block using Turbine protocol.
        
        Returns list of transmission tasks for the network layer.
        """
        # Shred the block
        shreds = self.shredder.shred_block(block)
        
        # Get direct children of the leader
        children = self.propagation_tree.get_children(leader_id)
        
        # Distribute shreds among children
        transmission_tasks = []
        if children:
            shreds_per_child = len(shreds) // len(children)
            remainder = len(shreds) % len(children)
            
            shred_index = 0
            for i, child_id in enumerate(children):
                # Calculate how many shreds this child gets
                child_shred_count = shreds_per_child + (1 if i < remainder else 0)
                child_shreds = shreds[shred_index:shred_index + child_shred_count]
                shred_index += child_shred_count
                
                transmission_tasks.append({
                    'target_node': child_id,
                    'shreds': child_shreds,
                    'action': 'send_shreds'
                })
        
        return transmission_tasks
    
    def receive_shred(self, shred: Shred, receiving_node_id: str) -> List[Dict]:
        """
        Process a received shred and forward it if necessary.
        
        Returns list of forwarding tasks.
        """
        block_hash = shred.block_hash
        
        # Store the shred
        if block_hash not in self.received_shreds:
            self.received_shreds[block_hash] = []
        self.received_shreds[block_hash].append(shred)
        
        # Try to reconstruct the block
        if block_hash not in self.reconstructed_blocks:
            reconstructed = self.shredder.reconstruct_block(self.received_shreds[block_hash])
            if reconstructed:
                self.reconstructed_blocks[block_hash] = reconstructed
        
        # Forward the shred to children
        children = self.propagation_tree.get_children(receiving_node_id)
        forwarding_tasks = []
        
        for child_id in children:
            forwarding_tasks.append({
                'target_node': child_id,
                'shreds': [shred],
                'action': 'forward_shred'
            })
        
        return forwarding_tasks
    
    def get_block_reconstruction_status(self, block_hash: str) -> Dict:
        """Get the status of block reconstruction"""
        received_count = len(self.received_shreds.get(block_hash, []))
        is_reconstructed = block_hash in self.reconstructed_blocks
        
        return {
            'block_hash': block_hash,
            'shreds_received': received_count,
            'is_reconstructed': is_reconstructed,
            'block_data': self.reconstructed_blocks.get(block_hash)
        }
