#!/usr/bin/env python3
"""
JSON Performance Log Viewer

View and search through blockchain performance logs with filtering options.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import Counter

def view_performance_logs(log_pattern="performance_logs_*.jsonl", 
                         event_type=None, 
                         node_id=None, 
                         limit=20,
                         tail=False):
    """View and filter performance logs"""
    
    # Find log files
    log_files = list(Path(".").glob(log_pattern))
    
    if not log_files:
        print(f"❌ No log files found matching pattern: {log_pattern}")
        return
    
    print(f"📁 Found {len(log_files)} log files:")
    for log_file in log_files:
        print(f"   📄 {log_file}")
    
    # Load all events
    all_events = []
    for log_file in log_files:
        try:
            with open(log_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        event = json.loads(line.strip())
                        event['_source_file'] = str(log_file)
                        event['_line_number'] = line_num
                        all_events.append(event)
                    except json.JSONDecodeError:
                        pass  # Skip malformed lines
        except Exception as e:
            print(f"⚠️  Error reading {log_file}: {e}")
    
    print(f"📊 Loaded {len(all_events)} total events")
    
    # Apply filters
    filtered_events = all_events
    
    if event_type:
        filtered_events = [e for e in filtered_events if e.get('event_type') == event_type]
        print(f"🔍 Filtered by event_type='{event_type}': {len(filtered_events)} events")
    
    if node_id:
        filtered_events = [e for e in filtered_events if e.get('node_id') == node_id]
        print(f"🔍 Filtered by node_id='{node_id}': {len(filtered_events)} events")
    
    # Sort by timestamp
    filtered_events.sort(key=lambda x: x.get('timestamp_ns', 0))
    
    # Apply limit
    if tail:
        display_events = filtered_events[-limit:] if len(filtered_events) > limit else filtered_events
        print(f"📋 Showing last {len(display_events)} events:")
    else:
        display_events = filtered_events[:limit] if len(filtered_events) > limit else filtered_events
        print(f"📋 Showing first {len(display_events)} events:")
    
    # Display events
    print("\n" + "="*80)
    for i, event in enumerate(display_events, 1):
        timestamp = datetime.fromtimestamp(event.get('timestamp_ns', 0) / 1_000_000_000)
        event_type = event.get('event_type', 'unknown')
        node_id = event.get('node_id', 'unknown')
        event_id = event.get('event_id', 'unknown')[:8]
        
        print(f"Event #{i:2d} | {timestamp.strftime('%H:%M:%S.%f')[:-3]} | {event_type:<25} | {node_id}")
        print(f"         ID: {event_id}... | Source: {event.get('_source_file', 'unknown')}")
        
        metadata = event.get('metadata', {})
        if metadata:
            print(f"         Metadata: {metadata}")
        
        print("-" * 80)
    
    # Show statistics
    if filtered_events:
        print(f"\n📊 STATISTICS")
        print(f"   Total Events: {len(filtered_events)}")
        
        # Event type distribution
        event_types = Counter(e.get('event_type') for e in filtered_events)
        print(f"   Event Types:")
        for et, count in event_types.most_common():
            print(f"      • {et}: {count}")
        
        # Node distribution
        nodes = Counter(e.get('node_id') for e in filtered_events)
        print(f"   Nodes:")
        for node, count in nodes.most_common():
            print(f"      • {node}: {count}")
        
        # Time span
        if len(filtered_events) > 1:
            earliest = min(e.get('timestamp_ns', 0) for e in filtered_events)
            latest = max(e.get('timestamp_ns', 0) for e in filtered_events)
            time_span = (latest - earliest) / 1_000_000_000
            print(f"   Time Span: {time_span:.2f} seconds")

def main():
    parser = argparse.ArgumentParser(description="View blockchain performance logs")
    parser.add_argument("--pattern", default="performance_logs_*.jsonl",
                       help="Log file pattern (default: performance_logs_*.jsonl)")
    parser.add_argument("--event-type", 
                       help="Filter by event type (e.g., transaction_ingress)")
    parser.add_argument("--node-id",
                       help="Filter by node ID")
    parser.add_argument("--limit", type=int, default=20,
                       help="Maximum number of events to show (default: 20)")
    parser.add_argument("--tail", action="store_true",
                       help="Show last N events instead of first N")
    
    args = parser.parse_args()
    
    view_performance_logs(
        log_pattern=args.pattern,
        event_type=args.event_type,
        node_id=args.node_id,
        limit=args.limit,
        tail=args.tail
    )

if __name__ == "__main__":
    main()
