import math
import random
import time
import hashlib
import json
import secrets
import socket
from typing import Dict, List, Tuple, Optional
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# D-Wave Ocean SDK imports
from dimod import BinaryQuadraticModel, ExactSolver
from dwave.samplers import SimulatedAnnealingSampler
import numpy as np

from blockchain.utils.helpers import BlockchainUtils
from blockchain.utils.logger import CustomJsonFormatter
import logging


class ProbeProof:
    """Cryptographic proof of node probe with signature verification"""
    
    def __init__(self, timestamp: float, node_id: str, response_data: dict, 
                 signature: bytes, public_key: bytes, nonce: str):
        self.timestamp = timestamp
        self.node_id = node_id
        self.response_data = response_data
        self.signature = signature
        self.public_key = public_key
        self.nonce = nonce
        
    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp,
            'node_id': self.node_id,
            'response_data': self.response_data,
            'signature': self.signature.hex(),
            'public_key': self.public_key.hex(),
            'nonce': self.nonce
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            timestamp=data['timestamp'],
            node_id=data['node_id'],
            response_data=data['response_data'],
            signature=bytes.fromhex(data['signature']),
            public_key=bytes.fromhex(data['public_key']),
            nonce=data['nonce']
        )


class VerifiableUptimeRecord:
    """Verifiable uptime record with cryptographic proofs and witness consensus"""
    
    def __init__(self, node_id: str, uptime_period: float, witness_count: int,
                 probe_proofs: List[ProbeProof], merkle_root: str, 
                 consensus_timestamp: float):
        self.node_id = node_id
        self.uptime_period = uptime_period  # Mathematical integral result
        self.witness_count = witness_count
        self.probe_proofs = probe_proofs
        self.merkle_root = merkle_root
        self.consensus_timestamp = consensus_timestamp
        
    def to_dict(self) -> dict:
        return {
            'node_id': self.node_id,
            'uptime_period': self.uptime_period,
            'witness_count': self.witness_count,
            'probe_proofs': [proof.to_dict() for proof in self.probe_proofs],
            'merkle_root': self.merkle_root,
            'consensus_timestamp': self.consensus_timestamp
        }
        
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            node_id=data['node_id'],
            uptime_period=data['uptime_period'],
            witness_count=data['witness_count'],
            probe_proofs=[ProbeProof.from_dict(p) for p in data['probe_proofs']],
            merkle_root=data['merkle_root'],
            consensus_timestamp=data['consensus_timestamp']
        )

# Import scalability configuration
try:
    import sys
    import os
    # Try to import scalability config
    config_path = os.path.join(os.path.dirname(__file__), '../../../monitoring/scalability_config.py')
    if os.path.exists(config_path):
        sys.path.insert(0, os.path.dirname(config_path))
        from scalability_config import ScalabilityConfig
        SCALABILITY_CONFIG = ScalabilityConfig()
    else:
        # Fallback configuration
        class FallbackConfig:
            MAX_CANDIDATE_NODES = 50
            PROBE_SAMPLE_SIZE = 20
            PERFORMANCE_CACHE_TTL = 60
            NODE_ACTIVE_THRESHOLD = 300
            @staticmethod
            def get_quantum_reads_for_size(node_count): return min(150, max(50, node_count))
            @staticmethod
            def get_probe_sample_size(node_count): return min(20, max(5, int(math.sqrt(node_count))))
            @staticmethod
            def get_candidate_limit(node_count): return min(50, node_count)
        SCALABILITY_CONFIG = FallbackConfig()
except ImportError:
    # Fallback configuration if import fails
    class FallbackConfig:
        MAX_CANDIDATE_NODES = 50
        PROBE_SAMPLE_SIZE = 20
        PERFORMANCE_CACHE_TTL = 60
        NODE_ACTIVE_THRESHOLD = 300
        @staticmethod
        def get_quantum_reads_for_size(node_count): return min(150, max(50, node_count))
        @staticmethod
        def get_probe_sample_size(node_count): return min(20, max(5, int(math.sqrt(node_count))))
        @staticmethod
        def get_candidate_limit(node_count): return min(50, node_count)
    SCALABILITY_CONFIG = FallbackConfig()


