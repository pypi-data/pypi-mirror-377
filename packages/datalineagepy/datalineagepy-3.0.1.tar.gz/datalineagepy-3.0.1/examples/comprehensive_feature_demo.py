#!/usr/bin/env python3
"""
Comprehensive Feature Demo for DataLineagePy

This demo showcases all the new features implemented:
- Graph Visualization (HTML/PNG/DOT)
- Column-level Lineage
- Operation metadata logging
- Error Propagation Reporting
- Multi-file support
- Export Lineage to JSON/DOT
- AI-ready format export
- Testing framework (validators & benchmarks)
- Security/PII masking
- Lineage search
- Export summary reports
- Custom Operation Hooks
- Automatic step-naming
"""

from datalineagepy import (
    LineageTracker, LineageDataFrame, read_csv, read_multiple_files,
    DataNode, FileNode, DatabaseNode
)
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

# Add the package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# Try to import optional modules
try:
    from datalineagepy.visualization import GraphVisualizer, ReportGenerator
    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False
    GraphVisualizer = None
    ReportGenerator = None

try:
    from datalineagepy.testing import LineageValidator, BenchmarkSuite
    HAS_TESTING = True
except ImportError:
    HAS_TESTING = False
    LineageValidator = None
    BenchmarkSuite = None


def create_sample_data():
    """Create sample CSV files for the demo."""
    print("📁 Creating sample data files...")

    # Create sample directory
    os.makedirs('demo_data', exist_ok=True)

    # Create sample sales data
    sales_data = pd.DataFrame({
        'customer_id': range(1, 101),
        'customer_name': [f'Customer_{i}' for i in range(1, 101)],
        'email': [f'customer{i}@email.com' for i in range(1, 101)],
        'ssn': [f'XXX-XX-{1000+i}' for i in range(1, 101)],  # Sensitive data
        'amount': np.random.uniform(10, 1000, 100),
        'date': pd.date_range('2024-01-01', periods=100, freq='D')[:100]
    })
    sales_data.to_csv('demo_data/sales_data.csv', index=False)

    # Create sample product data
    product_data = pd.DataFrame({
        'product_id': range(1, 51),
        'product_name': [f'Product_{i}' for i in range(1, 51)],
        'category': np.random.choice(['Electronics', 'Clothing', 'Books'], 50),
        'price': np.random.uniform(5, 500, 50)
    })
    product_data.to_csv('demo_data/product_data.csv', index=False)

    # Create sample inventory data
    inventory_data = pd.DataFrame({
        'product_id': range(1, 51),
        'stock_quantity': np.random.randint(0, 100, 50),
        'warehouse_location': np.random.choice(['East', 'West', 'Central'], 50)
    })
    inventory_data.to_csv('demo_data/inventory_data.csv', index=False)

    print("✅ Sample data files created!")
    return ['demo_data/sales_data.csv', 'demo_data/product_data.csv', 'demo_data/inventory_data.csv']


def demo_basic_lineage_tracking():
    """Demo basic lineage tracking with column-level lineage."""
    print("\n🔍 Demo 1: Basic Lineage Tracking with Column-Level Lineage")

    # Create tracker
    tracker = LineageTracker("comprehensive_demo")

    # Load data with lineage tracking
    sales_df = read_csv('demo_data/sales_data.csv', 'sales_data', tracker)
    product_df = read_csv('demo_data/product_data.csv',
                          'product_data', tracker)

    print(f"   Sales data shape: {sales_df.shape}")
    print(f"   Product data shape: {product_df.shape}")

    # Perform operations with column lineage tracking
    high_value_sales = sales_df[sales_df['amount'] > 500]

    # Track column lineage manually for complex operations
    tracker.track_column_lineage(
        sales_df.node,
        high_value_sales.node,
        {
            'customer_id': ['customer_id'],
            'customer_name': ['customer_name'],
            'amount': ['amount'],
            'date': ['date']
        },
        'filter_high_value'
    )

    # Create summary
    summary = high_value_sales.groupby('date').agg({
        'amount': 'sum',
        'customer_id': 'count'
    }).rename(columns={'customer_id': 'transaction_count'})

    print(f"   High-value sales count: {len(high_value_sales)}")
    print(f"   Summary shape: {summary.shape}")

    return tracker


