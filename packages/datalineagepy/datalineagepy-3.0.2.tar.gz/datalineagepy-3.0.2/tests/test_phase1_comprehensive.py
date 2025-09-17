"""
PHASE 1: COMPREHENSIVE TESTING OF ALL EXISTING FEATURES
Tests every single feature, module, and component in DataLineagePy
"""

from datalineagepy.testing.benchmarks import BenchmarkSuite
from datalineagepy.testing.validators import LineageValidator
from datalineagepy.visualization.report_generator import ReportGenerator
from datalineagepy.visualization.graph_visualizer import GraphVisualizer
from datalineagepy.utils.file_utils import read_multiple_files as utils_read_multiple_files
from datalineagepy.core.dataframe_wrapper import LineageDataFrame, read_multiple_files
from datalineagepy.core.operations import Operation
from datalineagepy.core.edges import LineageEdge as CoreEdge
from datalineagepy.core.nodes import DataNode as CoreNode
from datalineagepy.core.tracker import LineageTracker as CoreTracker
from datalineagepy import LineageTracker, DataNode, LineageEdge
import pytest
import os
import sys
import tempfile
import shutil
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


class TestPhase1Comprehensive:
    """Phase 1: Comprehensive test suite for all existing DataLineagePy features"""

    def setup_method(self):
        """Setup for each test method"""
        self.test_dir = tempfile.mkdtemp()
        self.tracker = LineageTracker("phase1_test")

    def teardown_method(self):
        """Cleanup after each test method"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    # ============================================================================
    # CORE FUNCTIONALITY TESTS
    # ============================================================================

    def test_1_lineage_tracker_core(self):
        """Test 1: LineageTracker core functionality"""
        print("Testing LineageTracker core functionality...")

        tracker = LineageTracker("test_tracker")

        # Test basic properties
        assert tracker.name == "test_tracker"
        assert tracker.nodes == {}
        assert tracker.edges == []
        assert tracker.operations == []

        # Test node creation
        node1 = tracker.create_node('data', 'test_node_1')
        assert isinstance(node1, LineageNode)
        assert node1.id in tracker.nodes

        # Test node retrieval
        retrieved = tracker.get_node(node1.id)
        assert retrieved == node1

        # Test edge creation
        node2 = tracker.create_node('data', 'test_node_2')
        edge = tracker.add_edge(node1, node2, 'transform')
        assert isinstance(edge, LineageEdge)
        assert edge in tracker.edges

        print("✅ LineageTracker core functionality: PASSED")

    def test_2_lineage_node_functionality(self):
        """Test 2: LineageNode functionality"""
        print("Testing LineageNode functionality...")

        node = LineageNode('test_id', 'data', 'test_node')

        # Test basic properties
        assert node.id == 'test_id'
        assert node.node_type == 'data'
        assert node.name == 'test_node'
        assert node.metadata == {}
        assert node.schema is None
        assert node.errors == []

        # Test metadata operations
        node.add_metadata('key1', 'value1')
        assert node.metadata['key1'] == 'value1'

        # Test schema operations
        schema = {'col1': 'int', 'col2': 'string'}
        node.set_schema(schema)
        assert node.schema == schema

        # Test error tracking
        node.add_error('test_error', 'test_type')
        assert len(node.errors) == 1

        print("✅ LineageNode functionality: PASSED")

    def test_3_lineage_edge_functionality(self):
        """Test 3: LineageEdge functionality"""
        print("Testing LineageEdge functionality...")

        node1 = LineageNode('node1', 'data', 'source')
        node2 = LineageNode('node2', 'data', 'target')
        edge = LineageEdge('edge1', node1, node2, 'transform')

        # Test basic properties
        assert edge.id == 'edge1'
        assert edge.source == node1
        assert edge.target == node2
        assert edge.edge_type == 'transform'

        # Test metadata operations
        edge.add_metadata('operation', 'filter')
        assert edge.metadata['operation'] == 'filter'

        print("✅ LineageEdge functionality: PASSED")

    def test_4_operation_functionality(self):
        """Test 4: Operation functionality"""
        print("Testing Operation functionality...")

        node1 = LineageNode('node1', 'data', 'input')
        node2 = LineageNode('node2', 'data', 'output')
        operation = Operation('op1', 'transform', [node1], [node2])

        # Test basic properties
        assert operation.id == 'op1'
        assert operation.operation_type == 'transform'
        assert operation.inputs == [node1]
        assert operation.outputs == [node2]

        print("✅ Operation functionality: PASSED")

    def test_5_lineage_dataframe_basic(self):
        """Test 5: LineageDataFrame basic functionality"""
        print("Testing LineageDataFrame basic functionality...")

        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e'],
            'C': [1.1, 2.2, 3.3, 4.4, 5.5]
        })

        tracker = LineageTracker("dataframe_test")
        wrapper = LineageDataFrame(df, name="test_data", tracker=tracker)

        # Test basic properties
        assert wrapper.name == "test_data"
        assert wrapper.tracker == tracker
        assert wrapper._df.equals(df)
        assert wrapper.node is not None

        # Test shape and columns
        assert wrapper.shape == df.shape
        assert list(wrapper.columns) == list(df.columns)
        assert len(wrapper) == len(df)

        print("✅ LineageDataFrame basic functionality: PASSED")

    def test_6_advanced_tracker_features(self):
        """Test 6: Advanced tracker features"""
        print("Testing advanced tracker features...")

        tracker = LineageTracker("advanced_test")
        node1 = tracker.create_node('data', 'source_node')
        node2 = tracker.create_node('data', 'target_node')

        # Test operation tracking
        operation = tracker.track_operation(
            'test_op', [node1], [node2], {'param': 'value'})
        assert isinstance(operation, Operation)
        assert operation in tracker.operations

        # Test column lineage
        tracker.track_column_lineage(
            node1, node2,
            {'col_b': ['col_a']},
            'column_transform'
        )

        # Test error tracking
        tracker.track_error(node1.id, "Test error", "test_type")
        assert len(tracker.get_node(node1.id).errors) > 0

        # Test search functionality
        results = tracker.search_lineage("source", "node_name")
        assert len(results) >= 1

        print("✅ Advanced tracker features: PASSED")

    def test_7_export_functionality(self):
        """Test 7: Export functionality"""
        print("Testing export functionality...")

        tracker = LineageTracker("export_test")
        node1 = tracker.create_node('data', 'export_node1')
        node2 = tracker.create_node('data', 'export_node2')
        tracker.add_edge(node1, node2, 'transform')

        # Test JSON export
        json_export = tracker.export_graph('json')
        assert isinstance(json_export, str)
        assert len(json_export) > 0

        # Test DOT export
        dot_export = tracker.export_graph('dot')
        assert isinstance(dot_export, str)
        assert 'digraph' in dot_export

        # Test AI-ready format
        ai_data = tracker.get_lineage_graph('ai_ready')
        assert 'natural_language' in ai_data
        assert 'structured_examples' in ai_data
        assert 'training_data' in ai_data

        print("✅ Export functionality: PASSED")

    def test_8_custom_hooks(self):
        """Test 8: Custom hooks functionality"""
        print("Testing custom hooks functionality...")

        tracker = LineageTracker("hooks_test")
        hook_called = []

        def test_hook(tracker_instance, **kwargs):
            hook_called.append(True)

        tracker.register_custom_hook('test_hook', test_hook)
        tracker.trigger_hooks('test_hook')
        assert len(hook_called) > 0

        print("✅ Custom hooks functionality: PASSED")

    def test_9_error_propagation(self):
        """Test 9: Error propagation"""
        print("Testing error propagation...")

        tracker = LineageTracker("error_test")
        node = tracker.create_node('data', 'error_node')
        tracker.track_error(node.id, "Test error", "test_error")

        error_analysis = tracker.propagate_error_analysis(node.id)
        assert 'source_errors' in error_analysis

        print("✅ Error propagation: PASSED")

    def test_10_operation_details_logging(self):
        """Test 10: Operation details logging"""
        print("Testing operation details logging...")

        tracker = LineageTracker("details_test")
        node1 = tracker.create_node('data', 'input')
        node2 = tracker.create_node('data', 'output')

        detailed_op = tracker.log_operation_details(
            'detailed_op', [node1], [node2],
            {'param1': 'value1'}, {'duration': 1.5}
        )
        assert 'execution_context' in detailed_op.metadata

        print("✅ Operation details logging: PASSED")

    def test_11_pii_masking(self):
        """Test 11: PII masking"""
        print("Testing PII masking...")

        tracker = LineageTracker("security_test")
        node = tracker.create_node('data', 'sensitive_data')
        node.set_schema({'email': 'string', 'name': 'string', 'id': 'int'})

        tracker.mask_sensitive_data([r'.*email.*', r'.*name.*'])
        assert '***MASKED***' in node.schema

        print("✅ PII masking: PASSED")

    def test_12_auto_step_naming(self):
        """Test 12: Auto step naming"""
        print("Testing auto step naming...")

        tracker = LineageTracker("naming_test")
        node1 = tracker.create_node('data', 'input_data')
        node2 = tracker.create_node('data', 'output_data')

        operation = tracker.track_operation('filter', [node1], [node2], {
            'filter_condition': 'value > 100'
        })

        tracker.auto_generate_step_names()
        has_generated_name = 'auto_named' in operation.metadata and operation.metadata[
            'auto_named']
        assert has_generated_name

        print("✅ Auto step naming: PASSED")

    # ============================================================================
    # FILE OPERATIONS TESTS
    # ============================================================================

    def test_13_file_utils_basic(self):
        """Test 13: File utils basic functionality"""
        print("Testing file utils basic functionality...")

        # Create test files
        test_files_dir = os.path.join(self.test_dir, 'test_files')
        os.makedirs(test_files_dir)

        # Create CSV files
        for i in range(2):
            df = pd.DataFrame({
                'id': range(i*5, (i+1)*5),
                'value': np.random.randn(5),
                'category': [f'cat_{i}'] * 5
            })
            df.to_csv(os.path.join(test_files_dir,
                      f'file_{i}.csv'), index=False)

        # Test reading multiple CSV files
        csv_pattern = os.path.join(test_files_dir, '*.csv')
        combined_csv = utils_read_multiple_files(
            [csv_pattern], 'csv', self.tracker)
        assert isinstance(combined_csv, LineageDataFrame)
        assert combined_csv._df.shape[0] == 10  # 2 files * 5 rows each

        # Verify lineage was tracked
        assert len(self.tracker.nodes) > 0
        assert len(self.tracker.operations) > 0

        print("✅ File utils basic functionality: PASSED")

    def test_14_multifile_operations(self):
        """Test 14: Multi-file operations from core module"""
        print("Testing multi-file operations from core module...")

        # Create test files
        test_files_dir = os.path.join(self.test_dir, 'multifile_test')
        os.makedirs(test_files_dir)

        for i in range(2):
            df = pd.DataFrame({
                'id': range(i*3, (i+1)*3),
                'data': [f'data_{j}' for j in range(i*3, (i+1)*3)]
            })
            df.to_csv(os.path.join(test_files_dir,
                      f'test_{i}.csv'), index=False)

        # Test using core module function
        file_patterns = [os.path.join(test_files_dir, '*.csv')]
        combined = read_multiple_files(
            file_patterns,
            file_format='csv',
            name='combined_test',
            tracker=self.tracker
        )

        assert isinstance(combined, LineageDataFrame)
        assert combined._df.shape[0] == 6  # 2 files * 3 rows each

        print("✅ Multi-file operations: PASSED")

    # ============================================================================
    # VISUALIZATION TESTS
    # ============================================================================

    def test_15_graph_visualization(self):
        """Test 15: Graph visualization"""
        print("Testing graph visualization...")

        # Create some test data with lineage
        node1 = self.tracker.create_node('data', 'source_data')
        node2 = self.tracker.create_node('data', 'processed_data')
        node3 = self.tracker.create_node('data', 'final_data')

        self.tracker.add_edge(node1, node2, 'transform')
        self.tracker.add_edge(node2, node3, 'aggregate')

        visualizer = GraphVisualizer(self.tracker)

        # Test HTML generation
        html_content = visualizer.generate_html()
        assert isinstance(html_content, str)
        assert len(html_content) > 100
        assert 'source_data' in html_content

        print("✅ Graph visualization: PASSED")

    def test_16_report_generation(self):
        """Test 16: Report generation"""
        print("Testing report generation...")

        # Create test data with rich lineage
        node1 = self.tracker.create_node('data', 'raw_data')
        node1.set_schema({'id': 'int', 'name': 'string', 'value': 'float'})
        node1.add_metadata('source', 'database')

        node2 = self.tracker.create_node('data', 'cleaned_data')
        node2.set_schema({'id': 'int', 'name': 'string', 'value': 'float'})

        operation = self.tracker.track_operation(
            'data_cleaning', [node1], [node2],
            {'remove_nulls': True, 'validate_types': True}
        )

        report_gen = ReportGenerator(self.tracker)

        # Test HTML report generation
        html_report = report_gen.generate_summary_report(
            'test_report.html', 'html')
        assert isinstance(html_report, str)
        assert len(html_report) > 100

        print("✅ Report generation: PASSED")

    # ============================================================================
    # TESTING MODULE TESTS
    # ============================================================================

    def test_17_lineage_validation(self):
        """Test 17: Lineage validation"""
        print("Testing lineage validation...")

        # Create test lineage with some issues
        node1 = self.tracker.create_node('data', 'source')
        node2 = self.tracker.create_node('data', 'target')
        self.tracker.add_edge(node1, node2, 'transform')

        # Create orphaned node
        orphan = self.tracker.create_node('data', 'orphan')

        validator = LineageValidator(self.tracker)

        # Test comprehensive validation
        validation_result = validator.validate_lineage()
        assert isinstance(validation_result, dict)
        assert 'is_valid' in validation_result
        assert 'issues' in validation_result

        # Test specific validations
        orphans = validator.find_orphaned_nodes()
        assert len(orphans) >= 1

        print("✅ Lineage validation: PASSED")

    def test_18_benchmarking(self):
        """Test 18: Benchmarking functionality"""
        print("Testing benchmarking functionality...")

        benchmark = BenchmarkSuite()

        def test_function():
            tracker = LineageTracker("perf_test")
            for i in range(10):
                tracker.create_node('data', f'node_{i}')
            return tracker

        # Test performance measurement
        results = benchmark.measure_performance(test_function, iterations=2)
        assert isinstance(results, dict)
        assert 'avg_time' in results
        assert results['avg_time'] > 0

        print("✅ Benchmarking functionality: PASSED")

    # ============================================================================
    # INTEGRATION TESTS
    # ============================================================================

    def test_19_integration_modules_exist(self):
        """Test 19: Integration modules exist"""
        print("Testing integration modules exist...")

        # Test that integration modules exist
        airflow_exists = os.path.exists(
            'datalineagepy/integrations/airflow_integration.py')
        spark_exists = os.path.exists(
            'datalineagepy/integrations/spark_integration.py')

        assert airflow_exists, "Airflow integration module should exist"
        assert spark_exists, "Spark integration module should exist"

        print("✅ Integration modules exist: PASSED")

    # ============================================================================
    # ERROR HANDLING AND EDGE CASES
    # ============================================================================

    def test_20_error_handling(self):
        """Test 20: Error handling and edge cases"""
        print("Testing error handling and edge cases...")

        tracker = LineageTracker("error_test")

        # Test non-existent node retrieval
        non_existent = tracker.get_node('non_existent_id')
        assert non_existent is None

        # Test invalid export format
        try:
            tracker.export_graph('invalid_format')
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected

        # Test search with empty query
        results = tracker.search_lineage('', 'node_name')
        assert isinstance(results, list)

        print("✅ Error handling: PASSED")


def run_phase1_comprehensive_test():
    """Run Phase 1 comprehensive test suite"""
    print("🚀 STARTING PHASE 1: COMPREHENSIVE TESTING")
    print("=" * 80)

    # Run pytest with detailed output
    import subprocess
    import sys

    result = subprocess.run([
        sys.executable, '-m', 'pytest',
        'tests/test_phase1_comprehensive.py',
        '-v', '--tb=short', '--no-header', '-s'
    ], capture_output=True, text=True)

    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)

    # Generate summary
    total_tests = result.stdout.count('PASSED') + result.stdout.count('FAILED')
    passed_tests = result.stdout.count('PASSED')

    print("\n" + "=" * 80)
    print("🏆 PHASE 1 COMPREHENSIVE TEST RESULTS")
    print("=" * 80)
    print(f"Total Tests Run: {total_tests}")
    print(f"Tests Passed: {passed_tests}")
    print(f"Tests Failed: {total_tests - passed_tests}")
    print(
        f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests found")

    if result.returncode == 0:
        print("🎉 PHASE 1 COMPLETE! All existing features are fully functional!")
        print("Ready to proceed to Phase 2: Adding new features")
    else:
        print("⚠️ Some tests failed. Review the output above.")

    return result.returncode == 0


if __name__ == "__main__":
    success = run_phase1_comprehensive_test()
    sys.exit(0 if success else 1)
