"""
Benchmark suite for data lineage performance testing.
"""

import time
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import psutil
import os

from ..core.tracker import LineageTracker
from ..core.dataframe_wrapper import LineageDataFrame


class BenchmarkSuite:
    """
    Performance benchmarking suite for DataLineagePy.
    """

    def __init__(self):
        """Initialize the benchmark suite."""
        self.results = []
        self.current_tracker = None

    def run_all_benchmarks(self) -> Dict[str, Any]:
        """
        Run all available benchmarks.

        Returns:
            Dictionary containing all benchmark results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self._get_system_info(),
            'benchmarks': {}
        }

        # Run individual benchmarks
        results['benchmarks']['basic_operations'] = self.benchmark_basic_operations()
        results['benchmarks']['large_dataset'] = self.benchmark_large_dataset()
        results['benchmarks']['complex_lineage'] = self.benchmark_complex_lineage()
        results['benchmarks']['memory_usage'] = self.benchmark_memory_usage()
        results['benchmarks']['export_performance'] = self.benchmark_export_performance()

        return results

    def benchmark_basic_operations(self,
                                   num_operations: int = 1000) -> Dict[str, Any]:
        """
        Benchmark basic lineage tracking operations.

        Args:
            num_operations: Number of operations to benchmark

        Returns:
            Benchmark results for basic operations
        """
        tracker = LineageTracker("benchmark_basic")

        # Benchmark node creation
        start_time = time.time()
        nodes = []
        for i in range(num_operations):
            node = tracker.create_node("data", f"node_{i}")
            nodes.append(node)
        node_creation_time = time.time() - start_time

        # Benchmark edge creation
        start_time = time.time()
        for i in range(num_operations - 1):
            tracker.add_edge(nodes[i], nodes[i + 1])
        edge_creation_time = time.time() - start_time

        # Benchmark operation tracking
        start_time = time.time()
        for i in range(0, num_operations - 1, 2):
            if i + 1 < len(nodes):
                tracker.track_operation(
                    "transform",
                    [nodes[i]],
                    [nodes[i + 1]]
                )
        operation_tracking_time = time.time() - start_time

        # Benchmark lineage retrieval
        start_time = time.time()
        for i in range(min(100, num_operations)):  # Sample 100 nodes
            tracker.get_lineage(nodes[i].id)
        lineage_retrieval_time = time.time() - start_time

        return {
            'num_operations': num_operations,
            'node_creation_time': node_creation_time,
            'edge_creation_time': edge_creation_time,
            'operation_tracking_time': operation_tracking_time,
            'lineage_retrieval_time': lineage_retrieval_time,
            'nodes_per_second': num_operations / node_creation_time if node_creation_time > 0 else 0,
            'edges_per_second': (num_operations - 1) / edge_creation_time if edge_creation_time > 0 else 0,
            'total_nodes': len(tracker.nodes),
            'total_edges': len(tracker.edges),
            'total_operations': len(tracker.operations)
        }

    def benchmark_large_dataset(self,
                                rows: int = 100000,
                                cols: int = 50) -> Dict[str, Any]:
        """
        Benchmark lineage tracking with large datasets.

        Args:
            rows: Number of rows in test dataset
            cols: Number of columns in test dataset

        Returns:
            Benchmark results for large dataset operations
        """
        # Create large test dataset
        data_creation_start = time.time()
        data = pd.DataFrame(
            np.random.randn(rows, cols),
            columns=[f'col_{i}' for i in range(cols)]
        )
        data_creation_time = time.time() - data_creation_start

        # Test lineage tracking with large dataset
        tracker = LineageTracker("benchmark_large")

        # Create LineageDataFrame
        wrapper_creation_start = time.time()
        ldf = LineageDataFrame(data, "large_dataset", tracker)
        wrapper_creation_time = time.time() - wrapper_creation_start

        # Test operations on large dataset
        operations_start = time.time()

        # Test filtering
        filtered = ldf.head(1000)

        # Test aggregation
        aggregated = filtered.groupby(filtered.columns[0]).mean()

        # Test joining (create second dataset)
        data2 = pd.DataFrame(
            np.random.randn(1000, 10),
            columns=[f'join_col_{i}' for i in range(10)]
        )
        ldf2 = LineageDataFrame(data2, "join_dataset", tracker)

        operations_time = time.time() - operations_start

        # Test lineage retrieval
        lineage_start = time.time()
        lineage = tracker.get_lineage(aggregated.node.id)
        lineage_time = time.time() - lineage_start

        return {
            'dataset_size': {'rows': rows, 'cols': cols},
            'data_creation_time': data_creation_time,
            'wrapper_creation_time': wrapper_creation_time,
            'operations_time': operations_time,
            'lineage_retrieval_time': lineage_time,
            'total_nodes': len(tracker.nodes),
            'total_edges': len(tracker.edges),
            'memory_usage_mb': self._get_memory_usage()
        }

    def benchmark_complex_lineage(self,
                                  depth: int = 10,
                                  width: int = 5) -> Dict[str, Any]:
        """
        Benchmark complex lineage graphs with multiple branches.

        Args:
            depth: Depth of the lineage graph
            width: Width (branching factor) of the lineage graph

        Returns:
            Benchmark results for complex lineage
        """
        tracker = LineageTracker("benchmark_complex")

        # Create complex lineage graph
        creation_start = time.time()

        # Create initial nodes
        current_level = []
        for i in range(width):
            node = tracker.create_node("data", f"level_0_node_{i}")
            current_level.append(node)

        # Create multiple levels with branching
        for level in range(1, depth):
            next_level = []
            for i in range(width):
                # Create new node
                new_node = tracker.create_node(
                    "data", f"level_{level}_node_{i}")
                next_level.append(new_node)

                # Connect to multiple nodes from previous level
                for prev_node in current_level:
                    tracker.track_operation(
                        f"transform_level_{level}",
                        [prev_node],
                        [new_node],
                        metadata={'level': level, 'branch': i}
                    )

            current_level = next_level

        creation_time = time.time() - creation_start

        # Benchmark lineage queries
        query_start = time.time()

        # Test upstream lineage for final nodes
        upstream_times = []
        for node in current_level:
            start = time.time()
            upstream = tracker.get_lineage(node.id, 'upstream')
            upstream_times.append(time.time() - start)

        # Test downstream lineage for initial nodes
        downstream_times = []
        for i in range(width):
            initial_node_id = list(tracker.nodes.keys())[i]
            start = time.time()
            downstream = tracker.get_lineage(initial_node_id, 'downstream')
            downstream_times.append(time.time() - start)

        query_time = time.time() - query_start

        return {
            'graph_dimensions': {'depth': depth, 'width': width},
            'creation_time': creation_time,
            'query_time': query_time,
            'avg_upstream_query_time': np.mean(upstream_times),
            'avg_downstream_query_time': np.mean(downstream_times),
            'total_nodes': len(tracker.nodes),
            'total_edges': len(tracker.edges),
            'total_operations': len(tracker.operations)
        }

    def benchmark_memory_usage(self) -> Dict[str, Any]:
        """
        Benchmark memory usage patterns.

        Returns:
            Memory usage benchmark results
        """
        initial_memory = self._get_memory_usage()

        tracker = LineageTracker("benchmark_memory")
        memory_samples = [initial_memory]

        # Create nodes and track memory
        for i in range(1000):
            tracker.create_node("data", f"node_{i}")
            if i % 100 == 0:
                memory_samples.append(self._get_memory_usage())

        # Create edges and track memory
        nodes = list(tracker.nodes.values())
        for i in range(0, len(nodes) - 1, 2):
            tracker.add_edge(nodes[i], nodes[i + 1])
            if i % 200 == 0:
                memory_samples.append(self._get_memory_usage())

        final_memory = self._get_memory_usage()

        return {
            'initial_memory_mb': initial_memory,
            'final_memory_mb': final_memory,
            'memory_increase_mb': final_memory - initial_memory,
            'memory_samples': memory_samples,
            'peak_memory_mb': max(memory_samples),
            'nodes_created': len(tracker.nodes),
            'edges_created': len(tracker.edges)
        }

    def benchmark_export_performance(self) -> Dict[str, Any]:
        """
        Benchmark export performance for different formats.

        Returns:
            Export performance benchmark results
        """
        # Create test tracker with substantial data
        tracker = LineageTracker("benchmark_export")

        # Create nodes
        nodes = []
        for i in range(500):
            node = tracker.create_node("data", f"export_node_{i}")
            nodes.append(node)

        # Create edges
        for i in range(len(nodes) - 1):
            tracker.add_edge(nodes[i], nodes[i + 1])

        # Create operations
        for i in range(0, len(nodes) - 1, 3):
            if i + 1 < len(nodes):
                tracker.track_operation(
                    "transform",
                    [nodes[i]],
                    [nodes[i + 1]]
                )

        # Benchmark different export formats
        formats = ['dict', 'json', 'dot']
        export_times = {}

        for format_name in formats:
            start_time = time.time()
            try:
                result = tracker.export_graph(format_name)
                export_times[format_name] = time.time() - start_time
            except Exception as e:
                export_times[format_name] = None

        return {
            'graph_size': {
                'nodes': len(tracker.nodes),
                'edges': len(tracker.edges),
                'operations': len(tracker.operations)
            },
            'export_times': export_times,
            'fastest_format': min(export_times.items(), key=lambda x: x[1] if x[1] is not None else float('inf'))
        }

    def benchmark_custom_operation(self,
                                   operation_func: Callable,
                                   setup_func: Optional[Callable] = None,
                                   iterations: int = 100) -> Dict[str, Any]:
        """
        Benchmark a custom operation.

        Args:
            operation_func: Function to benchmark
            setup_func: Optional setup function
            iterations: Number of iterations to run

        Returns:
            Custom operation benchmark results
        """
        if setup_func:
            setup_func()

        times = []
        for i in range(iterations):
            start_time = time.time()
            operation_func()
            times.append(time.time() - start_time)

        return {
            'iterations': iterations,
            'total_time': sum(times),
            'average_time': np.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_time': np.std(times),
            'operations_per_second': iterations / sum(times) if sum(times) > 0 else 0
        }

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for benchmarking context."""
        return {
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / (1024**3),
            'python_version': os.sys.version,
            'platform': os.name
        }

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024**2)