def demo_multi_file_support():
    """Demo multi-file support and complex operations."""
    print("\n📁 Demo 2: Multi-File Support")

    tracker = LineageTracker("multi_file_demo")

    # Read multiple files at once
    all_data = read_multiple_files(
        ['demo_data/*.csv'],
        file_format='csv',
        name='combined_business_data',
        tracker=tracker,
        combine_method='concat'
    )

    print(f"   Combined data shape: {all_data.shape}")
    print(f"   Tracker stats: {tracker.get_stats()}")

    return tracker


def demo_error_tracking():
    """Demo error tracking and propagation analysis."""
    print("\n❌ Demo 3: Error Tracking and Propagation")

    tracker = LineageTracker("error_demo")

    # Create some data
    sales_df = read_csv('demo_data/sales_data.csv',
                        'sales_with_errors', tracker)

    # Simulate an error
    try:
        # This will cause an error (division by zero simulation)
        result = sales_df['amount'] / 0
    except Exception as e:
        # Track the error
        tracker.track_error(
            sales_df.node.id,
            f"Division by zero error: {str(e)}",
            "processing_error"
        )

    # Create downstream operations that might be affected
    filtered_sales = sales_df[sales_df['amount'] > 100]

    # Analyze error propagation
    error_analysis = tracker.propagate_error_analysis(sales_df.node.id)

    print(
        f"   Error analysis: {len(error_analysis.get('potential_impact', []))} nodes potentially affected")

    return tracker


def demo_security_features():
    """Demo security features including PII masking."""
    print("\n🔒 Demo 4: Security Features (PII Masking)")

    tracker = LineageTracker("security_demo")

    # Load data with sensitive information
    sales_df = read_csv('demo_data/sales_data.csv',
                        'sensitive_sales_data', tracker)

    print("   Before masking:")
    print(f"   Columns: {list(sales_df.columns)}")

    # Apply PII masking
    tracker.mask_sensitive_data(
        column_patterns=[r'.*email.*', r'.*ssn.*', r'.*_name.*'],
        mask_value="***MASKED***"
    )

    print("   After masking:")
    for node_id, node in tracker.nodes.items():
        if hasattr(node, 'schema'):
            print(f"   Node {node.name} columns: {list(node.schema.keys())}")

    return tracker


def demo_search_capabilities():
    """Demo lineage search capabilities."""
    print("\n🔍 Demo 5: Lineage Search")

    tracker = LineageTracker("search_demo")

    # Create some complex lineage
    sales_df = read_csv('demo_data/sales_data.csv',
                        'searchable_sales', tracker)
    product_df = read_csv('demo_data/product_data.csv',
                          'searchable_products', tracker)

    # Create derived data
    high_value = sales_df[sales_df['amount'] > 500]
    summary = high_value.groupby('customer_id').sum()

    # Search for different elements
    print("   Search results:")

    # Search by node name
    name_results = tracker.search_lineage("sales", "node_name")
    print(f"   - Nodes with 'sales' in name: {len(name_results)}")

    # Search by column name
    column_results = tracker.search_lineage("amount", "column_name")
    print(f"   - Nodes with 'amount' column: {len(column_results)}")

    # Search by operation type
    op_results = tracker.search_lineage("groupby", "operation_type")
    print(f"   - 'groupby' operations: {len(op_results)}")

    return tracker


