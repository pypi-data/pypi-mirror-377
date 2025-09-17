"""
Performance Monitoring and Optimization Module for DataLineagePy
Provides performance tracking, memory usage monitoring, and optimization suggestions.
"""

import time
import gc
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from functools import wraps

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from .tracker import LineageTracker
from .nodes import DataNode


class PerformanceMonitor:
    """Monitor and track performance metrics with lineage tracking."""

    def __init__(self, tracker: LineageTracker):
        self.tracker = tracker
        self.metrics = {}
        self.operation_times = {}
        self.memory_snapshots = []
        self.start_time = time.time()
        self.monitoring_enabled = True

    def start_monitoring(self):
        """Start performance monitoring."""
        self.monitoring_enabled = True
        self.start_time = time.time()
        self._take_memory_snapshot("monitoring_start")

    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring_enabled = False
        self._take_memory_snapshot("monitoring_end")

    def time_operation(self, operation_name: str, func: Callable, *args, **kwargs):
        """Time an operation and track performance."""
        if not self.monitoring_enabled:
            return func(*args, **kwargs)

        # Take memory snapshot before operation
        memory_before = self._get_memory_usage()
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
            raise
        finally:
            # Record metrics regardless of success/failure
            end_time = time.time()
            execution_time = end_time - start_time
            memory_after = self._get_memory_usage()
            memory_delta = memory_after - memory_before

            # Store operation metrics
            self.operation_times[operation_name] = {
                'execution_time': execution_time,
                'memory_before': memory_before,
                'memory_after': memory_after,
                'memory_delta': memory_delta,
                'timestamp': datetime.now().isoformat(),
                'success': success,
                'error': error
            }

            # Create performance node
            perf_node = self.tracker.create_node(
                "performance", f"{operation_name}_performance")
            perf_node.add_metadata("execution_time", execution_time)
            perf_node.add_metadata("memory_usage", memory_delta)
            perf_node.add_metadata("success", success)

            if error:
                perf_node.add_metadata("error", error)

        return result

    def performance_decorator(self, operation_name: Optional[str] = None):
        """Decorator to automatically track function performance."""
        def decorator(func):
            nonlocal operation_name
            if operation_name is None:
                operation_name = f"{func.__module__}.{func.__name__}"

            @wraps(func)
            def wrapper(*args, **kwargs):
                return self.time_operation(operation_name, func, *args, **kwargs)
            return wrapper
        return decorator

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                return process.memory_info().rss / 1024 / 1024
            except Exception:
                pass

        # Fallback for when psutil is not available
        return 0.0

    def _take_memory_snapshot(self, label: str):
        """Take a memory usage snapshot."""
        snapshot = {
            'label': label,
            'timestamp': datetime.now().isoformat(),
            'memory_mb': self._get_memory_usage(),
        }

        if PSUTIL_AVAILABLE:
            try:
                snapshot['cpu_percent'] = psutil.cpu_percent()
            except Exception:
                snapshot['cpu_percent'] = 0.0
        else:
            snapshot['cpu_percent'] = 0.0

        self.memory_snapshots.append(snapshot)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        if not self.operation_times:
            return {"message": "No operations tracked yet"}

        # Calculate summary statistics
        execution_times = [op['execution_time']
                           for op in self.operation_times.values() if op['success']]
        memory_deltas = [op['memory_delta']
                         for op in self.operation_times.values() if op['success']]

        summary = {
            'total_operations': len(self.operation_times),
            'successful_operations': sum(1 for op in self.operation_times.values() if op['success']),
            'failed_operations': sum(1 for op in self.operation_times.values() if not op['success']),
            'total_execution_time': sum(execution_times),
            'average_execution_time': sum(execution_times) / len(execution_times) if execution_times else 0,
            'total_memory_delta': sum(memory_deltas),
            'average_memory_delta': sum(memory_deltas) / len(memory_deltas) if memory_deltas else 0,
            'current_memory_usage': self._get_memory_usage(),
            'monitoring_duration': time.time() - self.start_time,
            'operation_details': self.operation_times,
            'memory_snapshots': self.memory_snapshots
        }

        # Identify bottlenecks
        if execution_times:
            slowest_operation = max(self.operation_times.items(),
                                    key=lambda x: x[1]['execution_time'] if x[1]['success'] else 0)
            summary['slowest_operation'] = {
                'name': slowest_operation[0],
                'time': slowest_operation[1]['execution_time']
            }

        if memory_deltas:
            memory_intensive_operation = max(self.operation_times.items(),
                                             key=lambda x: x[1]['memory_delta'] if x[1]['success'] else 0)
            summary['most_memory_intensive'] = {
                'name': memory_intensive_operation[0],
                'memory_delta': memory_intensive_operation[1]['memory_delta']
            }

        return summary

    def get_optimization_suggestions(self) -> List[str]:
        """Generate optimization suggestions based on performance data."""
        suggestions = []

        if not self.operation_times:
            return ["No performance data available for analysis"]

        # Analyze execution times
        execution_times = [op['execution_time']
                           for op in self.operation_times.values() if op['success']]
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            slow_operations = [name for name, op in self.operation_times.items()
                               if op['success'] and op['execution_time'] > avg_time * 2]

            if slow_operations:
                suggestions.append(
                    f"Consider optimizing slow operations: {', '.join(slow_operations)}")

        # Analyze memory usage
        memory_deltas = [op['memory_delta']
                         for op in self.operation_times.values() if op['success']]
        if memory_deltas:
            high_memory_ops = [name for name, op in self.operation_times.items()
                               # >100MB
                               if op['success'] and op['memory_delta'] > 100]

            if high_memory_ops:
                suggestions.append(
                    f"High memory usage detected in: {', '.join(high_memory_ops)}")
                suggestions.append(
                    "Consider using chunking or streaming for large datasets")

        # Check for failed operations
        failed_ops = [name for name,
                      op in self.operation_times.items() if not op['success']]
        if failed_ops:
            suggestions.append(
                f"Failed operations detected: {', '.join(failed_ops)}")
            suggestions.append("Review error handling and data validation")

        # Check memory trends
        if len(self.memory_snapshots) > 1:
            memory_trend = self.memory_snapshots[-1]['memory_mb'] - \
                self.memory_snapshots[0]['memory_mb']
            if memory_trend > 50:  # >50MB increase
                suggestions.append(
                    "Memory usage trend increasing - consider memory cleanup")
                suggestions.append(
                    "Use gc.collect() or clear unused variables")

        if not suggestions:
            suggestions.append(
                "Performance looks good! No obvious bottlenecks detected.")

        return suggestions


