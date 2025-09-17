"""
Serialization and Export Module for DataLineagePy
Comprehensive data export/import capabilities with lineage tracking.
"""

import json
import pickle
import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import pandas as pd

from .tracker import LineageTracker
from .nodes import DataNode
from .dataframe_wrapper import LineageDataFrame


class DataSerializer:
    """Advanced serialization for LineageDataFrame and tracker data."""

    def __init__(self, tracker: LineageTracker):
        self.tracker = tracker

    def export_to_formats(self, ldf: LineageDataFrame, base_path: str,
                          formats: List[str] = None) -> Dict[str, str]:
        """Export LineageDataFrame to multiple formats simultaneously."""
        if formats is None:
            formats = ['csv', 'json', 'parquet', 'excel']

        export_paths = {}
        export_node = self.tracker.create_node(
            "export", f"{ldf.name}_multi_export")

        for fmt in formats:
            try:
                if fmt == 'csv':
                    path = f"{base_path}.csv"
                    ldf._df.to_csv(path, index=False)
                    export_paths['csv'] = path

                elif fmt == 'json':
                    path = f"{base_path}.json"
                    ldf._df.to_json(path, orient='records', indent=2)
                    export_paths['json'] = path

                elif fmt == 'parquet':
                    path = f"{base_path}.parquet"
                    ldf._df.to_parquet(path)
                    export_paths['parquet'] = path

                elif fmt == 'excel':
                    path = f"{base_path}.xlsx"
                    ldf._df.to_excel(path, index=False)
                    export_paths['excel'] = path

                elif fmt == 'pickle':
                    path = f"{base_path}.pkl"
                    with open(path, 'wb') as f:
                        pickle.dump({
                            'dataframe': ldf._df,
                            'lineage_metadata': {
                                'name': ldf.name,
                                'node_id': ldf.node.id,
                                'metadata': ldf.node.metadata
                            }
                        }, f)
                    export_paths['pickle'] = path

            except Exception as e:
                export_paths[f'{fmt}_error'] = str(e)

        # Track the multi-export operation
        operation = self.tracker.track_operation(
            "multi_format_export",
            [ldf.node],
            [export_node],
            {"formats": formats, "base_path": base_path,
                "exported_formats": list(export_paths.keys())}
        )

        self.tracker.add_edge(ldf.node, export_node, operation)
        export_node.add_metadata("export_paths", export_paths)

        return export_paths

    def export_lineage_graph(self, output_path: str, format: str = 'json') -> str:
        """Export complete lineage graph to file."""
        graph_data = {
            'nodes': [
                {
                    'id': node.id,
                    'node_type': node.node_type,
                    'name': node.name,
                    'metadata': node.metadata,
                    'created_at': node.created_at.isoformat()
                }
                for node in self.tracker.nodes.values()
            ],
            'edges': [
                {
                    'source': edge.source.id,
                    'target': edge.target.id,
                    'operation': str(edge.operation),
                    'metadata': getattr(edge, 'metadata', {})
                }
                for edge in self.tracker.edges
            ],
            'export_timestamp': datetime.now().isoformat(),
            'total_nodes': len(self.tracker.nodes),
            'total_edges': len(self.tracker.edges)
        }

        if format.lower() == 'json':
            with open(output_path, 'w') as f:
                json.dump(graph_data, f, indent=2)
        elif format.lower() == 'pickle':
            with open(output_path, 'wb') as f:
                pickle.dump(graph_data, f)
        else:
            raise ValueError(f"Unsupported format: {format}")

        return output_path

    def import_lineage_graph(self, input_path: str, format: str = 'json') -> Dict[str, Any]:
        """Import lineage graph from file."""
        if format.lower() == 'json':
            with open(input_path, 'r') as f:
                graph_data = json.load(f)
        elif format.lower() == 'pickle':
            with open(input_path, 'rb') as f:
                graph_data = pickle.load(f)
        else:
            raise ValueError(f"Unsupported format: {format}")

        import_summary = {
            'nodes_imported': len(graph_data.get('nodes', [])),
            'edges_imported': len(graph_data.get('edges', [])),
            'operations_imported': len(graph_data.get('operations', [])),
            'original_export_timestamp': graph_data.get('export_timestamp'),
            'import_timestamp': datetime.now().isoformat()
        }

        return import_summary

    def create_data_package(self, ldf: LineageDataFrame, package_path: str) -> Dict[str, Any]:
        """Create a comprehensive data package with data + lineage."""
        os.makedirs(package_path, exist_ok=True)

        package_manifest = {
            'package_name': ldf.name,
            'created_at': datetime.now().isoformat(),
            'data_files': {},
            'lineage_file': '',
            'metadata_file': '',
            'schema_file': ''
        }

        # Export data in multiple formats
        data_exports = self.export_to_formats(ldf, os.path.join(package_path, 'data'),
                                              ['csv', 'json', 'parquet'])
        package_manifest['data_files'] = data_exports

        # Export lineage graph
        lineage_path = os.path.join(package_path, 'lineage.json')
        self.export_lineage_graph(lineage_path, 'json')
        package_manifest['lineage_file'] = lineage_path

        # Export metadata
        metadata_path = os.path.join(package_path, 'metadata.json')
        metadata = {
            'dataset_name': ldf.name,
            'shape': ldf.shape,
            'columns': list(ldf.columns),
            'dtypes': {col: str(dtype) for col, dtype in ldf.dtypes.items()},
            'memory_usage': ldf._df.memory_usage(deep=True).sum(),
            'lineage_node_id': ldf.node.id,
            'node_metadata': ldf.node.metadata
        }

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        package_manifest['metadata_file'] = metadata_path

        # Export schema information
        schema_path = os.path.join(package_path, 'schema.json')
        schema_info = {
            'columns': [
                {
                    'name': col,
                    'dtype': str(ldf._df[col].dtype),
                    'nullable': ldf._df[col].isnull().any(),
                    'unique_count': int(ldf._df[col].nunique()),
                    'sample_values': ldf._df[col].dropna().head(5).tolist()
                }
                for col in ldf.columns
            ],
            'constraints': {
                'primary_keys': [],
                'foreign_keys': [],
                'unique_columns': [col for col in ldf.columns if ldf._df[col].nunique() == len(ldf._df)]
            }
        }

        with open(schema_path, 'w') as f:
            json.dump(schema_info, f, indent=2)
        package_manifest['schema_file'] = schema_path

        # Save package manifest
        manifest_path = os.path.join(package_path, 'package_manifest.json')
        with open(manifest_path, 'w') as f:
            json.dump(package_manifest, f, indent=2)

        return package_manifest


