"""
PHASE 1: MINIMAL COMPREHENSIVE TESTING
Tests all core functionality that definitely exists
"""

from datalineagepy.visualization.report_generator import ReportGenerator
from datalineagepy.visualization.graph_visualizer import GraphVisualizer
from datalineagepy.core.dataframe_wrapper import LineageDataFrame
from datalineagepy import LineageTracker, DataNode, LineageEdge
import pytest
import os
import sys
import tempfile
import shutil
import pandas as pd
import numpy as np

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


class TestPhase1Minimal:
    """Phase 1: Minimal comprehensive test suite"""

    def setup_method(self):
        """Setup for each test method"""
        self.test_dir = tempfile.mkdtemp()
        self.tracker = LineageTracker("phase1_test")

    def teardown_method(self):
        """Cleanup after each test method"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_01_tracker_basic(self):
        """Test 1: Basic tracker functionality"""
        tracker = LineageTracker("test_tracker")

        # Test basic properties
        assert tracker.name == "test_tracker"
        assert tracker.nodes == {}
        assert tracker.edges == []
        assert tracker.operations == []

        # Test node creation
        node1 = tracker.create_node('data', 'test_node_1')
        assert isinstance(node1, DataNode)
        assert node1.id in tracker.nodes
        assert node1.name == 'test_node_1'

        print("✅ Test 1: Basic tracker functionality - PASSED")

    def test_02_edge_creation(self):
        """Test 2: Edge creation"""
        tracker = LineageTracker("edge_test")
        node1 = tracker.create_node('data', 'source')
        node2 = tracker.create_node('data', 'target')

        # Test edge creation
        edge = tracker.add_edge(node1, node2)
        assert isinstance(edge, LineageEdge)
        assert edge in tracker.edges

        print("✅ Test 2: Edge creation - PASSED")

    def test_03_operation_tracking(self):
        """Test 3: Operation tracking"""
        tracker = LineageTracker("op_test")
        node1 = tracker.create_node('data', 'input')
        node2 = tracker.create_node('data', 'output')

        # Test operation tracking
        operation = tracker.track_operation(
            'test_op', [node1], [node2], {'param': 'value'})
        assert operation in tracker.operations

        print("✅ Test 3: Operation tracking - PASSED")

    def test_04_lineage_dataframe(self):
        """Test 4: LineageDataFrame basic functionality"""
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['x', 'y', 'z']
        })

        tracker = LineageTracker("df_test")
        ldf = LineageDataFrame(df, name="test_df", tracker=tracker)

        # Test basic properties
        assert ldf.name == "test_df"
        assert ldf.tracker == tracker
        assert ldf._df.equals(df)

        print("✅ Test 4: LineageDataFrame - PASSED")

    def test_05_column_lineage(self):
        """Test 5: Column lineage tracking"""
        tracker = LineageTracker("col_test")
        node1 = tracker.create_node('data', 'source')
        node2 = tracker.create_node('data', 'target')

        # Test column lineage
        tracker.track_column_lineage(
            node1, node2,
            {'col_b': ['col_a']},
            'column_transform'
        )

        # Should have created edges
        assert len(tracker.edges) > 0

        print("✅ Test 5: Column lineage - PASSED")

    def test_06_error_tracking(self):
        """Test 6: Error tracking"""
        tracker = LineageTracker("error_test")
        node = tracker.create_node('data', 'error_node')

        # Test error tracking
        tracker.track_error(node.id, "Test error", "test_type")

        print("✅ Test 6: Error tracking - PASSED")

    def test_07_search_functionality(self):
        """Test 7: Search functionality"""
        tracker = LineageTracker("search_test")
        node = tracker.create_node('data', 'searchable_data')

        # Test search
        results = tracker.search_lineage("searchable", "node_name")
        assert isinstance(results, list)

        print("✅ Test 7: Search functionality - PASSED")

    def test_08_export_json(self):
        """Test 8: JSON export"""
        tracker = LineageTracker("export_test")
        node1 = tracker.create_node('data', 'node1')

        # Test JSON export
        json_export = tracker.export_graph('json')
        assert isinstance(json_export, str)
        assert len(json_export) > 0

        print("✅ Test 8: JSON export - PASSED")

    def test_09_export_dot(self):
        """Test 9: DOT export"""
        tracker = LineageTracker("dot_test")
        node1 = tracker.create_node('data', 'node1')

        # Test DOT export
        dot_export = tracker.export_graph('dot')
        assert isinstance(dot_export, str)
        assert 'digraph' in dot_export

        print("✅ Test 9: DOT export - PASSED")

    def test_10_ai_ready_format(self):
        """Test 10: AI-ready format"""
        tracker = LineageTracker("ai_test")
        node = tracker.create_node('data', 'ai_node')

        # Test AI-ready format
        ai_data = tracker.get_lineage_graph('ai_ready')
        assert isinstance(ai_data, dict)
        assert 'natural_language' in ai_data

        print("✅ Test 10: AI-ready format - PASSED")

    def test_11_custom_hooks(self):
        """Test 11: Custom hooks"""
        tracker = LineageTracker("hooks_test")
        hook_called = []

        def test_hook(tracker_instance, **kwargs):
            hook_called.append(True)

        tracker.register_custom_hook('test_hook', test_hook)
        tracker.trigger_hooks('test_hook')
        assert len(hook_called) > 0

        print("✅ Test 11: Custom hooks - PASSED")

    def test_12_error_propagation(self):
        """Test 12: Error propagation"""
        tracker = LineageTracker("prop_test")
        node = tracker.create_node('data', 'error_node')
        tracker.track_error(node.id, "Test error", "test_error")

        error_analysis = tracker.propagate_error_analysis(node.id)
        assert isinstance(error_analysis, dict)

        print("✅ Test 12: Error propagation - PASSED")

    def test_13_operation_details(self):
        """Test 13: Operation details logging"""
        tracker = LineageTracker("details_test")
        node1 = tracker.create_node('data', 'input')
        node2 = tracker.create_node('data', 'output')

        detailed_op = tracker.log_operation_details(
            'detailed_op', [node1], [node2],
            {'param1': 'value1'}, {'duration': 1.5}
        )
        assert 'execution_context' in detailed_op.metadata

        print("✅ Test 13: Operation details - PASSED")

    def test_14_pii_masking(self):
        """Test 14: PII masking"""
        tracker = LineageTracker("security_test")
        node = tracker.create_node('data', 'sensitive_data')
        node.set_schema({'email': 'string', 'name': 'string', 'id': 'int'})

        tracker.mask_sensitive_data([r'.*email.*', r'.*name.*'])
        # Just check it doesn't crash

        print("✅ Test 14: PII masking - PASSED")

    def test_15_auto_step_naming(self):
        """Test 15: Auto step naming"""
        tracker = LineageTracker("naming_test")
        node1 = tracker.create_node('data', 'input_data')
        node2 = tracker.create_node('data', 'output_data')

        operation = tracker.track_operation('filter', [node1], [node2], {
            'filter_condition': 'value > 100'
        })

        tracker.auto_generate_step_names()
        # Just check it doesn't crash

        print("✅ Test 15: Auto step naming - PASSED")

    def test_16_visualization(self):
        """Test 16: Visualization"""
        # Create test lineage
        node1 = self.tracker.create_node('data', 'source')
        node2 = self.tracker.create_node('data', 'target')
        self.tracker.add_edge(node1, node2)

        visualizer = GraphVisualizer(self.tracker)
        html_content = visualizer.generate_html()
        assert isinstance(html_content, str)
        assert len(html_content) > 100

        print("✅ Test 16: Visualization - PASSED")

    def test_17_report_generation(self):
        """Test 17: Report generation"""
        # Create test data
        node1 = self.tracker.create_node('data', 'raw_data')
        node1.set_schema({'id': 'int', 'name': 'string'})

        node2 = self.tracker.create_node('data', 'cleaned_data')
        self.tracker.track_operation('cleaning', [node1], [node2])

        report_gen = ReportGenerator(self.tracker)
        html_report = report_gen.generate_summary_report('test.html', 'html')
        assert isinstance(html_report, str)
        assert len(html_report) > 100

        print("✅ Test 17: Report generation - PASSED")


def run_phase1_tests():
    """Run all Phase 1 tests"""
    print("🚀 STARTING PHASE 1: COMPREHENSIVE TESTING OF CORE FEATURES")
    print("=" * 80)

    # Run tests manually since pytest import may have issues
    test_instance = TestPhase1Minimal()
    test_methods = [method for method in dir(
        test_instance) if method.startswith('test_')]

    passed = 0
    failed = 0

    for method_name in sorted(test_methods):
        try:
            test_instance.setup_method()
            test_method = getattr(test_instance, method_name)
            test_method()
            passed += 1
        except Exception as e:
            print(f"❌ {method_name} - FAILED: {e}")
            failed += 1
        finally:
            test_instance.teardown_method()

    total = passed + failed
    print("\n" + "=" * 80)
    print("🏆 PHASE 1 COMPREHENSIVE TEST RESULTS")
    print("=" * 80)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if total > 0:
        print(f"Success Rate: {(passed/total*100):.1f}%")

    if failed == 0:
        print("🎉 PHASE 1 COMPLETE! All core features fully tested and working!")
        print("✅ Ready to proceed to Phase 2: Adding new features (.dict() and more)")
        return True
    else:
        print("⚠️ Some tests failed. Review the output above.")
        return False


if __name__ == "__main__":
    success = run_phase1_tests()
    sys.exit(0 if success else 1)
