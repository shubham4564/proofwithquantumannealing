import os
import sys
import random
import string
import time

# Add the parent directory to Python path to find blockchain modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from blockchain.quantum_consensus.quantum_annealing_consensus import QuantumAnnealingConsensus


def get_random_string(length):
    letters = string.ascii_lowercase
    result_string = "".join(random.choice(letters) for i in range(length))
    return result_string


def test_quantum_annealing_consensus():
    """Test basic functionality of quantum annealing consensus"""
    consensus = QuantumAnnealingConsensus(initialize_genesis=False)
    
    # Register nodes
    consensus.register_node("alice", "alice_public_key")
    consensus.register_node("bob", "bob_public_key")
    consensus.register_node("charlie", "charlie_public_key")

    assert "alice" in consensus.nodes
    assert "bob" in consensus.nodes
    assert "charlie" in consensus.nodes
    assert consensus.nodes["alice"]["public_key"] == "alice_public_key"


def test_representative_node_selection():
    """Test quantum annealing representative node selection"""
    consensus = QuantumAnnealingConsensus(initialize_genesis=False)
    
    # Register nodes
    consensus.register_node("alice", "alice_public_key")
    consensus.register_node("bob", "bob_public_key")
    
    # Simulate some probe activity to establish metrics
    for i in range(10):
        consensus.execute_probe_protocol("alice", "bob", ["alice"])
        consensus.execute_probe_protocol("bob", "alice", ["bob"])
    
    # Test representative selection
    last_block_hash = get_random_string(32)
    selected_node = consensus.select_representative_node(last_block_hash)
    
    assert selected_node in ["alice", "bob"]


def test_suitability_score_calculation():
    """Test suitability score calculation"""
    consensus = QuantumAnnealingConsensus(initialize_genesis=False)
    
    # Register nodes with different performance characteristics
    consensus.register_node("alice", "alice_public_key")
    consensus.register_node("bob", "bob_public_key")
    
    # Simulate good performance for alice
    consensus.nodes["alice"]["proposal_success_count"] = 10
    consensus.nodes["alice"]["proposal_failure_count"] = 1
    consensus.nodes["alice"]["latency"] = 0.05
    consensus.nodes["alice"]["throughput"] = 100.0
    
    # Simulate poor performance for bob
    consensus.nodes["bob"]["proposal_success_count"] = 2
    consensus.nodes["bob"]["proposal_failure_count"] = 5
    consensus.nodes["bob"]["latency"] = 0.5
    consensus.nodes["bob"]["throughput"] = 10.0
    
    alice_score = consensus.calculate_suitability_score("alice")
    bob_score = consensus.calculate_suitability_score("bob")
    
    # Alice should have a better score
    assert alice_score > bob_score


def test_probe_protocol():
    """Test probe protocol execution"""
    consensus = QuantumAnnealingConsensus(initialize_genesis=False)
    
    # Register nodes
    consensus.register_node("source", "source_key")
    consensus.register_node("target", "target_key")
    consensus.register_node("witness1", "witness1_key")
    consensus.register_node("witness2", "witness2_key")
    
    # Execute probe protocol
    witnesses = ["witness1", "witness2"]
    probe_proof = consensus.execute_probe_protocol("source", "target", witnesses)
    
    assert probe_proof is not None
    assert probe_proof["source_node"] == "source"
    assert probe_proof["target_node"] == "target"
    assert probe_proof["valid"] == True


def test_single_node_scenario():
    """Test behavior with single node"""
    consensus = QuantumAnnealingConsensus(initialize_genesis=False)
    consensus.register_node("alice", "alice_key")
    
    # Single node should always be selected
    last_block_hash = get_random_string(32)
    selected = consensus.select_representative_node(last_block_hash)
    assert selected == "alice"


def test_consensus_determinism():
    """Test that the same seed produces consistent behavior"""
    consensus = QuantumAnnealingConsensus(initialize_genesis=False)
    consensus.register_node("alice", "alice_key")
    consensus.register_node("bob", "bob_key")
    
    # Execute some probes to establish metrics
    consensus.execute_probe_protocol("alice", "bob", ["alice"])
    consensus.execute_probe_protocol("bob", "alice", ["bob"])
    
    # With same input, selection should be deterministic
    last_block_hash = "consistent_hash"
    selection1 = consensus.select_representative_node(last_block_hash)
    selection2 = consensus.select_representative_node(last_block_hash)
    
    # Should get same result with same input
    assert selection1 == selection2


def test_qubo_optimization():
    """Test QUBO optimization and quantum annealing simulation"""
    consensus = QuantumAnnealingConsensus(initialize_genesis=False)
    consensus.register_node("high_performer", "hp_key")
    consensus.register_node("low_performer", "lp_key")
    
    # Set up different performance levels
    consensus.nodes["high_performer"]["proposal_success_count"] = 20
    consensus.nodes["high_performer"]["proposal_failure_count"] = 1
    consensus.nodes["low_performer"]["proposal_success_count"] = 5
    consensus.nodes["low_performer"]["proposal_failure_count"] = 10
    
    # Test multiple selections to see if better performer is chosen more often
    high_performer_wins = 0
    total_rounds = 50
    
    for i in range(total_rounds):
        last_block_hash = get_random_string(32) + str(i)
        selected = consensus.select_representative_node(last_block_hash)
        if selected == "high_performer":
            high_performer_wins += 1
    
    # High performer should be selected more often (at least 60% due to better metrics)
    assert high_performer_wins > total_rounds * 0.6  # At least 60% of the time
    # Test should pass even if high performer wins all the time (deterministic based on metrics)