class ConfigurationManager:
    """Manage configuration and settings for DataLineagePy."""

    def __init__(self):
        self.config = {
            'tracking': {
                'auto_tracking_enabled': True,
                'track_memory_usage': True,
                'track_execution_time': True,
                'max_operation_history': 1000
            },
            'visualization': {
                'default_layout': 'hierarchical',
                'node_colors': {
                    'data': '#4CAF50',
                    'operation': '#2196F3',
                    'file': '#FF9800',
                    'database': '#9C27B0'
                },
                'export_format': 'png',
                'figure_size': (12, 8)
            },
            'performance': {
                'enable_profiling': False,
                'memory_warning_threshold': 500,
                'memory_critical_threshold': 1000,
                'slow_operation_threshold': 5.0
            },
            'security': {
                'mask_pii_columns': True,
                'pii_patterns': ['ssn', 'social', 'phone', 'email'],
                'encryption_enabled': False
            },
            'export': {
                'default_formats': ['csv', 'json'],
                'include_lineage': True,
                'compress_exports': False
            }
        }

    def get_config(self, key_path: str = None):
        """Get configuration value by key path (e.g., 'tracking.auto_tracking_enabled')."""
        if key_path is None:
            return self.config

        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None

        return value

    def set_config(self, key_path: str, value: Any):
        """Set configuration value by key path."""
        keys = key_path.split('.')
        config_ref = self.config

        for key in keys[:-1]:
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]

        config_ref[keys[-1]] = value

    def load_config_from_file(self, config_path: str):
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            file_config = json.load(f)

        # Merge with default config
        self._deep_merge(self.config, file_config)

    def save_config_to_file(self, config_path: str):
        """Save current configuration to JSON file."""
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def _deep_merge(self, base_dict: Dict, update_dict: Dict):
        """Deep merge two dictionaries."""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_merge(base_dict[key], value)
            else:
                base_dict[key] = value

    def reset_to_defaults(self):
        """Reset configuration to default values."""
        self.__init__()

    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user-customizable preferences."""
        return {
            'visualization_layout': self.get_config('visualization.default_layout'),
            'auto_tracking': self.get_config('tracking.auto_tracking_enabled'),
            'performance_monitoring': self.get_config('performance.enable_profiling'),
            'pii_masking': self.get_config('security.mask_pii_columns'),
            'default_export_formats': self.get_config('export.default_formats')
        }

    def update_user_preferences(self, preferences: Dict[str, Any]):
        """Update user preferences."""
        preference_mappings = {
            'visualization_layout': 'visualization.default_layout',
            'auto_tracking': 'tracking.auto_tracking_enabled',
            'performance_monitoring': 'performance.enable_profiling',
            'pii_masking': 'security.mask_pii_columns',
            'default_export_formats': 'export.default_formats'
        }

        for pref_key, config_path in preference_mappings.items():
            if pref_key in preferences:
                self.set_config(config_path, preferences[pref_key])


class ReportGenerator:
    """Generate comprehensive reports about lineage and data operations."""

    def __init__(self, tracker: LineageTracker):
        self.tracker = tracker

    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate a comprehensive summary report."""
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'tracker_statistics': {
                'total_nodes': len(self.tracker.nodes),
                'total_edges': len(self.tracker.edges),
                'total_operations': len(self.tracker.operations)
            },
            'node_breakdown': self._analyze_nodes(),
            'operation_breakdown': self._analyze_operations(),
            'lineage_paths': self._analyze_lineage_paths(),
            'recommendations': self._generate_recommendations()
        }

        return report

    def _analyze_nodes(self) -> Dict[str, Any]:
        """Analyze node distribution and characteristics."""
        node_types = {}
        creation_timeline = []

        for node in self.tracker.nodes.values():
            node_type = node.node_type
            node_types[node_type] = node_types.get(node_type, 0) + 1

            creation_timeline.append({
                'timestamp': node.created_at.isoformat(),
                'node_type': node_type,
                'node_id': node.id
            })

        return {
            'node_type_distribution': node_types,
            'creation_timeline': sorted(creation_timeline, key=lambda x: x['timestamp']),
            'most_common_type': max(node_types.items(), key=lambda x: x[1])[0] if node_types else None
        }

    def _analyze_operations(self) -> Dict[str, Any]:
        """Analyze operation patterns and frequency."""
        operation_types = {}

        for operation in self.tracker.operations:
            op_type = getattr(operation, 'operation_type', str(operation))
            operation_types[op_type] = operation_types.get(op_type, 0) + 1

        return {
            'operation_type_distribution': operation_types,
            'most_common_operation': max(operation_types.items(), key=lambda x: x[1])[0] if operation_types else None,
            'total_unique_operations': len(operation_types)
        }

    def _analyze_lineage_paths(self) -> Dict[str, Any]:
        """Analyze lineage path complexity and depth."""
        lineage_analysis = {
            'max_depth': 0,
            'avg_depth': 0,
            'complex_paths': [],
            'leaf_nodes': [],
            'root_nodes': []
        }

        # Find root nodes (no incoming edges)
        nodes_with_incoming = {edge.target.id for edge in self.tracker.edges}
        root_nodes = [node for node in self.tracker.nodes.values()
                      if node.id not in nodes_with_incoming]

        # Find leaf nodes (no outgoing edges)
        nodes_with_outgoing = {edge.source.id for edge in self.tracker.edges}
        leaf_nodes = [node for node in self.tracker.nodes.values()
                      if node.id not in nodes_with_outgoing]

        lineage_analysis['root_nodes'] = [
            {'id': node.id, 'name': node.name} for node in root_nodes]
        lineage_analysis['leaf_nodes'] = [
            {'id': node.id, 'name': node.name} for node in leaf_nodes]

        return lineage_analysis

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on lineage analysis."""
        recommendations = []

        if len(self.tracker.nodes) > 100:
            recommendations.append(
                "Large lineage graph detected - consider periodic cleanup")

        if len(self.tracker.operations) > 500:
            recommendations.append(
                "High operation count - consider archiving old operations")

        # Check for disconnected nodes
        connected_nodes = set()
        for edge in self.tracker.edges:
            connected_nodes.add(edge.source.id)
            connected_nodes.add(edge.target.id)

        disconnected_count = len(self.tracker.nodes) - len(connected_nodes)
        if disconnected_count > 0:
            recommendations.append(
                f"{disconnected_count} disconnected nodes found - review lineage tracking")

        if not recommendations:
            recommendations.append(
                "Lineage tracking appears to be working well!")

        return recommendations

    def export_report(self, report: Dict[str, Any], output_path: str, format: str = 'json'):
        """Export report to file."""
        if format.lower() == 'json':
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
        elif format.lower() == 'txt':
            with open(output_path, 'w') as f:
                f.write(self._format_report_as_text(report))
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _format_report_as_text(self, report: Dict[str, Any]) -> str:
        """Format report as readable text."""
        text_lines = [
            "DataLineagePy Summary Report",
            "=" * 30,
            f"Generated: {report['report_timestamp']}",
            "",
            "Tracker Statistics:",
            f"  Total Nodes: {report['tracker_statistics']['total_nodes']}",
            f"  Total Edges: {report['tracker_statistics']['total_edges']}",
            f"  Total Operations: {report['tracker_statistics']['total_operations']}",
            "",
            "Node Type Distribution:",
        ]

        for node_type, count in report['node_breakdown']['node_type_distribution'].items():
            text_lines.append(f"  {node_type}: {count}")

        text_lines.extend([
            "",
            "Recommendations:",
        ])

        for rec in report['recommendations']:
            text_lines.append(f"  - {rec}")

        return "\n".join(text_lines)
