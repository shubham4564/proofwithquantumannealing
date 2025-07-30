#!/usr/bin/env python3
"""
Clean Individual Performance Graphs (No Annotations)

Minimal, clean graphs without improvement annotations for professional presentation.
"""

import matplotlib.pyplot as plt
import numpy as np

def create_clean_throughput_graph():
    """Clean transaction throughput graph without annotations"""
    
    plt.style.use('default')
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 30
    
    # Data
    networks = ['Our\nImplementation', 'Bitcoin', 'Ethereum']
    tps_values = [1001.92, 7.0, 15.0]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create bars
    bars = ax.bar(networks, tps_values, color=colors, width=0.6, alpha=0.8)
    
    # Styling
    ax.set_ylabel('Transactions per Second (TPS)', fontweight='bold', fontsize=30)
    # ax.set_title('Transaction Throughput Comparison', fontweight='bold', fontsize=18)
    
    # Add value labels
    for bar, value in zip(bars, tps_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 20,
                f'{value:.0f}', ha='center', va='bottom', 
                fontweight='bold', fontsize=30)
    
    # Clean formatting
    ax.set_ylim(0, 1100)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=30)
    
    plt.tight_layout()
    return fig

def create_clean_block_time_graph():
    """Clean block production time graph without annotations"""
    
    plt.style.use('default')
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 30
    
    # Data
    networks = ['Our\nImplementation', 'Bitcoin', 'Ethereum']
    block_times_seconds = [0.1, 600, 12]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create bars
    bars = ax.bar(networks, block_times_seconds, color=colors, width=0.6, alpha=0.8)
    
    # Styling
    ax.set_ylabel('Block Production Time (seconds)', fontweight='bold', fontsize=30)
    # ax.set_title('Block Production Speed Comparison', fontweight='bold', fontsize=18)
    ax.set_yscale('log')
    ax.set_ylim(0.05, 1000)
    
    # Add value labels
    labels = ['0.1 sec', '10 min', '12 sec']
    for bar, label in zip(bars, labels):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height * 1.8,
                label, ha='center', va='bottom', 
                fontweight='bold', fontsize=30)
    
    # Clean formatting
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=30)
    
    plt.tight_layout()
    return fig

def create_clean_finality_graph():
    """Clean transaction finality graph without annotations"""
    
    plt.style.use('default')
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 30
    
    # Data
    networks = ['Our\nImplementation', 'Bitcoin', 'Ethereum']
    finality_seconds = [0.2, 3600, 384]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create bars
    bars = ax.bar(networks, finality_seconds, color=colors, width=0.6, alpha=0.8)
    
    # Styling
    ax.set_ylabel('Transaction Finality Time (seconds)', fontweight='bold', fontsize=30)
    # ax.set_title('Transaction Finality Speed Comparison', fontweight='bold', fontsize=18)
    ax.set_yscale('log')
    ax.set_ylim(0.1, 10000)
    
    # Add value labels
    labels = ['0.2 sec', '1 hour', '6.4 min']
    for bar, label in zip(bars, labels):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height * 1.8,
                label, ha='center', va='bottom', 
                fontweight='bold', fontsize=30)
    
    # Clean formatting
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=30)
    
    plt.tight_layout()
    return fig

def create_minimal_combined_dashboard():
    """Minimal 3-panel dashboard without annotations"""
    
    plt.style.use('default')
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 30
    
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
    
    networks = ['Our\nImplementation', 'Bitcoin', 'Ethereum']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    # 1. Transaction Throughput
    tps_values = [1001.92, 7.0, 15.0]
    bars1 = ax1.bar(networks, tps_values, color=colors, width=0.6, alpha=0.8)
    ax1.set_ylabel('TPS', fontweight='bold', fontsize=30)
    # ax1.set_title('Throughput', fontweight='bold', fontsize=14)
    ax1.set_ylim(0, 1100)
    
    for bar, value in zip(bars1, tps_values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 20,
                f'{value:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=30)
    
    # 2. Block Production Time
    block_times = [0.1, 600, 12]
    bars2 = ax2.bar(networks, block_times, color=colors, width=0.6, alpha=0.8)
    ax2.set_ylabel('Seconds', fontweight='bold', fontsize=30)
    # ax2.set_title('Block Time', fontweight='bold', fontsize=14)
    ax2.set_yscale('log')
    ax2.set_ylim(0.05, 1000)
    
    labels2 = ['0.1s', '10m', '12s']
    for bar, label in zip(bars2, labels2):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height * 2,
                label, ha='center', va='bottom', fontweight='bold', fontsize=30)
    
    # 3. Transaction Finality
    finality_times = [0.2, 3600, 384]
    bars3 = ax3.bar(networks, finality_times, color=colors, width=0.6, alpha=0.8)
    ax3.set_ylabel('Seconds', fontweight='bold', fontsize=30)
    # ax3.set_title('Finality', fontweight='bold', fontsize=14)
    ax3.set_yscale('log')
    ax3.set_ylim(0.1, 10000)
    
    labels3 = ['0.2s', '1h', '6.4m']
    for bar, label in zip(bars3, labels3):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height * 2,
                label, ha='center', va='bottom', fontweight='bold', fontsize=30)
    
    # Clean formatting
    for ax in [ax1, ax2, ax3]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(axis='x', labelsize=30)
    
    # plt.suptitle('Blockchain Performance Comparison', 
                #  fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    
    return fig

def main():
    """Generate clean individual performance graphs"""
    
    print("📊 Creating clean individual performance graphs...")
    
    # Create clean individual graphs
    print("   • Creating clean transaction throughput graph...")
    fig1 = create_clean_throughput_graph()
    fig1.savefig('clean_transaction_throughput.svg', dpi=300, bbox_inches='tight', facecolor='white')
    
    print("   • Creating clean block production time graph...")
    fig2 = create_clean_block_time_graph()
    fig2.savefig('clean_block_production_time.svg', dpi=300, bbox_inches='tight', facecolor='white')
    
    print("   • Creating clean transaction finality graph...")
    fig3 = create_clean_finality_graph()
    fig3.savefig('clean_transaction_finality.svg', dpi=300, bbox_inches='tight', facecolor='white')
    
    print("   • Creating minimal combined dashboard...")
    fig4 = create_minimal_combined_dashboard()
    fig4.savefig('minimal_performance_dashboard.svg', dpi=300, bbox_inches='tight', facecolor='white')
    
    # Show all plots
    plt.show()
    
    print("\n✅ Clean individual performance graphs created!")
    print("\n📁 Generated Files:")
    print("   • clean_transaction_throughput.svg")
    print("   • clean_block_production_time.svg") 
    print("   • clean_transaction_finality.svg")
    print("   • minimal_performance_dashboard.svg")
    
    print(f"\n📊 METRICS SUMMARY:")
    print(f"   • Throughput: 1,002 vs 7 vs 15 TPS")
    print(f"   • Block Time: 0.1s vs 10m vs 12s")
    print(f"   • Finality: 0.2s vs 1h vs 6.4m")

if __name__ == "__main__":
    main()
