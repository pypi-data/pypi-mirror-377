"""
DataLineagePy Phase 2 - Ultimate Features Demo
Showcasing all new advanced features added in Phase 2.
"""

from datalineagepy.visualization.report_generator import ReportGenerator as VizReportGenerator
from datalineagepy.visualization.graph_visualizer import GraphVisualizer
from datalineagepy.core.validation import DataValidator, SchemaValidator
from datalineagepy.core.serialization import DataSerializer, ConfigurationManager, ReportGenerator
from datalineagepy.core.analytics import DataProfiler, StatisticalAnalyzer, TimeSeriesAnalyzer, DataTransformer
from datalineagepy.core.dataframe_wrapper import LineageDataFrame, read_csv
from datalineagepy import LineageTracker
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


def create_sample_datasets():
    """Create comprehensive sample datasets for testing."""
    print("🔧 Creating sample datasets...")

    # Dataset 1: Sales data with various data types
    np.random.seed(42)
    n_records = 1000

    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    sales_data = pd.DataFrame({
        'date': np.random.choice(dates, n_records),
        'product_id': np.random.choice(['P001', 'P002', 'P003', 'P004', 'P005'], n_records),
        'sales_amount': np.random.normal(100, 30, n_records),
        'quantity': np.random.poisson(5, n_records),
        'customer_email': [f'customer{i}@example.com' for i in np.random.randint(1, 200, n_records)],
        'region': np.random.choice(['North', 'South', 'East', 'West'], n_records),
        'discount': np.random.uniform(0, 0.3, n_records)
    })

    # Add some data quality issues for testing
    sales_data.loc[50:60, 'customer_email'] = 'invalid_email'  # Invalid emails
    sales_data.loc[100:110, 'sales_amount'] = np.nan  # Missing values
    sales_data.loc[200:210, 'sales_amount'] = -50  # Negative values (outliers)

    # Dataset 2: Time series data
    time_series_data = pd.DataFrame({
        'timestamp': pd.date_range(start='2023-01-01', end='2023-12-31', freq='H'),
        'temperature': 20 + 10 * np.sin(np.arange(8760) * 2 * np.pi / 24) + np.random.normal(0, 2, 8760),
        'humidity': 50 + 20 * np.cos(np.arange(8760) * 2 * np.pi / (24*7)) + np.random.normal(0, 5, 8760),
        'pressure': 1013 + np.random.normal(0, 10, 8760)
    })

    # Dataset 3: Customer data
    customer_data = pd.DataFrame({
        'customer_id': range(1, 201),
        'age': np.random.randint(18, 80, 200),
        'income': np.random.lognormal(10, 0.5, 200),
        'credit_score': np.random.randint(300, 850, 200),
        'signup_date': pd.date_range(start='2020-01-01', end='2023-12-31', periods=200)
    })

    # Save datasets
    os.makedirs('temp_data', exist_ok=True)
    sales_data.to_csv('temp_data/sales_data.csv', index=False)
    time_series_data.to_csv('temp_data/time_series_data.csv', index=False)
    customer_data.to_csv('temp_data/customer_data.csv', index=False)

    print("✅ Sample datasets created successfully!")
    return sales_data, time_series_data, customer_data