class BenchmarkSuite:
    """Comprehensive benchmarking suite for DataLineagePy operations."""

    def __init__(self, tracker: LineageTracker):
        self.tracker = tracker
        self.benchmark_results = {}

    def run_operation_benchmark(self, operation_func: Callable,
                                operation_name: str,
                                iterations: int = 5,
                                *args, **kwargs) -> Dict[str, Any]:
        """Run benchmark for a specific operation."""
        execution_times = []
        memory_usages = []

        for i in range(iterations):
            # Cleanup before each iteration
            gc.collect()

            memory_before = self._get_memory_usage()
            start_time = time.time()

            try:
                result = operation_func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                success = False
                error = str(e)
                result = None

            end_time = time.time()
            memory_after = self._get_memory_usage()

            execution_times.append(end_time - start_time)
            memory_usages.append(memory_after - memory_before)

        benchmark_result = {
            'operation_name': operation_name,
            'iterations': iterations,
            'avg_execution_time': sum(execution_times) / len(execution_times),
            'min_execution_time': min(execution_times),
            'max_execution_time': max(execution_times),
            'avg_memory_usage': sum(memory_usages) / len(memory_usages),
            'max_memory_usage': max(memory_usages),
            'success_rate': (len([t for t in execution_times if t > 0]) / iterations) * 100,
            'timestamp': datetime.now().isoformat()
        }

        self.benchmark_results[operation_name] = benchmark_result

        # Create benchmark node
        bench_node = self.tracker.create_node(
            "benchmark", f"{operation_name}_benchmark")
        bench_node.add_metadata("benchmark_results", benchmark_result)

        return benchmark_result

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                return process.memory_info().rss / 1024 / 1024
            except Exception:
                pass
        return 0.0

    def compare_operations(self, operation_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Compare multiple operation benchmark results."""
        if len(operation_results) < 2:
            return {"error": "Need at least 2 operations to compare"}

        comparison = {
            'operations_compared': list(operation_results.keys()),
            'fastest_operation': None,
            'most_memory_efficient': None,
            'most_reliable': None,
            'detailed_comparison': {}
        }

        # Find fastest operation
        fastest_op = min(operation_results.items(),
                         key=lambda x: x[1]['avg_execution_time'])
        comparison['fastest_operation'] = {
            'name': fastest_op[0],
            'avg_time': fastest_op[1]['avg_execution_time']
        }

        # Find most memory efficient
        most_efficient = min(operation_results.items(),
                             key=lambda x: x[1]['avg_memory_usage'])
        comparison['most_memory_efficient'] = {
            'name': most_efficient[0],
            'avg_memory': most_efficient[1]['avg_memory_usage']
        }

        # Find most reliable
        most_reliable = max(operation_results.items(),
                            key=lambda x: x[1]['success_rate'])
        comparison['most_reliable'] = {
            'name': most_reliable[0],
            'success_rate': most_reliable[1]['success_rate']
        }

        return comparison


class MemoryManager:
    """Advanced memory management for DataLineagePy operations."""

    def __init__(self, tracker: LineageTracker):
        self.tracker = tracker
        self.memory_thresholds = {
            'warning': 500,  # MB
            'critical': 1000  # MB
        }

    def cleanup_memory(self, force_gc: bool = True) -> Dict[str, Any]:
        """Perform memory cleanup and return cleanup report."""
        before_memory = self._get_memory_usage()

        # Force garbage collection
        if force_gc:
            collected = gc.collect()
        else:
            collected = 0

        after_memory = self._get_memory_usage()
        memory_freed = before_memory - after_memory

        cleanup_report = {
            'memory_before_mb': before_memory,
            'memory_after_mb': after_memory,
            'memory_freed_mb': memory_freed,
            'objects_collected': collected,
            'timestamp': datetime.now().isoformat()
        }

        # Create cleanup node
        cleanup_node = self.tracker.create_node("system", "memory_cleanup")
        cleanup_node.add_metadata("cleanup_report", cleanup_report)

        return cleanup_report

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                return process.memory_info().rss / 1024 / 1024
            except Exception:
                pass
        return 0.0

    def check_memory_health(self) -> Dict[str, Any]:
        """Check overall memory health and return status."""
        current_memory = self._get_memory_usage()

        health_status = {
            'current_memory_mb': current_memory,
            'warning_threshold_mb': self.memory_thresholds['warning'],
            'critical_threshold_mb': self.memory_thresholds['critical'],
            'status': 'healthy',
            'recommendations': []
        }

        if current_memory > self.memory_thresholds['critical']:
            health_status['status'] = 'critical'
            health_status['recommendations'].extend([
                'Memory usage is critical - immediate cleanup recommended',
                'Consider reducing dataset size or using chunking',
                'Review object lifecycle and cleanup unused variables'
            ])
        elif current_memory > self.memory_thresholds['warning']:
            health_status['status'] = 'warning'
            health_status['recommendations'].extend([
                'Memory usage approaching limit',
                'Consider periodic cleanup',
                'Monitor large object creation'
            ])
        else:
            health_status['recommendations'].append('Memory usage is healthy')

        return health_status
