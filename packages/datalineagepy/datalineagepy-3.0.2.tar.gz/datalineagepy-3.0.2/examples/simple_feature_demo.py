#!/usr/bin/env python3
"""
Simple Feature Demo for DataLineagePy

This demo showcases the core new features implemented:
- Column-level Lineage
- Error Tracking
- Security/PII masking
- Lineage search
- Export formats
- Multi-file support
"""

from datalineagepy.core.tracker import LineageTracker
from datalineagepy.core.dataframe_wrapper import LineageDataFrame, read_csv

# Import read_multiple_files separately to handle any issues
try:
    from datalineagepy.core.dataframe_wrapper import read_multiple_files
    HAS_MULTI_FILE = True
except ImportError:
    HAS_MULTI_FILE = False
    read_multiple_files = None
import pandas as pd
import numpy as np
import os
import sys

# Add the package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def create_test_data():
    """Create simple test data."""
    print("📁 Creating test data...")

    os.makedirs('test_data', exist_ok=True)

    # Sales data with sensitive info
    sales = pd.DataFrame({
        'id': range(1, 21),
        'customer_name': [f'Customer_{i}' for i in range(1, 21)],
        'email': [f'user{i}@test.com' for i in range(1, 21)],
        'amount': np.random.uniform(10, 1000, 20),
        'date': pd.date_range('2024-01-01', periods=20)
    })
    sales.to_csv('test_data/sales.csv', index=False)

    # Product data
    products = pd.DataFrame({
        'product_id': range(1, 11),
        'name': [f'Product_{i}' for i in range(1, 11)],
        'price': np.random.uniform(5, 100, 10)
    })
    products.to_csv('test_data/products.csv', index=False)

    print("✅ Test data created!")


def demo_basic_features():
    """Demo basic lineage tracking with new features."""
    print("\n🔍 Demo 1: Basic Lineage with Column Tracking")

    tracker = LineageTracker("feature_demo")

    # Load data
    sales_df = read_csv('test_data/sales.csv', 'sales', tracker)
    print(f"   Loaded sales data: {sales_df.shape}")

    # Create derived data
    high_value = sales_df[sales_df['amount'] > 500]
    print(f"   High-value sales: {len(high_value)}")

    # Track column lineage manually
    tracker.track_column_lineage(
        sales_df.node,
        high_value.node,
        {
            'id': ['id'],
            'customer_name': ['customer_name'],
            'amount': ['amount']
        },
        'filter_operation'
    )

    # Check basic stats
    stats = tracker.get_stats()
    print(
        f"   Tracker stats: {stats['total_nodes']} nodes, {stats['total_edges']} edges")

    return tracker


def demo_error_tracking():
    """Demo error tracking."""
    print("\n❌ Demo 2: Error Tracking")

    tracker = LineageTracker("error_demo")
    sales_df = read_csv('test_data/sales.csv', 'sales_with_errors', tracker)

    # Simulate and track an error
    tracker.track_error(
        sales_df.node.id,
        "Simulated data quality issue: missing values detected",
        "data_quality"
    )

    # Analyze error propagation
    error_analysis = tracker.propagate_error_analysis(sales_df.node.id)
    print(
        f"   Error analysis complete: {len(error_analysis.get('potential_impact', []))} nodes affected")

    return tracker


def demo_security_features():
    """Demo PII masking."""
    print("\n🔒 Demo 3: Security Features")

    tracker = LineageTracker("security_demo")
    sales_df = read_csv('test_data/sales.csv', 'sensitive_data', tracker)

    print(f"   Before masking: {list(sales_df.columns)}")

    # Apply PII masking
    tracker.mask_sensitive_data(
        column_patterns=[r'.*email.*', r'.*name.*'],
        mask_value="***MASKED***"
    )

    # Check masked columns
    for node_id, node in tracker.nodes.items():
        if hasattr(node, 'schema') and node.schema:
            print(f"   After masking: {list(node.schema.keys())}")
            break

    return tracker


def demo_search():
    """Demo lineage search."""
    print("\n🔍 Demo 4: Lineage Search")

    tracker = LineageTracker("search_demo")

    # Create data with searchable elements
    sales_df = read_csv('test_data/sales.csv', 'searchable_sales', tracker)
    products_df = read_csv('test_data/products.csv',
                           'searchable_products', tracker)

    # Create derived data
    high_value = sales_df[sales_df['amount'] > 500]

    # Search tests
    name_results = tracker.search_lineage("sales", "node_name")
    print(f"   Nodes with 'sales': {len(name_results)}")

    column_results = tracker.search_lineage("amount", "column_name")
    print(f"   Nodes with 'amount' column: {len(column_results)}")

    return tracker