def demo_enhanced_dataframe_methods():
    """Demonstrate new LineageDataFrame methods."""
    print("\n" + "="*60)
    print("🚀 ENHANCED DATAFRAME METHODS DEMO")
    print("="*60)

    tracker = LineageTracker()

    # Load sales data
    sales_ldf = read_csv('temp_data/sales_data.csv',
                         name='sales_data', tracker=tracker)

    print(f"📊 Original data shape: {sales_ldf.shape}")

    # Test .to_dict() method
    print("\n1. Testing .to_dict() method...")
    sales_dict = sales_ldf.head(5).to_dict(orient='records')
    print(f"   ✅ Converted to dict with {len(sales_dict)} records")

    # Test .to_list() method
    print("\n2. Testing .to_list() method...")
    sales_list = sales_ldf.head(3).to_list()
    print(f"   ✅ Converted to list with {len(sales_list)} rows")

    # Test .filter() method
    print("\n3. Testing .filter() method...")
    high_sales = sales_ldf.filter(sales_ldf._df['sales_amount'] > 150)
    print(f"   ✅ Filtered high sales: {high_sales.shape[0]} records")

    # Test .aggregate() method
    print("\n4. Testing .aggregate() method...")
    sales_agg = sales_ldf.aggregate({
        'sales_amount': ['mean', 'sum', 'std'],
        'quantity': ['mean', 'sum']
    })
    print(f"   ✅ Aggregated data shape: {sales_agg.shape}")

    # Test .pivot() method
    print("\n5. Testing .pivot() method...")
    try:
        # Create a smaller subset for pivoting
        pivot_data = sales_ldf.head(100)
        sales_pivot = pivot_data.pivot(
            index='region',
            columns='product_id',
            values='sales_amount'
        )
        print(f"   ✅ Pivoted data shape: {sales_pivot.shape}")
    except Exception as e:
        print(f"   ⚠️  Pivot demo skipped: {str(e)}")

    # Test rolling operations
    print("\n6. Testing rolling operations...")
    sorted_sales = sales_ldf._df.sort_values('date').reset_index(drop=True)
    sorted_ldf = LineageDataFrame(
        sorted_sales, name='sorted_sales', tracker=tracker)

    rolling_avg = sorted_ldf.rolling(window=7).mean()
    print(f"   ✅ Rolling average calculated: {rolling_avg.shape}")

    # Test concatenation
    print("\n7. Testing concatenation...")
    sales_subset1 = sales_ldf.head(100)
    sales_subset2 = sales_ldf.tail(100)
    concatenated = sales_subset1.concatenate([sales_subset2])
    print(f"   ✅ Concatenated data shape: {concatenated.shape}")

    # Test export methods
    print("\n8. Testing export methods...")
    os.makedirs('temp_exports', exist_ok=True)

    # Export to JSON
    json_result = sales_ldf.head(10).to_json('temp_exports/sales_sample.json')
    print(f"   ✅ Exported to JSON")

    # Export to CSV
    csv_result = sales_ldf.head(10).to_csv('temp_exports/sales_sample.csv')
    print(f"   ✅ Exported to CSV")

    print(
        f"\n📈 Lineage tracker now has {len(tracker.nodes)} nodes and {len(tracker.edges)} edges")

    return tracker


def demo_advanced_analytics():
    """Demonstrate advanced analytics capabilities."""
    print("\n" + "="*60)
    print("📊 ADVANCED ANALYTICS DEMO")
    print("="*60)

    tracker = LineageTracker()

    # Load datasets
    sales_ldf = read_csv('temp_data/sales_data.csv',
                         name='sales_data', tracker=tracker)
    customer_ldf = read_csv('temp_data/customer_data.csv',
                            name='customer_data', tracker=tracker)

    # 1. Data Profiling
    print("\n1. 🔍 DATA PROFILING")
    profiler = DataProfiler(tracker)

    sales_profile = profiler.profile_dataset(
        sales_ldf, include_correlations=True)
    print(f"   ✅ Sales data profile completed")
    print(f"   📊 Dataset info: {sales_profile['dataset_info']['shape']} shape")
    print(
        f"   📊 Data quality score: {sales_profile['data_quality']['quality_score']:.1f}/100")
    print(
        f"   📊 Missing data: {sales_profile['missing_data']['total_missing']} cells")

    # 2. Statistical Analysis
    print("\n2. 📈 STATISTICAL ANALYSIS")
    analyzer = StatisticalAnalyzer(tracker)

    # Normality test
    normality_results = analyzer.hypothesis_test(sales_ldf, 'normality',
                                                 columns=['sales_amount', 'quantity'])
    print(
        f"   ✅ Normality test completed for {len(normality_results)} columns")

    # Correlation test
    if 'sales_amount' in sales_ldf.columns and 'quantity' in sales_ldf.columns:
        correlation_results = analyzer.hypothesis_test(sales_ldf, 'correlation',
                                                       column1='sales_amount',
                                                       column2='quantity')
        print(f"   ✅ Correlation test completed")
        if 'pearson' in correlation_results:
            print(
                f"   📊 Pearson correlation: {correlation_results['pearson']['correlation']:.3f}")

    # 3. Time Series Analysis
    print("\n3. ⏰ TIME SERIES ANALYSIS")
    ts_analyzer = TimeSeriesAnalyzer(tracker)
    ts_ldf = read_csv('temp_data/time_series_data.csv',
                      name='time_series', tracker=tracker)

    # Anomaly detection
    anomalies = ts_analyzer.detect_anomalies(
        ts_ldf, 'temperature', method='iqr')
    anomaly_count = anomalies._df['is_anomaly'].sum()
    print(f"   ✅ Anomaly detection completed")
    print(f"   🚨 Found {anomaly_count} temperature anomalies")

    # 4. Data Transformation
    print("\n4. 🔄 DATA TRANSFORMATION")
    transformer = DataTransformer(tracker)

    # Standardization
    standardized = transformer.standardize(
        customer_ldf, columns=['age', 'income'])
    print(f"   ✅ Standardized customer data: {standardized.shape}")

    # Normalization
    normalized = transformer.normalize(
        customer_ldf, columns=['age', 'credit_score'])
    print(f"   ✅ Normalized customer data: {normalized.shape}")

    # Categorical encoding
    encoded = transformer.encode_categorical(
        sales_ldf, columns=['region', 'product_id'])
    print(f"   ✅ Encoded categorical data: {encoded.shape}")

    print(f"\n📈 Analytics tracker now has {len(tracker.nodes)} nodes")

    return tracker


