"""
Report generator for data lineage analysis and summaries.
"""

import json
import csv
from typing import Dict, List, Optional, Any
from datetime import datetime
from jinja2 import Template

from ..core.tracker import LineageTracker


class ReportGenerator:
    """
    Generates various types of reports for data lineage analysis.
    """

    def __init__(self, tracker: LineageTracker):
        """
        Initialize the report generator.

        Args:
            tracker: LineageTracker instance to generate reports for
        """
        self.tracker = tracker

    def generate_summary_report(self,
                                output_file: str,
                                format: str = 'html') -> str:
        """
        Generate a comprehensive summary report.

        Args:
            output_file: File path to save the report
            format: Format of the report ('html', 'markdown', 'json')

        Returns:
            Report content as string
        """
        # Collect data for the report
        report_data = self._collect_report_data()

        if format.lower() == 'html':
            return self._generate_html_report(report_data, output_file)
        elif format.lower() == 'markdown':
            return self._generate_markdown_report(report_data, output_file)
        elif format.lower() == 'json':
            return self._generate_json_report(report_data, output_file)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _collect_report_data(self) -> Dict[str, Any]:
        """Collect all data needed for the report."""
        stats = self.tracker.get_stats()

        # Node analysis
        nodes_by_type = {}
        for node_id, node in self.tracker.nodes.items():
            node_type = getattr(node, 'node_type', 'data')
            if node_type not in nodes_by_type:
                nodes_by_type[node_type] = []
            nodes_by_type[node_type].append({
                'id': node_id,
                'name': node.name,
                'schema': getattr(node, 'schema', {}),
                'metadata': node.metadata
            })

        # Operation analysis
        operations_by_type = {}
        for operation in self.tracker.operations:
            op_type = operation.operation_type
            if op_type not in operations_by_type:
                operations_by_type[op_type] = []
            operations_by_type[op_type].append({
                'id': operation.id,
                'inputs': operation.inputs,
                'outputs': operation.outputs,
                'execution_time': operation.execution_time,
                'status': operation.status,
                'parameters': operation.parameters
            })

        # Edge analysis
        edges_summary = []
        for edge in self.tracker.edges:
            edges_summary.append({
                'source': edge.source_id,
                'target': edge.target_id,
                'operation': edge.operation.operation_type if edge.operation else 'unknown',
                'metadata': edge.metadata
            })

        return {
            'tracker_info': {
                'name': self.tracker.name,
                'id': self.tracker.id,
                'created_at': self.tracker.created_at.isoformat(),
                'active': self.tracker.active
            },
            'stats': stats,
            'nodes_by_type': nodes_by_type,
            'operations_by_type': operations_by_type,
            'edges_summary': edges_summary,
            'generated_at': datetime.now().isoformat()
        }

    def _generate_html_report(self, data: Dict[str, Any], output_file: str) -> str:
        """Generate HTML report."""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Data Lineage Report - {{ data.tracker_info.name }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f5f5f5; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; }
        .stats { display: flex; flex-wrap: wrap; gap: 20px; }
        .stat-box { border: 1px solid #ddd; padding: 15px; border-radius: 5px; min-width: 150px; }
        .stat-value { font-size: 24px; font-weight: bold; color: #2196F3; }
        .node-list, .operation-list { margin: 10px 0; }
        .node-item, .operation-item { 
            background: #f9f9f9; padding: 10px; margin: 5px 0; border-radius: 3px; 
        }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Data Lineage Report</h1>
        <p><strong>Tracker:</strong> {{ data.tracker_info.name }}</p>
        <p><strong>Generated:</strong> {{ data.generated_at }}</p>
        <p><strong>Status:</strong> {{ "Active" if data.tracker_info.active else "Inactive" }}</p>
    </div>

    <div class="section">
        <h2>Overview Statistics</h2>
        <div class="stats">
            <div class="stat-box">
                <div class="stat-value">{{ data.stats.total_nodes }}</div>
                <div>Total Nodes</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{{ data.stats.total_edges }}</div>
                <div>Total Edges</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{{ data.stats.total_operations }}</div>
                <div>Operations</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>Nodes by Type</h2>
        {% for node_type, nodes in data.nodes_by_type.items() %}
        <div class="node-list">
            <h3>{{ node_type.title() }} Nodes ({{ nodes|length }})</h3>
            {% for node in nodes %}
            <div class="node-item">
                <strong>{{ node.name }}</strong> ({{ node.id[:8] }}...)
                {% if node.schema %}
                <br>Schema: {{ node.schema|length }} columns
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endfor %}
    </div>

    <div class="section">
        <h2>Operations by Type</h2>
        {% for op_type, operations in data.operations_by_type.items() %}
        <div class="operation-list">
            <h3>{{ op_type.title() }} Operations ({{ operations|length }})</h3>
            {% for op in operations %}
            <div class="operation-item">
                <strong>{{ op.id[:8] }}...</strong>
                <br>Inputs: {{ op.inputs|length }}, Outputs: {{ op.outputs|length }}
                {% if op.execution_time %}
                <br>Execution Time: {{ "%.3f"|format(op.execution_time) }}s
                {% endif %}
                <br>Status: {{ op.status }}
            </div>
            {% endfor %}
        </div>
        {% endfor %}
    </div>

    <div class="section">
        <h2>Lineage Edges</h2>
        <table>
            <tr>
                <th>Source</th>
                <th>Target</th>
                <th>Operation</th>
            </tr>
            {% for edge in data.edges_summary %}
            <tr>
                <td>{{ edge.source[:8] }}...</td>
                <td>{{ edge.target[:8] }}...</td>
                <td>{{ edge.operation }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
        """

        template = Template(html_template)
        html_content = template.render(data=data)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return html_content

    def _generate_markdown_report(self, data: Dict[str, Any], output_file: str) -> str:
        """Generate Markdown report."""
        lines = []
        lines.append(f"# Data Lineage Report - {data['tracker_info']['name']}")
        lines.append("")
        lines.append(f"**Generated:** {data['generated_at']}")
        lines.append(f"**Tracker ID:** {data['tracker_info']['id']}")
        lines.append(
            f"**Status:** {'Active' if data['tracker_info']['active'] else 'Inactive'}")
        lines.append("")

        # Overview Statistics
        lines.append("## Overview Statistics")
        lines.append("")
        stats = data['stats']
        lines.append(f"- **Total Nodes:** {stats.get('total_nodes', 0)}")
        lines.append(f"- **Total Edges:** {stats.get('total_edges', 0)}")
        lines.append(
            f"- **Total Operations:** {stats.get('total_operations', 0)}")
        lines.append("")

        # Nodes by Type
        lines.append("## Nodes by Type")
        lines.append("")
        for node_type, nodes in data['nodes_by_type'].items():
            lines.append(f"### {node_type.title()} Nodes ({len(nodes)})")
            lines.append("")
            for node in nodes:
                lines.append(f"- **{node['name']}** (`{node['id'][:8]}...`)")
                if node['schema']:
                    lines.append(f"  - Schema: {len(node['schema'])} columns")
            lines.append("")

        # Operations by Type
        lines.append("## Operations by Type")
        lines.append("")
        for op_type, operations in data['operations_by_type'].items():
            lines.append(
                f"### {op_type.title()} Operations ({len(operations)})")
            lines.append("")
            for op in operations:
                lines.append(f"- **{op['id'][:8]}...** ({op['status']})")
                lines.append(
                    f"  - Inputs: {len(op['inputs'])}, Outputs: {len(op['outputs'])}")
                if op['execution_time']:
                    lines.append(
                        f"  - Execution Time: {op['execution_time']:.3f}s")
            lines.append("")

        # Lineage Edges
        lines.append("## Lineage Edges")
        lines.append("")
        lines.append("| Source | Target | Operation |")
        lines.append("|--------|--------|-----------|")
        for edge in data['edges_summary']:
            lines.append(
                f"| {edge['source'][:8]}... | {edge['target'][:8]}... | {edge['operation']} |")
        lines.append("")

        markdown_content = '\n'.join(lines)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return markdown_content

    def _generate_json_report(self, data: Dict[str, Any], output_file: str) -> str:
        """Generate JSON report."""
        json_content = json.dumps(data, indent=2)

        with open(output_file, 'w') as f:
            f.write(json_content)

        return json_content

    def export_to_csv(self, output_file: str, data_type: str = 'edges') -> str:
        """
        Export lineage data to CSV format.

        Args:
            output_file: File path to save CSV
            data_type: Type of data to export ('edges', 'nodes', 'operations')

        Returns:
            CSV content as string
        """
        if data_type == 'edges':
            return self._export_edges_csv(output_file)
        elif data_type == 'nodes':
            return self._export_nodes_csv(output_file)
        elif data_type == 'operations':
            return self._export_operations_csv(output_file)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")

    def _export_edges_csv(self, output_file: str) -> str:
        """Export edges to CSV."""
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['source_id', 'target_id',
                            'operation_type', 'created_at'])

            for edge in self.tracker.edges:
                writer.writerow([
                    edge.source_id,
                    edge.target_id,
                    edge.operation.operation_type if edge.operation else 'unknown',
                    edge.created_at.isoformat()
                ])

        # Return content as string
        lines = []
        lines.append('source_id,target_id,operation_type,created_at')
        for edge in self.tracker.edges:
            lines.append(
                f"{edge.source_id},{edge.target_id},{edge.operation.operation_type if edge.operation else 'unknown'},{edge.created_at.isoformat()}")

        return '\n'.join(lines)

    def _export_nodes_csv(self, output_file: str) -> str:
        """Export nodes to CSV."""
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['node_id', 'name', 'node_type',
                            'created_at', 'schema_columns'])

            for node_id, node in self.tracker.nodes.items():
                schema_cols = len(getattr(node, 'schema', {}))
                writer.writerow([
                    node_id,
                    node.name,
                    getattr(node, 'node_type', 'data'),
                    node.created_at.isoformat(),
                    schema_cols
                ])

        # Return content as string
        lines = []
        lines.append('node_id,name,node_type,created_at,schema_columns')
        for node_id, node in self.tracker.nodes.items():
            schema_cols = len(getattr(node, 'schema', {}))
            lines.append(
                f"{node_id},{node.name},{getattr(node, 'node_type', 'data')},{node.created_at.isoformat()},{schema_cols}")

        return '\n'.join(lines)

    def _export_operations_csv(self, output_file: str) -> str:
        """Export operations to CSV."""
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['operation_id', 'operation_type', 'input_count',
                            'output_count', 'execution_time', 'status', 'created_at'])

            for operation in self.tracker.operations:
                writer.writerow([
                    operation.id,
                    operation.operation_type,
                    len(operation.inputs),
                    len(operation.outputs),
                    operation.execution_time or '',
                    operation.status,
                    operation.created_at.isoformat()
                ])

        # Return content as string
        lines = []
        lines.append(
            'operation_id,operation_type,input_count,output_count,execution_time,status,created_at')
        for operation in self.tracker.operations:
            lines.append(f"{operation.id},{operation.operation_type},{len(operation.inputs)},{len(operation.outputs)},{operation.execution_time or ''},{operation.status},{operation.created_at.isoformat()}")

        return '\n'.join(lines)

    def generate_ai_ready_format(self, output_file: str) -> Dict[str, Any]:
        """
        Export lineage in AI-ready format for training or analysis.

        Args:
            output_file: File path to save the AI-ready data

        Returns:
            AI-ready data structure
        """
        ai_data = {
            'dataset_info': {
                'name': self.tracker.name,
                'description': f'Data lineage from tracker {self.tracker.name}',
                'created_at': self.tracker.created_at.isoformat(),
                'version': '1.0'
            },
            'graph_structure': {
                'node_features': [],
                'edge_features': [],
                'graph_features': self.tracker.get_stats()
            },
            'sequences': [],
            'examples': []
        }

        # Node features for ML
        for node_id, node in self.tracker.nodes.items():
            node_features = {
                'id': node_id,
                'name': node.name,
                'type': getattr(node, 'node_type', 'data'),
                'schema_size': len(getattr(node, 'schema', {})),
                'in_degree': 0,
                'out_degree': 0,
                'metadata_keys': list(node.metadata.keys())
            }

            # Calculate degrees
            for edge in self.tracker.edges:
                if edge.target_id == node_id:
                    node_features['in_degree'] += 1
                if edge.source_id == node_id:
                    node_features['out_degree'] += 1

            ai_data['graph_structure']['node_features'].append(node_features)

        # Edge features for ML
        for edge in self.tracker.edges:
            edge_features = {
                'source': edge.source_id,
                'target': edge.target_id,
                'operation_type': edge.operation.operation_type if edge.operation else 'unknown',
                'has_operation': edge.operation is not None,
                'metadata_keys': list(edge.metadata.keys())
            }
            ai_data['graph_structure']['edge_features'].append(edge_features)

        # Operation sequences for pattern learning
        operation_sequences = []
        for operation in self.tracker.operations:
            sequence = {
                'operation_type': operation.operation_type,
                'input_count': len(operation.inputs),
                'output_count': len(operation.outputs),
                'execution_time': operation.execution_time,
                'status': operation.status,
                'parameters': operation.parameters
            }
            operation_sequences.append(sequence)

        ai_data['sequences'] = operation_sequences

        # Training examples (simplified lineage paths)
        examples = []
        for node_id in self.tracker.nodes.keys():
            try:
                lineage = self.tracker.get_lineage(node_id, 'upstream')
                if lineage['upstream']:
                    example = {
                        'target_node': node_id,
                        # Limit to 5 for simplicity
                        'upstream_path': [item['node']['id'] for item in lineage['upstream'][:5]],
                        'operations_used': [item['edge']['operation']['operation_type'] for item in lineage['upstream'] if item.get('edge', {}).get('operation')][:5]
                    }
                    examples.append(example)
            except:
                continue  # Skip if lineage tracing fails

        ai_data['examples'] = examples

        with open(output_file, 'w') as f:
            json.dump(ai_data, f, indent=2)

        return ai_data
