"""
Memory Profiler for DataLineagePy
Detailed memory usage analysis and optimization recommendations.
"""

import gc
import time
import tracemalloc
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import statistics

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from ..core.tracker import LineageTracker
from ..core.dataframe_wrapper import LineageDataFrame


class MemoryProfiler:
    """Detailed memory profiling for DataLineagePy operations."""

    def __init__(self):
        self.results = {}
        self.memory_snapshots = []
        self.tracking_enabled = False

    def start_memory_tracking(self):
        """Start memory tracking using tracemalloc."""
        tracemalloc.start()
        self.tracking_enabled = True

    def stop_memory_tracking(self):
        """Stop memory tracking."""
        if self.tracking_enabled:
            tracemalloc.stop()
            self.tracking_enabled = False

    def profile_comprehensive_memory_usage(self) -> Dict[str, Any]:
        """Run comprehensive memory profiling analysis."""
        print("🧠 Starting Comprehensive Memory Profiling")
        print("=" * 50)

        start_time = time.time()

        # Start memory tracking
        self.start_memory_tracking()

        # Test categories
        test_categories = [
            ("Baseline Memory", self._profile_baseline_memory),
            ("DataFrame Creation", self._profile_dataframe_creation),
            ("Operations Memory", self._profile_operations_memory),
            ("Lineage Memory", self._profile_lineage_memory),
            ("Scaling Analysis", self._profile_memory_scaling),
            ("Memory Leaks", self._profile_memory_leaks),
            ("Optimization Tips", self._analyze_memory_optimization)
        ]

        for category_name, profile_func in test_categories:
            print(f"\n🔍 Profiling {category_name}...")
            try:
                category_results = profile_func()
                self.results[category_name.lower().replace(" ", "_")
                             ] = category_results
                print(f"   ✅ {category_name} profiling completed")
            except Exception as e:
                print(f"   ❌ {category_name} profiling failed: {str(e)}")
                self.results[category_name.lower().replace(" ", "_")] = {
                    "error": str(e)}

        total_time = time.time() - start_time

        # Stop memory tracking
        self.stop_memory_tracking()

        # Generate memory summary
        summary = self._generate_memory_summary(total_time)
        self.results['memory_summary'] = summary

        print(f"\n🎉 Memory profiling completed in {total_time:.2f} seconds")
        return self.results

    def _profile_baseline_memory(self) -> Dict[str, Any]:
        """Profile baseline memory usage."""
        baseline_results = {}

        # Clean up before baseline
        gc.collect()

        # Baseline memory
        baseline_memory = self._get_memory_usage()
        baseline_results['initial_memory_mb'] = baseline_memory

        # Import memory impact
        import_start_memory = self._get_memory_usage()
        from ..core import tracker, dataframe_wrapper, analytics, validation
        import_end_memory = self._get_memory_usage()

        baseline_results['import_memory_impact'] = import_end_memory - \
            import_start_memory

        # Python environment info
        baseline_results['python_info'] = {
            'psutil_available': PSUTIL_AVAILABLE,
            'tracemalloc_available': tracemalloc.is_tracing() if hasattr(tracemalloc, 'is_tracing') else True
        }

        return baseline_results

    def _profile_dataframe_creation(self) -> Dict[str, Any]:
        """Profile memory usage during DataFrame creation."""
        creation_results = {}

        sizes = [100, 1000, 5000, 10000]

        for size in sizes:
            gc.collect()

            # Memory before creating data
            before_data = self._get_memory_usage()

            # Create test data
            test_data = self._create_test_data(size)
            after_data = self._get_memory_usage()

            # Create LineageTracker
            tracker = LineageTracker()
            after_tracker = self._get_memory_usage()

            # Create LineageDataFrame
            ldf = LineageDataFrame(
                test_data, name=f"test_{size}", tracker=tracker)
            after_ldf = self._get_memory_usage()

            creation_results[f"size_{size}"] = {
                'data_memory_mb': after_data - before_data,
                'tracker_memory_mb': after_tracker - after_data,
                'ldf_memory_mb': after_ldf - after_tracker,
                'total_memory_mb': after_ldf - before_data,
                'memory_per_row_kb': ((after_ldf - before_data) * 1024) / size,
                'rows': size,
                'columns': len(test_data.columns)
            }

        return creation_results

    def _profile_operations_memory(self) -> Dict[str, Any]:
        """Profile memory usage during operations."""
        operations_results = {}

        test_size = 5000
        test_data = self._create_test_data(test_size)

        operations = [
            ("filter", lambda ldf: ldf.filter(ldf._df['value1'] > 100)),
            ("aggregate", lambda ldf: ldf.aggregate(
                {'value1': 'mean', 'value2': 'sum'})),
            ("head", lambda ldf: ldf.head(100)),
            ("to_dict", lambda ldf: ldf.to_dict()),
            ("to_list", lambda ldf: ldf.to_list())
        ]

        for op_name, op_func in operations:
            gc.collect()

            # Setup
            tracker = LineageTracker()
            ldf = LineageDataFrame(
                test_data.copy(), name=f"op_test_{op_name}", tracker=tracker)

            before_op = self._get_memory_usage()

            # Take memory snapshot before operation
            if self.tracking_enabled:
                snapshot_before = tracemalloc.take_snapshot()

            # Execute operation
            try:
                result = op_func(ldf)
                after_op = self._get_memory_usage()

                # Take memory snapshot after operation
                if self.tracking_enabled:
                    snapshot_after = tracemalloc.take_snapshot()
                    top_stats = snapshot_after.compare_to(
                        snapshot_before, 'lineno')[:5]
                    memory_details = [str(stat) for stat in top_stats]
                else:
                    memory_details = []

                operations_results[op_name] = {
                    'memory_delta_mb': after_op - before_op,
                    # -1 for initial node
                    'lineage_nodes_added': len(tracker.nodes) - 1,
                    'lineage_edges_added': len(tracker.edges),
                    'operation_success': True,
                    'memory_details': memory_details
                }

            except Exception as e:
                operations_results[op_name] = {
                    'memory_delta_mb': 0,
                    'lineage_nodes_added': 0,
                    'lineage_edges_added': 0,
                    'operation_success': False,
                    'error': str(e)
                }

        return operations_results

    def _profile_lineage_memory(self) -> Dict[str, Any]:
        """Profile memory usage of lineage tracking components."""
        lineage_results = {}

        # Test different numbers of operations
        operation_counts = [1, 5, 10, 20, 50]

        for op_count in operation_counts:
            gc.collect()

            tracker = LineageTracker()
            test_data = self._create_test_data(1000)

            before_lineage = self._get_memory_usage()

            # Perform multiple operations to build lineage
            ldf = LineageDataFrame(
                test_data, name="lineage_test", tracker=tracker)

            for i in range(op_count):
                ldf = ldf.filter(ldf._df['value1'] > (50 + i))

            after_lineage = self._get_memory_usage()

            lineage_results[f"operations_{op_count}"] = {
                'lineage_memory_mb': after_lineage - before_lineage,
                'nodes_created': len(tracker.nodes),
                'edges_created': len(tracker.edges),
                'operations_performed': op_count + 1,  # +1 for initial DataFrame
                'memory_per_node_kb': ((after_lineage - before_lineage) * 1024) / len(tracker.nodes) if tracker.nodes else 0,
                'memory_per_edge_kb': ((after_lineage - before_lineage) * 1024) / len(tracker.edges) if tracker.edges else 0
            }

        return lineage_results

    def _profile_memory_scaling(self) -> Dict[str, Any]:
        """Analyze how memory scales with data size."""
        scaling_results = {}

        sizes = [100, 500, 1000, 2000, 5000]

        for size in sizes:
            gc.collect()

            before_total = self._get_memory_usage()

            # Create and process data
            test_data = self._create_test_data(size)
            tracker = LineageTracker()
            ldf = LineageDataFrame(
                test_data, name=f"scale_{size}", tracker=tracker)

            # Perform standard operations
            filtered = ldf.filter(ldf._df['value1'] > 100)
            aggregated = filtered.aggregate({'value1': 'mean'})

            after_total = self._get_memory_usage()

            scaling_results[f"size_{size}"] = {
                'total_memory_mb': after_total - before_total,
                'memory_per_row_kb': ((after_total - before_total) * 1024) / size,
                'rows': size,
                'lineage_nodes': len(tracker.nodes),
                'lineage_edges': len(tracker.edges),
                'memory_efficiency': size / ((after_total - before_total) * 1024) if after_total > before_total else 0
            }

        # Calculate scaling trends
        sizes_mb = [scaling_results[f"size_{size}"]
                    ['total_memory_mb'] for size in sizes]
        scaling_results['scaling_analysis'] = {
            'memory_growth_trend': 'linear' if max(sizes_mb) / min(sizes_mb) < (max(sizes) / min(sizes)) * 1.5 else 'super-linear',
            'average_memory_per_1k_rows': statistics.mean([scaling_results[f"size_{size}"]['memory_per_row_kb'] * 1000 for size in sizes]),
            'memory_efficiency_score': statistics.mean([scaling_results[f"size_{size}"]['memory_efficiency'] for size in sizes])
        }

        return scaling_results

    def _profile_memory_leaks(self) -> Dict[str, Any]:
        """Test for potential memory leaks."""
        leak_results = {}

        # Test repeated operations
        iterations = 10
        memory_readings = []

        tracker = LineageTracker()

        for i in range(iterations):
            gc.collect()
            memory_before = self._get_memory_usage()

            # Create and destroy DataFrame multiple times
            test_data = self._create_test_data(1000)
            ldf = LineageDataFrame(
                test_data, name=f"leak_test_{i}", tracker=tracker)
            filtered = ldf.filter(ldf._df['value1'] > 100)
            result = filtered.to_dict()

            # Explicitly delete references
            del ldf, filtered, result, test_data

            gc.collect()
            memory_after = self._get_memory_usage()
            memory_readings.append(memory_after)

        # Analyze memory trend
        memory_trend = 'increasing' if memory_readings[-1] > memory_readings[0] * \
            1.1 else 'stable'
        memory_growth = memory_readings[-1] - memory_readings[0]

        leak_results = {
            'memory_trend': memory_trend,
            'total_memory_growth_mb': memory_growth,
            'average_growth_per_iteration_mb': memory_growth / iterations,
            'memory_readings': memory_readings,
            'iterations_tested': iterations,
            'potential_leak_detected': memory_growth > 10,  # More than 10MB growth
            'lineage_nodes_accumulated': len(tracker.nodes),
            'lineage_cleanup_needed': len(tracker.nodes) > iterations * 2
        }

        return leak_results

    def _analyze_memory_optimization(self) -> Dict[str, Any]:
        """Analyze memory optimization opportunities."""
        optimization_results = {}

        # Test different optimization strategies
        test_data = self._create_test_data(5000)

        # Strategy 1: Regular usage
        gc.collect()
        before_regular = self._get_memory_usage()

        tracker1 = LineageTracker()
        ldf1 = LineageDataFrame(
            test_data.copy(), name="regular", tracker=tracker1)
        result1 = ldf1.filter(ldf1._df['value1'] > 100).aggregate(
            {'value1': 'mean'})

        after_regular = self._get_memory_usage()

        # Strategy 2: Manual cleanup
        gc.collect()
        before_cleanup = self._get_memory_usage()

        tracker2 = LineageTracker()
        ldf2 = LineageDataFrame(
            test_data.copy(), name="cleanup", tracker=tracker2)
        result2 = ldf2.filter(ldf2._df['value1'] > 100).aggregate(
            {'value1': 'mean'})

        # Manual cleanup
        del ldf2, result2
        tracker2.clear_cache()  # Assuming this method exists
        gc.collect()

        after_cleanup = self._get_memory_usage()

        optimization_results = {
            'regular_usage': {
                'memory_used_mb': after_regular - before_regular,
                'lineage_nodes': len(tracker1.nodes),
                'lineage_edges': len(tracker1.edges)
            },
            'with_cleanup': {
                'memory_used_mb': after_cleanup - before_cleanup,
                'lineage_nodes': len(tracker2.nodes),
                'lineage_edges': len(tracker2.edges)
            },
            'optimization_recommendations': [
                "Use gc.collect() after processing large datasets",
                "Clear lineage tracker cache when not needed for analysis",
                "Delete intermediate DataFrame references explicitly",
                "Consider processing data in chunks for very large datasets",
                "Monitor memory usage during long-running processes"
            ],
            'memory_savings_potential': max(0, (after_regular - before_regular) - (after_cleanup - before_cleanup))
        }

        return optimization_results

    def _create_test_data(self, size: int) -> pd.DataFrame:
        """Create test data of specified size."""
        np.random.seed(42)

        return pd.DataFrame({
            'id': range(size),
            'value1': np.random.normal(100, 20, size),
            'value2': np.random.uniform(0, 1000, size),
            'category': np.random.choice(['A', 'B', 'C', 'D'], size),
            'flag': np.random.choice([True, False], size),
        })

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                return process.memory_info().rss / 1024 / 1024
            except Exception:
                pass
        return 0.0

    def _generate_memory_summary(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive memory analysis summary."""
        summary = {
            'profiling_time': total_time,
            'timestamp': datetime.now().isoformat(),
            'memory_insights': {},
            'optimization_score': 0,
            'recommendations': []
        }

        # Analyze memory insights
        if 'scaling_analysis' in self.results.get('memory_scaling', {}):
            scaling = self.results['memory_scaling']['scaling_analysis']
            summary['memory_insights']['scaling_efficiency'] = scaling.get(
                'memory_efficiency_score', 0)
            summary['memory_insights']['growth_pattern'] = scaling.get(
                'memory_growth_trend', 'unknown')

        if 'memory_leaks' in self.results:
            leaks = self.results['memory_leaks']
            summary['memory_insights']['leak_risk'] = 'high' if leaks.get(
                'potential_leak_detected', False) else 'low'
            summary['memory_insights']['memory_stability'] = leaks.get(
                'memory_trend', 'unknown')

        # Calculate optimization score
        factors = []

        # Factor 1: Memory efficiency
        if 'memory_scaling' in self.results:
            efficiency = self.results['memory_scaling'].get(
                'scaling_analysis', {}).get('memory_efficiency_score', 0)
            factors.append(min(100, efficiency * 10))  # Scale to 0-100

        # Factor 2: Leak risk (inverted)
        if 'memory_leaks' in self.results:
            leak_detected = self.results['memory_leaks'].get(
                'potential_leak_detected', True)
            factors.append(20 if leak_detected else 100)

        # Factor 3: Operations efficiency
        if 'operations_memory' in self.results:
            successful_ops = sum(1 for op in self.results['operations_memory'].values()
                                 if isinstance(op, dict) and op.get('operation_success', False))
            total_ops = len(self.results['operations_memory'])
            factors.append((successful_ops / total_ops)
                           * 100 if total_ops > 0 else 0)

        summary['optimization_score'] = statistics.mean(
            factors) if factors else 50

        # Generate recommendations
        if summary['optimization_score'] > 80:
            summary['recommendations'].append(
                "Excellent memory management - no issues detected")
        elif summary['optimization_score'] > 60:
            summary['recommendations'].append(
                "Good memory usage with minor optimization opportunities")
        else:
            summary['recommendations'].append(
                "Consider implementing memory optimization strategies")

        summary['recommendations'].extend([
            "Monitor memory usage for production workloads",
            "Use appropriate data sizes for available memory",
            "Consider chunked processing for very large datasets"
        ])

        return summary

    def export_memory_profile(self, output_path: str, format: str = 'json'):
        """Export memory profile results."""
        import json

        if format.lower() == 'json':
            with open(output_path, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)

        return output_path