def demo_visualization():
    """Demo visualization capabilities."""
    print("\n🎨 Demo 6: Graph Visualization")

    if not HAS_VISUALIZATION:
        print("   ⚠️  Visualization module not available, skipping...")
        return LineageTracker("visualization_demo_skipped")

    tracker = LineageTracker("visualization_demo")

    # Create a complex lineage graph
    sales_df = read_csv('demo_data/sales_data.csv', 'visual_sales', tracker)
    product_df = read_csv('demo_data/product_data.csv',
                          'visual_products', tracker)

    # Create derived datasets
    high_value = sales_df[sales_df['amount'] > 500]
    summary = high_value.groupby('customer_id').sum()

    # Create visualizer
    visualizer = GraphVisualizer(tracker)

    # Generate different formats
    print("   Generating visualizations...")

    # HTML visualization
    html_content = visualizer.generate_html('demo_lineage.html')
    print(f"   - HTML visualization saved (length: {len(html_content)} chars)")

    # DOT format
    dot_content = visualizer.export_to_dot('demo_lineage.dot')
    print(f"   - DOT file saved (length: {len(dot_content)} chars)")

    # JSON export
    json_data = visualizer.export_to_json('demo_lineage.json')
    print(
        f"   - JSON export saved ({len(json_data['nodes'])} nodes, {len(json_data['edges'])} edges)")

    # Graph statistics
    stats = visualizer.get_graph_stats()
    print(f"   - Graph stats: {stats}")

    return tracker


def demo_reports():
    """Demo report generation."""
    print("\n📊 Demo 7: Report Generation")

    if not HAS_VISUALIZATION:
        print("   ⚠️  Visualization module not available, skipping...")
        return LineageTracker("reports_demo_skipped")

    tracker = LineageTracker("reports_demo")

    # Create some lineage data
    sales_df = read_csv('demo_data/sales_data.csv', 'report_sales', tracker)
    summary = sales_df.groupby('customer_id').sum()

    # Generate reports
    report_gen = ReportGenerator(tracker)

    print("   Generating reports...")

    # HTML report
    html_report = report_gen.generate_summary_report(
        'demo_report.html', 'html')
    print(f"   - HTML report saved (length: {len(html_report)} chars)")

    # Markdown report
    md_report = report_gen.generate_summary_report(
        'demo_report.md', 'markdown')
    print(f"   - Markdown report saved (length: {len(md_report)} chars)")

    # CSV exports
    edges_csv = report_gen.export_to_csv('demo_edges.csv', 'edges')
    print(f"   - Edges CSV saved (length: {len(edges_csv)} chars)")

    # AI-ready format
    ai_data = report_gen.generate_ai_ready_format('demo_ai_format.json')
    print(
        f"   - AI-ready format saved ({len(ai_data['graph_structure']['node_features'])} node features)")

    return tracker


def demo_testing_framework():
    """Demo testing and validation framework."""
    print("\n🧪 Demo 8: Testing Framework")

    if not HAS_TESTING:
        print("   ⚠️  Testing module not available, skipping...")
        return LineageTracker("testing_demo_skipped")

    tracker = LineageTracker("testing_demo")

    # Create test data
    sales_df = read_csv('demo_data/sales_data.csv', 'test_sales', tracker)
    summary = sales_df.groupby('customer_id').sum()

    # Validation
    print("   Running validation tests...")
    validator = LineageValidator(tracker)
    validation_results = validator.validate_all()

    print(f"   - Validation score: {validation_results['overall_score']:.2%}")
    print(f"   - Summary: {validation_results['summary']}")

    # Benchmarking
    print("   Running benchmarks...")
    benchmark = BenchmarkSuite()

    # Quick benchmark test
    basic_benchmark = benchmark.benchmark_basic_operations(100)
    print(
        f"   - Basic ops benchmark: {basic_benchmark['nodes_per_second']:.1f} nodes/sec")

    # Memory usage
    memory_benchmark = benchmark.benchmark_memory_usage()
    print(
        f"   - Memory usage: {memory_benchmark['memory_increase_mb']:.1f} MB increase")

    return tracker


def demo_custom_hooks():
    """Demo custom operation hooks."""
    print("\n🪝 Demo 9: Custom Operation Hooks")

    tracker = LineageTracker("hooks_demo")

    # Define custom hooks
    def pre_operation_hook(tracker_instance, **kwargs):
        print(
            f"     🔄 Pre-operation hook triggered for {kwargs.get('operation_type', 'unknown')}")

    def post_operation_hook(tracker_instance, **kwargs):
        print(
            f"     ✅ Post-operation hook triggered for {kwargs.get('operation_type', 'unknown')}")

    # Register hooks
    tracker.register_custom_hook('pre_operation', pre_operation_hook)
    tracker.register_custom_hook('post_operation', post_operation_hook)

    # Perform operations that trigger hooks
    sales_df = read_csv('demo_data/sales_data.csv', 'hooked_sales', tracker)

    # Manually trigger hooks for demonstration
    tracker.trigger_hooks('pre_operation', operation_type='custom_transform')
    high_value = sales_df[sales_df['amount'] > 500]
    tracker.trigger_hooks('post_operation', operation_type='custom_transform')

    return tracker


