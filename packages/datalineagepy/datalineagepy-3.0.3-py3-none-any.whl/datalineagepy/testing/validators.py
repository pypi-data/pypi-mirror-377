"""
Validation framework for data lineage integrity and correctness.
"""

from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from datetime import datetime

from ..core.tracker import LineageTracker
from ..core.nodes import DataNode


class LineageValidator:
    """
    Validates data lineage integrity and correctness.
    """

    def __init__(self, tracker: LineageTracker):
        """
        Initialize the lineage validator.

        Args:
            tracker: LineageTracker instance to validate
        """
        self.tracker = tracker
        self.validation_results = []

    def validate_all(self) -> Dict[str, Any]:
        """
        Run all validation checks.

        Returns:
            Dictionary containing all validation results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'tracker_name': self.tracker.name,
            'checks': {}
        }

        # Run individual validation checks
        results['checks']['graph_integrity'] = self.validate_graph_integrity()
        results['checks']['node_consistency'] = self.validate_node_consistency()
        results['checks']['edge_consistency'] = self.validate_edge_consistency()
        results['checks']['operation_consistency'] = self.validate_operation_consistency()
        results['checks']['column_lineage'] = self.validate_column_lineage()
        results['checks']['circular_dependencies'] = self.check_circular_dependencies()

        # Calculate overall score
        total_checks = len(results['checks'])
        passed_checks = sum(
            1 for check in results['checks'].values() if check.get('passed', False))
        results['overall_score'] = passed_checks / \
            total_checks if total_checks > 0 else 0
        results['summary'] = f"{passed_checks}/{total_checks} checks passed"

        return results

    def validate_graph_integrity(self) -> Dict[str, Any]:
        """
        Validate the overall integrity of the lineage graph.

        Returns:
            Validation results for graph integrity
        """
        issues = []

        # Check for orphaned edges
        valid_node_ids = set(self.tracker.nodes.keys())
        for edge in self.tracker.edges:
            if edge.source_id not in valid_node_ids:
                issues.append(
                    f"Edge references non-existent source node: {edge.source_id}")
            if edge.target_id not in valid_node_ids:
                issues.append(
                    f"Edge references non-existent target node: {edge.target_id}")

        # Check for operations with invalid node references
        for operation in self.tracker.operations:
            for input_id in operation.inputs:
                if input_id not in valid_node_ids:
                    issues.append(
                        f"Operation {operation.id} references non-existent input node: {input_id}")
            for output_id in operation.outputs:
                if output_id not in valid_node_ids:
                    issues.append(
                        f"Operation {operation.id} references non-existent output node: {output_id}")

        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'details': {
                'total_nodes': len(self.tracker.nodes),
                'total_edges': len(self.tracker.edges),
                'total_operations': len(self.tracker.operations)
            }
        }

    def validate_node_consistency(self) -> Dict[str, Any]:
        """
        Validate consistency of nodes in the lineage graph.

        Returns:
            Validation results for node consistency
        """
        issues = []
        node_stats = {'total': 0, 'with_schema': 0, 'with_metadata': 0}

        for node_id, node in self.tracker.nodes.items():
            node_stats['total'] += 1

            # Check if node has valid ID
            if not node.id or node.id != node_id:
                issues.append(f"Node {node_id} has inconsistent ID: {node.id}")

            # Check if node has name
            if not node.name:
                issues.append(f"Node {node_id} has no name")

            # Check schema consistency
            if hasattr(node, 'schema') and node.schema:
                node_stats['with_schema'] += 1
                if hasattr(node, 'columns'):
                    schema_cols = set(node.schema.keys())
                    node_cols = set(node.columns)
                    if schema_cols != node_cols:
                        issues.append(
                            f"Node {node_id} has inconsistent schema and columns")

            # Check metadata presence
            if node.metadata:
                node_stats['with_metadata'] += 1

        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'stats': node_stats
        }

    def validate_edge_consistency(self) -> Dict[str, Any]:
        """
        Validate consistency of edges in the lineage graph.

        Returns:
            Validation results for edge consistency
        """
        issues = []
        edge_stats = {'total': 0, 'with_operations': 0, 'with_metadata': 0}

        for edge in self.tracker.edges:
            edge_stats['total'] += 1

            # Check if edge has valid source and target
            if not edge.source_id:
                issues.append(f"Edge {edge.id} has no source ID")
            if not edge.target_id:
                issues.append(f"Edge {edge.id} has no target ID")

            # Check if source and target are different
            if edge.source_id == edge.target_id:
                issues.append(
                    f"Edge {edge.id} has same source and target: {edge.source_id}")

            # Track statistics
            if edge.operation:
                edge_stats['with_operations'] += 1
            if edge.metadata:
                edge_stats['with_metadata'] += 1

        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'stats': edge_stats
        }

    def validate_operation_consistency(self) -> Dict[str, Any]:
        """
        Validate consistency of operations in the lineage graph.

        Returns:
            Validation results for operation consistency
        """
        issues = []
        operation_stats = {'total': 0, 'with_parameters': 0, 'completed': 0}

        for operation in self.tracker.operations:
            operation_stats['total'] += 1

            # Check if operation has type
            if not operation.operation_type:
                issues.append(
                    f"Operation {operation.id} has no operation type")

            # Check if operation has inputs and outputs
            if not operation.inputs:
                issues.append(f"Operation {operation.id} has no inputs")
            if not operation.outputs:
                issues.append(f"Operation {operation.id} has no outputs")

            # Track statistics
            if operation.parameters:
                operation_stats['with_parameters'] += 1
            if operation.status == 'completed':
                operation_stats['completed'] += 1

        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'stats': operation_stats
        }

    def validate_column_lineage(self) -> Dict[str, Any]:
        """
        Validate column-level lineage tracking.

        Returns:
            Validation results for column lineage
        """
        issues = []
        column_stats = {'nodes_with_schema': 0, 'edges_with_column_lineage': 0}

        # Check nodes with schemas
        for node_id, node in self.tracker.nodes.items():
            if hasattr(node, 'schema') and node.schema:
                column_stats['nodes_with_schema'] += 1

        # Check edges with column lineage information
        for edge in self.tracker.edges:
            if 'column_lineage' in edge.metadata:
                column_stats['edges_with_column_lineage'] += 1

                # Validate column mapping
                column_mapping = edge.metadata['column_lineage']
                if not isinstance(column_mapping, dict):
                    issues.append(
                        f"Edge {edge.id} has invalid column lineage format")
                    continue

                # Check if referenced columns exist in source and target nodes
                source_node = self.tracker.nodes.get(edge.source_id)
                target_node = self.tracker.nodes.get(edge.target_id)

                if source_node and hasattr(source_node, 'schema'):
                    source_columns = set(source_node.schema.keys())
                    for target_col, source_cols in column_mapping.items():
                        for source_col in source_cols:
                            if source_col not in source_columns:
                                issues.append(
                                    f"Edge {edge.id} references non-existent source column: {source_col}")

                if target_node and hasattr(target_node, 'schema'):
                    target_columns = set(target_node.schema.keys())
                    for target_col in column_mapping.keys():
                        if target_col not in target_columns:
                            issues.append(
                                f"Edge {edge.id} references non-existent target column: {target_col}")

        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'stats': column_stats
        }

    def check_circular_dependencies(self) -> Dict[str, Any]:
        """
        Check for circular dependencies in the lineage graph.

        Returns:
            Validation results for circular dependencies
        """
        issues = []

        # Use DFS to detect cycles
        visited = set()
        rec_stack = set()

        def has_cycle(node_id):
            visited.add(node_id)
            rec_stack.add(node_id)

            # Check all neighbors
            for edge in self.tracker.edges:
                if edge.source_id == node_id:
                    neighbor = edge.target_id
                    if neighbor not in visited:
                        if has_cycle(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        issues.append(
                            f"Circular dependency detected involving nodes: {node_id} -> {neighbor}")
                        return True

            rec_stack.remove(node_id)
            return False

        # Check all nodes
        for node_id in self.tracker.nodes.keys():
            if node_id not in visited:
                has_cycle(node_id)

        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'details': {
                'is_dag': len(issues) == 0,
                'total_nodes_checked': len(self.tracker.nodes)
            }
        }

    def validate_data_quality(self,
                              node_id: str,
                              data: pd.DataFrame,
                              expected_schema: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Validate data quality for a specific node.

        Args:
            node_id: ID of the node to validate
            data: Actual data to validate
            expected_schema: Expected schema for validation

        Returns:
            Data quality validation results
        """
        issues = []
        stats = {
            'row_count': len(data),
            'column_count': len(data.columns),
            'null_counts': data.isnull().sum().to_dict(),
            'duplicate_rows': data.duplicated().sum()
        }

        # Check if node exists
        if node_id not in self.tracker.nodes:
            issues.append(f"Node {node_id} not found in tracker")
            return {'passed': False, 'issues': issues, 'stats': stats}

        node = self.tracker.nodes[node_id]

        # Validate against tracked schema
        if hasattr(node, 'schema') and node.schema:
            tracked_columns = set(node.schema.keys())
            actual_columns = set(data.columns)

            missing_columns = tracked_columns - actual_columns
            extra_columns = actual_columns - tracked_columns

            if missing_columns:
                issues.append(f"Missing columns in data: {missing_columns}")
            if extra_columns:
                issues.append(f"Extra columns in data: {extra_columns}")

        # Validate against expected schema if provided
        if expected_schema:
            expected_columns = set(expected_schema.keys())
            actual_columns = set(data.columns)

            if expected_columns != actual_columns:
                issues.append(
                    f"Schema mismatch. Expected: {expected_columns}, Actual: {actual_columns}")

        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'stats': stats
        }
