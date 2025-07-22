#!/usr/bin/env python3
"""
Node Stability Test

This script tests the node stability improvements and validates that nodes
don't shut down unexpectedly.
"""

import os
import sys
import time
import subprocess
import requests
import signal
from datetime import datetime

class NodeStabilityTester:
    def __init__(self):
        self.test_nodes = []
        self.base_port = 12000  # Use different ports to avoid conflicts
        
    def cleanup(self):
        """Clean up any running test nodes"""
        print("🧹 Cleaning up test nodes...")
        for proc in self.test_nodes:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
        
        # Also kill any stray processes
        subprocess.run(["pkill", "-f", "run_node.py"], capture_output=True)
        print("✅ Cleanup completed")
    
    def start_test_node(self, node_id):
        """Start a single test node"""
        node_port = self.base_port + node_id
        api_port = self.base_port + 1000 + node_id
        
        print(f"  Starting Node {node_id}: P2P:{node_port}, API:{api_port}")
        
        proc = subprocess.Popen([
            sys.executable, "run_node.py",
            "--ip", "localhost",
            "--node_port", str(node_port),
            "--api_port", str(api_port)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        self.test_nodes.append(proc)
        return proc, api_port
    
    def test_node_startup_stability(self):
        """Test that nodes start up properly and don't crash immediately"""
        print("\n🔍 Testing Node Startup Stability")
        print("=" * 50)
        
        success_count = 0
        total_nodes = 3
        
        for i in range(total_nodes):
            try:
                proc, api_port = self.start_test_node(i)
                
                # Wait for startup
                time.sleep(3)
                
                # Check if process is still running
                if proc.poll() is None:
                    print(f"  ✅ Node {i} started successfully")
                    
                    # Test API response
                    try:
                        response = requests.get(f"http://localhost:{api_port}/ping/", timeout=5)
                        if response.status_code == 200:
                            print(f"  ✅ Node {i} API responding correctly")
                            success_count += 1
                        else:
                            print(f"  ❌ Node {i} API returned status {response.status_code}")
                    except Exception as e:
                        print(f"  ❌ Node {i} API not responding: {e}")
                else:
                    print(f"  ❌ Node {i} crashed immediately (exit code: {proc.returncode})")
                    stdout, stderr = proc.communicate()
                    if stderr:
                        print(f"    Error: {stderr[:200]}...")
                        
            except Exception as e:
                print(f"  ❌ Failed to start Node {i}: {e}")
        
        print(f"\n📊 Startup Test Results: {success_count}/{total_nodes} nodes successful")
        return success_count == total_nodes
    
    def test_node_longevity(self):
        """Test that nodes stay running for an extended period"""
        print("\n⏱️  Testing Node Longevity (60 seconds)")
        print("=" * 50)
        
        if not self.test_nodes:
            print("❌ No nodes to test")
            return False
        
        # Monitor nodes for 60 seconds
        start_time = time.time()
        check_interval = 10  # Check every 10 seconds
        last_check = start_time
        
        alive_counts = []
        
        while time.time() - start_time < 60:
            current_time = time.time()
            
            if current_time - last_check >= check_interval:
                alive_count = 0
                for i, proc in enumerate(self.test_nodes):
                    if proc.poll() is None:
                        alive_count += 1
                    else:
                        print(f"  ⚠️  Node {i} died (exit code: {proc.returncode})")
                
                elapsed = int(current_time - start_time)
                print(f"  📊 t+{elapsed}s: {alive_count}/{len(self.test_nodes)} nodes alive")
                alive_counts.append(alive_count)
                last_check = current_time
            
            time.sleep(1)
        
        # Final check
        final_alive = sum(1 for proc in self.test_nodes if proc.poll() is None)
        print(f"\n📊 Longevity Test Results: {final_alive}/{len(self.test_nodes)} nodes survived 60 seconds")
        
        return final_alive == len(self.test_nodes)
    
    def test_port_conflict_handling(self):
        """Test that port conflicts are handled gracefully"""
        print("\n🔌 Testing Port Conflict Handling")
        print("=" * 50)
        
        # Start a node on specific ports
        test_port = 12100
        api_test_port = 13100
        
        print(f"  Starting first node on ports {test_port}/{api_test_port}")
        proc1 = subprocess.Popen([
            sys.executable, "run_node.py",
            "--ip", "localhost",
            "--node_port", str(test_port),
            "--api_port", str(api_test_port)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        time.sleep(3)
        
        # Try to start second node on same ports (should fail gracefully)
        print(f"  Trying to start second node on SAME ports (should fail gracefully)")
        proc2 = subprocess.Popen([
            sys.executable, "run_node.py",
            "--ip", "localhost",
            "--node_port", str(test_port),  # Same port!
            "--api_port", str(api_test_port)   # Same port!
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for second process to exit
        stdout2, stderr2 = proc2.communicate()
        
        # Check results
        if proc2.returncode == 1:  # Should exit with error code 1
            print("  ✅ Second node failed gracefully with exit code 1")
            if "already in use" in stderr2:
                print("  ✅ Proper error message displayed")
                result = True
            else:
                print("  ⚠️  Error message could be improved")
                result = True
        else:
            print(f"  ❌ Second node exit code: {proc2.returncode}")
            print(f"  STDERR: {stderr2}")
            result = False
        
        # Clean up
        proc1.terminate()
        proc1.wait()
        
        return result
    
    def test_health_monitoring_integration(self):
        """Test that health monitoring correctly detects node states"""
        print("\n🩺 Testing Health Monitoring Integration")
        print("=" * 50)
        
        # Start a few nodes using the start_nodes script
        print("  Starting nodes with health monitoring...")
        starter_proc = subprocess.Popen([
            sys.executable, "demos/start_nodes.py",
            "--nodes", "2",
            "--base-node-port", "12200",
            "--base-api-port", "13200",
            "--health-interval", "5",
            "--no-wait"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        stdout, stderr = starter_proc.communicate()
        
        if starter_proc.returncode == 0:
            print("  ✅ Nodes started successfully with health monitoring")
            
            # Wait a bit and test the endpoints
            time.sleep(5)
            
            healthy_count = 0
            for port_offset in [0, 1]:
                api_port = 13200 + port_offset
                try:
                    response = requests.get(f"http://localhost:{api_port}/ping/", timeout=3)
                    if response.status_code == 200:
                        healthy_count += 1
                        print(f"  ✅ Node on port {api_port} is healthy")
                    else:
                        print(f"  ❌ Node on port {api_port} returned status {response.status_code}")
                except Exception as e:
                    print(f"  ❌ Node on port {api_port} not responding: {e}")
            
            print(f"  📊 Health check result: {healthy_count}/2 nodes healthy")
            result = healthy_count > 0
        else:
            print(f"  ❌ Failed to start nodes: {stderr}")
            result = False
        
        # Cleanup
        subprocess.run(["pkill", "-f", "run_node.py"], capture_output=True)
        
        return result
    
    def run_all_tests(self):
        """Run all stability tests"""
        print("🧪 BLOCKCHAIN NODE STABILITY TEST SUITE")
        print("=" * 60)
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Set up signal handler for cleanup
        signal.signal(signal.SIGINT, lambda s, f: (self.cleanup(), sys.exit(1)))
        
        try:
            tests = [
                ("Startup Stability", self.test_node_startup_stability),
                ("Node Longevity", self.test_node_longevity),
                ("Port Conflict Handling", self.test_port_conflict_handling),
                ("Health Monitoring Integration", self.test_health_monitoring_integration),
            ]
            
            results = []
            
            for test_name, test_func in tests:
                try:
                    result = test_func()
                    results.append((test_name, result))
                    if result:
                        print(f"✅ {test_name}: PASSED")
                    else:
                        print(f"❌ {test_name}: FAILED")
                except Exception as e:
                    print(f"💥 {test_name}: ERROR - {e}")
                    results.append((test_name, False))
                
                print()
            
            # Summary
            passed = sum(1 for _, result in results if result)
            total = len(results)
            
            print("=" * 60)
            print("📊 TEST SUMMARY")
            print("=" * 60)
            for test_name, result in results:
                status = "✅ PASSED" if result else "❌ FAILED"
                print(f"  {test_name}: {status}")
            
            print(f"\nOverall: {passed}/{total} tests passed")
            
            if passed == total:
                print("🎉 ALL TESTS PASSED! Nodes are stable.")
                return True
            else:
                print("⚠️  Some tests failed. Node stability needs improvement.")
                return False
                
        finally:
            self.cleanup()

def main():
    """Main function"""
    tester = NodeStabilityTester()
    
    # Change to blockchain directory
    os.chdir("/Users/shubham/Documents/proofwithquantumannealing/blockchain")
    
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
