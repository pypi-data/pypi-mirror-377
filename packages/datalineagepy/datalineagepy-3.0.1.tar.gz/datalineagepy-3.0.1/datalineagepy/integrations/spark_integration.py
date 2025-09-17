"""
Apache Spark integration for DataLineagePy.

This module provides integration with Apache Spark to automatically track
data lineage in Spark applications and transformations.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    from pyspark.sql import SparkSession, DataFrame as SparkDataFrame
    from pyspark.sql.functions import col, lit
    from pyspark import SparkContext, SparkConf
    SPARK_AVAILABLE = True
except ImportError:
    SparkSession = object
    SparkDataFrame = object
    SparkContext = object
    SparkConf = object
    SPARK_AVAILABLE = False

from ..core.tracker import LineageTracker, default_tracker
from ..core.nodes import DataNode


class SparkLineageExtension:
    """
    Spark extension for automatic lineage tracking.

    This class provides methods to track lineage in Spark applications
    by intercepting DataFrame operations and capturing their metadata.
    """

    def __init__(self,
                 spark_session: Optional[SparkSession] = None,
                 lineage_tracker: Optional[LineageTracker] = None,
                 enable_auto_tracking: bool = True):
        """
        Initialize the Spark lineage extension.

        Args:
            spark_session: Spark session to use
            lineage_tracker: LineageTracker instance
            enable_auto_tracking: Whether to automatically track operations
        """
        if not SPARK_AVAILABLE:
            raise ImportError("PySpark is required for SparkLineageExtension")

        self.spark = spark_session or SparkSession.getActiveSession()
        self.lineage_tracker = lineage_tracker or default_tracker
        self.enable_auto_tracking = enable_auto_tracking
        self.logger = logging.getLogger(__name__)

        # Track DataFrame operations
        self._tracked_dataframes = {}
        self._operation_counter = 0

        if self.spark:
            self._setup_lineage_tracking()

    def _setup_lineage_tracking(self):
        """Set up automatic lineage tracking for Spark operations."""
        if not self.enable_auto_tracking:
            return

        # Add lineage configuration to Spark context
        spark_conf = self.spark.sparkContext.getConf()
        spark_conf.set("spark.sql.adaptive.enabled", "true")
        spark_conf.set("spark.lineage.enabled", "true")

        self.logger.info("Spark lineage tracking configured")

    def track_dataframe(self,
                        df: SparkDataFrame,
                        name: str,
                        source_info: Optional[Dict] = None) -> SparkDataFrame:
        """
        Track a Spark DataFrame in the lineage graph.

        Args:
            df: Spark DataFrame to track
            name: Name for the DataFrame in lineage
            source_info: Optional source information

        Returns:
            The same DataFrame (for chaining)
        """
        if not SPARK_AVAILABLE:
            return df

        # Create lineage node
        metadata = {
            'spark_info': {
                'schema': df.schema.json(),
                'columns': df.columns,
                'partitions': df.rdd.getNumPartitions(),
                'sql_context': str(df.sql_ctx)
            },
            'tracking_timestamp': datetime.now().isoformat()
        }

        if source_info:
            metadata.update(source_info)

        node = self.lineage_tracker.create_node('data', name, metadata)

        # Store DataFrame tracking info
        df_id = id(df)
        self._tracked_dataframes[df_id] = {
            'dataframe': df,
            'node': node,
            'name': name,
            'operations': []
        }

        self.logger.info(f"Tracking Spark DataFrame: {name}")
        return df

    def track_read_operation(self,
                             file_path: str,
                             format: str = 'parquet',
                             name: Optional[str] = None) -> SparkDataFrame:
        """
        Track a read operation and return a tracked DataFrame.

        Args:
            file_path: Path to the file to read
            format: File format (parquet, csv, json, etc.)
            name: Optional name for the DataFrame

        Returns:
            Tracked Spark DataFrame
        """
        if not SPARK_AVAILABLE:
            raise ImportError("PySpark is required")

        # Read the DataFrame
        reader = self.spark.read.format(format)
        if format == 'csv':
            reader = reader.option("header", "true").option(
                "inferSchema", "true")

        df = reader.load(file_path)

        # Create name if not provided
        if not name:
            name = f"spark_read_{format}_{file_path.split('/')[-1]}"

        # Track the read operation
        source_info = {
            'operation_type': 'read',
            'file_path': file_path,
            'file_format': format,
            'spark_read_options': {
                'format': format,
                'path': file_path
            }
        }

        tracked_df = self.track_dataframe(df, name, source_info)

        # Create file node
        file_node = self.lineage_tracker.create_node(
            'file',
            file_path,
            {
                'file_format': format,
                'file_path': file_path,
                'operation': 'spark_read'
            }
        )

        # Track the read operation
        operation = self.lineage_tracker.track_operation(
            operation_type=f'spark_read_{format}',
            inputs=[file_node],
            outputs=[self._tracked_dataframes[id(df)]['node']],
            metadata={
                'spark_operation': {
                    'type': 'read',
                    'format': format,
                    'path': file_path,
                    'schema': df.schema.json()
                }
            }
        )

        return tracked_df

    def track_transformation(self,
                             input_df: SparkDataFrame,
                             output_df: SparkDataFrame,
                             operation_type: str,
                             operation_name: Optional[str] = None,
                             parameters: Optional[Dict] = None) -> SparkDataFrame:
        """
        Track a DataFrame transformation.

        Args:
            input_df: Input DataFrame
            output_df: Output DataFrame
            operation_type: Type of transformation
            operation_name: Optional name for the operation
            parameters: Optional parameters used in transformation

        Returns:
            Tracked output DataFrame
        """
        if not SPARK_AVAILABLE:
            return output_df

        input_df_id = id(input_df)
        output_df_id = id(output_df)

        # Get input tracking info
        input_info = self._tracked_dataframes.get(input_df_id)
        if not input_info:
            # Auto-track input if not already tracked
            input_name = f"auto_tracked_input_{self._operation_counter}"
            input_df = self.track_dataframe(input_df, input_name)
            input_info = self._tracked_dataframes[input_df_id]

        # Create output tracking
        output_name = operation_name or f"{operation_type}_output_{self._operation_counter}"
        output_df = self.track_dataframe(output_df, output_name)
        output_info = self._tracked_dataframes[output_df_id]

        # Track the transformation operation
        operation_metadata = {
            'spark_transformation': {
                'type': operation_type,
                'input_schema': input_df.schema.json(),
                'output_schema': output_df.schema.json(),
                'input_columns': input_df.columns,
                'output_columns': output_df.columns,
                'parameters': parameters or {}
            }
        }

        operation = self.lineage_tracker.track_operation(
            operation_type=f'spark_{operation_type}',
            inputs=[input_info['node']],
            outputs=[output_info['node']],
            metadata=operation_metadata
        )

        # Track column lineage if possible
        self._track_column_lineage(input_df, output_df, operation_type)

        self._operation_counter += 1
        self.logger.info(f"Tracked Spark transformation: {operation_type}")

        return output_df

    def _track_column_lineage(self,
                              input_df: SparkDataFrame,
                              output_df: SparkDataFrame,
                              operation_type: str):
        """Track column-level lineage for transformations."""
        try:
            input_cols = set(input_df.columns)
            output_cols = set(output_df.columns)

            # Simple heuristic for column lineage
            column_mapping = {}

            if operation_type in ['select', 'filter', 'where']:
                # For select/filter, assume direct column mapping
                for col in output_cols:
                    if col in input_cols:
                        column_mapping[col] = [col]

            elif operation_type in ['withColumn', 'assign']:
                # For new columns, assume all input columns contribute
                for col in output_cols:
                    if col in input_cols:
                        column_mapping[col] = [col]
                    else:
                        column_mapping[col] = list(input_cols)

            if column_mapping:
                input_node_id = id(input_df)
                output_node_id = id(output_df)

                input_node = self._tracked_dataframes[input_node_id]['node']
                output_node = self._tracked_dataframes[output_node_id]['node']

                self.lineage_tracker.track_column_lineage(
                    input_node,
                    output_node,
                    column_mapping,
                    f'spark_{operation_type}'
                )

        except Exception as e:
            self.logger.warning(f"Could not track column lineage: {e}")

    def track_write_operation(self,
                              df: SparkDataFrame,
                              file_path: str,
                              format: str = 'parquet',
                              mode: str = 'overwrite') -> None:
        """
        Track a write operation.

        Args:
            df: DataFrame to write
            file_path: Output file path
            format: Output format
            mode: Write mode (overwrite, append, etc.)
        """
        if not SPARK_AVAILABLE:
            return

        # Execute the write operation
        writer = df.write.format(format).mode(mode)
        writer.save(file_path)

        # Track the write operation
        df_id = id(df)
        input_info = self._tracked_dataframes.get(df_id)

        if not input_info:
            # Auto-track if not already tracked
            input_name = f"auto_tracked_write_input_{self._operation_counter}"
            df = self.track_dataframe(df, input_name)
            input_info = self._tracked_dataframes[df_id]

        # Create output file node
        output_node = self.lineage_tracker.create_node(
            'file',
            file_path,
            {
                'file_format': format,
                'file_path': file_path,
                'write_mode': mode,
                'operation': 'spark_write'
            }
        )

        # Track the write operation
        operation = self.lineage_tracker.track_operation(
            operation_type=f'spark_write_{format}',
            inputs=[input_info['node']],
            outputs=[output_node],
            metadata={
                'spark_write': {
                    'format': format,
                    'path': file_path,
                    'mode': mode,
                    'schema': df.schema.json()
                }
            }
        )

        self.logger.info(f"Tracked Spark write operation: {file_path}")

    def get_spark_lineage_summary(self) -> Dict[str, Any]:
        """
        Get a summary of Spark lineage tracking.

        Returns:
            Dictionary with Spark lineage summary
        """
        spark_operations = []
        for operation in self.lineage_tracker.operations:
            if 'spark' in operation.operation_type:
                spark_operations.append(operation.to_dict())

        return {
            'tracked_dataframes': len(self._tracked_dataframes),
            'spark_operations': len(spark_operations),
            'operations': spark_operations,
            'spark_session_info': {
                'app_name': self.spark.sparkContext.appName if self.spark else 'unknown',
                'spark_version': self.spark.version if self.spark else 'unknown'
            }
        }

    def export_spark_lineage(self, output_file: Optional[str] = None) -> str:
        """
        Export Spark lineage to a file.

        Args:
            output_file: Optional file path to save lineage

        Returns:
            Lineage data as JSON string
        """
        lineage_data = {
            'spark_summary': self.get_spark_lineage_summary(),
            'full_lineage': self.lineage_tracker.get_lineage_graph()
        }

        import json
        lineage_json = json.dumps(lineage_data, indent=2, default=str)

        if output_file:
            with open(output_file, 'w') as f:
                f.write(lineage_json)

        return lineage_json


# Convenience functions for easy Spark integration
def create_spark_session_with_lineage(app_name: str = "DataLineagePy",
                                      lineage_tracker: Optional[LineageTracker] = None) -> SparkSession:
    """
    Create a Spark session with lineage tracking enabled.

    Args:
        app_name: Name for the Spark application
        lineage_tracker: LineageTracker instance to use

    Returns:
        Spark session with lineage extension
    """
    if not SPARK_AVAILABLE:
        raise ImportError("PySpark is required")

    # Create Spark session
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.lineage.enabled", "true") \
        .getOrCreate()

    # Add lineage extension
    lineage_extension = SparkLineageExtension(spark, lineage_tracker)

    # Attach extension to session for easy access
    spark.lineage = lineage_extension

    return spark


def track_spark_sql(spark: SparkSession,
                    sql_query: str,
                    result_name: str,
                    lineage_tracker: Optional[LineageTracker] = None) -> SparkDataFrame:
    """
    Execute and track a Spark SQL query.

    Args:
        spark: Spark session
        sql_query: SQL query to execute
        result_name: Name for the result DataFrame
        lineage_tracker: LineageTracker instance

    Returns:
        Tracked result DataFrame
    """
    if not SPARK_AVAILABLE:
        raise ImportError("PySpark is required")

    tracker = lineage_tracker or default_tracker

    # Execute SQL query
    result_df = spark.sql(sql_query)

    # Create lineage extension if not exists
    if not hasattr(spark, 'lineage'):
        spark.lineage = SparkLineageExtension(spark, tracker)

    # Track the SQL operation
    tracked_df = spark.lineage.track_dataframe(
        result_df,
        result_name,
        {
            'operation_type': 'spark_sql',
            'sql_query': sql_query,
            'execution_timestamp': datetime.now().isoformat()
        }
    )

    return tracked_df