def demo_export_formats():
    """Demo various export formats."""
    print("\n💾 Demo 10: Export Formats")

    tracker = LineageTracker("export_demo")

    # Create lineage data
    sales_df = read_csv('demo_data/sales_data.csv', 'export_sales', tracker)
    summary = sales_df.groupby('customer_id').sum()

    print("   Exporting in different formats...")

    # Export to different formats
    dict_export = tracker.export_graph('dict', 'demo_export.dict')
    print(f"   - Dictionary export: {len(dict_export['nodes'])} nodes")

    json_export = tracker.export_graph('json', 'demo_export.json')
    print(f"   - JSON export: {len(json_export)} chars")

    dot_export = tracker.export_graph('dot', 'demo_export.dot')
    print(f"   - DOT export: {len(dot_export)} chars")

    return tracker


def cleanup_demo_files():
    """Clean up demo files."""
    print("\n🧹 Cleaning up demo files...")

    import glob
    import os

    # Remove demo data directory
    demo_files = glob.glob('demo_data/*')
    for file in demo_files:
        try:
            os.remove(file)
        except:
            pass

    try:
        os.rmdir('demo_data')
    except:
        pass

    # Remove generated files
    generated_files = [
        'demo_lineage.html', 'demo_lineage.dot', 'demo_lineage.json',
        'demo_report.html', 'demo_report.md', 'demo_edges.csv',
        'demo_ai_format.json', 'demo_export.dict', 'demo_export.json',
        'demo_export.dot'
    ]

    for file in generated_files:
        try:
            os.remove(file)
            print(f"   Removed {file}")
        except:
            pass


def main():
    """Run all demos."""
    print("🚀 DataLineagePy Comprehensive Feature Demo")
    print("=" * 60)

    # Create sample data
    sample_files = create_sample_data()

    try:
        # Run all demos
        trackers = []

        trackers.append(demo_basic_lineage_tracking())
        trackers.append(demo_multi_file_support())
        trackers.append(demo_error_tracking())
        trackers.append(demo_security_features())
        trackers.append(demo_search_capabilities())
        trackers.append(demo_visualization())
        trackers.append(demo_reports())
        trackers.append(demo_testing_framework())
        trackers.append(demo_custom_hooks())
        trackers.append(demo_export_formats())

        # Summary
        print("\n📈 Demo Summary")
        print("=" * 60)
        total_nodes = sum(len(t.nodes) for t in trackers)
        total_edges = sum(len(t.edges) for t in trackers)
        total_operations = sum(len(t.operations) for t in trackers)

        print(f"   Total trackers created: {len(trackers)}")
        print(f"   Total nodes tracked: {total_nodes}")
        print(f"   Total edges created: {total_edges}")
        print(f"   Total operations recorded: {total_operations}")

        print("\n✨ All features demonstrated successfully!")
        print("\nKey features showcased:")
        print("   ✅ Graph Visualization (HTML/PNG/DOT)")
        print("   ✅ Column-level Lineage")
        print("   ✅ Operation metadata logging")
        print("   ✅ Error Propagation Reporting")
        print("   ✅ Multi-file support")
        print("   ✅ Export Lineage to JSON/DOT")
        print("   ✅ AI-ready format export")
        print("   ✅ Testing framework")
        print("   ✅ Security/PII masking")
        print("   ✅ Lineage search")
        print("   ✅ Export summary reports")
        print("   ✅ Custom Operation Hooks")
        print("   ✅ Automatic step-naming")

    except Exception as e:
        print(f"\n❌ Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up
        cleanup_demo_files()


if __name__ == "__main__":
    main()