def demo_serialization_and_export():
    """Demonstrate serialization and export capabilities."""
    print("\n" + "="*60)
    print("💾 SERIALIZATION & EXPORT DEMO")
    print("="*60)

    tracker = LineageTracker()
    sales_ldf = read_csv('temp_data/sales_data.csv',
                         name='sales_data', tracker=tracker)

    # 1. Data Serialization
    print("\n1. 📦 DATA SERIALIZATION")
    serializer = DataSerializer(tracker)

    # Multi-format export
    export_paths = serializer.export_to_formats(
        sales_ldf.head(100),
        'temp_exports/sales_multi',
        formats=['csv', 'json', 'excel']
    )
    print(f"   ✅ Multi-format export completed:")
    for fmt, path in export_paths.items():
        if not fmt.endswith('_error'):
            print(f"      📄 {fmt.upper()}: {path}")

    # Lineage graph export
    lineage_path = serializer.export_lineage_graph(
        'temp_exports/lineage_graph.json')
    print(f"   ✅ Lineage graph exported to: {lineage_path}")

    # 2. Configuration Management
    print("\n2. ⚙️ CONFIGURATION MANAGEMENT")
    config_manager = ConfigurationManager()

    # Show current config
    tracking_config = config_manager.get_config('tracking')
    print(f"   ✅ Current tracking config loaded")
    print(f"      🔧 Auto tracking: {tracking_config['auto_tracking_enabled']}")
    print(f"      🔧 Track memory: {tracking_config['track_memory_usage']}")

    # Update preferences
    config_manager.update_user_preferences({
        'auto_tracking': True,
        'performance_monitoring': True,
        'pii_masking': True
    })
    print(f"   ✅ User preferences updated")

    # Save config
    config_manager.save_config_to_file('temp_exports/datalineage_config.json')
    print(f"   ✅ Configuration saved")

    # 3. Report Generation
    print("\n3. 📊 REPORT GENERATION")
    report_gen = ReportGenerator(tracker)

    summary_report = report_gen.generate_summary_report()
    print(f"   ✅ Summary report generated")
    print(
        f"      📊 Total nodes: {summary_report['tracker_statistics']['total_nodes']}")
    print(
        f"      📊 Total operations: {summary_report['tracker_statistics']['total_operations']}")

    # Export report
    report_gen.export_report(
        summary_report, 'temp_exports/lineage_summary.json')
    report_gen.export_report(
        summary_report, 'temp_exports/lineage_summary.txt', format='txt')
    print(f"   ✅ Reports exported in JSON and TXT formats")

    return tracker


