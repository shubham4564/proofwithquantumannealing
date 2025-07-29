import sys
import signal
import socket
import time
from blockchain.node import Node
from blockchain.utils.logger import logger
from initialize_performance_metrics import (
    initialize_performance_metrics,
    cleanup_performance_metrics,
    validate_metrics_integration
)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info({"message": f"Received signal {signum}, shutting down gracefully"})
    
    # Clean up performance metrics if they were initialized
    if hasattr(signal_handler, 'node') and signal_handler.node:
        try:
            cleanup_performance_metrics(signal_handler.node)
        except Exception as e:
            logger.error({"message": f"Error during metrics cleanup: {e}"})
    
    sys.exit(0)

def check_port_available(ip, port):
    """Check if a port is available for binding"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((ip, port))
            return True
    except OSError:
        return False

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run blockchain node.")
    parser.add_argument(
        "--ip",
        required=True,
        type=str,
        help="The node IP address. Use 0.0.0.0 in Docker, and localhost for native.",
    )
    parser.add_argument(
        "--node_port",
        required=True,
        type=int,
        help="The port used for P2P communication between nodes.",
    )
    parser.add_argument(
        "--api_port",
        required=True,
        type=int,
        help="Port on which the Node API runs.",
    )
    parser.add_argument(
        "--key_file",
        required=False,
        type=str,
        default=None,
        help="The path to the key file of the node (optional).",
    )
    parser.add_argument(
        "--p2p_mode",
        required=False,
        type=str,
        choices=["enhanced", "legacy"],
        default="enhanced",
        help="P2P communication mode: 'enhanced' for Bitcoin-style INV/GETDATA, 'legacy' for direct broadcast (default: enhanced).",
    )
    args = parser.parse_args()

    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Check port availability before starting
        if not check_port_available(args.ip, args.node_port):
            logger.error({
                "message": f"P2P port {args.node_port} is already in use on {args.ip}",
                "port": args.node_port,
                "ip": args.ip
            })
            print(f"❌ Error: P2P port {args.node_port} is already in use on {args.ip}")
            sys.exit(1)

        if not check_port_available(args.ip, args.api_port):
            logger.error({
                "message": f"API port {args.api_port} is already in use on {args.ip}",
                "port": args.api_port,
                "ip": args.ip
            })
            print(f"❌ Error: API port {args.api_port} is already in use on {args.ip}")
            sys.exit(1)

        logger.info({
            "message": "Starting blockchain node",
            "node_port": args.node_port,
            "api_port": args.api_port,
            "ip": args.ip,
            "key_file": args.key_file,
            "p2p_mode": args.p2p_mode
        })

        # Create and start the node
        node = Node(args.ip, args.node_port, args.key_file)
        
        # Store node reference for cleanup in signal handler
        signal_handler.node = node

        # Start P2P communication with specified mode
        logger.info({"message": f"Starting P2P communication in {args.p2p_mode} mode"})
        if args.p2p_mode == "enhanced":
            node.start_p2p(enhanced=True)
            print(f"🚀 Enhanced P2P started with Bitcoin-style INV/GETDATA protocol")
        else:
            node.start_p2p(enhanced=False)
            print(f"🚀 Legacy P2P started with direct broadcast")

        # Start API server (this now runs in a separate thread)
        logger.info({"message": "Starting API server"})
        node.start_node_api(args.api_port)

        # Initialize performance metrics integration AFTER node is fully running
        logger.info({"message": "Initializing performance metrics collection"})
        metrics_success = initialize_performance_metrics(node)
        
        if metrics_success:
            logger.info({"message": "✓ Performance metrics initialized successfully"})
            print("📊 Performance metrics collection enabled")
            
            # Validate the integration
            validation = validate_metrics_integration(node)
            logger.info({"message": f"Metrics validation: {validation['overall_status']}", "details": validation["details"]})
            
            if validation["overall_status"] == "fully_integrated":
                print("✅ All metrics systems fully integrated")
            elif validation["overall_status"] == "partially_integrated":
                print("⚠️ Metrics partially integrated - some features may be limited")
            else:
                print("❌ Metrics integration validation failed")
        else:
            logger.warning({"message": "Performance metrics initialization failed - node will run without enhanced metrics"})
            print("⚠️ Running without enhanced performance metrics")

        # Keep the main thread alive
        logger.info({"message": "Node fully initialized, running..."})
        print(f"🌐 Node running at {args.ip}:{args.node_port} (P2P) and {args.ip}:{args.api_port} (API)")
        if metrics_success:
            print("📈 Enhanced API endpoints available:")
            print(f"   - Performance metrics: http://{args.ip}:{args.api_port}/api/v1/blockchain/performance-metrics/")
            print(f"   - Transaction pool: http://{args.ip}:{args.api_port}/api/v1/blockchain/transaction-pool/")
            print(f"   - Quantum metrics: http://{args.ip}:{args.api_port}/api/v1/blockchain/quantum-metrics/")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info({"message": "Node shutdown requested by user"})
            print("\n🛑 Node shutdown requested")
            cleanup_performance_metrics(node)
            sys.exit(0)

    except KeyboardInterrupt:
        logger.info({"message": "Node shutdown requested by user"})
        print("\n🛑 Node shutdown requested")
        if 'node' in locals():
            cleanup_performance_metrics(node)
        sys.exit(0)
    except OSError as e:
        if "Address already in use" in str(e):
            logger.error({
                "message": "Port conflict detected during startup",
                "error": str(e),
                "node_port": args.node_port,
                "api_port": args.api_port
            })
            print(f"❌ Port conflict: {e}")
            print(f"   P2P Port: {args.node_port}")
            print(f"   API Port: {args.api_port}")
            print("   Try using different ports or stop conflicting processes")
        else:
            logger.error({
                "message": "Network error during startup",
                "error": str(e)
            })
            print(f"❌ Network error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error({
            "message": "Unexpected error during node startup",
            "error": str(e),
            "error_type": type(e).__name__
        })
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
