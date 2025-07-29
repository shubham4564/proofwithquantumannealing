#!/usr/bin/env python3
"""
Simple Blockchain Performance Monitor

Quick and easy real-time monitoring of blockchain performance events.
"""

import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

def monitor_blockchain_performance(refresh_interval=3):
    """Simple real-time performance monitor"""
    
    print("🚀 Simple Blockchain Performance Monitor")
    print("=" * 60)
    print("💡 This monitors your blockchain performance in real-time")
    print("📊 Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Clear screen
            print("\033[2J\033[H")
            
            # Header
            print(f"🔥 BLOCKCHAIN PERFORMANCE MONITOR - {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 60)
            
            # Find log files
            log_files = list(Path(".").glob("performance_logs_*.jsonl"))
            
            if not log_files:
                print("⚠️  No performance logs found.")
                print("   Start your blockchain to see performance data!")
                print(f"\n   Expected files: performance_logs_*.jsonl")
            else:
                print(f"📁 Monitoring {len(log_files)} log files:")
                
                total_events = 0
                latest_events = []
                
                # Read latest events from each file
                for log_file in log_files:
                    print(f"   📄 {log_file.name}")
                    
                    try:
                        # Get last 10 lines
                        result = subprocess.run(
                            ["tail", "-n", "10", str(log_file)],
                            capture_output=True,
                            text=True
                        )
                        
                        lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
                        file_events = 0
                        
                        for line in lines:
                            try:
                                event = json.loads(line.strip())
                                latest_events.append(event)
                                file_events += 1
                            except json.JSONDecodeError:
                                pass
                        
                        total_events += file_events
                        print(f"      └─ {file_events} recent events")
                        
                    except Exception as e:
                        print(f"      └─ Error reading file: {e}")
                
                # Show summary
                print(f"\n📊 SUMMARY:")
                print(f"   🎯 Total Recent Events: {total_events}")
                
                # Count event types
                if latest_events:
                    event_types = {}
                    for event in latest_events:
                        event_type = event.get('event_type', 'unknown')
                        event_types[event_type] = event_types.get(event_type, 0) + 1
                    
                    print(f"   📈 Event Types in Last {len(latest_events)} Events:")
                    for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True):
                        print(f"      • {event_type}: {count}")
                    
                    # Show most recent event
                    if latest_events:
                        recent = max(latest_events, key=lambda x: x.get('timestamp_ns', 0))
                        timestamp = datetime.fromtimestamp(recent.get('timestamp_ns', 0) / 1_000_000_000)
                        print(f"\n   🕐 Most Recent Event:")
                        print(f"      • Type: {recent.get('event_type', 'unknown')}")
                        print(f"      • Time: {timestamp.strftime('%H:%M:%S.%f')[:-3]}")
                        print(f"      • Node: {recent.get('node_id', 'unknown')}")
                        
                        metadata = recent.get('metadata', {})
                        if metadata:
                            print(f"      • Data: {metadata}")
            
            print(f"\n🔄 Refreshing in {refresh_interval} seconds...")
            print("💡 Start your blockchain to see live performance data!")
            
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped. Goodbye!")

if __name__ == "__main__":
    monitor_blockchain_performance()
