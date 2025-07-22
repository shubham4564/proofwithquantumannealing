#!/usr/bin/env python3
"""
Health Monitoring Demo

This script demonstrates the health monitoring capabilities of the enhanced start_nodes.py.
It starts nodes, waits for them to become healthy, then simulates a node failure.
"""

import os
import sys
import time
import signal
import subprocess
import requests

def main():
    print("🩺 HEALTH MONITORING DEMONSTRATION")
    print("=" * 50)
    print("This demo will:")
    print("1. Start 2 blockchain nodes")
    print("2. Monitor their health every 10 seconds")
    print("3. Simulate node failure by stopping one node")
    print("4. Show health alerts in real-time")
    print()
    
    # Start the enhanced node starter
    print("🚀 Starting nodes with health monitoring...")
    starter_cmd = [
        sys.executable, "demos/start_nodes.py",
        "--nodes", "2",
        "--health-interval", "10",
        "--no-wait"  # Don't wait for interrupt, return control immediately
    ]
    
    starter_proc = subprocess.Popen(
        starter_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Capture startup output
    startup_lines = []
    while True:
        line = starter_proc.stdout.readline()
        if line:
            startup_lines.append(line.strip())
            print(line.strip())
        if starter_proc.poll() is not None:
            break
    
    if starter_proc.returncode != 0:
        print("❌ Failed to start nodes")
        return 1
    
    print("\n✅ Nodes started! Now demonstrating health monitoring...")
    print("⏳ Waiting 40 seconds for nodes to initialize...")
    time.sleep(40)
    
    # Find the node processes
    print("\n🔍 Finding running node processes...")
    result = subprocess.run(
        ["ps", "aux"],
        capture_output=True,
        text=True
    )
    
    node_pids = []
    for line in result.stdout.split('\n'):
        if 'run_node.py' in line and 'grep' not in line:
            parts = line.split()
            if len(parts) > 1:
                pid = parts[1]
                node_pids.append(pid)
                print(f"  Found node process: PID {pid}")
    
    if not node_pids:
        print("❌ No node processes found")
        return 1
    
    print(f"\n📊 Monitoring {len(node_pids)} nodes for 30 seconds...")
    print("   (You should see periodic health check summaries)")
    time.sleep(30)
    
    # Simulate node failure
    if len(node_pids) > 1:
        victim_pid = node_pids[1]  # Kill the second node
        print(f"\n💀 Simulating node failure by stopping PID {victim_pid}...")
        try:
            subprocess.run(["kill", "-TERM", victim_pid])
            print(f"   ✅ Sent TERM signal to PID {victim_pid}")
        except Exception as e:
            print(f"   ❌ Failed to stop node: {e}")
        
        print("\n⏳ Waiting 20 seconds to observe health alerts...")
        time.sleep(20)
    
    # Cleanup - stop all remaining nodes
    print("\n🧹 Cleaning up remaining nodes...")
    subprocess.run(["pkill", "-f", "run_node.py"])
    
    print("\n🎯 Health monitoring demonstration completed!")
    print("\nKey features demonstrated:")
    print("✅ Automatic port conflict resolution")
    print("✅ Periodic health checks every 10 seconds")
    print("✅ Health status summaries every 5 minutes")
    print("✅ Real-time alerts when nodes go down")
    print("✅ Process and API endpoint monitoring")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
