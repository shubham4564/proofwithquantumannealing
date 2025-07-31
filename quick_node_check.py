#!/usr/bin/env python3
"""
Node Availability Quick Check
============================

Quick script to check which nodes are available for transaction processing.
"""

import sys
import os

# Add current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from node_availability_checker import NodeAvailabilityChecker
    print("🔍 QUICK NODE AVAILABILITY CHECK")
    print("=" * 40)
    
    # Check nodes
    checker = NodeAvailabilityChecker(base_port=11000, max_nodes=10)
    available_nodes, unavailable_nodes = checker.check_all_nodes()
    
    # Print summary
    checker.print_summary()
    
    # Get best nodes for transactions
    best_nodes = checker.get_best_nodes_for_transactions(3)
    
    if best_nodes:
        print(f"\n🚀 QUICK COMMANDS:")
        print("─" * 20)
        
        # Single node test
        best_node = best_nodes[0]
        print(f"Test single node (recommended):")
        print(f"  python batch_transaction_test.py --node {best_node.api_port}")
        
        # Auto-select best node
        print(f"\nAuto-select best node:")
        print(f"  python batch_transaction_test.py --auto-select")
        
        # Multi-node test
        if len(best_nodes) > 1:
            print(f"\nMulti-node distributed test:")
            print(f"  python batch_transaction_test.py --multi-node")
        
        # Check availability first
        print(f"\nCheck availability before testing:")
        print(f"  python batch_transaction_test.py --check-availability")
        
        # Detailed availability report
        print(f"\nDetailed availability report:")
        print(f"  python node_availability_checker.py --detailed")
        
    else:
        print(f"\n❌ No nodes available for transactions!")
        print(f"💡 Start some nodes first:")
        print(f"   cd blockchain && ./start_nodes.sh 5")
        
        sys.exit(1)

except ImportError:
    print("❌ Could not import node_availability_checker")
    print("💡 Make sure node_availability_checker.py is in the same directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
