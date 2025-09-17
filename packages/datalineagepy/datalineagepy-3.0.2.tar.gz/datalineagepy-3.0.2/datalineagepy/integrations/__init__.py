"""
Integration modules for DataLineagePy.

This module provides integrations with popular data processing frameworks:
- Apache Airflow
- Apache Spark
- Jupyter Notebooks
- MLflow
"""

__all__ = []

try:
    from .airflow_integration import AirflowLineageOperator, AirflowLineagePlugin
    __all__.extend(['AirflowLineageOperator', 'AirflowLineagePlugin'])
except ImportError:
    # Airflow not available
    pass

try:
    from .spark_integration import SparkLineageExtension
    __all__.append('SparkLineageExtension')
except ImportError:
    # Spark not available
    pass

try:
    from .jupyter_integration import JupyterLineageExtension
    __all__.append('JupyterLineageExtension')
except ImportError:
    # Jupyter not available
    pass