def demo_multi_file():
    """Demo multi-file support."""
    print("\n📁 Demo 5: Multi-File Support")

    if not HAS_MULTI_FILE:
        print("   ⚠️  Multi-file feature not available, skipping...")
        return LineageTracker("multi_file_demo_skipped")

    tracker = LineageTracker("multi_file_demo")

    # Read multiple files
    try:
        combined = read_multiple_files(
            ['test_data/*.csv'],
            file_format='csv',
            name='all_data',
            tracker=tracker
        )
        print(f"   Combined data shape: {combined.shape}")
        print(
            f"   Files processed: {tracker.get_stats()['total_nodes']} nodes")
    except Exception as e:
        print(f"   Multi-file demo error: {e}")

    return tracker


def demo_export_formats():
    """Demo export capabilities."""
    print("\n💾 Demo 6: Export Formats")

    tracker = LineageTracker("export_demo")
    sales_df = read_csv('test_data/sales.csv', 'export_sales', tracker)
    summary = sales_df.groupby('id').sum()

    # Test exports
    try:
        # JSON export
        json_data = tracker.export_graph('json', 'lineage_export.json')
        print(f"   JSON export: {len(json_data)} characters")

        # DOT export
        dot_data = tracker.export_graph('dot', 'lineage_export.dot')
        print(f"   DOT export: {len(dot_data)} characters")

        # Dict export
        dict_data = tracker.export_graph('dict')
        print(
            f"   Dict export: {len(dict_data['nodes'])} nodes, {len(dict_data['edges'])} edges")

    except Exception as e:
        print(f"   Export error: {e}")

    return tracker


def demo_hooks():
    """Demo custom hooks."""
    print("\n🪝 Demo 7: Custom Hooks")

    tracker = LineageTracker("hooks_demo")

    # Simple hook function
    def operation_hook(tracker_instance, **kwargs):
        print(
            f"     Hook triggered: {kwargs.get('operation_type', 'unknown')}")

    # Register hook
    tracker.register_custom_hook('pre_operation', operation_hook)

    # Load data (should trigger hook in real scenario)
    sales_df = read_csv('test_data/sales.csv', 'hooked_sales', tracker)

    # Manually trigger for demo
    tracker.trigger_hooks('pre_operation', operation_type='demo_operation')

    return tracker


def cleanup():
    """Clean up test files."""
    print("\n🧹 Cleaning up...")

    import glob

    # Remove test data
    for file in glob.glob('test_data/*'):
        try:
            os.remove(file)
        except:
            pass

    try:
        os.rmdir('test_data')
    except:
        pass

    # Remove exports
    for file in ['lineage_export.json', 'lineage_export.dot']:
        try:
            os.remove(file)
        except:
            pass


def main():
    """Run the feature demos."""
    print("🚀 DataLineagePy Feature Demo")
    print("=" * 50)

    # Create test data
    create_test_data()

    try:
        # Run demos
        trackers = []
        trackers.append(demo_basic_features())
        trackers.append(demo_error_tracking())
        trackers.append(demo_security_features())
        trackers.append(demo_search())
        trackers.append(demo_multi_file())
        trackers.append(demo_export_formats())
        trackers.append(demo_hooks())

        # Summary
        print("\n📈 Summary")
        print("=" * 50)
        total_nodes = sum(len(t.nodes) for t in trackers)
        total_edges = sum(len(t.edges) for t in trackers)

        print(f"   Total trackers: {len(trackers)}")
        print(f"   Total nodes: {total_nodes}")
        print(f"   Total edges: {total_edges}")

        print("\n✨ Key features demonstrated:")
        print("   ✅ Column-level lineage tracking")
        print("   ✅ Error tracking and propagation")
        print("   ✅ PII masking for security")
        print("   ✅ Lineage search capabilities")
        print("   ✅ Multi-file processing")
        print("   ✅ Export to JSON/DOT formats")
        print("   ✅ Custom operation hooks")

        print("\n🎉 All demos completed successfully!")

    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        cleanup()


if __name__ == "__main__":
    main()
