#!/usr/bin/env python3
"""
Quick Timing Demo - Demonstrates how to measure blockchain timing components
============================================================================

This script shows practical examples of measuring:
1. Consensus time
2. Signature verification time
3. Communication time

Run this after starting blockchain nodes to see actual timing measurements.
"""

import time
import sys
import os
import json
from datetime import datetime

# Add the blockchain directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def measure_consensus_simulation():
    """Simulate consensus timing measurement without actual quantum hardware"""
    print("🔬 Measuring Consensus Time (Simulation)...")
    
    # Simulate quantum annealing consensus process
    start_time = time.perf_counter()
    
    # 1. Node eligibility check (simulated)
    eligibility_start = time.perf_counter()
    num_nodes = 5
    eligible_nodes = [f"node_{i}" for i in range(num_nodes)]
    eligibility_time = (time.perf_counter() - eligibility_start) * 1000
    
    # 2. Score calculation (simulated)
    scoring_start = time.perf_counter()
    node_scores = {}
    for node in eligible_nodes:
        # Simulate complex scoring calculation
        time.sleep(0.001)  # 1ms per node scoring
        node_scores[node] = hash(node) % 100
    scoring_time = (time.perf_counter() - scoring_start) * 1000
    
    # 3. Quantum annealing simulation (simulated D-Wave timing)
    quantum_start = time.perf_counter()
    
    # Simulate quantum annealing process
    quantum_annealing_time_us = 20.0  # Typical D-Wave annealing time in microseconds
    num_reads = 50  # Number of quantum samples
    
    # Simulate annealing delay
    time.sleep(quantum_annealing_time_us / 1_000_000 * num_reads)  # Convert to seconds
    
    # Select winner (highest score)
    selected_forger = max(node_scores, key=node_scores.get)
    quantum_time = (time.perf_counter() - quantum_start) * 1000
    
    total_time = (time.perf_counter() - start_time) * 1000
    
    results = {
        'total_consensus_time_ms': total_time,
        'eligibility_check_time_ms': eligibility_time,
        'scoring_time_ms': scoring_time,
        'quantum_annealing_time_ms': quantum_time,
        'quantum_annealing_time_us': quantum_annealing_time_us,
        'num_quantum_reads': num_reads,
        'num_eligible_nodes': len(eligible_nodes),
        'selected_forger': selected_forger,
        'node_scores': node_scores
    }
    
    print(f"   ✅ Consensus completed in {total_time:.3f} ms")
    print(f"   📊 Selected forger: {selected_forger}")
    print(f"   ⚡ Quantum annealing: {quantum_annealing_time_us} μs")
    
    return results