def demo_data_validation():
    """Demonstrate comprehensive data validation."""
    print("\n" + "="*60)
    print("✅ DATA VALIDATION DEMO")
    print("="*60)

    tracker = LineageTracker()
    sales_ldf = read_csv('temp_data/sales_data.csv',
                         name='sales_data', tracker=tracker)

    # 1. Basic Data Validation
    print("\n1. 🔍 BASIC DATA VALIDATION")
    validator = DataValidator(tracker)

    validation_results = validator.validate_dataframe(
        sales_ldf,
        rules=['completeness', 'uniqueness',
               'data_types', 'ranges', 'patterns']
    )

    print(
        f"   ✅ Validation completed with score: {validation_results['validation_score']:.1f}/100")
    print(
        f"   📊 Rules passed: {validation_results['validation_summary']['passed']}")
    print(
        f"   ⚠️  Warnings: {validation_results['validation_summary']['warnings']}")
    print(f"   ❌ Errors: {validation_results['validation_summary']['errors']}")

    # Show specific issues
    if 'completeness' in validation_results['rule_results']:
        completeness = validation_results['rule_results']['completeness']
        print(
            f"   📊 Data completeness: {completeness['completeness_percentage']:.1f}%")

    if 'patterns' in validation_results['rule_results']:
        patterns = validation_results['rule_results']['patterns']
        if patterns.get('pattern_issues'):
            print(f"   🔍 Pattern issues found in email column")

    # 2. Custom Validation Rules
    print("\n2. 🛠️ CUSTOM VALIDATION RULES")

    def validate_sales_amount(df):
        """Custom rule: sales amount should be positive."""
        negative_count = (df['sales_amount'] < 0).sum()
        return {
            'status': 'passed' if negative_count == 0 else 'error',
            'negative_sales_count': int(negative_count),
            'message': f'Found {negative_count} negative sales amounts'
        }

    def validate_discount_range(df):
        """Custom rule: discount should be between 0 and 1."""
        invalid_discounts = ((df['discount'] < 0) | (df['discount'] > 1)).sum()
        return {
            'status': 'passed' if invalid_discounts == 0 else 'warning',
            'invalid_discounts': int(invalid_discounts),
            'message': f'Found {invalid_discounts} invalid discounts'
        }

    # Add custom rules
    validator.add_validation_rule('positive_sales', validate_sales_amount)
    validator.add_validation_rule('valid_discount', validate_discount_range)

    custom_validation = validator.validate_dataframe(
        sales_ldf,
        rules=['positive_sales', 'valid_discount']
    )

    print(f"   ✅ Custom validation completed")
    for rule, result in custom_validation['rule_results'].items():
        print(f"      🔧 {rule}: {result['status']} - {result['message']}")

    # 3. Schema Validation
    print("\n3. 📋 SCHEMA VALIDATION")
    schema_validator = SchemaValidator(tracker)

    # Create schema from existing data
    sales_schema = schema_validator.create_schema_from_dataframe(
        sales_ldf, 'sales_schema')
    print(
        f"   ✅ Schema created with {len(sales_schema['required_columns'])} columns")

    # Validate against schema
    schema_validation = schema_validator.validate_against_schema(
        sales_ldf, 'sales_schema')
    print(
        f"   ✅ Schema validation: {'PASSED' if schema_validation['schema_compliance'] else 'FAILED'}")

    if schema_validation['issues']:
        print(
            f"      ⚠️  Found {len(schema_validation['issues'])} schema issues")

    # Validation summary
    validation_summary = validator.get_validation_summary()
    print(f"\n📊 Validation Summary:")
    print(
        f"   Total validations run: {validation_summary['total_validations_run']}")
    print(
        f"   Average score: {validation_summary['average_validation_score']:.1f}")

    return tracker