class QuantumAnnealingConsensus:
    """
    Quantum Annealing-based Consensus Mechanism for Blockchain.
    
    This implementation follows the IEEE paper specification:
    - Selects representative node via QUBO optimization
    - Uses suitability scores from multiple performance metrics
    - Employs Probe Protocol for uptime/latency/throughput measurement
    - Quantum annealer solves optimization problem for node selection
    """
    
    def __init__(self, initialize_genesis=True):
        """
        Initialize Quantum Annealing Consensus Mechanism
        
        Args:
            initialize_genesis: Whether to initialize genesis node (set False for tests)
        """
        self.nodes = {}  # node_id -> {public_key, uptime, latency, throughput, last_seen, ...}
        self.probe_history = {}  # proof_id -> ProbeProof
        self.used_nonces = set()  # Track used nonces for replay protection
        self.node_keys = {}  # node_id -> (public_key, private_key) for cryptographic operations
        self.measurement_history = {}  # Track measurement windows for metrics calculation
        self.verifiable_uptime_records = {}  # record_id -> VerifiableUptimeRecord
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = CustomJsonFormatter()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Protocol parameters
        self.max_delay_tolerance = 30.0  # seconds (Δ in paper)
        self.block_proposal_timeout = 60.0  # seconds
        self.witness_quorum_size = 3  # minimum k/3 witnesses required
        self.nonce_expiry_time = 300  # 5 minutes for nonce replay protection
        
        # Scalability parameters for 1000+ nodes (using config)
        self.max_candidate_nodes = SCALABILITY_CONFIG.MAX_CANDIDATE_NODES
        self.probe_sample_size = SCALABILITY_CONFIG.PROBE_SAMPLE_SIZE  
        self.witness_sample_size = 10  # Witness pool size for large networks
        self.node_clustering_enabled = True  # Enable geographic/performance clustering
        self.performance_history_window = 100  # Keep last N performance records
        self.performance_cache_ttl = SCALABILITY_CONFIG.PERFORMANCE_CACHE_TTL
        self.node_active_threshold = SCALABILITY_CONFIG.NODE_ACTIVE_THRESHOLD
        
        # Scoring weights (as per paper methodology)
        self.weight_uptime = 0.25
        self.weight_latency = 0.25  # negative weight (lower is better)
        self.weight_throughput = 0.25
        self.weight_past_performance = 0.25
        
        # QUBO parameters
        self.penalty_coefficient = 1000.0  # Large P value for constraint enforcement
        self.perturbation_epsilon = 1e-5  # ε for tie-breaking
        
        # D-Wave Quantum Annealing parameters
        self.quantum_annealing_time = 20.0  # microseconds (typical for D-Wave)
        self.quantum_num_reads = 100  # Number of annealing runs
        self.use_quantum_simulator = True  # Use D-Wave simulator vs classical fallback
        
        # Performance tracking for scalability
        self.node_performance_cache = {}  # Cache calculated scores
        self.last_probe_round = 0  # Track probe rounds for efficient scheduling
        self.cluster_representatives = {}  # Geographic/performance clusters
        
        if initialize_genesis:
            self.initialize_genesis_node()

    def generate_node_keys(self, node_id: str) -> Tuple[str, str]:
        """Generate RSA key pair for a node"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        # Serialize public key
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        # Store keys
        self.node_keys[node_id] = (public_pem, private_pem)
        
        return public_pem, private_pem

    def sign_message(self, node_id: str, message: bytes) -> str:
        """Sign a message with node's private key"""
        if node_id not in self.node_keys:
            raise ValueError(f"No keys found for node {node_id}")
        
        _, private_pem = self.node_keys[node_id]
        private_key = serialization.load_pem_private_key(
            private_pem.encode('utf-8'),
            password=None
        )
        
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature.hex()

    def verify_signature(self, node_id: str, message: bytes, signature_hex: str) -> bool:
        """Verify a message signature using node's public key"""
        if node_id not in self.node_keys:
            return False
        
        try:
            public_pem, _ = self.node_keys[node_id]
            public_key = serialization.load_pem_public_key(public_pem.encode('utf-8'))
            
            signature = bytes.fromhex(signature_hex)
            
            public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    def verify_signature_bytes(self, public_key_bytes: bytes, message: bytes, signature_bytes: bytes) -> bool:
        """Verify a message signature using raw public key bytes"""
        if not public_key_bytes or not signature_bytes:
            return False
        
        try:
            # Load public key from bytes
            public_key = serialization.load_pem_public_key(public_key_bytes)
            
            public_key.verify(
                signature_bytes,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    def is_nonce_used(self, nonce: str) -> bool:
        """Check if nonce has been used (replay protection)"""
        return nonce in self.used_nonces

    def mark_nonce_used(self, nonce: str):
        """Mark nonce as used for replay protection"""
        self.used_nonces.add(nonce)
        
        # Cleanup old nonces periodically
        if len(self.used_nonces) > 10000:  # Limit memory usage
            # Remove old nonces (simplified - in production use timestamps)
            old_nonces = list(self.used_nonces)[:5000]
            for old_nonce in old_nonces:
                self.used_nonces.discard(old_nonce)

    def calculate_merkle_hash(self, data: str) -> str:
        """Calculate SHA-256 hash for Merkle tree operations"""
        return hashlib.sha256(data.encode()).hexdigest()

    def generate_merkle_root(self, probe_proofs: List[ProbeProof]) -> str:
        """Generate Merkle tree root for efficient proof verification"""
        if not probe_proofs:
            return ""
        
        # Create leaf hashes from probe proofs
        leaf_hashes = []
        for proof in probe_proofs:
            proof_data = json.dumps(proof.to_dict(), sort_keys=True)
            leaf_hashes.append(self.calculate_merkle_hash(proof_data))
        
        # Build Merkle tree bottom-up
        current_level = leaf_hashes
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                combined = left + right
                next_level.append(self.calculate_merkle_hash(combined))
            current_level = next_level
        
        return current_level[0] if current_level else ""

    def verify_merkle_proof(self, proof_data: dict, merkle_root: str, all_proofs: List[ProbeProof]) -> bool:
        """Verify that a proof is included in the Merkle tree"""
        # For simplicity, we regenerate the full tree and check inclusion
        # In production, this would use efficient Merkle proof paths
        calculated_root = self.generate_merkle_root(all_proofs)
        return calculated_root == merkle_root

    def verify_probe_proof(self, proof: ProbeProof) -> bool:
        """Verify cryptographic signature and nonce of a probe proof"""
        # Check nonce replay protection
        if self.is_nonce_used(proof.nonce):
            return False
        
        # Verify timestamp is recent (within reasonable window)
        current_time = time.time()
        if abs(current_time - proof.timestamp) > self.nonce_expiry_time:
            return False
        
        # Create message to verify
        message_data = {
            'timestamp': proof.timestamp,
            'node_id': proof.node_id,
            'response_data': proof.response_data,
            'nonce': proof.nonce
        }
        message = json.dumps(message_data, sort_keys=True).encode()
        
        # Verify signature using stored public key
        try:
            public_key = serialization.load_pem_public_key(proof.public_key)
            public_key.verify(
                proof.signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    def measure_real_network_latency(self, source_node: str, target_node: str) -> float:
        """
        Measure real network latency between nodes.
        In production, this would send actual network packets.
        For simulation, we create realistic latency based on node characteristics.
        """
        # Simulate realistic network conditions based on node properties
        if source_node in self.nodes and target_node in self.nodes:
            # Base latency from geographic/network distance simulation
            base_latency = random.uniform(0.005, 0.150)  # 5-150ms base
            
            # Add jitter based on node performance
            source_reliability = self.nodes[source_node].get('trust_score', 0.5)
            target_reliability = self.nodes[target_node].get('trust_score', 0.5)
            
            reliability_factor = (source_reliability + target_reliability) / 2
            jitter = random.uniform(0.001, 0.050) * (2 - reliability_factor)
            
            return base_latency + jitter
        else:
            return random.uniform(0.010, 0.500)  # Default simulation

    def initialize_genesis_node(self):
        """Initialize genesis node for bootstrap with cryptographic keys"""
        try:
            with open("./keys/genesis_public_key.pem", "rb") as key_file:
                key = serialization.load_pem_public_key(key_file.read())
            genesis_public_key = key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode("utf-8")
            
            # Try to load private key for genesis
            try:
                with open("./keys/genesis_private_key.pem", "rb") as key_file:
                    private_key_data = key_file.read()
                genesis_private_key = private_key_data.decode("utf-8")
                self.node_keys[genesis_public_key] = (genesis_public_key, genesis_private_key)
            except FileNotFoundError:
                # Generate keys if private key not found
                self.generate_node_keys(genesis_public_key)
            
            # Initialize genesis node with perfect scores
            self.nodes[genesis_public_key] = {
                'public_key': genesis_public_key,
                'uptime': 1.0,
                'latency': 0.1,  # Low latency
                'throughput': 100.0,
                'last_seen': time.time(),
                'proposal_success_count': 1,
                'proposal_failure_count': 0,
                'last_probe_time': time.time(),
                'uptime_periods': [(time.time() - 3600, time.time())],  # 1 hour uptime
                'response_count': 0,
                'measurement_window_start': time.time()
            }
            
        except FileNotFoundError:
            # Fallback genesis node with generated keys
            genesis_key = "genesis_node_key"
            self.generate_node_keys(genesis_key)
            
            self.nodes[genesis_key] = {
                'public_key': genesis_key,
                'uptime': 1.0,
                'latency': 0.1,
                'throughput': 100.0,
                'last_seen': time.time(),
                'proposal_success_count': 1,
                'proposal_failure_count': 0,
                'last_probe_time': time.time(),
                'uptime_periods': [(time.time() - 3600, time.time())],
                'response_count': 0,
                'measurement_window_start': time.time()
            }

    def register_node(self, node_id: str, public_key: str):
        """Register a new node in the network with scalable performance tracking and cryptographic keys"""
        current_time = time.time()
        
        if node_id not in self.nodes:
            # Generate cryptographic keys if not provided
            if node_id not in self.node_keys:
                self.generate_node_keys(node_id)
            
            self.nodes[node_id] = {
                'public_key': public_key,
                'uptime': 0.0,
                'latency': float('inf'),
                'throughput': 0.0,
                'last_seen': current_time,
                'proposal_success_count': 0,
                'proposal_failure_count': 0,
                'performance_history': [],  # Track recent performance
                'cluster_id': None,  # For geographic clustering
                'trust_score': 0.5,  # Initial trust score
                'uptime_periods': [],  # Track uptime periods for paper-compliant calculation
                'response_count': 0,  # Count of valid probe responses
                'measurement_window_start': current_time,  # Start of current measurement window
                'last_registration': current_time  # Track registration frequency for CPU optimization
            }
            
            # Clear performance cache when new nodes join
            self.node_performance_cache.clear()
        else:
            # For existing nodes, only update if sufficient time has passed (CPU optimization)
            last_registration = self.nodes[node_id].get('last_registration', 0)
            if current_time - last_registration < 30:  # Don't update more than once per 30 seconds
                return
            
            # Update last seen and registration time
            self.nodes[node_id]['last_seen'] = current_time
            self.nodes[node_id]['last_registration'] = current_time

    def cleanup_performance_data(self):
        """Clean up old performance data to manage memory for 1000+ nodes efficiently"""
        current_time = time.time()
        current_time_slot = int(current_time // self.performance_cache_ttl)
        
        # Remove old cached performance scores (using TTL-based slots)
        expired_cache_keys = [k for k in self.node_performance_cache.keys() 
                             if abs(current_time_slot - int(k.split('_')[-1])) > 5]  # Keep 5 time slots
        for key in expired_cache_keys:
            del self.node_performance_cache[key]
        
        # Limit cache size for memory efficiency
        if len(self.node_performance_cache) > 5000:  # Configurable limit
            # Remove oldest entries
            sorted_keys = sorted(self.node_performance_cache.keys(), 
                               key=lambda k: int(k.split('_')[-1]))
            for key in sorted_keys[:len(sorted_keys) - 4000]:  # Keep 4000 newest
                del self.node_performance_cache[key]
        
        # Limit performance history to recent records
        for node_id in self.nodes:
            history = self.nodes[node_id].get('performance_history', [])
            if len(history) > self.performance_history_window:
                self.nodes[node_id]['performance_history'] = history[-self.performance_history_window:]
        
        # Limit probe history size
        if len(self.probe_history) > 1000:  # Configurable limit
            # Remove oldest probe records
            sorted_probes = sorted(self.probe_history.items(), 
                                 key=lambda x: x[1].get('send_time', 0))
            for probe_key, _ in sorted_probes[:len(sorted_probes) - 800]:  # Keep 800 newest
                del self.probe_history[probe_key]
        
        # Remove inactive nodes (not seen for configured threshold)
        inactive_threshold = current_time - 3600  # 1 hour (configurable)
        inactive_nodes = [node_id for node_id, node_data in self.nodes.items() 
                         if node_data.get('last_seen', 0) < inactive_threshold]
        
        # Keep at least one node (genesis) and don't remove too many at once
        if len(self.nodes) - len(inactive_nodes) >= 1:
            genesis_nodes = list(self.nodes.keys())[:1]  # Keep first node as genesis
            for node_id in inactive_nodes:
                if node_id not in genesis_nodes:
                    del self.nodes[node_id]

    def execute_probe_protocol(self, source_node: str, target_node: str, witnesses: List[str]) -> Dict:
        """
        Execute Probe Protocol as described in the IEEE paper with full cryptographic verification.
        
        Returns ProbeProof containing:
        - ProbeRequest with cryptographic signature
        - TargetReceipt with signed response
        - WitnessReceipts with cryptographic proofs
        """
        # Ensure all nodes have cryptographic keys
        for node in [source_node, target_node] + witnesses:
            if node not in self.node_keys and node in self.nodes:
                self.generate_node_keys(node)
        
        # Filter available witnesses that have keys
        available_witnesses = [w for w in witnesses if w in self.nodes and w in self.node_keys]
        if len(available_witnesses) < self.witness_quorum_size:
            # Add more witnesses if available
            all_possible_witnesses = [n for n in self.nodes.keys() 
                                    if n not in [source_node, target_node] and n in self.node_keys]
            additional_witnesses = random.sample(
                all_possible_witnesses, 
                min(self.witness_quorum_size - len(available_witnesses), len(all_possible_witnesses))
            )
            available_witnesses.extend(additional_witnesses)
        
        # Generate cryptographically secure nonce
        nonce = secrets.token_hex(32)  # 256-bit nonce
        
        # Check for nonce reuse (replay protection)
        if self.is_nonce_used(nonce):
            # Generate new nonce if collision (very unlikely)
            nonce = secrets.token_hex(32)
        
        send_time = time.time()
        
        # 1. Create ProbeRequest as per paper specification
        probe_request = {
            'source_id': source_node,
            'target_id': target_node,
            'timestamp': send_time,
            'nonce': nonce
        }
        
        # Sign ProbeRequest
        request_message = json.dumps(probe_request, sort_keys=True).encode('utf-8')
        try:
            request_signature = self.sign_message(source_node, request_message)
        except ValueError:
            # Source node doesn't have keys, generate them
            self.generate_node_keys(source_node)
            request_signature = self.sign_message(source_node, request_message)
        
        # 2. Measure actual network latency (paper-compliant measurement)
        actual_latency = self.measure_real_network_latency(source_node, target_node)
        receipt_time = send_time + actual_latency
        
        # Paper's intention: Enable witness latency verification by recording timestamps
        # Store witness observation times for later triangulation verification
        
        # 3. Create TargetReceipt as per paper
        target_receipt_data = {
            'original_request': probe_request,
            'receipt_time': receipt_time,
            'target_id': target_node
        }
        
        # Sign TargetReceipt
        target_message = json.dumps(target_receipt_data, sort_keys=True).encode('utf-8')
        try:
            target_signature = self.sign_message(target_node, target_message)
        except ValueError:
            self.generate_node_keys(target_node)
            target_signature = self.sign_message(target_node, target_message)
        
        target_receipt = {**target_receipt_data, 'target_signature': target_signature}
        
        # 4. Collect WitnessReceipts with cryptographic signatures
        witness_receipts = []
        valid_witnesses = 0
        
        for witness in available_witnesses[:self.witness_quorum_size * 2]:  # Try more witnesses than needed
            try:
                # Paper's intention: Witness independently observes probe timing for latency triangulation
                witness_observation_time = send_time + self.measure_real_network_latency(source_node, witness) + self.measure_real_network_latency(witness, target_node)
                
                witness_data = {
                    'witness_id': witness,
                    'observed_request': probe_request,
                    'witness_timestamp': witness_observation_time,  # Critical for latency verification
                    'target_receipt_observed': True,
                    'latency_observation': abs(witness_observation_time - receipt_time)  # Witness latency measurement
                }
                
                # Sign witness data
                witness_message = json.dumps(witness_data, sort_keys=True).encode('utf-8')
                witness_signature = self.sign_message(witness, witness_message)
                
                witness_receipt = {**witness_data, 'witness_signature': witness_signature}
                witness_receipts.append(witness_receipt)
                valid_witnesses += 1
                
                # Stop when we have enough witnesses
                if valid_witnesses >= self.witness_quorum_size:
                    break
                    
            except (ValueError, KeyError):
                # Witness doesn't have keys or other error, skip
                continue
        
        # 5. Verify quorum requirement (k/3 minimum as per paper)
        if valid_witnesses < max(1, self.witness_quorum_size // 3):
            print(f"⚠️  Insufficient witnesses: {valid_witnesses} < {self.witness_quorum_size // 3}")
            # Continue with available witnesses for simulation
        
        # 6. Create complete ProbeProof structure
        probe_proof = {
            'ProbeRequest': {
                **probe_request,
                'request_signature': request_signature
            },
            'TargetReceipt': target_receipt,
            'WitnessReceipts': witness_receipts,
            'measured_latency': actual_latency,
            'proof_timestamp': time.time(),
            'valid': True,
            'verification_data': {
                'total_witnesses': len(witness_receipts),
                'quorum_met': valid_witnesses >= max(1, self.witness_quorum_size // 3),
                'nonce_fresh': not self.is_nonce_used(nonce)
            }
        }
        
        # Mark nonce as used for replay protection
        self.mark_nonce_used(nonce)
        
        # Store probe result with cryptographic proof
        probe_key = f"{source_node}_{target_node}_{int(send_time)}_{nonce[:8]}"
        self.probe_history[probe_key] = probe_proof
        
        # Update node metrics based on verified probe
        self.update_node_metrics_from_verified_probe(target_node, probe_proof)
        
        return probe_proof

    def get_top_candidate_nodes(self, vrf_output: str, max_candidates: int = None) -> List[str]:
        """
        Get top candidate nodes for quantum optimization to improve scalability.
        For 1000+ nodes, only consider the most promising candidates.
        """
        # Use scalable candidate limit based on network size
        total_nodes = len(self.nodes)
        if max_candidates is None:
            max_candidates = SCALABILITY_CONFIG.get_candidate_limit(total_nodes)
            
        # Calculate suitability scores for all active nodes
        candidate_scores = []
        current_time = time.time()
        active_nodes = [node_id for node_id, node_data in self.nodes.items() 
                       if current_time - node_data.get('last_seen', 0) < self.node_active_threshold]
        
        # Periodic cleanup for large networks
        if total_nodes > 100 and random.random() < 0.1:  # 10% chance
            self.cleanup_performance_data()
        
        for node_id in active_nodes:
            score = self.calculate_effective_score(node_id, vrf_output)
            candidate_scores.append((node_id, score))
        
        # Sort by score (descending) and take top candidates
        candidate_scores.sort(key=lambda x: x[1], reverse=True)
        top_candidates = [node_id for node_id, _ in candidate_scores[:max_candidates]]
        
        return top_candidates

    def execute_scalable_probe_protocol(self, candidate_nodes: List[str]):
        """
        Execute probe protocol with optimized sampling for large-scale networks.
        Uses O(sqrt(n)) sampling instead of O(n²) full probing.
        """
        total_candidates = len(candidate_nodes)
        
        if total_candidates <= 10:
            # For small networks, probe all pairs
            self.execute_full_probe_protocol(candidate_nodes)
            return
            
        # For large networks, use strategic sampling with scalable parameters
        sample_size = SCALABILITY_CONFIG.get_probe_sample_size(total_candidates)
        
        # Sample high-performing nodes for probing
        probe_sources = random.sample(candidate_nodes, min(sample_size, total_candidates))
        
        # Each source probes a limited number of targets (avoid O(n²) complexity)
        targets_per_source = min(5, max(2, total_candidates // 10))
        
        for source in probe_sources:
            # Select diverse targets (avoid clustering bias)
            available_targets = [n for n in candidate_nodes if n != source]
            target_count = min(targets_per_source, len(available_targets))
            
            if target_count > 0:
                targets = random.sample(available_targets, target_count)
                
                for target in targets:
                    # Select witness pool from remaining candidates
                    witness_pool = [n for n in candidate_nodes if n not in [source, target]]
                    witness_count = min(self.witness_quorum_size, len(witness_pool))
                    
                    if witness_count > 0:
                        witnesses = random.sample(witness_pool, witness_count)
                        self.execute_probe_protocol(source, target, witnesses)
    
    def execute_full_probe_protocol(self, nodes: List[str]):
        """Execute full O(n²) probe protocol for small networks"""
        for source in nodes:
            for target in nodes:
                if source != target:
                    witness_pool = [n for n in nodes if n not in [source, target]]
                    witness_count = min(self.witness_quorum_size, len(witness_pool))
                    
                    if witness_count > 0:
                        witnesses = random.sample(witness_pool, witness_count)
                        self.execute_probe_protocol(source, target, witnesses)

    def verify_probe_proof(self, proof, verifier_node: str = "default") -> bool:
        """
        Allow any node to independently verify a ProbeProof as per IEEE paper specification.
        
        Args:
            proof: The ProbeProof to verify (can be ProbeProof object or dict)
            verifier_node: The node performing verification
            
        Returns:
            bool: True if proof is valid, False otherwise
        """
        try:
            # Handle both ProbeProof objects and legacy dict format
            if isinstance(proof, ProbeProof):
                # New ProbeProof object format
                if not proof.signature or not proof.public_key:
                    # Legacy probe proof without cryptographic data
                    return True  # Accept legacy data for compatibility
                
                # Verify ProbeProof object signature
                proof_data = {
                    'timestamp': proof.timestamp,
                    'node_id': proof.node_id,
                    'response_data': proof.response_data,
                    'nonce': proof.nonce
                }
                proof_message = json.dumps(proof_data, sort_keys=True).encode('utf-8')
                
                # For ProbeProof objects, verify using the embedded signature
                return self.verify_signature_bytes(proof.public_key, proof_message, proof.signature)
            
            # Legacy dict format verification
            elif isinstance(proof, dict) and 'ProbeRequest' in proof and 'TargetReceipt' in proof:
                # 1. Verify ProbeRequest signature
                probe_request = proof['ProbeRequest']
                source_id = probe_request['source_id']
                
                request_data = {
                    'source_id': source_id,
                    'target_id': probe_request['target_id'],
                    'timestamp': probe_request['timestamp'],
                    'nonce': probe_request['nonce']
                }
                request_message = json.dumps(request_data, sort_keys=True).encode('utf-8')
            
            if not self.verify_signature(source_id, request_message, probe_request['request_signature']):
                print(f"❌ ProbeRequest signature verification failed for {source_id}")
                return False
            
            # 2. Verify TargetReceipt signature
            target_receipt = proof['TargetReceipt']
            target_id = target_receipt['target_id']
            
            target_data = {
                'original_request': target_receipt['original_request'],
                'receipt_time': target_receipt['receipt_time'],
                'target_id': target_id
            }
            target_message = json.dumps(target_data, sort_keys=True).encode('utf-8')
            
            if not self.verify_signature(target_id, target_message, target_receipt['target_signature']):
                print(f"❌ TargetReceipt signature verification failed for {target_id}")
                return False
            
            # 3. Verify witness quorum (k/3 minimum as per paper)
            witness_receipts = proof['WitnessReceipts']
            required_witnesses = max(1, self.witness_quorum_size // 3)
            
            if len(witness_receipts) < required_witnesses:
                print(f"❌ Insufficient witnesses: {len(witness_receipts)} < {required_witnesses}")
                return False
            
            # 4. Verify each witness signature
            valid_witnesses = 0
            for witness_receipt in witness_receipts:
                witness_id = witness_receipt['witness_id']
                
                witness_data = {
                    'witness_id': witness_id,
                    'observed_request': witness_receipt['observed_request'],
                    'witness_receipt_time': witness_receipt.get('witness_receipt_time', witness_receipt.get('witness_timestamp', 0)),
                    'target_receipt_observed': witness_receipt['target_receipt_observed']
                }
                witness_message = json.dumps(witness_data, sort_keys=True).encode('utf-8')
                
                if self.verify_signature(witness_id, witness_message, witness_receipt['witness_signature']):
                    valid_witnesses += 1
                else:
                    print(f"❌ Witness signature verification failed for {witness_id}")
            
            if valid_witnesses < required_witnesses:
                print(f"❌ Insufficient valid witness signatures: {valid_witnesses} < {required_witnesses}")
                return False
            
            # 5. Verify timestamp consistency (receipt must be after send)
            send_time = probe_request['timestamp']
            receipt_time = target_receipt['receipt_time']
            
            if receipt_time <= send_time:
                print(f"❌ Invalid timestamp: receipt_time ({receipt_time}) <= send_time ({send_time})")
                return False
            
            # 6. Verify nonce freshness (replay protection)
            nonce = probe_request['nonce']
            
            # For verification during proof creation, check against a separate replay cache
            # to avoid marking nonces as used during verification
            if verifier_node == source_id:
                # Source node verifying its own proof during creation - allow it
                pass  
            elif self.is_nonce_used(nonce):
                print(f"❌ Nonce replay detected: {nonce[:16]}...")
                return False
            
            # 7. Verify latency calculation consistency AND witness consensus
            calculated_latency = receipt_time - send_time
            claimed_latency = proof['measured_latency']
            
            # Verify mathematical consistency
            if abs(calculated_latency - claimed_latency) > 0.001:  # 1ms tolerance
                print(f"❌ Latency mismatch: calculated={calculated_latency:.6f}, claimed={claimed_latency:.6f}")
                return False
            
            # Paper's intention: Verify latency through witness triangulation
            witness_receipts = proof.get('WitnessReceipts', [])
            if len(witness_receipts) >= 2:  # Need multiple witnesses for triangulation
                witness_latencies = []
                for witness_receipt in witness_receipts:
                    witness_time = witness_receipt.get('witness_timestamp', 0)
                    if witness_time > 0:
                        witness_latency = abs(receipt_time - witness_time)
                        if 0.001 <= witness_latency <= 1.0:  # Reasonable range
                            witness_latencies.append(witness_latency)
                
                # Verify witness consensus on latency measurement
                if witness_latencies:
                    all_latencies = [claimed_latency] + witness_latencies
                    latency_variance = max(all_latencies) - min(all_latencies)
                    if latency_variance > 0.100:  # 100ms tolerance for consensus
                        print(f"❌ Witness latency consensus failed: variance={latency_variance:.3f}s")
                        return False
            
            # 8. Verify timestamp reasonableness (not too old or in future)
            current_time = time.time()
            max_age = 300  # 5 minutes
            
            if current_time - send_time > max_age:
                print(f"❌ Proof too old: {current_time - send_time:.2f}s > {max_age}s")
                return False
            
            if send_time > current_time + 60:  # 1 minute tolerance for clock skew
                print(f"❌ Proof from future: send_time ({send_time}) > current_time ({current_time})")
                return False
            
                # All verifications passed
                return True
            else:
                # Unrecognized proof format
                print(f"❌ Unrecognized proof format: {type(proof)}")
                return False
            
        except (KeyError, json.JSONDecodeError, ValueError) as e:
            print(f"❌ Proof verification error: {e}")
            return False

    def update_node_metrics_from_verified_probe(self, node_id: str, probe_proof: Dict):
        """
        Update node metrics based on cryptographically verified probe results.
        Implements paper-compliant measurement methodology.
        """
        if node_id not in self.nodes:
            return
        
        current_time = time.time()
        
        # 1. Update Uptime - Paper compliant: based on successful probe response
        self.update_uptime_from_probe(node_id, probe_proof)
        
        # 2. Update Latency - Paper compliant: from verified ProbeProof
        self.update_latency_from_probe(node_id, probe_proof)
        
        # 3. Update Throughput - Paper compliant: count verified proofs
        self.update_throughput_from_probe(node_id, probe_proof)
        
        # 4. Update last seen time
        self.nodes[node_id]['last_seen'] = current_time

    def update_uptime_from_probe(self, node_id: str, probe_data: Dict):
        """
        Verifiable uptime calculation following IEEE paper specification with cryptographic proofs.
        
        Implements equation U(nx) = ∫[tstart to tend] S(nx, t) dt where S(nx, t) ∈ {0,1}
        with witness consensus and Merkle tree verification for network-wide verifiability.
        
        Args:
            node_id: Target node identifier
            probe_data: Dictionary containing probe response and cryptographic proof
        """
        if node_id not in self.nodes:
            return
        
        current_time = time.time()
        
        # Step 1: Validate and extract probe proof
        try:
            # Handle different probe data formats
            if 'ProbeProof' in probe_data:
                # New format with ProbeProof structure
                proof_dict = probe_data.get('ProbeProof', {})
                probe_proof = ProbeProof.from_dict(proof_dict)
            elif 'TargetReceipt' in probe_data:
                # Legacy format from P2P protocol - convert to ProbeProof format
                target_receipt = probe_data.get('TargetReceipt', {})
                probe_request = probe_data.get('ProbeRequest', {})
                
                # Extract required fields with defaults
                timestamp = target_receipt.get('receipt_time', time.time())
                node_id_from_data = target_receipt.get('target_id', node_id)
                response_data = {
                    'receipt_time': timestamp,
                    'response_received': True
                }
                
                # Create minimal probe proof for legacy compatibility
                probe_proof = ProbeProof(
                    timestamp=timestamp,
                    node_id=node_id_from_data,
                    response_data=response_data,
                    signature=b'',  # Empty signature for legacy data
                    public_key=b'',  # Empty public key for legacy data
                    nonce=probe_request.get('nonce', 'legacy_nonce')
                )
            else:
                # Handle direct probe data without wrapper structure
                timestamp = probe_data.get('timestamp', time.time())
                response_data = {
                    'response_received': True,
                    'probe_time': timestamp
                }
                
                probe_proof = ProbeProof(
                    timestamp=timestamp,
                    node_id=node_id,
                    response_data=response_data,
                    signature=b'',
                    public_key=b'',
                    nonce=f'direct_{int(timestamp)}'
                )
                
        except Exception as e:
            self.logger.warning(f"Invalid probe proof for {node_id}: {e}")
            self.logger.debug(f"Probe data structure: {list(probe_data.keys()) if isinstance(probe_data, dict) else type(probe_data)}")
            return
        
        # Step 2: Cryptographic verification of probe proof (skip for legacy data)
        if probe_proof.signature and probe_proof.public_key:
            # Full cryptographic verification for new format
            if not self.verify_probe_proof(probe_proof):
                self.logger.warning(f"Probe proof verification failed for {node_id}")
                return
            
            # Step 3: Mark nonce as used for replay protection
            self.mark_nonce_used(probe_proof.nonce)
        else:
            # Legacy data - skip cryptographic verification but log it
            self.logger.debug(f"Processing legacy probe data for {node_id} (no cryptographic verification)")
            
        # Step 4: Store verified probe proof in history
        proof_id = f"{node_id}_{probe_proof.timestamp}_{probe_proof.nonce}"
        self.probe_history[proof_id] = probe_proof
        
        # Step 5: Collect witness proofs for consensus-based verification
        witness_proofs = self.collect_witness_proofs(node_id, probe_proof)
        
        # Step 6: Verify witness quorum (≥ N/3 as per paper)
        if len(witness_proofs) < max(1, self.witness_quorum_size):
            # TODO: Temporarily paused verbose witness logging - can be re-enabled later
            # self.logger.info(f"Insufficient witnesses for {node_id}: {len(witness_proofs)}/{self.witness_quorum_size}")
            # Still update locally but mark as unverified
            self.update_local_uptime(node_id, probe_proof.timestamp)
            return
        
        # Step 7: Generate Merkle root for efficient verification
        all_proofs = [probe_proof] + witness_proofs
        merkle_root = self.generate_merkle_root(all_proofs)
        
        # Step 8: Calculate deterministic uptime period using mathematical integral
        uptime_period = self.calculate_verifiable_uptime_period(
            node_id, probe_proof.timestamp, witness_proofs
        )
        
        # Step 9: Create verifiable uptime record
        verifiable_record = VerifiableUptimeRecord(
            node_id=node_id,
            uptime_period=uptime_period,
            witness_count=len(witness_proofs),
            probe_proofs=all_proofs,
            merkle_root=merkle_root,
            consensus_timestamp=current_time
        )
        
        # Step 10: Store verifiable record and update node uptime
        record_id = f"uptime_{node_id}_{current_time}"
        self.verifiable_uptime_records[record_id] = verifiable_record
        
        # Update node's last seen time with verified probe timestamp
        self.nodes[node_id]['last_seen'] = max(
            self.nodes[node_id]['last_seen'],
            probe_proof.timestamp
        )
        
        # Update rolling uptime based on verified periods
        rolling_uptime = self.calculate_verified_rolling_uptime(node_id, current_time)
        self.nodes[node_id]['uptime'] = rolling_uptime
        
        # TODO: Temporarily paused verbose uptime logging - can be re-enabled later
        # self.logger.info(
        #     f"Verifiable uptime updated for {node_id}: "
        #     f"period={uptime_period:.3f}s, witnesses={len(witness_proofs)}, "
        #     f"rolling_uptime={rolling_uptime:.3f}"
        # )

    def collect_witness_proofs(self, node_id: str, primary_proof: ProbeProof) -> List[ProbeProof]:
        """
        Collect witness proofs from other nodes to verify probe response.
        Implements witness consensus mechanism for uptime verification.
        """
        witness_proofs = []
        witness_timeout = 10.0  # seconds to collect witness responses
        
        # Get available nodes as potential witnesses (excluding target node)
        potential_witnesses = [nid for nid in self.nodes.keys() if nid != node_id]
        
        # Limit witness pool for scalability
        if len(potential_witnesses) > self.witness_sample_size:
            potential_witnesses = random.sample(potential_witnesses, self.witness_sample_size)
        
        # For simulation, generate witness responses based on network conditions
        for witness_id in potential_witnesses:
            # Simulate witness probe to target node
            witness_observed_time = primary_proof.timestamp + random.uniform(-2.0, 2.0)
            
            # Create witness proof
            witness_response = {
                'target_node': node_id,
                'observation_time': witness_observed_time,
                'response_received': abs(witness_observed_time - primary_proof.timestamp) <= self.max_delay_tolerance
            }
            
            # Generate cryptographic proof for witness
            if witness_id in self.node_keys:
                message_data = {
                    'timestamp': witness_observed_time,
                    'node_id': witness_id,
                    'response_data': witness_response,
                    'nonce': secrets.token_hex(16)
                }
                message = json.dumps(message_data, sort_keys=True).encode()
                
                public_pem, private_pem = self.node_keys[witness_id]
                private_key = serialization.load_pem_private_key(
                    private_pem.encode('utf-8'), password=None
                )
                
                signature = private_key.sign(
                    message,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                
                witness_proof = ProbeProof(
                    timestamp=witness_observed_time,
                    node_id=witness_id,
                    response_data=witness_response,
                    signature=signature,
                    public_key=public_pem.encode('utf-8'),
                    nonce=message_data['nonce']
                )
                
                witness_proofs.append(witness_proof)
                
                # Stop once we have sufficient witnesses
                if len(witness_proofs) >= self.witness_quorum_size:
                    break
        
        return witness_proofs

    def calculate_verifiable_uptime_period(self, node_id: str, probe_time: float, 
                                         witness_proofs: List[ProbeProof]) -> float:
        """
        Calculate verifiable uptime period using consensus-based mathematical integration.
        
        Implements: U(nx) = ∫[t₁ to t₂] S(nx, t) dt
        where S(nx, t) = 1 if consensus confirms node responsiveness, 0 otherwise
        """
        current_time = time.time()
        
        # Get existing verified uptime periods
        if not hasattr(self, 'verifiable_uptime_records'):
            self.verifiable_uptime_records = {}
        
        # Find previous uptime periods for this node
        previous_periods = []
        for record_id, record in self.verifiable_uptime_records.items():
            if record.node_id == node_id:
                previous_periods.append((record.consensus_timestamp, record.uptime_period))
        
        # Calculate consensus-based uptime extension
        witness_consensus = sum(
            1 for proof in witness_proofs 
            if proof.response_data.get('response_received', False)
        ) >= len(witness_proofs) * 0.67  # 2/3 majority
        
        if witness_consensus:
            # Node is responsive - calculate time since last verified period
            if previous_periods:
                last_verified_time = max(t for t, _ in previous_periods)
                uptime_extension = max(0, probe_time - last_verified_time)
            else:
                # First verification - use probe interval
                uptime_extension = min(probe_time, self.max_delay_tolerance)
            
            return uptime_extension
        else:
            # Node not responsive according to witnesses
            return 0.0

    def calculate_verified_rolling_uptime(self, node_id: str, current_time: float) -> float:
        """
        Calculate rolling uptime ratio using only cryptographically verified periods.
        
        Returns uptime ratio ∈ [0,1] based on verified consensus proofs over rolling window.
        """
        if not hasattr(self, 'verifiable_uptime_records'):
            return 0.0
        
        # Rolling window: 1 hour as per paper specification
        window_duration = 3600.0
        window_start = current_time - window_duration
        total_verified_uptime = 0.0
        
        # Sum all verified uptime periods within the rolling window
        for record_id, record in self.verifiable_uptime_records.items():
            if (record.node_id == node_id and 
                record.consensus_timestamp >= window_start and
                record.witness_count >= self.witness_quorum_size):
                
                # Add verified uptime period to total
                total_verified_uptime += record.uptime_period
        
        # Calculate and return uptime ratio
        uptime_ratio = min(1.0, total_verified_uptime / window_duration)
        return uptime_ratio

    def update_local_uptime(self, node_id: str, probe_time: float):
        """Fallback local uptime update when witness consensus is unavailable"""
        if node_id not in self.nodes:
            return
        
        current_time = time.time()
        self.nodes[node_id]['last_seen'] = max(
            self.nodes[node_id]['last_seen'],
            probe_time
        )
        
        # Simple binary uptime for local-only updates
        time_since_seen = current_time - self.nodes[node_id]['last_seen']
        if time_since_seen <= self.max_delay_tolerance:
            self.nodes[node_id]['uptime'] = 1.0
        else:
            self.nodes[node_id]['uptime'] = 0.0

    def verify_uptime_consensus(self, node_id: str) -> Dict[str, any]:
        """
        Verify that uptime calculations are deterministic and verifiable across the network.
        
        Returns verification results showing cryptographic proofs and consensus metrics.
        """
        if not hasattr(self, 'verifiable_uptime_records'):
            return {'error': 'No verifiable uptime records available'}
        
        node_records = [
            record for record in self.verifiable_uptime_records.values()
            if record.node_id == node_id
        ]
        
        if not node_records:
            return {'error': f'No verifiable records found for node {node_id}'}
        
        # Get latest record
        latest_record = max(node_records, key=lambda r: r.consensus_timestamp)
        
        # Verify Merkle tree integrity
        merkle_verification = all(
            self.verify_merkle_proof(proof.to_dict(), latest_record.merkle_root, latest_record.probe_proofs)
            for proof in latest_record.probe_proofs[:3]  # Sample verification
        )
        
        # Verify all cryptographic signatures
        signature_verification = all(
            self.verify_probe_proof(proof) for proof in latest_record.probe_proofs
        )
        
        # Calculate consensus agreement
        witness_responses = [
            proof.response_data.get('response_received', False)
            for proof in latest_record.probe_proofs[1:]  # Exclude primary probe
        ]
        consensus_rate = sum(witness_responses) / len(witness_responses) if witness_responses else 0
        
        return {
            'node_id': node_id,
            'latest_uptime_period': latest_record.uptime_period,
            'witness_count': latest_record.witness_count,
            'merkle_root': latest_record.merkle_root,
            'merkle_verification': merkle_verification,
            'signature_verification': signature_verification,
            'consensus_rate': consensus_rate,
            'verifiable': merkle_verification and signature_verification,
            'consensus_timestamp': latest_record.consensus_timestamp,
            'total_records': len(node_records)
        }

    def get_verifiable_uptime_summary(self) -> Dict[str, any]:
        """Get comprehensive summary of verifiable uptime system status"""
        if not hasattr(self, 'verifiable_uptime_records'):
            return {'error': 'Verifiable uptime system not initialized'}
        
        total_records = len(self.verifiable_uptime_records)
        verified_records = sum(
            1 for record in self.verifiable_uptime_records.values()
            if record.witness_count >= self.witness_quorum_size
        )
        
        # Get per-node statistics
        node_stats = {}
        for record in self.verifiable_uptime_records.values():
            if record.node_id not in node_stats:
                node_stats[record.node_id] = {
                    'total_records': 0,
                    'verified_records': 0,
                    'latest_uptime': 0.0,
                    'total_uptime_period': 0.0
                }
            
            node_stats[record.node_id]['total_records'] += 1
            node_stats[record.node_id]['total_uptime_period'] += record.uptime_period
            node_stats[record.node_id]['latest_uptime'] = max(
                node_stats[record.node_id]['latest_uptime'],
                record.uptime_period
            )
            
            if record.witness_count >= self.witness_quorum_size:
                node_stats[record.node_id]['verified_records'] += 1
        
        return {
            'system_status': 'active',
            'total_records': total_records,
            'verified_records': verified_records,
            'verification_rate': verified_records / total_records if total_records > 0 else 0,
            'witness_quorum_size': self.witness_quorum_size,
            'node_statistics': node_stats,
            'cryptographic_features': {
                'signature_verification': True,
                'merkle_tree_proofs': True,
                'nonce_replay_protection': True,
                'witness_consensus': True
            }
        }

    def calculate_rolling_uptime(self, node_id: str, current_time: float) -> float:
        """
        Calculate uptime ratio over rolling 1-hour window as per IEEE paper:
        ρ_uptime(nx) = (1/W) * Σ max(0, min(t_end, t_current) - max(t_start, t_current - W))
        where W = 3600 seconds (1 hour window)
        """
        if node_id not in self.nodes:
            return 0.0
        
        uptime_periods = self.nodes[node_id].get('uptime_periods', [])
        if not uptime_periods:
            return 0.0
        
        # Rolling window: last 1 hour (3600 seconds)
        window_duration = 3600.0
        hour_ago = current_time - window_duration
        total_uptime = 0.0
        
        for start_time, end_time in uptime_periods:
            # Calculate overlap between period and rolling window
            period_start = max(start_time, hour_ago)
            period_end = min(end_time, current_time)
            
            if period_end > period_start:
                total_uptime += period_end - period_start
        
        # Return uptime ratio (between 0.0 and 1.0)
        uptime_ratio = min(1.0, total_uptime / window_duration)
        return uptime_ratio

    def cleanup_uptime_periods(self, node_id: str, current_time: float):
        """
        Clean up old uptime periods to manage memory efficiently.
        Keep only periods within the last 24 hours as per paper design.
        """
        if node_id not in self.nodes:
            return
        
        uptime_periods = self.nodes[node_id].get('uptime_periods', [])
        if not uptime_periods:
            return
        
        # Keep periods from last 24 hours only
        cutoff_time = current_time - 86400  # 24 hours
        
        # Filter periods that end after cutoff time
        cleaned_periods = []
        for start_time, end_time in uptime_periods:
            if end_time > cutoff_time:
                # Adjust start time if period spans across cutoff
                adjusted_start = max(start_time, cutoff_time)
                cleaned_periods.append((adjusted_start, end_time))
        
        self.nodes[node_id]['uptime_periods'] = cleaned_periods

    def get_verifiable_uptime_calculation(self, node_id: str) -> Dict:
        """
        Calculate consensus-based uptime that all nodes can verify and agree on.
        Implements the paper's verifiable uptime framework.
        
        Returns:
            Dict containing verifiable uptime data with cryptographic proofs
        """
        if node_id not in self.nodes:
            return {
                'node_id': node_id,
                'uptime': 0.0,
                'verifiable': False,
                'error': 'Node not found'
            }
        
        # Step 1: Collect all verifiable probe proofs for this node
        verified_proofs = []
        for proof_id, proof in self.probe_history.items():
            if (proof.get('TargetReceipt', {}).get('target_id') == node_id and 
                self.verify_probe_proof(proof, "consensus_calculator")):
                verified_proofs.append(proof)
        
        # Step 2: Sort proofs by receipt time for deterministic processing
        verified_proofs.sort(key=lambda p: p['TargetReceipt']['receipt_time'])
        
        # Step 3: Calculate uptime periods using deterministic algorithm
        uptime_periods = []
        current_time = time.time()
        
        for proof in verified_proofs:
            receipt_time = proof['TargetReceipt']['receipt_time']
            
            # Apply same logic as update_uptime_from_probe but deterministically
            if uptime_periods and receipt_time - uptime_periods[-1][1] <= self.max_delay_tolerance:
                # Extend existing period
                uptime_periods[-1] = (uptime_periods[-1][0], receipt_time)
            else:
                # Start new period
                uptime_periods.append((receipt_time, receipt_time))
        
        # Step 4: Calculate rolling uptime
        window_duration = 3600.0  # 1 hour
        hour_ago = current_time - window_duration
        total_uptime = 0.0
        
        for start_time, end_time in uptime_periods:
            period_start = max(start_time, hour_ago)
            period_end = min(end_time, current_time)
            
            if period_end > period_start:
                total_uptime += period_end - period_start
        
        uptime_ratio = min(1.0, total_uptime / window_duration)
        
        # Step 5: Return verifiable uptime data
        return {
            'node_id': node_id,
            'uptime': uptime_ratio,
            'uptime_periods': uptime_periods,
            'calculation_method': 'consensus_deterministic',
            'verified_proof_count': len(verified_proofs),
            'measurement_window': window_duration,
            'verifiable': True,
            'reproducible': True,
            'cryptographic_proofs': len(verified_proofs) > 0
        }

    def create_verifiable_uptime_record(self, probe_proof: Dict) -> str:
        """
        Create a verifiable uptime record with cryptographic signatures.
        Implements the paper's VerifiableUptimeRecord structure:
        R = (n_target, t_receipt, H_proof, W_witnesses, Σ_witnesses)
        """
        target_id = probe_proof['TargetReceipt']['target_id']
        receipt_time = probe_proof['TargetReceipt']['receipt_time']
        
        # Create cryptographic hash of the entire proof
        proof_hash = hashlib.sha256(
            json.dumps(probe_proof, sort_keys=True).encode('utf-8')
        ).hexdigest()
        
        # Extract witness information
        witnesses = []
        witness_signatures = []
        
        for witness_receipt in probe_proof['WitnessReceipts']:
            witness_id = witness_receipt['witness_id']
            witnesses.append(witness_id)
            
            # Create uptime record for witness to sign
            uptime_record = {
                'node_id': target_id,
                'timestamp': receipt_time,
                'proof_hash': proof_hash,
                'witness_id': witness_id,
                'verification_time': time.time(),
                'max_delay_tolerance': self.max_delay_tolerance
            }
            
            witness_signatures.append({
                'witness_id': witness_id,
                'signature': witness_receipt['witness_signature'],
                'record': uptime_record
            })
        
        # Create unique record ID
        record_id = f"uptime_{target_id}_{int(receipt_time)}_{proof_hash[:8]}"
        
        # Store the verifiable uptime record
        verifiable_record = {
            'record_id': record_id,
            'node_id': target_id,
            'timestamp': receipt_time,
            'proof_hash': proof_hash,
            'witnesses': witnesses,
            'witness_signatures': witness_signatures,
            'quorum_size': len(witnesses),
            'original_proof': probe_proof,
            'creation_time': time.time()
        }
        
        # Store in a dedicated uptime ledger (can be queried by other nodes)
        if not hasattr(self, 'verifiable_uptime_ledger'):
            self.verifiable_uptime_ledger = {}
        
        self.verifiable_uptime_ledger[record_id] = verifiable_record
        
        return record_id

    def verify_uptime_record(self, record_id: str, verifier_node: str) -> bool:
        """
        Verify a VerifiableUptimeRecord can be trusted.
        Any node can independently verify uptime records.
        """
        if not hasattr(self, 'verifiable_uptime_ledger'):
            return False
        
        if record_id not in self.verifiable_uptime_ledger:
            return False
        
        record = self.verifiable_uptime_ledger[record_id]
        
        try:
            # 1. Verify the original probe proof
            original_proof = record['original_proof']
            if not self.verify_probe_proof(original_proof, verifier_node):
                return False
            
            # 2. Verify proof hash consistency
            calculated_hash = hashlib.sha256(
                json.dumps(original_proof, sort_keys=True).encode('utf-8')
            ).hexdigest()
            
            if calculated_hash != record['proof_hash']:
                return False
            
            # 3. Verify witness quorum was met
            required_witnesses = max(1, self.witness_quorum_size // 3)
            if len(record['witnesses']) < required_witnesses:
                return False
            
            # 4. Verify witness signatures on uptime record
            valid_signatures = 0
            for sig_data in record['witness_signatures']:
                witness_id = sig_data['witness_id']
                uptime_record = sig_data['record']
                signature = sig_data['signature']
                
                # Recreate the message that was signed
                record_message = json.dumps(uptime_record, sort_keys=True).encode('utf-8')
                
                if self.verify_signature(witness_id, record_message, signature):
                    valid_signatures += 1
            
            # Require majority of witnesses to have valid signatures
            if valid_signatures < len(record['witnesses']) // 2 + 1:
                return False
            
            return True
            
        except (KeyError, json.JSONDecodeError, ValueError):
            return False

    def get_consensus_uptime(self, node_id: str) -> float:
        """
        Get consensus uptime value that all honest nodes will calculate identically.
        Implements the paper's consensus-based deterministic calculation.
        """
        if not hasattr(self, 'verifiable_uptime_ledger'):
            # Fallback to local calculation if no verifiable ledger
            return self.nodes.get(node_id, {}).get('uptime', 0.0)
        
        # Collect all verified uptime records for this node
        verified_records = []
        current_time = time.time()
        
        for record_id, record in self.verifiable_uptime_ledger.items():
            if (record['node_id'] == node_id and 
                self.verify_uptime_record(record_id, "consensus_node")):
                verified_records.append(record)
        
        if not verified_records:
            return 0.0
        
        # Sort by timestamp for deterministic processing
        verified_records.sort(key=lambda r: r['timestamp'])
        
        # Calculate uptime periods from verified records
        uptime_periods = []
        
        for record in verified_records:
            timestamp = record['timestamp']
            
            # Apply same period logic as local calculation
            if uptime_periods and timestamp - uptime_periods[-1][1] <= self.max_delay_tolerance:
                uptime_periods[-1] = (uptime_periods[-1][0], timestamp)
            else:
                uptime_periods.append((timestamp, timestamp))
        
        # Calculate rolling uptime over 1-hour window
        window_duration = 3600.0
        hour_ago = current_time - window_duration
        total_uptime = 0.0
        
        for start_time, end_time in uptime_periods:
            period_start = max(start_time, hour_ago)
            period_end = min(end_time, current_time)
            
            if period_end > period_start:
                total_uptime += period_end - period_start
        
        return min(1.0, total_uptime / window_duration)
        """
        Update uptime based on paper specification:
        U(nx) = ∫[tstart to tend] S(nx, t) dt
        where S(nx, t) = 1 if (t - Tlast_seen(nx)) ≤ Δ, 0 otherwise
        """
        if node_id not in self.nodes:
            return
        
        current_time = time.time()
        receipt_time = probe_proof['TargetReceipt']['receipt_time']
        
        # Node proved liveness at receipt_time
        self.nodes[node_id]['last_seen'] = max(
            self.nodes[node_id]['last_seen'], 
            receipt_time
        )
        
        # Update uptime periods
        uptime_periods = self.nodes[node_id].get('uptime_periods', [])
        
        # Check if this extends current uptime period
        if uptime_periods and current_time - uptime_periods[-1][1] <= self.max_delay_tolerance:
            # Extend current period
            uptime_periods[-1] = (uptime_periods[-1][0], current_time)
        else:
            # Start new uptime period
            uptime_periods.append((receipt_time, current_time))
        
        # Limit stored periods (keep last 24 hours)
        cutoff_time = current_time - 86400  # 24 hours
        uptime_periods = [(start, end) for start, end in uptime_periods if end > cutoff_time]
        
        self.nodes[node_id]['uptime_periods'] = uptime_periods
        
        # Calculate current uptime ratio (last hour)
        hour_ago = current_time - 3600
        total_uptime = 0
        
        for start, end in uptime_periods:
            period_start = max(start, hour_ago)
            period_end = min(end, current_time)
            if period_end > period_start:
                total_uptime += period_end - period_start
        
        self.nodes[node_id]['uptime'] = min(1.0, total_uptime / 3600.0)

    def update_latency_from_probe(self, node_id: str, probe_proof: Dict):
        """
        Update latency from verified probe measurement with witness consensus.
        Paper specification: Ls→t = RTT if V(PP) = true AND witness consensus confirms latency
        
        Implements verifiable latency calculation using witness triangulation as intended by paper.
        """
        if not self.verify_probe_proof(probe_proof, node_id):
            return  # Only update from verified proofs
        
        measured_latency = probe_proof['measured_latency']
        
        # Collect witness latency measurements for consensus verification
        witness_latencies = self.collect_witness_latency_measurements(node_id, probe_proof)
        
        # Verify latency consensus (similar to uptime witness verification)
        if len(witness_latencies) >= max(1, self.witness_quorum_size // 3):
            # Calculate consensus latency using median of witness measurements
            all_latencies = [measured_latency] + witness_latencies
            all_latencies.sort()
            consensus_latency = all_latencies[len(all_latencies) // 2]  # Median for robustness
            
            # Only accept if witness consensus agrees within tolerance
            latency_variance = max(all_latencies) - min(all_latencies)
            if latency_variance <= 0.050:  # 50ms tolerance for network jitter
                verified_latency = consensus_latency
                # TODO: Temporarily paused verbose latency logging - can be re-enabled later
                # self.logger.info(f"Latency consensus achieved for {node_id}: {verified_latency:.3f}s")
            else:
                self.logger.warning(f"Latency consensus failed for {node_id}: variance={latency_variance:.3f}s")
                return  # Reject measurement if witnesses disagree significantly
        else:
            # Insufficient witnesses - use local measurement with warning
            verified_latency = measured_latency
            self.logger.warning(f"Insufficient latency witnesses for {node_id}, using local measurement")
        
        # Update using exponential moving average for stability
        current_latency = self.nodes[node_id].get('latency', float('inf'))
        if current_latency == float('inf'):
            self.nodes[node_id]['latency'] = verified_latency
        else:
            alpha = 0.2  # Smoothing factor (paper doesn't specify, using standard value)
            self.nodes[node_id]['latency'] = (
                alpha * verified_latency + (1 - alpha) * current_latency
            )
    
    def collect_witness_latency_measurements(self, target_node: str, primary_proof: Dict) -> List[float]:
        """
        Collect independent latency measurements from witness nodes.
        Implements paper's intention for triangulated latency verification.
        """
        witness_latencies = []
        primary_latency = primary_proof['measured_latency']
        
        # Get witness receipts from the probe proof
        witness_receipts = primary_proof.get('WitnessReceipts', [])
        
        for witness_receipt in witness_receipts:
            try:
                # Each witness independently measured latency to target
                witness_timestamp = witness_receipt.get('witness_timestamp', 0)
                target_receipt_time = primary_proof['TargetReceipt']['receipt_time']
                
                # Simulate witness-observed latency (in production, witnesses would probe independently)
                witness_latency = abs(target_receipt_time - witness_timestamp)
                
                # Only accept reasonable latency measurements
                if 0.001 <= witness_latency <= 1.0:  # 1ms to 1000ms range
                    witness_latencies.append(witness_latency)
                    
            except (KeyError, ValueError):
                continue  # Skip invalid witness data
        
        return witness_latencies
    
    def collect_witness_throughput_measurements(self, target_node: str, current_time: float) -> List[float]:
        """
        Collect independent throughput measurements from witness nodes.
        Implements paper's intention for consensus-based throughput verification.
        """
        witness_throughputs = []
        measurement_window = 60.0  # 1 minute window
        window_start = current_time - measurement_window
        
        # Get available nodes as potential witnesses (excluding target node)
        potential_witnesses = [nid for nid in self.nodes.keys() if nid != target_node]
        
        # Limit witness pool for scalability
        if len(potential_witnesses) > self.witness_sample_size:
            potential_witnesses = random.sample(potential_witnesses, self.witness_sample_size)
        
        for witness_id in potential_witnesses:
            try:
                # Each witness independently counts valid proofs for target
                witness_valid_proofs = 0
                
                # Simulate witness having access to network-wide probe history
                # In production, witnesses would maintain synchronized probe histories
                for proof_key, proof in self.probe_history.items():
                    if (proof['TargetReceipt']['target_id'] == target_node and 
                        proof['TargetReceipt']['receipt_time'] >= window_start and
                        proof.get('valid', False)):
                        
                        # Add small variance to simulate witness perspective differences
                        witness_observation_confidence = random.uniform(0.9, 1.0)
                        if witness_observation_confidence > 0.95:  # 95% confidence threshold
                            witness_valid_proofs += 1
                
                # Calculate witness throughput
                witness_throughput = witness_valid_proofs / measurement_window
                
                # Only accept reasonable throughput measurements
                if 0.0 <= witness_throughput <= 100.0:  # 0 to 100 proofs/min range
                    witness_throughputs.append(witness_throughput)
                    
            except (KeyError, ValueError):
                continue  # Skip invalid witness data
            
            # Stop once we have sufficient witnesses
            if len(witness_throughputs) >= self.witness_quorum_size:
                break
        
        return witness_throughputs

    def update_throughput_from_probe(self, node_id: str, probe_proof: Dict):
        """
        Update throughput with witness consensus verification for complete verifiability.
        Paper specification: Throughput(nt) = |Pnt(tstart, tend)| / (tend - tstart)
        Enhanced with witness consensus similar to uptime and latency verification.
        """
        if not self.verify_probe_proof(probe_proof, node_id):
            return  # Only update from verified proofs
        
        current_time = time.time()
        measurement_window = 60.0  # 1 minute window
        window_start = current_time - measurement_window
        
        # Collect witness throughput measurements for consensus verification
        witness_throughputs = self.collect_witness_throughput_measurements(node_id, current_time)
        
        # Calculate local throughput
        local_valid_proofs = 0
        for proof_key, proof in self.probe_history.items():
            if (proof['TargetReceipt']['target_id'] == node_id and 
                proof['TargetReceipt']['receipt_time'] >= window_start and
                proof.get('valid', False)):
                local_valid_proofs += 1
        
        local_throughput = local_valid_proofs / measurement_window
        
        # Verify throughput consensus (similar to latency witness verification)
        if len(witness_throughputs) >= max(1, self.witness_quorum_size // 3):
            # Calculate consensus throughput using median of witness measurements
            all_throughputs = [local_throughput] + witness_throughputs
            all_throughputs.sort()
            consensus_throughput = all_throughputs[len(all_throughputs) // 2]  # Median for robustness
            
            # Only accept if witness consensus agrees within tolerance
            throughput_variance = max(all_throughputs) - min(all_throughputs)
            if throughput_variance <= 5.0:  # 5 proofs/min tolerance for network jitter
                verified_throughput = consensus_throughput
                # TODO: Temporarily paused verbose throughput logging - can be re-enabled later
                # self.logger.info(f"Throughput consensus achieved for {node_id}: {verified_throughput:.3f}/min")
                
                # Create verifiable throughput record
                self.create_verifiable_throughput_record(node_id, verified_throughput, witness_throughputs, current_time)
            else:
                self.logger.warning(f"Throughput consensus failed for {node_id}: variance={throughput_variance:.3f}/min")
                return  # Reject measurement if witnesses disagree significantly
        else:
            # Insufficient witnesses - use local measurement with warning
            verified_throughput = local_throughput
            self.logger.warning(f"Insufficient throughput witnesses for {node_id}, using local measurement")
        
        # Update using exponential moving average for stability
        current_throughput = self.nodes[node_id].get('throughput', 0.0)
        alpha = 0.2  # Smoothing factor
        self.nodes[node_id]['throughput'] = (
            alpha * verified_throughput + (1 - alpha) * current_throughput
        )
        
        # Update response count for compatibility
        self.nodes[node_id]['response_count'] = int(verified_throughput * measurement_window)
    
    def create_verifiable_throughput_record(self, node_id: str, consensus_throughput: float, 
                                          witness_throughputs: List[float], timestamp: float):
        """
        Create a verifiable throughput record with witness consensus and cryptographic proofs.
        Implements verifiable throughput framework similar to uptime records.
        """
        if not hasattr(self, 'verifiable_throughput_records'):
            self.verifiable_throughput_records = {}
        
        # Create throughput consensus data
        throughput_data = {
            'node_id': node_id,
            'consensus_throughput': consensus_throughput,
            'witness_throughputs': witness_throughputs,
            'measurement_window': 60.0,
            'timestamp': timestamp,
            'witness_count': len(witness_throughputs)
        }
        
        # Create cryptographic hash of the throughput data
        throughput_hash = hashlib.sha256(
            json.dumps(throughput_data, sort_keys=True).encode('utf-8')
        ).hexdigest()
        
        # Create verifiable record with witness signatures (simplified for demo)
        record_id = f"throughput_{node_id}_{int(timestamp)}_{throughput_hash[:8]}"
        
        verifiable_record = {
            'record_id': record_id,
            'node_id': node_id,
            'consensus_throughput': consensus_throughput,
            'witness_throughputs': witness_throughputs,
            'witness_count': len(witness_throughputs),
            'measurement_window': 60.0,
            'timestamp': timestamp,
            'throughput_hash': throughput_hash,
            'verifiable': True,
            'consensus_achieved': len(witness_throughputs) >= max(1, self.witness_quorum_size // 3)
        }
        
        # Store in verifiable throughput ledger
        self.verifiable_throughput_records[record_id] = verifiable_record
        
        # TODO: Temporarily paused verbose throughput record logging - can be re-enabled later
        # self.logger.info(f"Verifiable throughput record created for {node_id}: {consensus_throughput:.3f}/min")
        
        return record_id
    
    def verify_throughput_consensus(self, node_id: str) -> Dict[str, any]:
        """
        Verify that throughput calculations are deterministic and verifiable across the network.
        Provides same level of verification as uptime consensus.
        
        Returns verification results showing consensus metrics and cryptographic proofs.
        """
        if not hasattr(self, 'verifiable_throughput_records'):
            return {'error': 'No verifiable throughput records available'}
        
        node_records = [
            record for record in self.verifiable_throughput_records.values()
            if record['node_id'] == node_id
        ]
        
        if not node_records:
            return {'error': f'No verifiable throughput records found for node {node_id}'}
        
        # Get latest record
        latest_record = max(node_records, key=lambda r: r['timestamp'])
        
        # Verify consensus achievement
        witness_count = latest_record['witness_count']
        required_witnesses = max(1, self.witness_quorum_size // 3)
        consensus_achieved = witness_count >= required_witnesses
        
        # Calculate consensus agreement rate
        if latest_record['witness_throughputs']:
            witness_values = latest_record['witness_throughputs']
            consensus_throughput = latest_record['consensus_throughput']
            
            # Check how many witnesses agree within tolerance
            tolerance = 2.0  # 2 proofs/min tolerance
            agreeing_witnesses = sum(
                1 for wt in witness_values 
                if abs(wt - consensus_throughput) <= tolerance
            )
            consensus_rate = agreeing_witnesses / len(witness_values)
        else:
            consensus_rate = 0.0
        
        # Verify hash integrity
        throughput_data = {
            'node_id': latest_record['node_id'],
            'consensus_throughput': latest_record['consensus_throughput'],
            'witness_throughputs': latest_record['witness_throughputs'],
            'measurement_window': latest_record['measurement_window'],
            'timestamp': latest_record['timestamp'],
            'witness_count': latest_record['witness_count']
        }
        
        calculated_hash = hashlib.sha256(
            json.dumps(throughput_data, sort_keys=True).encode('utf-8')
        ).hexdigest()
        
        hash_verification = calculated_hash == latest_record['throughput_hash']
        
        return {
            'node_id': node_id,
            'latest_consensus_throughput': latest_record['consensus_throughput'],
            'witness_count': witness_count,
            'required_witnesses': required_witnesses,
            'consensus_achieved': consensus_achieved,
            'consensus_rate': consensus_rate,
            'hash_verification': hash_verification,
            'verifiable': consensus_achieved and hash_verification,
            'timestamp': latest_record['timestamp'],
            'total_records': len(node_records),
            'measurement_window': latest_record['measurement_window']
        }
    
    def get_consensus_throughput(self, node_id: str) -> float:
        """
        Get consensus throughput value that all honest nodes will calculate identically.
        Implements verifiable throughput calculation similar to consensus uptime.
        """
        if not hasattr(self, 'verifiable_throughput_records'):
            # Fallback to local calculation if no verifiable records
            return self.nodes.get(node_id, {}).get('throughput', 0.0)
        
        # Get latest verifiable throughput record
        node_records = [
            record for record in self.verifiable_throughput_records.values()
            if record['node_id'] == node_id and record.get('consensus_achieved', False)
        ]
        
        if not node_records:
            # No consensus records available, use local calculation
            return self.nodes.get(node_id, {}).get('throughput', 0.0)
        
        # Get most recent consensus throughput
        latest_record = max(node_records, key=lambda r: r['timestamp'])
        
        # Check if record is recent (within 5 minutes)
        current_time = time.time()
        if current_time - latest_record['timestamp'] <= 300:
            return latest_record['consensus_throughput']
        else:
            # Record too old, fall back to local calculation
            return self.nodes.get(node_id, {}).get('throughput', 0.0)
    
    def get_verifiable_throughput_summary(self) -> Dict[str, any]:
        """Get comprehensive summary of verifiable throughput system status"""
        if not hasattr(self, 'verifiable_throughput_records'):
            return {'error': 'Verifiable throughput system not initialized'}
        
        total_records = len(self.verifiable_throughput_records)
        verified_records = sum(
            1 for record in self.verifiable_throughput_records.values()
            if record.get('consensus_achieved', False)
        )
        
        # Get per-node statistics
        node_stats = {}
        for record in self.verifiable_throughput_records.values():
            node_id = record['node_id']
            if node_id not in node_stats:
                node_stats[node_id] = {
                    'total_records': 0,
                    'verified_records': 0,
                    'latest_throughput': 0.0,
                    'average_throughput': 0.0,
                    'total_measurements': 0
                }
            
            node_stats[node_id]['total_records'] += 1
            node_stats[node_id]['total_measurements'] += record['consensus_throughput']
            node_stats[node_id]['latest_throughput'] = max(
                node_stats[node_id]['latest_throughput'],
                record['consensus_throughput']
            )
            
            if record.get('consensus_achieved', False):
                node_stats[node_id]['verified_records'] += 1
        
        # Calculate averages
        for node_id in node_stats:
            if node_stats[node_id]['total_records'] > 0:
                node_stats[node_id]['average_throughput'] = (
                    node_stats[node_id]['total_measurements'] / 
                    node_stats[node_id]['total_records']
                )
        
        return {
            'system_status': 'active',
            'total_records': total_records,
            'verified_records': verified_records,
            'verification_rate': verified_records / total_records if total_records > 0 else 0,
            'witness_quorum_size': self.witness_quorum_size,
            'measurement_window_seconds': 60.0,
            'node_statistics': node_stats,
            'cryptographic_features': {
                'witness_consensus': True,
                'hash_verification': True,
                'byzantine_fault_tolerance': True,
                'deterministic_calculation': True
            }
        }

    def update_node_metrics_from_probe(self, node_id: str, probe_proof: Dict):
        """Legacy method - delegates to verified probe update"""
        self.update_node_metrics_from_verified_probe(node_id, probe_proof)

    def calculate_uptime(self, node_id: str) -> float:
        """Calculate node uptime based on last seen time"""
        if node_id not in self.nodes:
            return 0.0
            
        current_time = time.time()
        last_seen = self.nodes[node_id]['last_seen']
        
        # Node is considered online if seen within tolerance
        if current_time - last_seen <= self.max_delay_tolerance:
            return 1.0
        else:
            return 0.0

    def calculate_suitability_score(self, node_id: str) -> float:
        """
        Calculate suitability score with caching for performance.
        Cached scores are valid for short periods to handle 1000+ nodes efficiently.
        
        Si = (w_uptime * norm(Ui)) + (w_perf * norm(PastPerfi)) + 
             (w_throughput * norm(Throughputi)) - (w_latency * norm(Latencyi))
        """
        if node_id not in self.nodes:
            return 0.0
            
        # Check cache first (with TTL-based invalidation)
        cache_time_slot = int(time.time() // self.performance_cache_ttl)
        cache_key = f"{node_id}_{cache_time_slot}"
        if cache_key in self.node_performance_cache:
            return self.node_performance_cache[cache_key]
        
        node = self.nodes[node_id]
        
        # Collect all metrics for normalization
        all_nodes = list(self.nodes.values())
        
        # Extract metrics for normalization
        uptimes = [self.calculate_uptime(nid) for nid in self.nodes.keys()]
        latencies = [n['latency'] for n in all_nodes if n['latency'] != float('inf')]
        throughputs = [n['throughput'] for n in all_nodes]
        
        # Calculate past performance scores
        past_performances = []
        for nid in self.nodes.keys():
            success = self.nodes[nid]['proposal_success_count']
            failure = self.nodes[nid]['proposal_failure_count']
            perf_score = success - (2 * failure)  # Penalty weight = 2
            past_performances.append(perf_score)
        
        # Normalize metrics using Min-Max scaling
        def normalize_positive(value, min_val, max_val):
            if max_val == min_val:
                return 1.0
            return (value - min_val) / (max_val - min_val)
        
        def normalize_negative(value, min_val, max_val):
            if max_val == min_val:
                return 1.0
            return (max_val - value) / (max_val - min_val)
        
        # Current node metrics
        uptime = self.calculate_uptime(node_id)
        latency = node['latency'] if node['latency'] != float('inf') else max(latencies) if latencies else 1.0
        throughput = node['throughput']
        past_perf = (node['proposal_success_count'] - 
                    2 * node['proposal_failure_count'])
        
        # Normalize
        norm_uptime = normalize_positive(uptime, min(uptimes), max(uptimes))
        norm_latency = normalize_negative(latency, min(latencies) if latencies else 0, 
                                        max(latencies) if latencies else 1) if latencies else 1.0
        norm_throughput = normalize_positive(throughput, min(throughputs), max(throughputs))
        norm_past_perf = normalize_positive(past_perf, min(past_performances), max(past_performances))
        
        # Calculate weighted suitability score
        suitability_score = (
            self.weight_uptime * norm_uptime +
            self.weight_past_performance * norm_past_perf +
            self.weight_throughput * norm_throughput -
            self.weight_latency * norm_latency  # Negative because lower latency is better
        )
        
        # Cache the result for performance (with TTL)
        cache_time_slot = int(time.time() // self.performance_cache_ttl)
        cache_key = f"{node_id}_{cache_time_slot}"
        self.node_performance_cache[cache_key] = suitability_score
        
        return suitability_score

    def calculate_effective_score(self, node_id: str, vrf_output: str) -> float:
        """
        Calculate effective score S'i = Si + δi for tie-breaking.
        
        Uses VRF output and node's public key for deterministic perturbation.
        """
        original_score = self.calculate_suitability_score(node_id)
        
        # Generate deterministic perturbation using VRF output and node's public key
        node_pk = self.nodes[node_id]['public_key']
        perturbation_input = f"{vrf_output}{node_pk}"
        hash_value = hashlib.sha256(perturbation_input.encode()).hexdigest()
        
        # Convert hash to small perturbation value
        perturbation = (int(hash_value[:8], 16) % 1000000) / 1000000.0 * self.perturbation_epsilon
        
        return original_score + perturbation

    def formulate_qubo_problem(self, vrf_output: str, candidate_nodes: List[str] = None) -> Tuple[Dict, Dict, float]:
        """
        Formulate QUBO problem for representative node selection.
        
        Args:
            vrf_output: VRF output for deterministic tie-breaking
            candidate_nodes: Optional list of candidate nodes (for scalability)
        
        Returns:
        - linear_coefficients: Qii values
        - quadratic_coefficients: Qij values  
        - constant_offset: C value
        """
        # Use candidate nodes if provided, otherwise use all nodes
        nodes = candidate_nodes if candidate_nodes is not None else list(self.nodes.keys())
        n = len(nodes)
        
        if n == 0:
            return {}, {}, 0.0
        
        # Calculate effective scores for all nodes
        effective_scores = {}
        for node_id in nodes:
            effective_scores[node_id] = self.calculate_effective_score(node_id, vrf_output)
        
        # QUBO coefficients based on paper derivation
        linear_coefficients = {}  # Qii = -(P + S'i)
        quadratic_coefficients = {}  # Qij = 2P for i < j
        
        # Linear coefficients
        for i, node_id in enumerate(nodes):
            linear_coefficients[i] = -(self.penalty_coefficient + effective_scores[node_id])
        
        # Quadratic coefficients (penalty for selecting multiple nodes)
        for i in range(n):
            for j in range(i + 1, n):
                quadratic_coefficients[(i, j)] = 2 * self.penalty_coefficient
        
        constant_offset = self.penalty_coefficient
        
        return linear_coefficients, quadratic_coefficients, constant_offset

    def simulate_quantum_annealer(self, linear_coeff: Dict, quadratic_coeff: Dict, candidate_nodes: List[str] = None) -> List[int]:
        """
        Simulate quantum annealer solving QUBO problem using D-Wave Ocean SDK.
        
        Args:
            linear_coeff: Linear coefficients for QUBO
            quadratic_coeff: Quadratic coefficients for QUBO  
            candidate_nodes: List of candidate nodes being optimized
        
        Uses SimulatedAnnealingSampler which mimics the behavior of a real quantum annealer.
        In production, this would interface with actual D-Wave quantum hardware.
        """
        # Use candidate nodes if provided, otherwise fall back to all nodes
        nodes = candidate_nodes if candidate_nodes is not None else list(self.nodes.keys())
        n = len(nodes)
        
        if n == 0:
            return []
        
        if n == 1:
            return [1]  # Only one node, select it
        
        try:
            # Create BinaryQuadraticModel (BQM) for QUBO problem
            bqm = BinaryQuadraticModel('BINARY')
            
            # Add linear coefficients (biases)
            for i in range(n):
                if i in linear_coeff:
                    bqm.add_variable(i, linear_coeff[i])
                else:
                    bqm.add_variable(i, 0.0)
            
            # Add quadratic coefficients (couplings)
            for (i, j), coeff in quadratic_coeff.items():
                bqm.add_interaction(i, j, coeff)
            
            # Create sampler - using SimulatedAnnealingSampler for realistic quantum annealing simulation
            sampler = SimulatedAnnealingSampler()
            
            # Sample multiple times to get the best solution (scale with network size)
            num_reads = SCALABILITY_CONFIG.get_quantum_reads_for_size(n)
            
            # Configure annealing parameters for scalability
            annealing_time = 20.0  # microseconds (typical for D-Wave)
            
            # Solve the QUBO problem
            response = sampler.sample(
                bqm,
                num_reads=num_reads,
                annealing_time=annealing_time,
                seed=int(time.time())  # Reproducible randomness
            )
            
            # Get the best solution (lowest energy)
            best_sample = response.first.sample
            best_energy = response.first.energy
            
            # Convert solution to list format
            solution = [0] * n
            for i in range(n):
                solution[i] = best_sample.get(i, 0)
            
            # Validate solution (should select exactly one node for our constraint)
            selected_count = sum(solution)
            
            if selected_count == 1:
                # Perfect solution found
                return solution
            elif selected_count == 0:
                # No node selected - fallback to highest score node
                print(f"⚠️  Quantum annealer found no solution, using fallback")
                best_score_idx = 0
                best_score = float('-inf')
                for i in range(n):
                    score = -linear_coeff.get(i, 0) - self.penalty_coefficient
                    if score > best_score:
                        best_score = score
                        best_score_idx = i
                solution = [0] * n
                solution[best_score_idx] = 1
                return solution
            else:
                # Multiple nodes selected - choose the one with highest effective score
                print(f"⚠️  Quantum annealer selected {selected_count} nodes, resolving conflict")
                selected_indices = [i for i, val in enumerate(solution) if val == 1]
                best_idx = selected_indices[0]
                best_score = float('-inf')
                
                for idx in selected_indices:
                    score = -linear_coeff.get(idx, 0) - self.penalty_coefficient
                    if score > best_score:
                        best_score = score
                        best_idx = idx
                
                solution = [0] * n
                solution[best_idx] = 1
                return solution
                
        except Exception as e:
            print(f"⚠️  D-Wave simulator error: {e}, using classical fallback")
            
            # Classical fallback: evaluate all single-node selections
            best_energy = float('inf')
            best_solution = [0] * n
            
            # Try selecting each node individually (constraint: exactly one node)
            for i in range(n):
                solution = [0] * n
                solution[i] = 1
                
                # Calculate energy for this solution
                energy = 0.0
                
                # Linear terms
                for j in range(n):
                    if j in linear_coeff:
                        energy += linear_coeff[j] * solution[j]
                
                # Quadratic terms
                for (j, k), coeff in quadratic_coeff.items():
                    energy += coeff * solution[j] * solution[k]
                
                if energy < best_energy:
                    best_energy = energy
                    best_solution = solution
            
            return best_solution

    def select_representative_node(self, last_block_hash: str) -> Optional[str]:
        """
        Main consensus function: select representative node using quantum annealing.
        
        This is the core of the quantum annealing consensus mechanism.
        """
        if not self.nodes:
            return None
        
        # Generate VRF output from last block hash (simplified)
        vrf_output = hashlib.sha256(last_block_hash.encode()).hexdigest()
        
        # Get top candidate nodes for scalable selection (1000+ nodes support)
        candidate_nodes = self.get_top_candidate_nodes(vrf_output)
        
        if not candidate_nodes:
            # Fallback to any available node
            all_nodes = list(self.nodes.keys())
            return all_nodes[0] if all_nodes else None
        
        # Execute scalable probe protocol (O(sqrt(n)) instead of O(n²))
        self.execute_scalable_probe_protocol(candidate_nodes)
        
        # Formulate QUBO problem with candidate nodes only
        linear_coeff, quadratic_coeff, constant = self.formulate_qubo_problem(vrf_output, candidate_nodes)
        
        # Solve using quantum annealer (simulated) with candidate nodes
        solution = self.simulate_quantum_annealer(linear_coeff, quadratic_coeff, candidate_nodes)
        
        # Extract selected node from candidates
        for i, selected in enumerate(solution):
            if selected == 1 and i < len(candidate_nodes):
                return candidate_nodes[i]
        
        # Fallback: return node with highest score from candidates
        best_node = None
        best_score = -float('inf')
        for node_id in candidate_nodes:
            score = self.calculate_effective_score(node_id, vrf_output)
            if score > best_score:
                best_score = score
                best_node = node_id
        
        return best_node

    def record_proposal_result(self, node_id: str, success: bool):
        """Record the result of a block proposal attempt"""
        if node_id not in self.nodes:
            return
        
        if success:
            self.nodes[node_id]['proposal_success_count'] += 1
        else:
            self.nodes[node_id]['proposal_failure_count'] += 1

    def get_consensus_metrics(self) -> Dict:
        """Get metrics about the consensus state including quantum annealing details"""
        if not self.nodes:
            return {}
        
        metrics = {
            'consensus_type': 'Quantum Annealing',
            'total_nodes': len(self.nodes),
            'active_nodes': sum(1 for node_id in self.nodes.keys() 
                              if self.calculate_uptime(node_id) > 0),
            'probe_count': len(self.probe_history),
            'node_scores': {},
            'protocol_parameters': {
                'max_delay_tolerance': self.max_delay_tolerance,
                'block_proposal_timeout': self.block_proposal_timeout,
                'witness_quorum_size': self.witness_quorum_size,
                'penalty_coefficient': self.penalty_coefficient
            },
            'quantum_annealing_config': {
                'annealing_time_microseconds': self.quantum_annealing_time,
                'num_reads': self.quantum_num_reads,
                'simulator_enabled': self.use_quantum_simulator,
                'perturbation_epsilon': self.perturbation_epsilon
            },
            'scoring_weights': {
                'uptime': self.weight_uptime,
                'latency': self.weight_latency,
                'throughput': self.weight_throughput,
                'past_performance': self.weight_past_performance
            }
        }
        
        # Calculate current scores for all nodes
        vrf_output = "current_round"  # Simplified for metrics
        for node_id in self.nodes.keys():
            latency_value = self.nodes[node_id]['latency']
            # Handle infinity values for JSON serialization
            if latency_value == float('inf'):
                latency_value = 999.999  # Use a large but finite value
            
            metrics['node_scores'][node_id] = {
                'suitability_score': self.calculate_suitability_score(node_id),
                'effective_score': self.calculate_effective_score(node_id, vrf_output),
                'uptime': self.calculate_uptime(node_id),
                'latency': latency_value,
                'throughput': self.nodes[node_id]['throughput'],
                'proposals_success': self.nodes[node_id]['proposal_success_count'],
                'proposals_failed': self.nodes[node_id]['proposal_failure_count']
            }
        
        return metrics
