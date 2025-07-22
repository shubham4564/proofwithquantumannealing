#!/usr/bin/env python3
"""
Comparison script between traditional PoS and Quantum Annealing Consensus
This script demonstrates the differences in validator selection behavior.
"""

import sys
import os

# Add parent directory to path for blockchain module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import string
from collections import defaultdict
from datetime import datetime

# Mock traditional PoS for comparison (since we removed the original)
class MockProofOfStake:
    """Simple mock PoS implementation for comparison purposes"""
    def __init__(self):
        self.stakes = {}
    
    def update(self, validator_id: str, stake: int):
        self.stakes[validator_id] = stake
    
    def forger(self, last_block_hash: str) -> str:
        """Select validator based on stake weight"""
        if not self.stakes:
            return None
        
        total_stake = sum(self.stakes.values())
        if total_stake == 0:
            return random.choice(list(self.stakes.keys()))
        
        # Weighted random selection based on stake
        rand_value = random.randint(1, total_stake)
        current_weight = 0
        
        for validator, stake in self.stakes.items():
            current_weight += stake
            if rand_value <= current_weight:
                return validator
        
        return list(self.stakes.keys())[-1]  # Fallback

from blockchain.quantum_consensus.quantum_annealing_consensus import QuantumAnnealingConsensus


