#!/usr/bin/env python3
"""
Blockchain Metrics Exporter

This utility exports comprehensive blockchain metrics in multiple formats:
- JSON reports for programmatic access
- CSV files for spreadsheet analysis
- HTML reports for web viewing
- Markdown reports for documentation

Usage:
    python metrics_exporter.py --format json
    python metrics_exporter.py --format csv --output ./exports/
    python metrics_exporter.py --format html --include-charts
    python metrics_exporter.py --format all --duration 24h
"""

import json
import csv
import time
import requests
import argparse
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import base64


class MetricsExporter:
    """Export blockchain metrics in various formats"""
    
    def __init__(self, num_nodes: int = 3, base_api_port: int = 8050):
        self.num_nodes = num_nodes
        self.base_api_port = base_api_port
        self.collected_data = {
            'metadata': {},
            'node_metrics': {},
            'network_summary': {},
            'performance_metrics': {},
            'quantum_consensus': {},
            'historical_data': []
        }
    
    def collect_current_metrics(self) -> Dict:
        """Collect current metrics from all nodes"""
        print("📊 Collecting current metrics from blockchain network...")
        
        # Metadata
        self.collected_data['metadata'] = {
            'collection_time': datetime.now().isoformat(),
            'num_nodes': self.num_nodes,
            'base_api_port': self.base_api_port,
            'exporter_version': '1.0.0'
        }
        
        # Node-specific metrics
        node_metrics = {}
        online_nodes = 0
        total_blocks = []
        response_times = []
        
        for node_id in range(self.num_nodes):
            api_port = self.base_api_port + node_id
            node_key = f"node_{node_id}"
            
            try:
                # Basic blockchain state
                start_time = time.time()
                blockchain_response = requests.get(f"http://localhost:{api_port}/api/v1/blockchain/", timeout=5)
                response_time = time.time() - start_time
                
                if blockchain_response.status_code == 200:
                    blockchain_data = blockchain_response.json()
                    blocks = blockchain_data.get('blocks', [])
                    
                    # Quantum consensus metrics
                    quantum_response = requests.get(f"http://localhost:{api_port}/api/v1/blockchain/quantum-metrics/", timeout=5)
                    quantum_data = quantum_response.json() if quantum_response.status_code == 200 else {}
                    
                    node_metrics[node_key] = {
                        'status': 'online',
                        'api_port': api_port,
                        'response_time': response_time,
                        'block_count': len(blocks),
                        'latest_block': blocks[-1] if blocks else None,
                        'quantum_metrics': quantum_data,
                        'blockchain_state': blockchain_data
                    }
                    
                    online_nodes += 1
                    total_blocks.append(len(blocks))
                    response_times.append(response_time)
                    
                else:
                    node_metrics[node_key] = {
                        'status': 'error',
                        'api_port': api_port,
                        'error_code': blockchain_response.status_code,
                        'response_time': response_time
                    }
                    
            except Exception as e:
                node_metrics[node_key] = {
                    'status': 'offline',
                    'api_port': api_port,
                    'error': str(e),
                    'response_time': 999.0
                }
        
        self.collected_data['node_metrics'] = node_metrics
        
        # Network summary
        self.collected_data['network_summary'] = {
            'total_nodes': self.num_nodes,
            'online_nodes': online_nodes,
            'offline_nodes': self.num_nodes - online_nodes,
            'availability_percentage': (online_nodes / self.num_nodes) * 100,
            'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'block_sync_status': {
                'min_blocks': min(total_blocks) if total_blocks else 0,
                'max_blocks': max(total_blocks) if total_blocks else 0,
                'sync_difference': max(total_blocks) - min(total_blocks) if total_blocks else 0
            }
        }
        
        # Performance metrics (run quick test)
        self.collect_performance_metrics()
        
        # Quantum consensus analysis
        self.analyze_quantum_consensus()
        
        return self.collected_data
    
    def collect_performance_metrics(self):
        """Collect performance metrics through quick testing"""
        print("⚡ Running performance analysis...")
        
        try:
            # Quick transaction test (simplified)
            from blockchain.transaction.wallet import Wallet
            from blockchain.utils.helpers import BlockchainUtils
            
            sender = Wallet()
            receiver = Wallet()
            
            # Measure transaction creation time
            start_time = time.time()
            transaction = sender.create_transaction(receiver.public_key_string(), 1.0, "TRANSFER")
            creation_time = time.time() - start_time
            
            # Test transaction submission to first available node
            for node_id in range(self.num_nodes):
                api_port = self.base_api_port + node_id
                try:
                    package = {"transaction": BlockchainUtils.encode(transaction)}
                    submit_start = time.time()
                    response = requests.post(f"http://localhost:{api_port}/api/v1/transaction/create/", 
                                           json=package, timeout=10)
                    submit_time = time.time() - submit_start
                    
                    self.collected_data['performance_metrics'] = {
                        'transaction_creation_time': creation_time,
                        'transaction_submit_time': submit_time,
                        'total_transaction_time': creation_time + submit_time,
                        'submission_success': response.status_code == 200,
                        'test_node': f"node_{node_id}",
                        'estimated_tps': 1.0 / (creation_time + submit_time) if (creation_time + submit_time) > 0 else 0
                    }
                    break
                except:
                    continue
            
        except Exception as e:
            self.collected_data['performance_metrics'] = {
                'error': f"Performance test failed: {str(e)}",
                'transaction_creation_time': 0,
                'transaction_submit_time': 0,
                'total_transaction_time': 0,
                'submission_success': False,
                'estimated_tps': 0
            }
    
    def analyze_quantum_consensus(self):
        """Analyze quantum consensus metrics across all nodes"""
        print("🔬 Analyzing quantum consensus metrics...")
        
        consensus_analysis = {
            'total_probe_count': 0,
            'active_nodes_distribution': {},
            'node_scores_summary': {},
            'consensus_health': 'unknown'
        }
        
        all_node_scores = []
        active_nodes_counts = []
        
        for node_key, node_data in self.collected_data['node_metrics'].items():
            if node_data.get('status') == 'online' and 'quantum_metrics' in node_data:
                quantum_data = node_data['quantum_metrics']
                
                # Aggregate probe counts
                probe_count = quantum_data.get('probe_count', 0)
                consensus_analysis['total_probe_count'] += probe_count
                
                # Track active nodes
                active_nodes = quantum_data.get('active_nodes', 0)
                active_nodes_counts.append(active_nodes)
                
                # Collect node scores
                node_scores = quantum_data.get('node_scores', {})
                for node_id, score_data in node_scores.items():
                    if isinstance(score_data, dict):
                        suitability_score = score_data.get('suitability_score', 0)
                        all_node_scores.append(suitability_score)
        
        # Calculate consensus health
        if active_nodes_counts:
            avg_active_nodes = sum(active_nodes_counts) / len(active_nodes_counts)
            if avg_active_nodes >= self.num_nodes * 0.8:
                consensus_analysis['consensus_health'] = 'excellent'
            elif avg_active_nodes >= self.num_nodes * 0.6:
                consensus_analysis['consensus_health'] = 'good'
            else:
                consensus_analysis['consensus_health'] = 'poor'
        
        # Node scores summary
        if all_node_scores:
            consensus_analysis['node_scores_summary'] = {
                'average_score': sum(all_node_scores) / len(all_node_scores),
                'min_score': min(all_node_scores),
                'max_score': max(all_node_scores),
                'score_distribution': len(all_node_scores)
            }
        
        consensus_analysis['active_nodes_stats'] = {
            'average': sum(active_nodes_counts) / len(active_nodes_counts) if active_nodes_counts else 0,
            'min': min(active_nodes_counts) if active_nodes_counts else 0,
            'max': max(active_nodes_counts) if active_nodes_counts else 0
        }
        
        self.collected_data['quantum_consensus'] = consensus_analysis
    
    def export_json(self, output_path: str = "./") -> str:
        """Export metrics as JSON"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"blockchain_metrics_{timestamp}.json"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.collected_data, f, indent=2, default=str)
        
        print(f"📄 JSON export saved: {filepath}")
        return filepath
    
    def export_csv(self, output_path: str = "./") -> List[str]:
        """Export metrics as multiple CSV files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        files = []
        
        # Node metrics CSV
        node_csv = os.path.join(output_path, f"node_metrics_{timestamp}.csv")
        with open(node_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['node_id', 'status', 'api_port', 'response_time', 'block_count', 
                           'probe_count', 'active_nodes'])
            
            for node_id, data in self.collected_data['node_metrics'].items():
                quantum = data.get('quantum_metrics', {})
                writer.writerow([
                    node_id,
                    data.get('status', 'unknown'),
                    data.get('api_port', 0),
                    data.get('response_time', 0),
                    data.get('block_count', 0),
                    quantum.get('probe_count', 0),
                    quantum.get('active_nodes', 0)
                ])
        files.append(node_csv)
        
        # Network summary CSV
        network_csv = os.path.join(output_path, f"network_summary_{timestamp}.csv")
        with open(network_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            summary = self.collected_data['network_summary']
            for key, value in summary.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        writer.writerow([f"{key}_{subkey}", subvalue])
                else:
                    writer.writerow([key, value])
        files.append(network_csv)
        
        # Performance CSV
        perf_csv = os.path.join(output_path, f"performance_metrics_{timestamp}.csv")
        with open(perf_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['metric', 'value'])
            for key, value in self.collected_data['performance_metrics'].items():
                writer.writerow([key, value])
        files.append(perf_csv)
        
        print(f"📊 CSV exports saved: {len(files)} files")
        return files
    
    def export_html(self, output_path: str = "./", include_charts: bool = False) -> str:
        """Export metrics as HTML report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"blockchain_report_{timestamp}.html"
        filepath = os.path.join(output_path, filename)
        
        html_content = self.generate_html_report(include_charts)
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        print(f"🌐 HTML report saved: {filepath}")
        return filepath
    
    def generate_html_report(self, include_charts: bool = False) -> str:
        """Generate HTML report content"""
        metadata = self.collected_data['metadata']
        network = self.collected_data['network_summary']
        performance = self.collected_data['performance_metrics']
        quantum = self.collected_data['quantum_consensus']
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Blockchain Metrics Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .metric {{ margin: 10px 0; }}
        .status-online {{ color: green; font-weight: bold; }}
        .status-offline {{ color: red; font-weight: bold; }}
        .status-error {{ color: orange; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .good {{ color: green; }}
        .warning {{ color: orange; }}
        .error {{ color: red; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Quantum Annealing Blockchain Metrics Report</h1>
        <p>Generated: {metadata.get('collection_time', 'Unknown')}</p>
        <p>Network: {metadata.get('num_nodes', 0)} nodes</p>
    </div>

    <div class="section">
        <h2>📊 Network Summary</h2>
        <div class="metric">Total Nodes: <strong>{network.get('total_nodes', 0)}</strong></div>
        <div class="metric">Online Nodes: <strong class="good">{network.get('online_nodes', 0)}</strong></div>
        <div class="metric">Offline Nodes: <strong class="{'error' if network.get('offline_nodes', 0) > 0 else 'good'}">{network.get('offline_nodes', 0)}</strong></div>
        <div class="metric">Availability: <strong>{network.get('availability_percentage', 0):.1f}%</strong></div>
        <div class="metric">Avg Response Time: <strong>{network.get('avg_response_time', 0):.3f}s</strong></div>
        <div class="metric">Sync Difference: <strong class="{'good' if network.get('block_sync_status', {}).get('sync_difference', 0) <= 1 else 'warning'}">{network.get('block_sync_status', {}).get('sync_difference', 0)} blocks</strong></div>
    </div>

    <div class="section">
        <h2>🚀 Performance Metrics</h2>
        <div class="metric">Transaction Creation Time: <strong>{performance.get('transaction_creation_time', 0):.6f}s</strong></div>
        <div class="metric">Transaction Submit Time: <strong>{performance.get('transaction_submit_time', 0):.3f}s</strong></div>
        <div class="metric">Total Transaction Time: <strong>{performance.get('total_transaction_time', 0):.3f}s</strong></div>
        <div class="metric">Estimated TPS: <strong>{performance.get('estimated_tps', 0):.1f}</strong></div>
        <div class="metric">Submission Success: <strong class="{'good' if performance.get('submission_success', False) else 'error'}">{'✅ Yes' if performance.get('submission_success', False) else '❌ No'}</strong></div>
    </div>

    <div class="section">
        <h2>🔬 Quantum Consensus Analysis</h2>
        <div class="metric">Total Probe Count: <strong>{quantum.get('total_probe_count', 0)}</strong></div>
        <div class="metric">Consensus Health: <strong class="{'good' if quantum.get('consensus_health') == 'excellent' else 'warning' if quantum.get('consensus_health') == 'good' else 'error'}">{quantum.get('consensus_health', 'unknown').title()}</strong></div>
        
        {self._generate_node_scores_table()}
        
        <h3>Active Nodes Statistics</h3>
        <div class="metric">Average Active Nodes: <strong>{quantum.get('active_nodes_stats', {}).get('average', 0):.1f}</strong></div>
        <div class="metric">Min Active Nodes: <strong>{quantum.get('active_nodes_stats', {}).get('min', 0)}</strong></div>
        <div class="metric">Max Active Nodes: <strong>{quantum.get('active_nodes_stats', {}).get('max', 0)}</strong></div>
    </div>

    <div class="section">
        <h2>🖥️ Node Details</h2>
        <table>
            <tr>
                <th>Node ID</th>
                <th>Status</th>
                <th>API Port</th>
                <th>Response Time</th>
                <th>Block Count</th>
                <th>Probe Count</th>
            </tr>
            {self._generate_node_table()}
        </table>
    </div>

    {"<div class='section'><h2>📈 Charts</h2><p>Chart functionality would be implemented here with JavaScript libraries like Chart.js</p></div>" if include_charts else ""}

    <div class="section">
        <h2>📋 Raw Data</h2>
        <details>
            <summary>Click to view raw JSON data</summary>
            <pre>{json.dumps(self.collected_data, indent=2, default=str)}</pre>
        </details>
    </div>

    <footer style="margin-top: 50px; text-align: center; color: #666;">
        <p>Report generated by Quantum Annealing Blockchain Metrics Exporter v1.0.0</p>
    </footer>
</body>
</html>
        """
        
        return html
    
    def _generate_node_table(self) -> str:
        """Generate HTML table for node details"""
        rows = []
        for node_id, data in self.collected_data['node_metrics'].items():
            status = data.get('status', 'unknown')
            status_class = f"status-{status}"
            quantum = data.get('quantum_metrics', {})
            
            rows.append(f"""
            <tr>
                <td>{node_id}</td>
                <td class="{status_class}">{status.title()}</td>
                <td>{data.get('api_port', 'N/A')}</td>
                <td>{data.get('response_time', 0):.3f}s</td>
                <td>{data.get('block_count', 0)}</td>
                <td>{quantum.get('probe_count', 0)}</td>
            </tr>
            """)
        
        return "\n".join(rows)
    
    def _generate_node_scores_table(self) -> str:
        """Generate node scores summary"""
        scores = self.collected_data['quantum_consensus'].get('node_scores_summary', {})
        if not scores:
            return "<p>No node scores available</p>"
        
        return f"""
        <h3>Node Scores Summary</h3>
        <div class="metric">Average Score: <strong>{scores.get('average_score', 0):.4f}</strong></div>
        <div class="metric">Min Score: <strong>{scores.get('min_score', 0):.4f}</strong></div>
        <div class="metric">Max Score: <strong>{scores.get('max_score', 0):.4f}</strong></div>
        <div class="metric">Participating Nodes: <strong>{scores.get('score_distribution', 0)}</strong></div>
        """
    
    def export_markdown(self, output_path: str = "./") -> str:
        """Export metrics as Markdown report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"blockchain_report_{timestamp}.md"
        filepath = os.path.join(output_path, filename)
        
        markdown_content = self.generate_markdown_report()
        
        with open(filepath, 'w') as f:
            f.write(markdown_content)
        
        print(f"📝 Markdown report saved: {filepath}")
        return filepath
    
    def generate_markdown_report(self) -> str:
        """Generate Markdown report content"""
        metadata = self.collected_data['metadata']
        network = self.collected_data['network_summary']
        performance = self.collected_data['performance_metrics']
        quantum = self.collected_data['quantum_consensus']
        
        md = f"""# 🎯 Quantum Annealing Blockchain Metrics Report

**Generated:** {metadata.get('collection_time', 'Unknown')}  
**Network:** {metadata.get('num_nodes', 0)} nodes  
**Exporter Version:** {metadata.get('exporter_version', 'Unknown')}

## 📊 Network Summary

| Metric | Value |
|--------|--------|
| Total Nodes | {network.get('total_nodes', 0)} |
| Online Nodes | {network.get('online_nodes', 0)} |
| Offline Nodes | {network.get('offline_nodes', 0)} |
| Availability | {network.get('availability_percentage', 0):.1f}% |
| Avg Response Time | {network.get('avg_response_time', 0):.3f}s |
| Sync Difference | {network.get('block_sync_status', {}).get('sync_difference', 0)} blocks |

## 🚀 Performance Metrics

| Metric | Value |
|--------|--------|
| Transaction Creation Time | {performance.get('transaction_creation_time', 0):.6f}s |
| Transaction Submit Time | {performance.get('transaction_submit_time', 0):.3f}s |
| Total Transaction Time | {performance.get('total_transaction_time', 0):.3f}s |
| Estimated TPS | {performance.get('estimated_tps', 0):.1f} |
| Submission Success | {'✅ Yes' if performance.get('submission_success', False) else '❌ No'} |

## 🔬 Quantum Consensus Analysis

| Metric | Value |
|--------|--------|
| Total Probe Count | {quantum.get('total_probe_count', 0)} |
| Consensus Health | {quantum.get('consensus_health', 'unknown').title()} |
| Avg Active Nodes | {quantum.get('active_nodes_stats', {}).get('average', 0):.1f} |
| Min Active Nodes | {quantum.get('active_nodes_stats', {}).get('min', 0)} |
| Max Active Nodes | {quantum.get('active_nodes_stats', {}).get('max', 0)} |

### Node Scores Summary

{self._generate_markdown_node_scores()}

## 🖥️ Node Details

| Node ID | Status | API Port | Response Time | Block Count | Probe Count |
|---------|--------|----------|---------------|-------------|-------------|
{self._generate_markdown_node_table()}

## 📋 Recommendations

{self._generate_recommendations()}

---

*Report generated by Quantum Annealing Blockchain Metrics Exporter*
"""
        
        return md
    
    def _generate_markdown_node_table(self) -> str:
        """Generate Markdown table for node details"""
        rows = []
        for node_id, data in self.collected_data['node_metrics'].items():
            status = data.get('status', 'unknown')
            quantum = data.get('quantum_metrics', {})
            
            rows.append(f"| {node_id} | {status.title()} | {data.get('api_port', 'N/A')} | {data.get('response_time', 0):.3f}s | {data.get('block_count', 0)} | {quantum.get('probe_count', 0)} |")
        
        return "\n".join(rows)
    
    def _generate_markdown_node_scores(self) -> str:
        """Generate node scores summary for Markdown"""
        scores = self.collected_data['quantum_consensus'].get('node_scores_summary', {})
        if not scores:
            return "No node scores available"
        
        return f"""
- **Average Score:** {scores.get('average_score', 0):.4f}
- **Min Score:** {scores.get('min_score', 0):.4f}
- **Max Score:** {scores.get('max_score', 0):.4f}
- **Participating Nodes:** {scores.get('score_distribution', 0)}
"""
    
    def _generate_recommendations(self) -> str:
        """Generate recommendations based on metrics"""
        recommendations = []
        
        network = self.collected_data['network_summary']
        performance = self.collected_data['performance_metrics']
        quantum = self.collected_data['quantum_consensus']
        
        # Network recommendations
        if network.get('availability_percentage', 100) < 80:
            recommendations.append("⚠️ **Network availability is low.** Consider investigating offline nodes.")
        
        sync_diff = network.get('block_sync_status', {}).get('sync_difference', 0)
        if sync_diff > 3:
            recommendations.append("⚠️ **Poor block synchronization.** Check network connectivity between nodes.")
        
        # Performance recommendations
        if performance.get('total_transaction_time', 0) > 1.0:
            recommendations.append("⚠️ **High transaction times.** Consider optimizing consensus or network latency.")
        
        if not performance.get('submission_success', True):
            recommendations.append("❌ **Transaction submission failed.** Check node health and wallet funding.")
        
        # Quantum consensus recommendations
        if quantum.get('consensus_health') == 'poor':
            recommendations.append("❌ **Poor consensus health.** Investigate quantum annealing probe protocol.")
        
        if quantum.get('total_probe_count', 0) < 50:
            recommendations.append("⚠️ **Low probe activity.** Check if quantum consensus is active.")
        
        if not recommendations:
            recommendations.append("✅ **All metrics look healthy!** Continue monitoring for optimal performance.")
        
        return "\n".join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations))


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Blockchain Metrics Exporter")
    parser.add_argument("--format", choices=['json', 'csv', 'html', 'markdown', 'all'], 
                       default='json', help="Export format")
    parser.add_argument("--output", default="./", help="Output directory")
    parser.add_argument("--nodes", type=int, default=3, help="Number of nodes to collect from")
    parser.add_argument("--api-port", type=int, default=8050, help="Base API port")
    parser.add_argument("--include-charts", action="store_true", help="Include charts in HTML export")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    print("🔍 Starting blockchain metrics export...")
    print(f"📊 Format: {args.format}")
    print(f"📁 Output: {args.output}")
    print(f"🖥️ Nodes: {args.nodes}")
    print()
    
    # Create exporter and collect metrics
    exporter = MetricsExporter(num_nodes=args.nodes, base_api_port=args.api_port)
    exporter.collect_current_metrics()
    
    # Export in requested format(s)
    exported_files = []
    
    if args.format == 'json' or args.format == 'all':
        file_path = exporter.export_json(args.output)
        exported_files.append(file_path)
    
    if args.format == 'csv' or args.format == 'all':
        file_paths = exporter.export_csv(args.output)
        exported_files.extend(file_paths)
    
    if args.format == 'html' or args.format == 'all':
        file_path = exporter.export_html(args.output, args.include_charts)
        exported_files.append(file_path)
    
    if args.format == 'markdown' or args.format == 'all':
        file_path = exporter.export_markdown(args.output)
        exported_files.append(file_path)
    
    print(f"\n✅ Export complete! Generated {len(exported_files)} files:")
    for file_path in exported_files:
        print(f"   📄 {file_path}")


if __name__ == "__main__":
    main()
