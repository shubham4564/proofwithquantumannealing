#!/usr/bin/env python3
"""
Test script for enhanced performance analysis capabilities
"""

import sys
sys.path.append('/Users/shubham/Documents/fromgithub/proofwithquantumannealing/blockchain')

from performance_analysis import BlockchainPerformanceAnalyzer

def test_enhanced_calculations():
    """Test the enhanced calculation methods"""
    analyzer = BlockchainPerformanceAnalyzer()
    
    print("🧪 Testing Enhanced Performance Analysis Calculations")
    print("=" * 60)
    
    # Test energy calculation
    energy = analyzer.calculate_energy_consumption()
    print(f"💡 Energy per transaction: {energy:.6f} kWh")
    print(f"   - Quantum component: 25e-6 kWh")
    print(f"   - Classical component: 5e-6 kWh") 
    print(f"   - Network component: 2e-6 kWh")
    
    # Test scalability calculations
    print(f"\n📈 Scalability Analysis:")
    node_counts = [10, 100, 1000, 5000]
    for nodes in node_counts:
        tps = analyzer.calculate_theoretical_scalability(nodes)
        degradation = (1 - tps/analyzer.network_data['Your Quantum Network']['tps']) * 100
        print(f"   {nodes:4d} nodes: {tps:4.0f} TPS ({degradation:4.1f}% degradation)")
    
    # Test network data sources
    print(f"\n📊 Data Sources:")
    for network, data in analyzer.network_data.items():
        print(f"   {network}: {data['source']}")
    
    # Test connection attempt
    print(f"\n🔗 Testing blockchain connection...")
    metrics = analyzer.get_real_network_metrics()
    if metrics.get('connected'):
        print("   ✅ Connected successfully")
        blockchain_data = metrics.get('blockchain', {})
        print(f"   📦 Current blocks: {len(blockchain_data.get('blocks', []))}")
        print(f"   ⏱️  Timestamp: {metrics.get('timestamp', 'N/A')}")
    else:
        print("   ❌ Not connected - using theoretical values")
    
    print(f"\n✅ Enhanced calculations test complete!")

if __name__ == "__main__":
    test_enhanced_calculations()