def get_random_string(length=10):
    """Generate random string for testing"""
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def run_comparison():
    """Run comparison between traditional PoS and Quantum Annealing PoS"""
    
    print("=" * 60)
    print("PROOF OF STAKE COMPARISON")
    print("Traditional PoS vs Quantum Annealing PoS")
    print("=" * 60)
    
    # Setup both systems with same initial conditions
    traditional_pos = MockProofOfStake()
    quantum_pos = QuantumAnnealingConsensus()
    
    # Add validators with different stake amounts
    validators = [
        ("Alice", 100),    # Large staker
        ("Bob", 50),       # Medium staker  
        ("Charlie", 25),   # Small staker
        ("Diana", 10),     # Very small staker
    ]
    
    for name, stake in validators:
        traditional_pos.update(name, stake)
        quantum_pos.update(name, stake)
    
    print(f"Initial Setup:")
    for name, stake in validators:
        percentage = (stake / sum([s for _, s in validators])) * 100
        print(f"  {name}: {stake} tokens ({percentage:.1f}%)")
    print()
    
    # Run selection rounds
    rounds = 1000
    traditional_results = defaultdict(int)
    quantum_results = defaultdict(int)
    
    print(f"Running {rounds} validator selection rounds...")
    print()
    
    for i in range(rounds):
        seed = get_random_string()
        
        # Traditional PoS selection
        traditional_forger = traditional_pos.forger(seed)
        traditional_results[traditional_forger] += 1
        
        # Quantum Annealing PoS selection
        quantum_forger = quantum_pos.forger(seed)
        quantum_results[quantum_forger] += 1
    
    # Display results
    print("RESULTS:")
    print("-" * 40)
    print(f"{'Validator':<10} {'Traditional PoS':<15} {'Quantum PoS':<15} {'Difference':<12}")
    print("-" * 40)
    
    for name, stake in validators:
        traditional_count = traditional_results.get(name, 0)
        quantum_count = quantum_results.get(name, 0)
        difference = quantum_count - traditional_count
        
        traditional_pct = (traditional_count / rounds) * 100
        quantum_pct = (quantum_count / rounds) * 100
        
        print(f"{name:<10} {traditional_count:>4} ({traditional_pct:>5.1f}%) "
              f"{quantum_count:>6} ({quantum_pct:>5.1f}%) {difference:>+4}")
    
    print("-" * 40)
    print()
    
    # Analysis
    print("ANALYSIS:")
    print("-" * 40)
    
    # Calculate Gini coefficient for fairness analysis
    def gini_coefficient(results):
        """Calculate Gini coefficient for distribution fairness"""
        values = list(results.values())
        if not values:
            return 0
        
        values.sort()
        n = len(values)
        cumsum = sum((i + 1) * val for i, val in enumerate(values))
        return (2 * cumsum) / (n * sum(values)) - (n + 1) / n
    
    traditional_gini = gini_coefficient(traditional_results)
    quantum_gini = gini_coefficient(quantum_results)
    
    print(f"Traditional PoS Gini coefficient: {traditional_gini:.4f}")
    print(f"Quantum PoS Gini coefficient: {quantum_gini:.4f}")
    print(f"(Lower Gini = more fair distribution)")
    print()
    
    # Stake correlation analysis
    print("Stake vs Selection Correlation:")
    for name, stake in validators:
        expected_pct = (stake / sum([s for _, s in validators])) * 100
        traditional_pct = (traditional_results.get(name, 0) / rounds) * 100
        quantum_pct = (quantum_results.get(name, 0) / rounds) * 100
        
        traditional_deviation = traditional_pct - expected_pct
        quantum_deviation = quantum_pct - expected_pct
        
        print(f"  {name}: Expected {expected_pct:.1f}%, "
              f"Traditional {traditional_deviation:+.1f}%, "
              f"Quantum {quantum_deviation:+.1f}%")
    
    print()
    
    # Quantum PoS specific analysis
    print("QUANTUM ANNEALING FEATURES:")
    print("-" * 40)
    
    # Get energy state analysis
    sample_seed = get_random_string()
    energy_state = quantum_pos.get_energy_state(sample_seed)
    
    print("Energy Analysis (sample round):")
    for name in [v[0] for v in validators]:
        if name in energy_state:
            energy = energy_state[name]['energy']
            stake_ratio = energy_state[name]['stake_ratio']
            print(f"  {name}: Energy={energy:.3f}, Stake ratio={stake_ratio:.3f}")
    
    print()
    print("Quantum PoS Features:")
    print("  ✓ Energy minimization for validator selection")
    print("  ✓ Simulated annealing with temperature scheduling")
    print("  ✓ Fairness component prevents monopolization") 
    print("  ✓ Quantum-inspired randomness for unpredictability")
    print("  ✓ Dynamic parameter adjustment based on network conditions")
    
    # Save comparison results to organized output directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'reports')
    os.makedirs(output_dir, exist_ok=True)
    
    filename = os.path.join(output_dir, f"pos_comparison_{timestamp}.txt")
    
    # Capture the comparison results in text format for saving
    comparison_report = f"""PoS Mechanisms Comparison Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 60}

Initial Validator Setup:
"""
    
    for name, stake in validators:
        percentage = (stake / sum([s for _, s in validators])) * 100
        comparison_report += f"  {name}: {stake} tokens ({percentage:.1f}%)\n"
    
    comparison_report += f"""
Selection Results ({rounds} rounds):

Traditional PoS:
"""
    for name in [v[0] for v in validators]:
        count = traditional_results[name]
        percentage = (count / rounds) * 100
        comparison_report += f"  {name}: {count} selections ({percentage:.1f}%)\n"
    
    comparison_report += "\nQuantum Annealing Consensus:\n"
    for name in [v[0] for v in validators]:
        count = quantum_results[name]
        percentage = (count / rounds) * 100
        comparison_report += f"  {name}: {count} selections ({percentage:.1f}%)\n"
    
    comparison_report += f"""
Energy Analysis (sample round):
"""
    for name in [v[0] for v in validators]:
        if name in energy_state:
            energy = energy_state[name]['energy']
            stake_ratio = energy_state[name]['stake_ratio']
            comparison_report += f"  {name}: Energy={energy:.3f}, Stake ratio={stake_ratio:.3f}\n"
    
    comparison_report += """
Quantum PoS Features:
  ✓ Energy minimization for validator selection
  ✓ Simulated annealing with temperature scheduling
  ✓ Fairness component prevents monopolization
  ✓ Quantum-inspired randomness for unpredictability
  ✓ Dynamic parameter adjustment based on network conditions
"""
    
    with open(filename, 'w') as f:
        f.write(comparison_report)
    print(f"📄 Comparison report saved to: {filename}")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    # Set random seed for reproducible results in demo
    random.seed(42)
    run_comparison()
