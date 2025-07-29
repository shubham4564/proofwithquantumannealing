#!/usr/bin/env python3
"""
Extract Performance Data from Node Logs

This script extracts performance monitoring events from blockchain node logs
and creates a structured dataset for TPS analysis.
"""

import json
import glob
import re
from datetime import datetime
import time


def extract_performance_events():
    """Extract all performance events from node logs"""
    events = []
    
    # Find all log files
    log_files = glob.glob('blockchain/logs/node*.log')
    print(f"🔍 Found {len(log_files)} log files to analyze")
    
    for log_file in log_files:
        print(f"📄 Processing {log_file}")
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                
            for line in lines:
                try:
                    # Parse the JSON log entry
                    log_entry = json.loads(line.strip())
                    message = log_entry.get('message', '')
                    
                    # Check if the message contains a performance event
                    if message.startswith('{') and 'event_type' in message:
                        try:
                            event_data = json.loads(message)
                            events.append(event_data)
                        except json.JSONDecodeError:
                            continue
                            
                except json.JSONDecodeError:
                    continue
                    
        except Exception as e:
            print(f"⚠️  Error processing {log_file}: {e}")
            continue
    
    print(f"✅ Extracted {len(events)} performance events")
    return events


def save_performance_data(events):
    """Save events to a structured JSON file"""
    # Sort events by timestamp
    events.sort(key=lambda x: x.get('timestamp_ns', 0))
    
    # Save to file
    with open('blockchain_performance_data.json', 'w') as f:
        json.dump(events, f, indent=2)
    
    print(f"💾 Saved {len(events)} events to blockchain_performance_data.json")


def analyze_recent_performance(events):
    """Analyze recent performance data"""
    if not events:
        print("❌ No events found")
        return
    
    # Get events from last 10 minutes
    current_time = time.time_ns()
    ten_minutes_ago = current_time - (10 * 60 * 1_000_000_000)  # 10 minutes in nanoseconds
    
    recent_events = [e for e in events if e.get('timestamp_ns', 0) > ten_minutes_ago]
    
    print(f"\n📊 RECENT PERFORMANCE ANALYSIS (Last 10 minutes)")
    print(f"="*60)
    print(f"Total events: {len(recent_events)}")
    
    # Count by event type
    event_types = {}
    transaction_events = []
    
    for event in recent_events:
        event_type = event.get('event_type', 'unknown')
        event_types[event_type] = event_types.get(event_type, 0) + 1
        
        if 'transaction' in event_type:
            transaction_events.append(event)
    
    print(f"\n🔍 Event Type Breakdown:")
    for event_type, count in sorted(event_types.items()):
        print(f"   {event_type}: {count}")
    
    print(f"\n💰 Transaction Events: {len(transaction_events)}")
    
    if transaction_events:
        # Calculate time span
        start_time = min(e.get('timestamp_ns', 0) for e in transaction_events)
        end_time = max(e.get('timestamp_ns', 0) for e in transaction_events)
        time_span_seconds = (end_time - start_time) / 1_000_000_000
        
        if time_span_seconds > 0:
            fresh_tps = len(transaction_events) / time_span_seconds
            print(f"⚡ Fresh TPS: {fresh_tps:.2f}")
            print(f"📏 Time span: {time_span_seconds:.2f} seconds")
        else:
            print(f"⚠️  All transactions in same nanosecond")


if __name__ == "__main__":
    print("🚀 PERFORMANCE DATA EXTRACTION")
    print("="*50)
    
    # Extract events from logs
    events = extract_performance_events()
    
    # Save to structured file
    save_performance_data(events)
    
    # Analyze recent performance
    analyze_recent_performance(events)
    
    print(f"\n✅ Performance data extraction completed!")
