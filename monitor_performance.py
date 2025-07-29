#!/usr/bin/env python3
"""
Real-Time Blockchain Performance Monitor

This script provides real-time monitoring of blockchain performance
using the built-in performance monitoring framework.
"""

import json
import time
import sys
import subprocess
from pathlib import Path
from collections import defaultdict, deque
from datetime import datetime, timedelta

class BlockchainPerformanceMonitor:
    """Real-time performance monitoring dashboard"""
    
    def __init__(self, log_file_pattern="performance_logs_*.jsonl"):
        self.log_pattern = log_file_pattern
        self.events = deque(maxlen=1000)  # Keep last 1000 events
        self.metrics = defaultdict(list)
        self.start_time = time.time()
        
    def find_log_files(self):
        """Find all performance log files"""
        current_dir = Path(".")
        log_files = list(current_dir.glob(self.log_pattern))
        return log_files
    
    def tail_log_file(self, log_file, lines=50):
        """Get the last N lines from a log file"""
        try:
            result = subprocess.run(
                ["tail", "-n", str(lines), str(log_file)],
                capture_output=True,
                text=True
            )
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        except Exception as e:
            print(f"Error reading {log_file}: {e}")
            return []
    
    def parse_event(self, line):
        """Parse a JSON event line"""
        try:
            return json.loads(line.strip())
        except json.JSONDecodeError:
            return None
    
    def calculate_metrics(self, events):
        """Calculate performance metrics from events"""
        if not events:
            return {}
        
        # Count events by type
        event_counts = defaultdict(int)
        transaction_events = []
        block_events = []
        consensus_events = []
        
        for event in events:
            event_type = event.get('event_type', '')
            event_counts[event_type] += 1
            timestamp_ns = event.get('timestamp_ns', 0)
            
            if 'transaction' in event_type.lower():
                transaction_events.append((timestamp_ns, event))
            elif 'block' in event_type.lower():
                block_events.append((timestamp_ns, event))
            elif 'consensus' in event_type.lower():
                consensus_events.append((timestamp_ns, event))
        
        # Calculate time-based metrics
        if len(events) > 1:
            earliest = min(e.get('timestamp_ns', 0) for e in events)
            latest = max(e.get('timestamp_ns', 0) for e in events)
            time_span_seconds = (latest - earliest) / 1_000_000_000
        else:
            time_span_seconds = 1.0
        
        # Transaction throughput (TPS)
        transaction_count = len(transaction_events)
        tps = transaction_count / time_span_seconds if time_span_seconds > 0 else 0
        
        # Block production rate
        block_finalization_events = [e for e in block_events if e[1].get('event_type') == 'block_finalization']
        blocks_per_minute = (len(block_finalization_events) / time_span_seconds) * 60 if time_span_seconds > 0 else 0
        
        return {
            'total_events': len(events),
            'time_span_seconds': time_span_seconds,
            'transaction_throughput_tps': tps,
            'blocks_per_minute': blocks_per_minute,
            'event_distribution': dict(event_counts),
            'unique_event_types': len(event_counts)
        }
    
    def display_dashboard(self, events, metrics):
        """Display the monitoring dashboard"""
        # Clear screen
        print("\033[2J\033[H")
        
        # Header
        print("🔥" * 20 + " BLOCKCHAIN PERFORMANCE MONITOR " + "🔥" * 20)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 📊 Monitoring Runtime: {time.time() - self.start_time:.1f}s")
        print("=" * 80)
        
        # Key Performance Indicators
        print("\n📈 KEY PERFORMANCE INDICATORS")
        print("-" * 40)
        print(f"🚀 Transaction Throughput:     {metrics.get('transaction_throughput_tps', 0):.2f} TPS")
        print(f"🧱 Block Production Rate:      {metrics.get('blocks_per_minute', 0):.2f} blocks/minute")
        print(f"📊 Total Events Tracked:       {metrics.get('total_events', 0)}")
        print(f"⏱️  Monitoring Time Span:       {metrics.get('time_span_seconds', 0):.1f} seconds")
        print(f"🎯 Unique Event Types:         {metrics.get('unique_event_types', 0)}")
        
        # Event Distribution
        print("\n📋 EVENT DISTRIBUTION")
        print("-" * 40)
        event_dist = metrics.get('event_distribution', {})
        for event_type, count in sorted(event_dist.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / metrics.get('total_events', 1)) * 100
            print(f"  {event_type:<25} {count:>4} events ({percentage:>5.1f}%)")
        
        # Recent Events
        print("\n🕐 RECENT EVENTS (Last 5)")
        print("-" * 40)
        recent_events = sorted(events, key=lambda x: x.get('timestamp_ns', 0))[-5:]
        for event in recent_events:
            timestamp = datetime.fromtimestamp(event.get('timestamp_ns', 0) / 1_000_000_000)
            event_type = event.get('event_type', 'unknown')
            node_id = event.get('node_id', 'unknown')[:15]
            metadata = event.get('metadata', {})
            
            # Format metadata for display
            meta_str = ""
            if metadata:
                key_items = []
                for k, v in list(metadata.items())[:2]:  # Show first 2 metadata items
                    key_items.append(f"{k}={v}")
                meta_str = f" | {', '.join(key_items)}" if key_items else ""
            
            print(f"  {timestamp.strftime('%H:%M:%S.%f')[:-3]} | {event_type:<20} | {node_id}{meta_str}")
        
        print("\n" + "=" * 80)
        print("💡 Press Ctrl+C to stop monitoring")
    
    def run_monitoring(self, refresh_interval=2.0):
        """Run the real-time monitoring dashboard"""
        print("🚀 Starting Real-Time Blockchain Performance Monitor...")
        print(f"📁 Scanning for log files: {self.log_pattern}")
        
        try:
            while True:
                # Find and read log files
                log_files = self.find_log_files()
                all_events = []
                
                if not log_files:
                    print(f"\n⚠️  No log files found matching '{self.log_pattern}'")
                    print("   Start your blockchain to generate performance logs")
                    time.sleep(refresh_interval)
                    continue
                
                # Read events from all log files
                for log_file in log_files:
                    lines = self.tail_log_file(log_file, lines=100)
                    for line in lines:
                        event = self.parse_event(line)
                        if event:
                            all_events.append(event)
                
                # Calculate metrics
                metrics = self.calculate_metrics(all_events)
                
                # Display dashboard
                self.display_dashboard(all_events, metrics)
                
                # Wait before next refresh
                time.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped by user")
            return
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")
            return

def main():
    """Main monitoring function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Real-time blockchain performance monitor")
    parser.add_argument("--pattern", default="performance_logs_*.jsonl", 
                       help="Log file pattern to monitor")
    parser.add_argument("--interval", type=float, default=2.0,
                       help="Refresh interval in seconds")
    
    args = parser.parse_args()
    
    monitor = BlockchainPerformanceMonitor(args.pattern)
    monitor.run_monitoring(args.interval)

if __name__ == "__main__":
    main()
