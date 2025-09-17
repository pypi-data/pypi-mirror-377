"""
Apache Airflow integration for DataLineagePy.

This module provides integration with Apache Airflow to automatically track
data lineage in Airflow DAGs and tasks.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    from airflow.models import BaseOperator
    from airflow.plugins_manager import AirflowPlugin
    from airflow.hooks.base import BaseHook
    from airflow.utils.decorators import apply_defaults
    from airflow.lineage import Dataset
    AIRFLOW_AVAILABLE = True
except ImportError:
    # Create dummy classes if Airflow is not available
    BaseOperator = object
    AirflowPlugin = object
    BaseHook = object
    AIRFLOW_AVAILABLE = False

from ..core.tracker import LineageTracker, default_tracker
from ..core.nodes import DataNode


class AirflowLineageOperator(BaseOperator):
    """
    Airflow operator that automatically tracks data lineage.

    This operator wraps other operations and captures their lineage
    information for integration with DataLineagePy.
    """

    if AIRFLOW_AVAILABLE:
        @apply_defaults
        def __init__(self,
                     operation_callable: callable,
                     input_datasets: Optional[List[str]] = None,
                     output_datasets: Optional[List[str]] = None,
                     lineage_tracker: Optional[LineageTracker] = None,
                     operation_type: str = "airflow_task",
                     capture_context: bool = True,
                     *args, **kwargs):
            """
            Initialize the Airflow lineage operator.

            Args:
                operation_callable: Function to execute
                input_datasets: List of input dataset identifiers
                output_datasets: List of output dataset identifiers
                lineage_tracker: LineageTracker instance to use
                operation_type: Type of operation for lineage tracking
                capture_context: Whether to capture Airflow context
            """
            super().__init__(*args, **kwargs)
            self.operation_callable = operation_callable
            self.input_datasets = input_datasets or []
            self.output_datasets = output_datasets or []
            self.lineage_tracker = lineage_tracker or default_tracker
            self.operation_type = operation_type
            self.capture_context = capture_context
            self.logger = logging.getLogger(__name__)
    else:
        def __init__(self, *args, **kwargs):
            """Dummy init when Airflow is not available."""
            pass

    def execute(self, context: Dict[str, Any]) -> Any:
        """Execute the operation with lineage tracking."""
        if not AIRFLOW_AVAILABLE:
            raise ImportError(
                "Apache Airflow is required for AirflowLineageOperator")

        # Capture Airflow context
        dag_id = context.get('dag').dag_id if context.get('dag') else 'unknown'
        task_id = context.get('task_instance').task_id if context.get(
            'task_instance') else self.task_id
        execution_date = context.get('execution_date', datetime.now())

        self.logger.info(
            f"Starting lineage tracking for task {dag_id}.{task_id}")

        # Create input nodes
        input_nodes = []
        for dataset_id in self.input_datasets:
            node = self.lineage_tracker.create_node(
                'data',
                dataset_id,
                {
                    'airflow_dag': dag_id,
                    'airflow_task': task_id,
                    'execution_date': execution_date.isoformat(),
                    'dataset_type': 'airflow_input'
                }
            )
            input_nodes.append(node)

        # Execute the actual operation
        start_time = datetime.now()
        try:
            if self.capture_context:
                result = self.operation_callable(context)
            else:
                result = self.operation_callable()

            execution_status = 'success'
            error_message = None
        except Exception as e:
            execution_status = 'failed'
            error_message = str(e)
            self.logger.error(f"Operation failed: {e}")
            raise
        finally:
            end_time = datetime.now()
            execution_duration = (end_time - start_time).total_seconds()

        # Create output nodes
        output_nodes = []
        for dataset_id in self.output_datasets:
            node = self.lineage_tracker.create_node(
                'data',
                dataset_id,
                {
                    'airflow_dag': dag_id,
                    'airflow_task': task_id,
                    'execution_date': execution_date.isoformat(),
                    'dataset_type': 'airflow_output',
                    'execution_status': execution_status
                }
            )
            output_nodes.append(node)

        # Track the operation
        operation_metadata = {
            'airflow_context': {
                'dag_id': dag_id,
                'task_id': task_id,
                'execution_date': execution_date.isoformat(),
                'run_id': context.get('run_id', 'unknown')
            },
            'execution_metrics': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': execution_duration,
                'status': execution_status
            }
        }

        if error_message:
            operation_metadata['error'] = error_message

        operation = self.lineage_tracker.track_operation(
            operation_type=self.operation_type,
            inputs=input_nodes,
            outputs=output_nodes,
            metadata=operation_metadata
        )

        # Track any errors
        if error_message:
            for output_node in output_nodes:
                self.lineage_tracker.track_error(
                    output_node.id,
                    error_message,
                    'airflow_execution_error',
                    operation.id
                )

        self.logger.info(
            f"Lineage tracking completed for task {dag_id}.{task_id}")
        return result


class AirflowLineageHook(BaseHook if AIRFLOW_AVAILABLE else object):
    """
    Hook for integrating DataLineagePy with Airflow connections and metadata.
    """

    def __init__(self,
                 lineage_tracker: Optional[LineageTracker] = None,
                 connection_id: Optional[str] = None):
        """
        Initialize the Airflow lineage hook.

        Args:
            lineage_tracker: LineageTracker instance to use
            connection_id: Airflow connection ID for lineage storage
        """
        if AIRFLOW_AVAILABLE:
            super().__init__()
        self.lineage_tracker = lineage_tracker or default_tracker
        self.connection_id = connection_id

    def get_dag_lineage(self, dag_id: str) -> Dict[str, Any]:
        """
        Get lineage information for an entire DAG.

        Args:
            dag_id: Airflow DAG ID

        Returns:
            Dictionary with DAG lineage information
        """
        # Search for nodes related to this DAG
        dag_nodes = []
        for node_id, node in self.lineage_tracker.nodes.items():
            if node.metadata.get('airflow_dag') == dag_id:
                dag_nodes.append(node)

        # Get operations for this DAG
        dag_operations = []
        for operation in self.lineage_tracker.operations:
            if operation.metadata.get('airflow_context', {}).get('dag_id') == dag_id:
                dag_operations.append(operation)

        return {
            'dag_id': dag_id,
            'nodes': [node.to_dict() for node in dag_nodes],
            'operations': [op.to_dict() for op in dag_operations],
            'lineage_graph': self.lineage_tracker.get_lineage_graph()
        }

    def export_dag_lineage(self,
                           dag_id: str,
                           output_file: Optional[str] = None) -> str:
        """
        Export DAG lineage to a file or return as string.

        Args:
            dag_id: Airflow DAG ID
            output_file: Optional file path to save lineage

        Returns:
            Lineage data as JSON string
        """
        dag_lineage = self.get_dag_lineage(dag_id)

        import json
        lineage_json = json.dumps(dag_lineage, indent=2, default=str)

        if output_file:
            with open(output_file, 'w') as f:
                f.write(lineage_json)

        return lineage_json


class AirflowLineagePlugin(AirflowPlugin if AIRFLOW_AVAILABLE else object):
    """
    Airflow plugin for DataLineagePy integration.
    """

    name = "datalineage_plugin"
    operators = [AirflowLineageOperator] if AIRFLOW_AVAILABLE else []
    hooks = [AirflowLineageHook] if AIRFLOW_AVAILABLE else []


def create_lineage_dag_factory(lineage_tracker: Optional[LineageTracker] = None):
    """
    Factory function to create DAGs with automatic lineage tracking.

    Args:
        lineage_tracker: LineageTracker instance to use

    Returns:
        Function that creates lineage-enabled DAGs
    """
    tracker = lineage_tracker or default_tracker

    def lineage_dag_wrapper(dag_function):
        """Wrapper that adds lineage tracking to DAG tasks."""

        def wrapped_dag(*args, **kwargs):
            # Create the DAG
            dag = dag_function(*args, **kwargs)

            if not AIRFLOW_AVAILABLE:
                return dag

            # Add lineage tracking to all tasks in the DAG
            for task_id, task in dag.task_dict.items():
                if hasattr(task, 'lineage_tracker'):
                    continue  # Already has lineage tracking

                # Add lineage metadata to task
                if not hasattr(task, 'metadata'):
                    task.metadata = {}

                task.metadata.update({
                    'lineage_tracker': tracker,
                    'lineage_enabled': True,
                    'dag_id': dag.dag_id
                })

            return dag

        return wrapped_dag

    return lineage_dag_wrapper


# Example usage functions
def create_example_lineage_dag():
    """Create an example DAG with lineage tracking."""
    if not AIRFLOW_AVAILABLE:
        return None

    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from datetime import timedelta

    def extract_data(**context):
        """Example extract function."""
        return "data extracted"

    def transform_data(**context):
        """Example transform function."""
        return "data transformed"

    def load_data(**context):
        """Example load function."""
        return "data loaded"

    default_args = {
        'owner': 'datalineage',
        'depends_on_past': False,
        'start_date': datetime(2024, 1, 1),
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5)
    }

    dag = DAG(
        'example_lineage_dag',
        default_args=default_args,
        description='Example DAG with automatic lineage tracking',
        schedule_interval=timedelta(days=1),
        catchup=False
    )

    # Create lineage-enabled tasks
    extract_task = AirflowLineageOperator(
        task_id='extract',
        operation_callable=extract_data,
        output_datasets=['raw_data'],
        operation_type='extract',
        dag=dag
    )

    transform_task = AirflowLineageOperator(
        task_id='transform',
        operation_callable=transform_data,
        input_datasets=['raw_data'],
        output_datasets=['processed_data'],
        operation_type='transform',
        dag=dag
    )

    load_task = AirflowLineageOperator(
        task_id='load',
        operation_callable=load_data,
        input_datasets=['processed_data'],
        output_datasets=['final_data'],
        operation_type='load',
        dag=dag
    )

    # Set dependencies
    extract_task >> transform_task >> load_task

    return dag


# Make the example DAG available for Airflow discovery
if AIRFLOW_AVAILABLE:
    example_lineage_dag = create_example_lineage_dag()
