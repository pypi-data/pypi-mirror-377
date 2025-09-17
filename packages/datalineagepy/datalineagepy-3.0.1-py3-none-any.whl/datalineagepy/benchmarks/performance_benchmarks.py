"""
Performance Benchmarking Suite for DataLineagePy
Comprehensive speed and memory testing for all operations.
"""

import time
import gc
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime
import statistics
import os

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from ..core.tracker import LineageTracker
from ..core.dataframe_wrapper import LineageDataFrame, read_csv
from ..core.analytics import DataProfiler, StatisticalAnalyzer, DataTransformer
from ..core.validation import DataValidator
from ..core.serialization import DataSerializer


class PerformanceBenchmarkSuite:
    """Comprehensive performance benchmarking for all DataLineagePy operations."""

    def __init__(self):
        self.results = {}
        self.test_data_sizes = [100, 1000, 5000]
        self.iterations = 3

    def run_comprehensive_benchmarks(self) -> Dict[str, Any]:
        """Run complete performance benchmark suite."""
        print("🚀 Starting Comprehensive Performance Benchmarks")
        print("=" * 60)

        start_time = time.time()

        # Test categories
        test_categories = [
            ("DataFrame Operations", self._benchmark_dataframe_operations),
            ("Analytics Operations", self._benchmark_analytics_operations),
            ("Validation Operations", self._benchmark_validation_operations),
            ("Lineage Tracking", self._benchmark_lineage_tracking),
            ("Memory Usage", self._benchmark_memory_usage),
        ]

        for category_name, benchmark_func in test_categories:
            print(f"\n📊 Benchmarking {category_name}...")
            try:
                category_results = benchmark_func()
                self.results[category_name.lower().replace(" ", "_")
                             ] = category_results
                print(f"   ✅ {category_name} benchmarks completed")
            except Exception as e:
                print(f"   ❌ {category_name} benchmarks failed: {str(e)}")
                self.results[category_name.lower().replace(" ", "_")] = {
                    "error": str(e)}

        total_time = time.time() - start_time

        # Generate summary
        summary = self._generate_benchmark_summary(total_time)
        self.results['summary'] = summary

        print(f"\n🎉 Benchmarks completed in {total_time:.2f} seconds")
        return self.results

    def _benchmark_dataframe_operations(self) -> Dict[str, Any]:
        """Benchmark core DataFrame operations."""
        operations_results = {}

        operations_to_test = [
            ("head", lambda ldf: ldf.head(10)),
            ("filter", lambda ldf: ldf.filter(ldf._df[ldf.columns[0]] > 0)),
            ("to_dict", lambda ldf: ldf.to_dict()),
            ("to_list", lambda ldf: ldf.to_list()),
        ]

        for op_name, op_func in operations_to_test:
            op_results = {}

            for size in self.test_data_sizes:
                test_data = self._create_test_data(size)
                tracker = LineageTracker()
                ldf = LineageDataFrame(
                    test_data, name=f"test_{size}", tracker=tracker)

                times = []
                memory_before = self._get_memory_usage()

                for _ in range(self.iterations):
                    gc.collect()
                    start_time = time.time()

                    try:
                        result = op_func(ldf)
                        execution_time = time.time() - start_time
                        times.append(execution_time)
                    except Exception as e:
                        times.append(float('inf'))

                memory_after = self._get_memory_usage()

                op_results[f"size_{size}"] = {
                    'avg_time': statistics.mean([t for t in times if t != float('inf')]) if times else 0,
                    'min_time': min([t for t in times if t != float('inf')]) if times else 0,
                    'max_time': max([t for t in times if t != float('inf')]) if times else 0,
                    'memory_delta': memory_after - memory_before,
                    'success_rate': len([t for t in times if t != float('inf')]) / len(times)
                }

            operations_results[op_name] = op_results

        return operations_results

    def _benchmark_analytics_operations(self) -> Dict[str, Any]:
        """Benchmark analytics operations."""
        analytics_results = {}

        analytics_operations = [
            ("data_profiling", self._test_data_profiling),
            ("statistical_analysis", self._test_statistical_analysis),
            ("data_transformation", self._test_data_transformation)
        ]

        for op_name, op_func in analytics_operations:
            op_results = {}

            for size in self.test_data_sizes:
                test_data = self._create_test_data(size)
                tracker = LineageTracker()
                ldf = LineageDataFrame(
                    test_data, name=f"analytics_{size}", tracker=tracker)

                times = []
                memory_before = self._get_memory_usage()

                for _ in range(self.iterations):
                    gc.collect()
                    start_time = time.time()

                    try:
                        op_func(ldf, tracker)
                        execution_time = time.time() - start_time
                        times.append(execution_time)
                    except Exception as e:
                        times.append(float('inf'))

                memory_after = self._get_memory_usage()

                op_results[f"size_{size}"] = {
                    'avg_time': statistics.mean([t for t in times if t != float('inf')]) if times else 0,
                    'memory_delta': memory_after - memory_before,
                    'success_rate': len([t for t in times if t != float('inf')]) / len(times)
                }

            analytics_results[op_name] = op_results

        return analytics_results

    def _benchmark_validation_operations(self) -> Dict[str, Any]:
        """Benchmark validation operations."""
        validation_results = {}

        for size in self.test_data_sizes:
            test_data = self._create_test_data(size)
            tracker = LineageTracker()
            ldf = LineageDataFrame(
                test_data, name=f"validation_{size}", tracker=tracker)

            validator = DataValidator(tracker)

            times = []
            memory_before = self._get_memory_usage()

            for _ in range(self.iterations):
                gc.collect()
                start_time = time.time()

                try:
                    validation_result = validator.validate_dataframe(ldf)
                    execution_time = time.time() - start_time
                    times.append(execution_time)
                except Exception as e:
                    times.append(float('inf'))

            memory_after = self._get_memory_usage()

            validation_results[f"size_{size}"] = {
                'avg_time': statistics.mean([t for t in times if t != float('inf')]) if times else 0,
                'memory_delta': memory_after - memory_before,
                'success_rate': len([t for t in times if t != float('inf')]) / len(times)
            }

        return validation_results

    def _benchmark_lineage_tracking(self) -> Dict[str, Any]:
        """Benchmark lineage tracking overhead."""
        lineage_results = {}

        for size in self.test_data_sizes:
            # Test with lineage tracking
            tracker_times = []
            for _ in range(self.iterations):
                gc.collect()
                test_data = self._create_test_data(size)
                tracker = LineageTracker()

                start_time = time.time()
                ldf = LineageDataFrame(
                    test_data, name=f"lineage_{size}", tracker=tracker)
                filtered = ldf.filter(ldf._df[ldf.columns[0]] > 0)
                execution_time = time.time() - start_time
                tracker_times.append(execution_time)

            # Test without lineage tracking (pure pandas)
            pandas_times = []
            for _ in range(self.iterations):
                gc.collect()
                test_data = self._create_test_data(size)

                start_time = time.time()
                filtered = test_data[test_data[test_data.columns[0]] > 0]
                execution_time = time.time() - start_time
                pandas_times.append(execution_time)

            avg_tracker_time = statistics.mean(tracker_times)
            avg_pandas_time = statistics.mean(pandas_times)
            overhead_percentage = ((avg_tracker_time - avg_pandas_time) /
                                   avg_pandas_time) * 100 if avg_pandas_time > 0 else 0

            lineage_results[f"size_{size}"] = {
                'lineage_time': avg_tracker_time,
                'pandas_time': avg_pandas_time,
                'overhead_percentage': overhead_percentage,
                'overhead_absolute': avg_tracker_time - avg_pandas_time
            }

        return lineage_results

    def _benchmark_memory_usage(self) -> Dict[str, Any]:
        """Benchmark memory usage patterns."""
        memory_results = {}

        for size in self.test_data_sizes:
            gc.collect()
            initial_memory = self._get_memory_usage()

            # Create test data and tracker
            test_data = self._create_test_data(size)
            tracker = LineageTracker()
            after_data_memory = self._get_memory_usage()

            # Create LineageDataFrame
            ldf = LineageDataFrame(
                test_data, name=f"memory_{size}", tracker=tracker)
            after_ldf_memory = self._get_memory_usage()

            # Perform operations
            filtered = ldf.filter(ldf._df[ldf.columns[0]] > 0)
            after_ops_memory = self._get_memory_usage()

            memory_results[f"size_{size}"] = {
                'initial_memory': initial_memory,
                'data_memory_delta': after_data_memory - initial_memory,
                'ldf_memory_delta': after_ldf_memory - after_data_memory,
                'operations_memory_delta': after_ops_memory - after_ldf_memory,
                'total_memory_delta': after_ops_memory - initial_memory,
                'lineage_nodes': len(tracker.nodes),
                'lineage_edges': len(tracker.edges)
            }

        return memory_results

    def _test_data_profiling(self, ldf: LineageDataFrame, tracker: LineageTracker):
        """Test data profiling performance."""
        profiler = DataProfiler(tracker)
        return profiler.profile_dataset(ldf, include_correlations=False)

    def _test_statistical_analysis(self, ldf: LineageDataFrame, tracker: LineageTracker):
        """Test statistical analysis performance."""
        analyzer = StatisticalAnalyzer(tracker)
        numeric_cols = ldf._df.select_dtypes(include=[np.number]).columns[:2]
        if len(numeric_cols) >= 1:
            return analyzer.hypothesis_test(ldf, 'normality', columns=numeric_cols[:1].tolist())
        return {}

    def _test_data_transformation(self, ldf: LineageDataFrame, tracker: LineageTracker):
        """Test data transformation performance."""
        transformer = DataTransformer(tracker)
        numeric_cols = ldf._df.select_dtypes(include=[np.number]).columns[:2]
        if len(numeric_cols) >= 1:
            return transformer.normalize(ldf, columns=numeric_cols[:1].tolist())
        return ldf

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

    def _generate_benchmark_summary(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive benchmark summary."""
        summary = {
            'total_benchmark_time': total_time,
            'timestamp': datetime.now().isoformat(),
            'test_data_sizes': self.test_data_sizes,
            'iterations_per_test': self.iterations,
            'performance_highlights': {},
            'recommendations': []
        }

        # Analyze results for highlights
        if 'dataframe_operations' in self.results:
            df_ops = self.results['dataframe_operations']
            if df_ops:
                fastest_op = min(df_ops.items(),
                                 key=lambda x: x[1].get('size_1000', {}).get('avg_time', float('inf')))
                summary['performance_highlights']['fastest_dataframe_operation'] = fastest_op[0]

        if 'lineage_tracking' in self.results:
            lineage = self.results['lineage_tracking']
            overheads = []
            for result in lineage.values():
                if isinstance(result, dict) and 'overhead_percentage' in result:
                    overheads.append(result['overhead_percentage'])

            if overheads:
                avg_overhead = statistics.mean(overheads)
                summary['performance_highlights'][
                    'average_lineage_overhead'] = f"{avg_overhead:.1f}%"

                # Generate recommendations
                if avg_overhead > 50:
                    summary['recommendations'].append(
                        "Consider optimizing lineage tracking for better performance")
                else:
                    summary['recommendations'].append(
                        "Lineage tracking overhead is acceptable")

        summary['recommendations'].append(
            "Use appropriate data sizes for your use case")

        return summary

    def export_results(self, output_path: str, format: str = 'json'):
        """Export benchmark results to file."""
        import json

        if format.lower() == 'json':
            with open(output_path, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)

        return output_path

    def get_performance_score(self) -> float:
        """Calculate overall performance score (0-100)."""
        if not self.results:
            return 0.0

        scores = []

        # Score lineage overhead (lower is better)
        if 'lineage_tracking' in self.results:
            lineage = self.results['lineage_tracking']
            overheads = []
            for result in lineage.values():
                if isinstance(result, dict) and 'overhead_percentage' in result:
                    overheads.append(result['overhead_percentage'])

            if overheads:
                avg_overhead = statistics.mean(overheads)
                # 0% overhead = 100 points
                overhead_score = max(0, 100 - avg_overhead)
                scores.append(overhead_score)

        # Score operation success rates
        for category in ['dataframe_operations', 'analytics_operations', 'validation_operations']:
            if category in self.results:
                success_rates = []
                for op_results in self.results[category].values():
                    if isinstance(op_results, dict):
                        for size_result in op_results.values():
                            if isinstance(size_result, dict) and 'success_rate' in size_result:
                                success_rates.append(
                                    size_result['success_rate'] * 100)

                if success_rates:
                    avg_success_rate = statistics.mean(success_rates)
                    scores.append(avg_success_rate)

        return statistics.mean(scores) if scores else 0.0
