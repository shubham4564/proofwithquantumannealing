#!/usr/bin/env python3
"""
Performance Metrics Integration Test

This script tests the complete performance metrics integration system
including real-time data collection, API endpoints, and validation.
"""

import requests
import time
import json
import sys
from datetime import datetime


class PerformanceMetricsTest:
    def __init__(self, node_ip="127.0.0.1", api_port=8001):
        self.base_url = f"http://{node_ip}:{api_port}/api/v1/blockchain"
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": []
        }
    
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results["test_details"].append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        if passed:
            self.test_results["tests_passed"] += 1
        else:
            self.test_results["tests_failed"] += 1
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            passed = response.status_code == 200
            self.log_test("Basic API Connectivity", passed, 
                         f"Status: {response.status_code}")
            return passed
        except Exception as e:
            self.log_test("Basic API Connectivity", False, f"Error: {e}")
            return False
    
    def test_quantum_metrics_endpoint(self):
        """Test quantum metrics endpoint"""
        try:
            response = requests.get(f"{self.base_url}/quantum-metrics/", timeout=5)
            passed = response.status_code == 200
            
            if passed:
                data = response.json()
                has_consensus_type = "consensus_type" in data
                has_scoring_weights = "scoring_weights" in data
                passed = has_consensus_type and has_scoring_weights
                self.log_test("Quantum Metrics Endpoint", passed,
                             f"Has consensus_type: {has_consensus_type}, Has scoring_weights: {has_scoring_weights}")
            else:
                self.log_test("Quantum Metrics Endpoint", False,
                             f"HTTP {response.status_code}")
            return passed
        except Exception as e:
            self.log_test("Quantum Metrics Endpoint", False, f"Error: {e}")
            return False
    
    def test_performance_metrics_endpoint(self):
        """Test enhanced performance metrics endpoint"""
        try:
            response = requests.get(f"{self.base_url}/performance-metrics/", timeout=5)
            passed = response.status_code == 200
            
            if passed:
                data = response.json()
                has_enhanced = data.get("enhanced_metrics_available", False)
                has_real_time = "real_time_data" in data
                has_quantum_data = "quantum_consensus" in data
                
                details = f"Enhanced: {has_enhanced}, Real-time: {has_real_time}, Quantum: {has_quantum_data}"
                if has_enhanced:
                    metrics_data = data.get("metrics", {})
                    has_timing = "timing_metrics" in metrics_data
                    has_pool = "transaction_pool_metrics" in metrics_data
                    details += f", Timing: {has_timing}, Pool: {has_pool}"
                
                self.log_test("Performance Metrics Endpoint", passed, details)
            else:
                self.log_test("Performance Metrics Endpoint", False,
                             f"HTTP {response.status_code}")
            return passed
        except Exception as e:
            self.log_test("Performance Metrics Endpoint", False, f"Error: {e}")
            return False
    
    def test_transaction_pool_endpoint(self):
        """Test transaction pool metrics endpoint"""
        try:
            response = requests.get(f"{self.base_url}/transaction-pool/", timeout=5)
            passed = response.status_code == 200
            
            if passed:
                data = response.json()
                has_pool_stats = "transaction_pool_stats" in data
                has_timing = "timing_metrics" in data
                has_capacity = "capacity_analysis" in data
                
                details = f"Pool stats: {has_pool_stats}, Timing: {has_timing}, Capacity: {has_capacity}"
                if has_timing:
                    timing = data["timing_metrics"]
                    forge_interval = timing.get("forge_interval_ms", 0)
                    details += f", Forge interval: {forge_interval}ms"
                
                self.log_test("Transaction Pool Endpoint", passed, details)
            else:
                self.log_test("Transaction Pool Endpoint", False,
                             f"HTTP {response.status_code}")
            return passed
        except Exception as e:
            self.log_test("Transaction Pool Endpoint", False, f"Error: {e}")
            return False
    
    def test_real_time_data_consistency(self):
        """Test that real-time data is consistent across calls"""
        try:
            # Make two calls 1 second apart
            response1 = requests.get(f"{self.base_url}/performance-metrics/", timeout=5)
            time.sleep(1)
            response2 = requests.get(f"{self.base_url}/performance-metrics/", timeout=5)
            
            if response1.status_code != 200 or response2.status_code != 200:
                self.log_test("Real-time Data Consistency", False,
                             "Failed to get both responses")
                return False
            
            data1 = response1.json()
            data2 = response2.json()
            
            # Check if timestamps are different (indicating real-time updates)
            timestamp1 = data1.get("metrics", {}).get("timestamp")
            timestamp2 = data2.get("metrics", {}).get("timestamp")
            
            timestamps_different = timestamp1 != timestamp2
            self.log_test("Real-time Data Consistency", timestamps_different,
                         f"Timestamps differ: {timestamps_different}")
            return timestamps_different
        except Exception as e:
            self.log_test("Real-time Data Consistency", False, f"Error: {e}")
            return False
    
    def test_performance_metrics_data_structure(self):
        """Test the structure of performance metrics data"""
        try:
            response = requests.get(f"{self.base_url}/performance-metrics/", timeout=5)
            if response.status_code != 200:
                self.log_test("Performance Data Structure", False,
                             f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            
            # Check required fields
            required_fields = ["enhanced_metrics_available", "quantum_consensus"]
            optional_enhanced_fields = ["metrics", "real_time_data"]
            
            has_required = all(field in data for field in required_fields)
            
            details = f"Required fields present: {has_required}"
            
            if data.get("enhanced_metrics_available"):
                has_enhanced = all(field in data for field in optional_enhanced_fields)
                details += f", Enhanced fields present: {has_enhanced}"
                
                if "metrics" in data:
                    metrics = data["metrics"]
                    expected_metrics = ["timestamp", "timing_metrics", "transaction_pool_metrics"]
                    has_metric_fields = any(field in metrics for field in expected_metrics)
                    details += f", Metric fields present: {has_metric_fields}"
                    has_required = has_required and has_enhanced and has_metric_fields
            
            self.log_test("Performance Data Structure", has_required, details)
            return has_required
        except Exception as e:
            self.log_test("Performance Data Structure", False, f"Error: {e}")
            return False
    
    def test_quantum_annealing_configuration(self):
        """Test quantum annealing specific configuration"""
        try:
            response = requests.get(f"{self.base_url}/quantum-metrics/", timeout=5)
            if response.status_code != 200:
                self.log_test("Quantum Annealing Config", False,
                             f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            
            # Check for quantum-specific fields
            consensus_type = data.get("consensus_type")
            is_quantum = consensus_type and "quantum" in consensus_type.lower()
            
            has_scoring = "scoring_weights" in data
            has_protocol = "protocol_parameters" in data
            
            # Check for 450ms configuration
            timing_correct = False
            slot_duration = "unknown"
            if "protocol_parameters" in data:
                params = data["protocol_parameters"]
                slot_duration = params.get("slot_duration_ms", "None")
                timing_correct = slot_duration == 450
            
            details = f"Consensus: {consensus_type}, Scoring: {has_scoring}, Protocol: {has_protocol}, Timing: {slot_duration}ms"
            
            passed = is_quantum and has_scoring and timing_correct
            self.log_test("Quantum Annealing Config", passed, details)
            return passed
        except Exception as e:
            self.log_test("Quantum Annealing Config", False, f"Error: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests and provide a comprehensive report"""
        print("🧪 Performance Metrics Integration Test Suite")
        print("=" * 60)
        print()
        
        # Run all tests
        tests = [
            self.test_basic_connectivity,
            self.test_quantum_metrics_endpoint,
            self.test_performance_metrics_endpoint,
            self.test_transaction_pool_endpoint,
            self.test_real_time_data_consistency,
            self.test_performance_metrics_data_structure,
            self.test_quantum_annealing_configuration
        ]
        
        for test in tests:
            test()
            print()
        
        # Summary
        total_tests = self.test_results["tests_passed"] + self.test_results["tests_failed"]
        pass_rate = (self.test_results["tests_passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print("📊 Test Summary")
        print("-" * 30)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.test_results['tests_passed']} ✅")
        print(f"Failed: {self.test_results['tests_failed']} ❌")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print()
        
        if pass_rate >= 80:
            print("🎉 Performance metrics integration is working well!")
        elif pass_rate >= 60:
            print("⚠️ Performance metrics partially working - some issues detected")
        else:
            print("🚨 Performance metrics integration has significant issues")
        
        return self.test_results


def main():
    """Main test execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test performance metrics integration")
    parser.add_argument("--ip", default="127.0.0.1", help="Node IP address")
    parser.add_argument("--port", type=int, default=8001, help="API port")
    parser.add_argument("--output", help="Output file for test results (JSON)")
    
    args = parser.parse_args()
    
    print(f"🎯 Testing performance metrics at {args.ip}:{args.port}")
    print()
    
    tester = PerformanceMetricsTest(args.ip, args.port)
    results = tester.run_comprehensive_test()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"📁 Test results saved to {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if results["tests_failed"] == 0 else 1)


if __name__ == "__main__":
    main()
