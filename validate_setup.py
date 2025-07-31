#!/usr/bin/env python3
"""
Blockchain Network Setup Validator
=================================

This script validates that your system is ready to run the blockchain network.

Usage:
    python validate_setup.py
"""

import os
import sys
import subprocess
import importlib
import socket
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print("✅ Python version:", f"{version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print("❌ Python version:", f"{version.major}.{version.minor}.{version.micro}")
        print("   Required: Python 3.8 or higher")
        return False

def check_required_modules():
    """Check if required Python modules are available"""
    required_modules = [
        'requests',
        'json',
        'threading',
        'socket',
        'time',
        'concurrent.futures',
        'dataclasses'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ Module: {module}")
        except ImportError:
            print(f"❌ Module: {module} (missing)")
            missing_modules.append(module)
    
    return len(missing_modules) == 0, missing_modules

def check_blockchain_modules():
    """Check if blockchain-specific modules are available"""
    blockchain_dir = Path(__file__).parent / "blockchain"
    
    if not blockchain_dir.exists():
        print("❌ Blockchain directory not found")
        return False
    
    # Add blockchain directory to Python path
    sys.path.insert(0, str(blockchain_dir))
    
    blockchain_modules = [
        'blockchain.blockchain',
        'blockchain.transaction.wallet',
        'blockchain.utils.logger',
        'blockchain.node'
    ]
    
    missing_modules = []
    
    for module in blockchain_modules:
        try:
            importlib.import_module(module)
            print(f"✅ Blockchain module: {module}")
        except ImportError as e:
            print(f"❌ Blockchain module: {module} (error: {e})")
            missing_modules.append(module)
    
    return len(missing_modules) == 0, missing_modules

def check_port_availability():
    """Check if required ports are available"""
    required_ports = [
        8050, 8051, 8052, 8053, 8054, 8055,  # API ports
        10000, 10001, 10002, 10003, 10004, 10005,  # P2P ports
        12000, 12001, 12002, 12003, 12004, 12005,  # Gossip ports
        13000, 13001, 13002, 13003, 13004, 13005,  # TPU ports
        14000, 14001, 14002, 14003, 14004, 14005   # TVU ports
    ]
    
    available_ports = []
    unavailable_ports = []
    
    for port in required_ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('127.0.0.1', port))
                available_ports.append(port)
                if port <= 8055:  # Only show status for API ports to avoid spam
                    print(f"✅ Port {port} available")
        except OSError:
            unavailable_ports.append(port)
            if port <= 8055:  # Only show status for API ports to avoid spam
                print(f"❌ Port {port} in use")
    
    if unavailable_ports:
        print(f"⚠️ {len(unavailable_ports)} ports are in use (may need cleanup)")
        if len(unavailable_ports) > 10:
            print("   Run './stop_network.sh' to clean up previous blockchain processes")
    
    return len(unavailable_ports) < len(required_ports) * 0.5  # Allow up to 50% ports to be in use

def check_genesis_config():
    """Check if genesis configuration exists"""
    genesis_dir = Path(__file__).parent / "genesis_config"
    genesis_file = genesis_dir / "genesis.json"
    
    if genesis_file.exists():
        print("✅ Genesis configuration found")
        return True
    else:
        print("⚠️ Genesis configuration not found (will be created automatically)")
        return True  # Not a blocker, will be created

def check_scripts_executable():
    """Check if startup scripts are executable"""
    scripts = [
        "start_single_computer_network.sh",
        "start_distributed_node.sh", 
        "stop_network.sh",
        "network_health_checker.py"
    ]
    
    all_executable = True
    
    for script in scripts:
        script_path = Path(__file__).parent / script
        if script_path.exists():
            if os.access(script_path, os.X_OK):
                print(f"✅ Script executable: {script}")
            else:
                print(f"❌ Script not executable: {script}")
                print(f"   Run: chmod +x {script}")
                all_executable = False
        else:
            print(f"❌ Script missing: {script}")
            all_executable = False
    
    return all_executable

def check_system_resources():
    """Check available system resources"""
    try:
        import psutil
        
        # Check RAM
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)
        
        if available_gb >= 4:
            print(f"✅ Available RAM: {available_gb:.1f} GB")
        else:
            print(f"⚠️ Available RAM: {available_gb:.1f} GB (recommend 4+ GB)")
        
        # Check CPU cores
        cpu_count = psutil.cpu_count()
        print(f"✅ CPU cores: {cpu_count}")
        
        # Check disk space
        disk = psutil.disk_usage('.')
        available_disk_gb = disk.free / (1024**3)
        
        if available_disk_gb >= 1:
            print(f"✅ Available disk: {available_disk_gb:.1f} GB")
        else:
            print(f"⚠️ Available disk: {available_disk_gb:.1f} GB (recommend 1+ GB)")
        
        return True
        
    except ImportError:
        print("⚠️ System resource check skipped (psutil not available)")
        print("   Install with: pip install psutil")
        return True

def check_network_connectivity():
    """Check basic network connectivity for distributed mode"""
    try:
        # Test local network interface
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        
        print(f"✅ Local IP address: {local_ip}")
        
        # Check if we can bind to the local IP
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((local_ip, 0))  # Bind to any available port
            print("✅ Can bind to local IP address")
        except OSError:
            print("⚠️ Cannot bind to local IP address")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Network connectivity check failed: {e}")
        return False

def main():
    print("🔍 Blockchain Network Setup Validator")
    print("=" * 50)
    
    checks = []
    
    print("\n📋 System Requirements:")
    checks.append(check_python_version())
    
    print("\n📦 Python Modules:")
    modules_ok, missing = check_required_modules()
    checks.append(modules_ok)
    
    if missing:
        print(f"\n💡 Install missing modules with:")
        print(f"   pip install {' '.join(missing)}")
    
    print("\n🔗 Blockchain Modules:")
    blockchain_ok, blockchain_missing = check_blockchain_modules()
    checks.append(blockchain_ok)
    
    print("\n🌐 Network Ports:")
    checks.append(check_port_availability())
    
    print("\n📁 Configuration Files:")
    checks.append(check_genesis_config())
    
    print("\n🔧 Executable Scripts:")
    checks.append(check_scripts_executable())
    
    print("\n💻 System Resources:")
    checks.append(check_system_resources())
    
    print("\n🌍 Network Connectivity:")
    checks.append(check_network_connectivity())
    
    # Summary
    passed = sum(checks)
    total = len(checks)
    
    print("\n" + "=" * 50)
    print(f"📊 VALIDATION SUMMARY: {passed}/{total} checks passed")
    
    if passed == total:
        print("🟢 READY: System is ready for blockchain network deployment!")
        print("\n🚀 Next steps:")
        print("   Single computer: ./start_single_computer_network.sh")
        print("   Distributed:     ./start_distributed_node.sh <computer_id>")
        print("   Health check:    python network_health_checker.py --mode single")
        return True
    else:
        print("🟡 ISSUES FOUND: Some issues need to be resolved before deployment")
        failed = total - passed
        print(f"   {failed} check(s) failed - see details above")
        
        if not blockchain_ok:
            print("\n🔧 To fix blockchain module issues:")
            print("   1. Ensure you're in the correct directory")
            print("   2. Check that blockchain/ directory exists")
            print("   3. Install missing dependencies")
        
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Validation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        sys.exit(1)
