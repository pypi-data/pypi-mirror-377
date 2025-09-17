"""
Testing framework for DataLineagePy.

This module provides validation and benchmarking capabilities for lineage tracking.
"""

try:
    from .validators import LineageValidator
    from .benchmarks import BenchmarkSuite
except ImportError:
    # Graceful fallback if testing modules aren't available yet
    pass

__all__ = ['LineageValidator', 'BenchmarkSuite']