def demo_comprehensive_workflow():
    """Demonstrate a complete data workflow with all Phase 2 features."""
    print("\n" + "="*60)
    print("🎯 COMPREHENSIVE WORKFLOW DEMO")
    print("="*60)

    tracker = LineageTracker()

    # 1. Load and validate data
    print("\n1. 📥 LOADING & VALIDATION")
    sales_ldf = read_csv('temp_data/sales_data.csv',
                         name='sales_data', tracker=tracker)
    validator = DataValidator(tracker)
    validation_results = validator.validate_dataframe(sales_ldf)
    print(
        f"   ✅ Data loaded and validated (score: {validation_results['validation_score']:.1f})")

    # 2. Data profiling and analysis
    print("\n2. 🔍 PROFILING & ANALYSIS")
    profiler = DataProfiler(tracker)
    profile = profiler.profile_dataset(sales_ldf)
    print(
        f"   ✅ Data profiled (quality: {profile['data_quality']['quality_score']:.1f})")

    # 3. Data cleaning and transformation
    print("\n3. 🧹 CLEANING & TRANSFORMATION")
    # Remove rows with negative sales (data quality issue)
    cleaned_ldf = sales_ldf.filter(sales_ldf._df['sales_amount'] >= 0)
    print(f"   ✅ Cleaned data: {cleaned_ldf.shape[0]} valid records")

    # Transform and aggregate
    transformer = DataTransformer(tracker)
    normalized_ldf = transformer.normalize(
        cleaned_ldf, columns=['sales_amount', 'discount'])

    regional_summary = cleaned_ldf.aggregate({
        'sales_amount': ['sum', 'mean', 'count'],
        'quantity': ['sum', 'mean']
    })
    print(f"   ✅ Data transformed and aggregated")

    # 4. Analysis and insights
    print("\n4. 📊 ANALYSIS & INSIGHTS")
    analyzer = StatisticalAnalyzer(tracker)
    correlation_test = analyzer.hypothesis_test(
        cleaned_ldf, 'correlation',
        column1='sales_amount', column2='quantity'
    )

    if 'pearson' in correlation_test:
        corr_value = correlation_test['pearson']['correlation']
        print(f"   ✅ Sales-Quantity correlation: {corr_value:.3f}")

    # 5. Export results
    print("\n5. 💾 EXPORT & SERIALIZATION")
    serializer = DataSerializer(tracker)

    # Export processed data
    export_paths = serializer.export_to_formats(
        normalized_ldf,
        'temp_exports/processed_sales',
        formats=['csv', 'json']
    )

    # Export lineage and reports
    lineage_path = serializer.export_lineage_graph(
        'temp_exports/workflow_lineage.json')

    report_gen = ReportGenerator(tracker)
    workflow_report = report_gen.generate_summary_report()
    report_gen.export_report(
        workflow_report, 'temp_exports/workflow_report.json')

    print(f"   ✅ Results exported to multiple formats")
    print(f"   📄 Lineage graph: {lineage_path}")

    # 6. Visualization
    print("\n6. 📈 VISUALIZATION")
    try:
        visualizer = GraphVisualizer()
        viz_path = visualizer.create_lineage_graph(
            tracker, 'temp_exports/workflow_lineage.png')
        print(f"   ✅ Lineage visualization created: {viz_path}")
    except Exception as e:
        print(f"   ⚠️  Visualization skipped: {str(e)}")

    # Final summary
    print(f"\n🎉 WORKFLOW COMPLETED!")
    print(f"   📊 Total nodes created: {len(tracker.nodes)}")
    print(f"   🔗 Total edges created: {len(tracker.edges)}")
    print(f"   ⚙️  Total operations: {len(tracker.operations)}")

    return tracker


def main():
    """Run the complete Phase 2 features demonstration."""
    print("🚀 DataLineagePy Phase 2 - Ultimate Features Demo")
    print("=" * 60)
    print("This demo showcases all the advanced features added in Phase 2:")
    print("• Enhanced DataFrame methods (.to_dict, .filter, .aggregate, etc.)")
    print("• Advanced analytics (profiling, statistics, time series)")
    print("• Comprehensive serialization and export")
    print("• Data validation and schema validation")
    print("• Configuration management")
    print("• Comprehensive reporting")
    print("=" * 60)

    try:
        # Create sample data
        create_sample_datasets()

        # Run all demos
        demo_enhanced_dataframe_methods()
        demo_advanced_analytics()
        demo_serialization_and_export()
        demo_data_validation()
        final_tracker = demo_comprehensive_workflow()

        print("\n" + "="*60)
        print("🎉 PHASE 2 DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"✅ All new features demonstrated successfully")
        print(f"📊 Final lineage graph contains:")
        print(f"   • {len(final_tracker.nodes)} nodes")
        print(f"   • {len(final_tracker.edges)} edges")
        print(f"   • {len(final_tracker.operations)} operations")
        print(f"📁 Generated files available in:")
        print(f"   • temp_data/ (sample datasets)")
        print(f"   • temp_exports/ (results and exports)")

        print(f"\n🚀 Ready for Phase 3: Benchmarking and Performance Testing!")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up temporary files...")
        import shutil
        try:
            if os.path.exists('temp_data'):
                shutil.rmtree('temp_data')
            if os.path.exists('temp_exports'):
                shutil.rmtree('temp_exports')
            print(f"✅ Cleanup completed")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {str(e)}")


if __name__ == "__main__":
    main()