def measure_signature_timing():
    """Measure actual signature generation and verification timing"""
    print("\n🔐 Measuring Signature Verification Time...")
    
    try:
        from cryptography.hazmat.primitives.asymmetric import rsa, padding
        from cryptography.hazmat.primitives import hashes, serialization
        
        # Generate RSA key pair
        key_generation_start = time.perf_counter()
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        key_generation_time = (time.perf_counter() - key_generation_start) * 1000
        
        message = b"Test transaction data for signature timing"
        
        # Measure signature generation
        signing_times = []
        verification_times = []
        
        for i in range(10):  # 10 iterations for average
            # Signature generation
            sign_start = time.perf_counter()
            signature = private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            sign_time = (time.perf_counter() - sign_start) * 1000
            signing_times.append(sign_time)
            
            # Signature verification
            verify_start = time.perf_counter()
            try:
                public_key.verify(
                    signature,
                    message,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                verification_success = True
            except:
                verification_success = False
            verify_time = (time.perf_counter() - verify_start) * 1000
            verification_times.append(verify_time)
        
        avg_sign_time = sum(signing_times) / len(signing_times)
        avg_verify_time = sum(verification_times) / len(verification_times)
        
        results = {
            'key_generation_time_ms': key_generation_time,
            'average_signing_time_ms': avg_sign_time,
            'average_verification_time_ms': avg_verify_time,
            'min_signing_time_ms': min(signing_times),
            'max_signing_time_ms': max(signing_times),
            'min_verification_time_ms': min(verification_times),
            'max_verification_time_ms': max(verification_times),
            'signing_throughput_per_second': 1000 / avg_sign_time,
            'verification_throughput_per_second': 1000 / avg_verify_time,
            'total_crypto_overhead_ms': avg_sign_time + avg_verify_time
        }
        
        print(f"   ✅ Key generation: {key_generation_time:.3f} ms")
        print(f"   ✏️ Average signing: {avg_sign_time:.3f} ms")
        print(f"   ✔️ Average verification: {avg_verify_time:.3f} ms")
        print(f"   🚀 Verification throughput: {results['verification_throughput_per_second']:.1f} verifications/sec")
        
        return results
        
    except ImportError:
        print("   ❌ Cryptography library not available for signature testing")
        return {}

def measure_communication_timing(api_ports=[11000, 11001]):
    """Measure network communication timing between nodes"""
    print(f"\n📡 Measuring Communication Time to ports {api_ports}...")
    
    try:
        import requests
        
        communication_results = []
        
        for port in api_ports:
            print(f"   Testing communication to port {port}...")
            
            # Test different endpoint types
            endpoints = [
                ('blockchain', f'http://localhost:{port}/api/v1/blockchain/'),
                ('transaction_pool', f'http://localhost:{port}/api/v1/transaction/pool/'),
                ('quantum_metrics', f'http://localhost:{port}/api/v1/blockchain/quantum-metrics/')
            ]
            
            port_results = {'port': port, 'endpoint_timings': []}
            
            for endpoint_name, url in endpoints:
                response_times = []
                
                for attempt in range(3):  # 3 attempts per endpoint
                    start_time = time.perf_counter()
                    try:
                        response = requests.get(url, timeout=5)
                        end_time = time.perf_counter()
                        response_time = (end_time - start_time) * 1000
                        success = response.status_code == 200
                        status_code = response.status_code
                    except Exception as e:
                        end_time = time.perf_counter()
                        response_time = (end_time - start_time) * 1000
                        success = False
                        status_code = 0
                    
                    response_times.append({
                        'attempt': attempt + 1,
                        'response_time_ms': response_time,
                        'success': success,
                        'status_code': status_code
                    })
                
                # Calculate endpoint statistics
                successful_times = [r['response_time_ms'] for r in response_times if r['success']]
                
                endpoint_stats = {
                    'endpoint': endpoint_name,
                    'url': url,
                    'attempts': response_times,
                    'average_response_time_ms': sum(successful_times) / len(successful_times) if successful_times else 0,
                    'min_response_time_ms': min(successful_times) if successful_times else 0,
                    'max_response_time_ms': max(successful_times) if successful_times else 0,
                    'success_rate': len(successful_times) / len(response_times)
                }
                
                port_results['endpoint_timings'].append(endpoint_stats)
                
                if successful_times:
                    print(f"     {endpoint_name}: {endpoint_stats['average_response_time_ms']:.3f} ms (success: {endpoint_stats['success_rate']:.1%})")
                else:
                    print(f"     {endpoint_name}: Failed to connect")
            
            communication_results.append(port_results)
        
        # Calculate overall statistics
        all_response_times = []
        for port_result in communication_results:
            for endpoint in port_result['endpoint_timings']:
                all_response_times.extend([r['response_time_ms'] for r in endpoint['attempts'] if r['success']])
        
        if all_response_times:
            overall_stats = {
                'ports_tested': api_ports,
                'total_successful_requests': len(all_response_times),
                'average_response_time_ms': sum(all_response_times) / len(all_response_times),
                'min_response_time_ms': min(all_response_times),
                'max_response_time_ms': max(all_response_times),
                'estimated_network_latency_ms': (sum(all_response_times) / len(all_response_times)) / 2,
                'communication_throughput_requests_per_second': 1000 / (sum(all_response_times) / len(all_response_times)),
                'port_results': communication_results
            }
            
            print(f"   ✅ Average response time: {overall_stats['average_response_time_ms']:.3f} ms")
            print(f"   🌐 Estimated network latency: {overall_stats['estimated_network_latency_ms']:.3f} ms")
            
            return overall_stats
        else:
            print("   ❌ No successful communications measured")
            return {'error': 'No successful communications', 'port_results': communication_results}
            
    except ImportError:
        print("   ❌ Requests library not available for communication testing")
        return {}

def measure_transaction_creation_timing():
    """Measure transaction creation and encoding timing"""
    print("\n💳 Measuring Transaction Creation Time...")
    
    try:
        # Simulate transaction creation process
        creation_times = []
        encoding_times = []
        
        for i in range(5):  # 5 transactions for averaging
            # Simulate transaction creation (wallet operations)
            creation_start = time.perf_counter()
            
            # Simulate complex transaction creation steps
            time.sleep(0.001)  # 1ms for transaction object creation
            time.sleep(0.002)  # 2ms for signature generation
            time.sleep(0.0005)  # 0.5ms for validation
            
            creation_time = (time.perf_counter() - creation_start) * 1000
            creation_times.append(creation_time)
            
            # Simulate transaction encoding
            encoding_start = time.perf_counter()
            
            # Simulate JSON encoding of transaction
            test_transaction = {
                'sender': f'sender_key_{i}',
                'receiver': f'receiver_key_{i}',
                'amount': 10.0 + i,
                'timestamp': time.time(),
                'signature': f'signature_data_{i}' * 100  # Simulate signature data
            }
            
            encoded_data = json.dumps(test_transaction)
            encoding_time = (time.perf_counter() - encoding_start) * 1000
            encoding_times.append(encoding_time)
        
        avg_creation_time = sum(creation_times) / len(creation_times)
        avg_encoding_time = sum(encoding_times) / len(encoding_times)
        
        results = {
            'average_creation_time_ms': avg_creation_time,
            'average_encoding_time_ms': avg_encoding_time,
            'total_transaction_preparation_time_ms': avg_creation_time + avg_encoding_time,
            'min_creation_time_ms': min(creation_times),
            'max_creation_time_ms': max(creation_times),
            'min_encoding_time_ms': min(encoding_times),
            'max_encoding_time_ms': max(encoding_times),
            'transaction_preparation_throughput_per_second': 1000 / (avg_creation_time + avg_encoding_time)
        }
        
        print(f"   ✅ Average creation time: {avg_creation_time:.3f} ms")
        print(f"   📦 Average encoding time: {avg_encoding_time:.3f} ms")
        print(f"   🚀 Preparation throughput: {results['transaction_preparation_throughput_per_second']:.1f} tx/sec")
        
        return results
        
    except Exception as e:
        print(f"   ❌ Error measuring transaction creation: {e}")
        return {}

def run_quick_timing_demo():
    """Run all timing demonstrations"""
    print("🚀 Quick Blockchain Timing Demo")
    print("=" * 40)
    print(f"⏰ Start time: {datetime.now().strftime('%H:%M:%S')}")
    
    demo_start = time.time()
    
    # Collect all results
    results = {
        'demo_metadata': {
            'timestamp': datetime.now().isoformat(),
            'demo_type': 'quick_timing_demo'
        }
    }
    
    # 1. Consensus timing
    results['consensus'] = measure_consensus_simulation()
    
    # 2. Signature timing
    results['signatures'] = measure_signature_timing()
    
    # 3. Communication timing
    results['communication'] = measure_communication_timing()
    
    # 4. Transaction creation timing
    results['transaction_creation'] = measure_transaction_creation_timing()
    
    demo_end = time.time()
    demo_duration = demo_end - demo_start
    
    # Summary
    print(f"\n📊 TIMING DEMO SUMMARY")
    print("=" * 40)
    print(f"⏱️ Total demo time: {demo_duration:.2f} seconds")
    
    if 'consensus' in results and results['consensus']:
        print(f"🔬 Consensus: {results['consensus']['total_consensus_time_ms']:.3f} ms")
    
    if 'signatures' in results and results['signatures']:
        print(f"🔐 Signature verification: {results['signatures']['average_verification_time_ms']:.3f} ms")
    
    if 'communication' in results and 'average_response_time_ms' in results['communication']:
        print(f"📡 Communication: {results['communication']['average_response_time_ms']:.3f} ms")
    
    if 'transaction_creation' in results and results['transaction_creation']:
        print(f"💳 Transaction creation: {results['transaction_creation']['total_transaction_preparation_time_ms']:.3f} ms")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"timing_demo_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to: {filename}")
    
    return results

if __name__ == "__main__":
    run_quick_timing_demo()
