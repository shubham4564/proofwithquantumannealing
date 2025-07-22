#!/usr/bin/env python3
"""
📁 BLOCKCHAIN PROJECT ORGANIZATION SUMMARY
==========================================
This script provides an overview of the newly organized blockchain project structure.
"""

import os
from pathlib import Path

def count_files_by_type(directory):
    """Count files by extension in a directory"""
    counts = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            ext = Path(file).suffix.lower()
            if ext:
                counts[ext] = counts.get(ext, 0) + 1
    return counts

def main():
    print("🌌 QUANTUM ANNEALING BLOCKCHAIN - PROJECT ORGANIZATION")
    print("=" * 70)
    
    base_path = "/Users/shubham/Documents/proofwithquantumannealing/blockchain"
    
    structure = {
        "🛠️ Tools": {
            "tools/testing": "Testing utilities and demos",
            "tools/monitoring": "Real-time monitoring and observability",
            "tools/deployment": "Network deployment scripts",
            "tools/analysis": "Performance and data analysis"
        },
        "📊 Outputs": {
            "outputs/reports": "Generated reports and analysis",
            "outputs/logs": "Application and monitoring logs"
        },
        "📖 Documentation": {
            "docs": "Project documentation and research papers"
        },
        "🔧 Core System": {
            "api": "REST API implementation",
            "blockchain": "Core blockchain logic",
            "tests": "Unit and integration tests",
            "keys": "Cryptographic keys",
            "requirements": "Python dependencies"
        }
    }
    
    print("\n📁 ORGANIZED DIRECTORY STRUCTURE")
    print("-" * 40)
    
    for category, dirs in structure.items():
        print(f"\n{category}")
        for dir_name, description in dirs.items():
            full_path = os.path.join(base_path, dir_name)
            if os.path.exists(full_path):
                file_count = len([f for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))])
                print(f"   {dir_name:<20} - {description} ({file_count} files)")
            else:
                print(f"   {dir_name:<20} - {description} (not found)")
    
    print(f"\n🔍 FILE TYPE ANALYSIS")
    print("-" * 30)
    
    file_counts = count_files_by_type(base_path)
    total_files = sum(file_counts.values())
    
    for ext, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_files) * 100
        print(f"   {ext:<8} {count:3d} files ({percentage:5.1f}%)")
    
    print(f"\n📈 PROJECT METRICS")
    print("-" * 20)
    print(f"   Total Files: {total_files}")
    print(f"   Python Files: {file_counts.get('.py', 0)}")
    print(f"   Documentation: {file_counts.get('.md', 0)}")
    print(f"   Configuration: {file_counts.get('.yml', 0) + file_counts.get('.cfg', 0) + file_counts.get('.txt', 0)}")
    
    print(f"\n🎯 KEY CAPABILITIES")
    print("-" * 20)
    print("   ✅ D-Wave Quantum Annealing Integration")
    print("   ✅ 50-Node Network Deployment")
    print("   ✅ Real-time Consensus Monitoring")
    print("   ✅ Comprehensive Testing Suite")
    print("   ✅ Performance Analysis Tools")
    print("   ✅ Production-Ready Organization")
    
    print(f"\n🚀 QUICK ACCESS COMMANDS")
    print("-" * 30)
    print("   # Testing")
    print("   cd tools/testing && python transaction_stress_test.py")
    print("   cd tools/testing && python quantum_consensus_demo.py")
    print("")
    print("   # Deployment")
    print("   cd tools/deployment && python launch_50_nodes.py")
    print("")
    print("   # Monitoring")
    print("   cd tools/monitoring && python monitor_quantum_consensus.py")
    print("")
    print("   # Analysis")
    print("   cd tools/analysis && python final_quantum_report.py")
    
    print(f"\n🌟 ORGANIZATION COMPLETE!")
    print("="*50)
    print("All files have been organized into logical categories")
    print("for better maintainability and operational clarity.")

if __name__ == "__main__":
    main()
