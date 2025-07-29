#!/usr/bin/env python3
"""
Improved TPS Calculator

Provides multiple TPS calculation methods for different scenarios:
- Burst TPS: TPS during active periods
- Sustained TPS: TPS over entire monitoring period  
- Window TPS: TPS in configurable time windows
- Real-time TPS: TPS for live blockchain operations
"""

import json
import statistics
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

class ImprovedTPSCalculator:
    """Advanced TPS calculation with multiple methodologies"""
    
    def __init__(self):
        self.events = []
        self.transaction_events = []
    
    def load_events(self, log_pattern="performance_logs_*.jsonl"):
        """Load events from log files"""
        log_files = list(Path(".").glob(log_pattern))
        
        all_events = []
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())
                            all_events.append(event)
                        except json.JSONDecodeError:
                            pass
            except Exception as e:
                print(f"Error reading {log_file}: {e}")
        
        # Sort by timestamp
        all_events.sort(key=lambda x: x.get('timestamp_ns', 0))
        self.events = all_events
        
        # Extract transaction events
        self.transaction_events = [e for e in all_events 
                                 if e.get('event_type') == 'transaction_ingress']
        
        print(f"📊 Loaded {len(all_events)} total events")
        print(f"💰 Found {len(self.transaction_events)} transaction events")
        
        return len(self.transaction_events)
    
    def calculate_traditional_tps(self):
        """Traditional TPS: Total transactions / Total time span"""
        if len(self.transaction_events) < 2:
            return 0, "Insufficient data"
        
        earliest = min(e.get('timestamp_ns', 0) for e in self.transaction_events)
        latest = max(e.get('timestamp_ns', 0) for e in self.transaction_events)
        time_span_seconds = (latest - earliest) / 1_000_000_000
        
        if time_span_seconds <= 0:
            return 0, "Invalid time span"
        
        tps = len(self.transaction_events) / time_span_seconds
        
        return tps, f"{len(self.transaction_events)} transactions over {time_span_seconds:.2f} seconds"
    
    def calculate_burst_tps(self, burst_threshold_seconds=60):
        """Burst TPS: Identify active periods and calculate TPS during bursts"""
        if len(self.transaction_events) < 2:
            return 0, "Insufficient data"
        
        # Group transactions into bursts (periods of activity)
        bursts = []
        current_burst = []
        
        for i, event in enumerate(self.transaction_events):
            if not current_burst:
                current_burst = [event]
            else:
                # Check time gap from last event in current burst
                last_time = current_burst[-1].get('timestamp_ns', 0)
                curr_time = event.get('timestamp_ns', 0)
                gap_seconds = (curr_time - last_time) / 1_000_000_000
                
                if gap_seconds <= burst_threshold_seconds:
                    # Continue current burst
                    current_burst.append(event)
                else:
                    # Start new burst
                    if len(current_burst) > 1:
                        bursts.append(current_burst)
                    current_burst = [event]
        
        # Add final burst if it has multiple events
        if len(current_burst) > 1:
            bursts.append(current_burst)
        
        if not bursts:
            return 0, "No transaction bursts identified"
        
        # Calculate TPS for each burst
        burst_tps_values = []
        burst_details = []
        
        for i, burst in enumerate(bursts):
            if len(burst) < 2:
                continue
                
            burst_start = min(e.get('timestamp_ns', 0) for e in burst)
            burst_end = max(e.get('timestamp_ns', 0) for e in burst)
            burst_duration = (burst_end - burst_start) / 1_000_000_000
            
            if burst_duration > 0:
                burst_tps = len(burst) / burst_duration
                burst_tps_values.append(burst_tps)
                burst_details.append({
                    'burst_id': i + 1,
                    'transactions': len(burst),
                    'duration_seconds': burst_duration,
                    'tps': burst_tps
                })
        
        if not burst_tps_values:
            return 0, "No valid bursts found"
        
        avg_burst_tps = statistics.mean(burst_tps_values)
        max_burst_tps = max(burst_tps_values)
        
        details = f"Found {len(bursts)} bursts, avg {avg_burst_tps:.2f} TPS, max {max_burst_tps:.2f} TPS"
        
        return avg_burst_tps, details, burst_details
    
    def calculate_window_tps(self, window_seconds=60):
        """Window TPS: Calculate TPS in sliding time windows"""
        if len(self.transaction_events) < 2:
            return 0, "Insufficient data"
        
        window_ns = window_seconds * 1_000_000_000
        window_tps_values = []
        
        # Get time range
        earliest = min(e.get('timestamp_ns', 0) for e in self.transaction_events)
        latest = max(e.get('timestamp_ns', 0) for e in self.transaction_events)
        
        # Calculate TPS for each window
        current_time = earliest
        while current_time + window_ns <= latest:
            window_end = current_time + window_ns
            
            # Count transactions in this window
            window_transactions = [e for e in self.transaction_events 
                                 if current_time <= e.get('timestamp_ns', 0) < window_end]
            
            if len(window_transactions) > 0:
                window_tps = len(window_transactions) / window_seconds
                window_tps_values.append(window_tps)
            
            # Move window forward (overlap by 50%)
            current_time += window_ns // 2
        
        if not window_tps_values:
            return 0, f"No {window_seconds}s windows with transactions"
        
        avg_window_tps = statistics.mean(window_tps_values)
        max_window_tps = max(window_tps_values)
        
        details = f"{len(window_tps_values)} windows of {window_seconds}s, avg {avg_window_tps:.2f} TPS, max {max_window_tps:.2f} TPS"
        
        return avg_window_tps, details
    
    def calculate_real_time_tps(self, active_threshold_seconds=10):
        """Real-time TPS: Focus on continuous transaction periods"""
        if len(self.transaction_events) < 2:
            return 0, "Insufficient data"
        
        # Find periods of continuous activity
        active_periods = []
        current_period = []
        
        for event in self.transaction_events:
            if not current_period:
                current_period = [event]
            else:
                # Check gap from last transaction
                last_time = current_period[-1].get('timestamp_ns', 0)
                curr_time = event.get('timestamp_ns', 0)
                gap_seconds = (curr_time - last_time) / 1_000_000_000
                
                if gap_seconds <= active_threshold_seconds:
                    current_period.append(event)
                else:
                    # End current period, start new one
                    if len(current_period) >= 2:
                        active_periods.append(current_period)
                    current_period = [event]
        
        # Add final period
        if len(current_period) >= 2:
            active_periods.append(current_period)
        
        if not active_periods:
            return 0, "No continuous transaction periods found"
        
        # Calculate TPS for active periods
        period_tps_values = []
        total_active_time = 0
        total_active_transactions = 0
        
        for period in active_periods:
            period_start = min(e.get('timestamp_ns', 0) for e in period)
            period_end = max(e.get('timestamp_ns', 0) for e in period)
            period_duration = (period_end - period_start) / 1_000_000_000
            
            if period_duration > 0:
                period_tps = len(period) / period_duration
                period_tps_values.append(period_tps)
                total_active_time += period_duration
                total_active_transactions += len(period)
        
        if not period_tps_values:
            return 0, "No valid active periods"
        
        # Weighted average TPS across all active periods
        real_time_tps = total_active_transactions / total_active_time if total_active_time > 0 else 0
        
        details = f"{len(active_periods)} active periods, {total_active_time:.2f}s total active time"
        
        return real_time_tps, details
    
    def analyze_transaction_intervals(self):
        """Analyze intervals between consecutive transactions"""
        if len(self.transaction_events) < 2:
            return {}
        
        intervals_ms = []
        for i in range(1, len(self.transaction_events)):
            prev_time = self.transaction_events[i-1].get('timestamp_ns', 0)
            curr_time = self.transaction_events[i].get('timestamp_ns', 0)
            interval_ms = (curr_time - prev_time) / 1_000_000
            intervals_ms.append(interval_ms)
        
        return {
            'count': len(intervals_ms),
            'mean_ms': statistics.mean(intervals_ms),
            'median_ms': statistics.median(intervals_ms),
            'min_ms': min(intervals_ms),
            'max_ms': max(intervals_ms),
            'std_dev_ms': statistics.stdev(intervals_ms) if len(intervals_ms) > 1 else 0
        }
    
    def comprehensive_tps_analysis(self):
        """Run all TPS calculation methods and provide comprehensive analysis"""
        if not self.transaction_events:
            print("❌ No transaction events found!")
            return
        
        print("\n" + "="*80)
        print("🚀 COMPREHENSIVE TPS ANALYSIS")
        print("="*80)
        
        # Traditional TPS
        trad_tps, trad_details = self.calculate_traditional_tps()
        print(f"\n📊 TRADITIONAL TPS (Total Time Span)")
        print(f"   TPS: {trad_tps:.4f}")
        print(f"   Details: {trad_details}")
        
        # Burst TPS
        burst_result = self.calculate_burst_tps()
        if len(burst_result) == 3:
            burst_tps, burst_details, burst_breakdown = burst_result
            print(f"\n⚡ BURST TPS (Active Periods Only)")
            print(f"   TPS: {burst_tps:.4f}")
            print(f"   Details: {burst_details}")
            
            if burst_breakdown:
                print(f"   Burst Breakdown:")
                for burst in burst_breakdown[:3]:  # Show first 3 bursts
                    print(f"      • Burst {burst['burst_id']}: {burst['transactions']} tx in {burst['duration_seconds']:.2f}s = {burst['tps']:.2f} TPS")
        
        # Window TPS
        window_tps, window_details = self.calculate_window_tps(window_seconds=60)
        print(f"\n🕰️  WINDOW TPS (60-second windows)")
        print(f"   TPS: {window_tps:.4f}")
        print(f"   Details: {window_details}")
        
        # Real-time TPS
        rt_tps, rt_details = self.calculate_real_time_tps()
        print(f"\n🔥 REAL-TIME TPS (Continuous periods)")
        print(f"   TPS: {rt_tps:.4f}")
        print(f"   Details: {rt_details}")
        
        # Transaction intervals
        intervals = self.analyze_transaction_intervals()
        if intervals:
            print(f"\n📈 TRANSACTION TIMING ANALYSIS")
            print(f"   Average interval: {intervals['mean_ms']:.2f} ms")
            print(f"   Median interval: {intervals['median_ms']:.2f} ms")
            print(f"   Min interval: {intervals['min_ms']:.2f} ms")
            print(f"   Max interval: {intervals['max_ms']:.2f} ms")
            print(f"   Standard deviation: {intervals['std_dev_ms']:.2f} ms")
        
        # Recommendations
        print(f"\n💡 TPS INTERPRETATION")
        print("-" * 50)
        
        if trad_tps < 0.1:
            print("   🐌 Traditional TPS is very low - indicates test/development scenario")
        elif trad_tps < 1:
            print("   📊 Traditional TPS is low - normal for test environments")
        elif trad_tps < 10:
            print("   ✅ Traditional TPS is moderate - good for small-scale testing")
        else:
            print("   🚀 Traditional TPS is high - excellent performance!")
        
        if burst_result[0] > trad_tps * 5:
            print("   ⚡ Burst TPS much higher than traditional - system can handle bursts well")
        
        if rt_tps > trad_tps * 2:
            print("   🔥 Real-time TPS higher than traditional - good sustained performance during active periods")

def main():
    """Main analysis function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced TPS calculation tool")
    parser.add_argument("--pattern", default="performance_logs_*.jsonl", 
                       help="Log file pattern to analyze")
    
    args = parser.parse_args()
    
    calculator = ImprovedTPSCalculator()
    
    if calculator.load_events(args.pattern) > 0:
        calculator.comprehensive_tps_analysis()
    else:
        print("❌ No transaction events found in log files!")
        print("💡 Make sure your blockchain is generating transaction_ingress events")

if __name__ == "__main__":
    main()
