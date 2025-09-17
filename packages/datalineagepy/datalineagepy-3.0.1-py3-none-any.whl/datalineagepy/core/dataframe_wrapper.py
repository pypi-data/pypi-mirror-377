"""
LineageDataFrame - A wrapper around pandas DataFrame that automatically tracks lineage.
"""

import pandas as pd
from typing import Dict, List, Optional, Any, Union
import functools

from .tracker import default_tracker
from .nodes import DataNode
from .operations import PandasOperation


class LineageDataFrame:
    """
    A wrapper around pandas DataFrame that automatically tracks data lineage.

    This class intercepts pandas operations and records them in the lineage graph,
    providing transparent lineage tracking without changing user code.
    """

    def __init__(self,
                 data: Union[pd.DataFrame, Dict, List],
                 name: Optional[str] = None,
                 tracker=None,
                 source_node: Optional[DataNode] = None):
        """
        Initialize a LineageDataFrame.

        Args:
            data: The underlying pandas DataFrame or data to create one
            name: Optional name for this DataFrame
            tracker: LineageTracker instance to use (defaults to global tracker)
            source_node: Optional source node if this DataFrame comes from a specific source
        """
        # Convert to pandas DataFrame if needed
        if isinstance(data, pd.DataFrame):
            self._df = data
        else:
            self._df = pd.DataFrame(data)

        self.name = name or f"dataframe_{id(self)}"
        self.tracker = tracker or default_tracker

        # Create or use provided source node
        if source_node:
            self.node = source_node
        else:
            self.node = self.tracker.create_node("data", self.name)

        # Update node schema
        self._update_node_schema()

    def _update_node_schema(self):
        """Update the lineage node with current DataFrame schema."""
        schema = {}
        for col in self._df.columns:
            dtype = str(self._df[col].dtype)
            schema[col] = dtype
        self.node.set_schema(schema)

    def _create_operation_wrapper(self, method_name: str):
        """Create a wrapper for pandas operations that tracks lineage."""
        original_method = getattr(self._df, method_name)

        @functools.wraps(original_method)
        def wrapper(*args, **kwargs):
            # Execute the original pandas operation
            result = original_method(*args, **kwargs)

            # If result is a DataFrame, wrap it and track the operation
            if isinstance(result, pd.DataFrame):
                # Create new LineageDataFrame for the result
                result_name = f"{self.name}_{method_name}"
                result_ldf = LineageDataFrame(
                    result,
                    name=result_name,
                    tracker=self.tracker
                )

                # Track the operation
                operation = PandasOperation(
                    operation_type=method_name,
                    inputs=[self.node.id],
                    outputs=[result_ldf.node.id],
                    method_name=method_name,
                    args=args,
                    kwargs=kwargs
                )

                self.tracker.operations.append(operation)
                self.tracker.add_edge(self.node, result_ldf.node, operation)

                return result_ldf
            else:
                # For non-DataFrame results, return as-is
                return result

        return wrapper

    def __getattr__(self, name):
        """Intercept attribute access to wrap pandas methods."""
        if hasattr(self._df, name):
            attr = getattr(self._df, name)

            # If it's a method that returns a DataFrame, wrap it
            if callable(attr) and name in self._trackable_methods():
                return self._create_operation_wrapper(name)
            else:
                return attr
        else:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'")

    def _trackable_methods(self) -> List[str]:
        """Return list of pandas methods that should be tracked."""
        return [
            # Selection and filtering
            'query', 'loc', 'iloc', 'head', 'tail', 'sample',

            # Transformation
            'drop', 'drop_duplicates', 'dropna', 'fillna', 'replace',
            'rename', 'astype', 'assign', 'pipe', 'copy',

            # Grouping and aggregation
            'groupby', 'agg', 'aggregate', 'sum', 'mean', 'count',
            'min', 'max', 'std', 'var', 'median',

            # Merging and joining
            'merge', 'join', 'concat', 'append',

            # Reshaping
            'pivot', 'pivot_table', 'melt', 'stack', 'unstack',
            'transpose', 'T',

            # Sorting
            'sort_values', 'sort_index', 'nlargest', 'nsmallest',

            # String operations (for string columns)
            'str',

            # Mathematical operations
            'abs', 'round', 'clip', 'rank',

            # Window operations
            'rolling', 'expanding', 'ewm',
        ]

    # Delegate common DataFrame properties
    @property
    def shape(self):
        return self._df.shape

    @property
    def columns(self):
        return self._df.columns

    @property
    def index(self):
        return self._df.index

    @property
    def dtypes(self):
        return self._df.dtypes

    @property
    def values(self):
        return self._df.values

    def __len__(self):
        return len(self._df)

    def __getitem__(self, key):
        """Handle DataFrame indexing operations."""
        result = self._df[key]

        if isinstance(result, pd.DataFrame):
            # Create new LineageDataFrame for subset
            result_name = f"{self.name}_subset"
            result_ldf = LineageDataFrame(
                result,
                name=result_name,
                tracker=self.tracker
            )

            # Track the selection operation
            operation = PandasOperation(
                operation_type="selection",
                inputs=[self.node.id],
                outputs=[result_ldf.node.id],
                method_name="__getitem__",
                args=(key,),
                kwargs={}
            )

            self.tracker.operations.append(operation)
            self.tracker.add_edge(self.node, result_ldf.node, operation)

            return result_ldf
        else:
            # Return Series as-is (could be extended to track Series lineage)
            return result

    def __setitem__(self, key, value):
        """Handle DataFrame assignment operations."""
        self._df[key] = value
        self._update_node_schema()

    def __add__(self, other):
        """Handle addition operations."""
        if isinstance(other, LineageDataFrame):
            result = self._df + other._df
            result_name = f"{self.name}_add_{other.name}"
            result_ldf = LineageDataFrame(
                result, name=result_name, tracker=self.tracker)

            # Track the operation
            operation = PandasOperation(
                operation_type="add",
                inputs=[self.node.id, other.node.id],
                outputs=[result_ldf.node.id],
                method_name="__add__",
                args=(other,),
                kwargs={}
            )

            self.tracker.operations.append(operation)
            self.tracker.add_edge(self.node, result_ldf.node, operation)
            self.tracker.add_edge(other.node, result_ldf.node, operation)

            return result_ldf
        else:
            result = self._df + other
            result_name = f"{self.name}_add_scalar"
            result_ldf = LineageDataFrame(
                result, name=result_name, tracker=self.tracker)

            # Track the operation
            operation = PandasOperation(
                operation_type="add_scalar",
                inputs=[self.node.id],
                outputs=[result_ldf.node.id],
                method_name="__add__",
                args=(other,),
                kwargs={}
            )

            self.tracker.operations.append(operation)
            self.tracker.add_edge(self.node, result_ldf.node, operation)

            return result_ldf

    def to_pandas(self) -> pd.DataFrame:
        """Return the underlying pandas DataFrame."""
        return self._df

    def get_lineage(self, direction: str = 'both') -> Dict:
        """Get lineage information for this DataFrame."""
        return self.tracker.get_lineage(self.node.id, direction)

    def __str__(self):
        return f"LineageDataFrame(name='{self.name}', shape={self.shape})\n{str(self._df)}"

    def __repr__(self):
        return f"LineageDataFrame(name='{self.name}', shape={self.shape})"

    # Delegate display methods
    def head(self, n=5):
        """Return first n rows as LineageDataFrame."""
        result = self._df.head(n)
        result_name = f"{self.name}_head_{n}"
        result_ldf = LineageDataFrame(
            result,
            name=result_name,
            tracker=self.tracker
        )

        # Track the operation
        operation = PandasOperation(
            operation_type="head",
            inputs=[self.node.id],
            outputs=[result_ldf.node.id],
            method_name="head",
            args=(n,),
            kwargs={}
        )

        self.tracker.operations.append(operation)
        self.tracker.add_edge(self.node, result_ldf.node, operation)

        return result_ldf

    def info(self, *args, **kwargs):
        """Delegate to pandas info method."""
        return self._df.info(*args, **kwargs)

    def describe(self, *args, **kwargs):
        """Delegate to pandas describe method."""
        return self._df.describe(*args, **kwargs)

    def to_dict(self, orient='dict', into=dict):
        """
        Convert the DataFrame to a dictionary with lineage tracking.

        Args:
            orient: The type of the values of the dictionary
            into: The collections.abc.Mapping subclass to use for all Mappings

        Returns:
            Dictionary representation of the DataFrame
        """
        # Track this operation
        dict_node = self.tracker.create_node("data", f"{self.name}_dict")
        dict_node.add_metadata("operation", "to_dict")
        dict_node.add_metadata("orient", orient)
        dict_node.add_metadata("source_shape", self._df.shape)

        # Execute the operation
        result_dict = self._df.to_dict(orient=orient, into=into)

        # Track the operation
        operation = self.tracker.track_operation(
            "to_dict",
            [self.node],
            [dict_node],
            {"orient": orient, "into": str(into)}
        )

        # Add edge
        self.tracker.add_edge(self.node, dict_node, operation)

        return result_dict

    def to_list(self):
        """Convert DataFrame to a list of lists with lineage tracking."""
        list_node = self.tracker.create_node("data", f"{self.name}_list")
        list_node.add_metadata("operation", "to_list")
        list_node.add_metadata("source_shape", self._df.shape)

        result_list = self._df.values.tolist()

        operation = self.tracker.track_operation(
            "to_list",
            [self.node],
            [list_node],
            {"output_type": "list"}
        )

        self.tracker.add_edge(self.node, list_node, operation)
        return result_list

    def to_numpy(self):
        """Convert DataFrame to numpy array with lineage tracking."""
        numpy_node = self.tracker.create_node("data", f"{self.name}_numpy")
        numpy_node.add_metadata("operation", "to_numpy")
        numpy_node.add_metadata("source_shape", self._df.shape)

        result_array = self._df.values

        operation = self.tracker.track_operation(
            "to_numpy",
            [self.node],
            [numpy_node],
            {"output_type": "numpy_array"}
        )

        self.tracker.add_edge(self.node, numpy_node, operation)
        return result_array

    def to_json(self, path_or_buf=None, orient='records', **kwargs):
        """Export to JSON with lineage tracking."""
        if path_or_buf:
            # File export
            file_node = self.tracker.create_node(
                "file", f"{self.name}_json_export")
            file_node.add_metadata("file_path", path_or_buf)
            file_node.add_metadata("file_format", "json")
            file_node.add_metadata("orient", orient)

            result = self._df.to_json(path_or_buf, orient=orient, **kwargs)

            operation = self.tracker.track_operation(
                "to_json_file",
                [self.node],
                [file_node],
                {"path": path_or_buf, "orient": orient, **kwargs}
            )

            self.tracker.add_edge(self.node, file_node, operation)
            return result
        else:
            # String export
            json_node = self.tracker.create_node("data", f"{self.name}_json")
            json_node.add_metadata("operation", "to_json")
            json_node.add_metadata("orient", orient)

            result = self._df.to_json(orient=orient, **kwargs)

            operation = self.tracker.track_operation(
                "to_json",
                [self.node],
                [json_node],
                {"orient": orient, **kwargs}
            )

            self.tracker.add_edge(self.node, json_node, operation)
            return result

    def to_csv(self, path_or_buf=None, **kwargs):
        """Export to CSV with lineage tracking."""
        if path_or_buf:
            # File export
            file_node = self.tracker.create_node(
                "file", f"{self.name}_csv_export")
            file_node.add_metadata("file_path", path_or_buf)
            file_node.add_metadata("file_format", "csv")

            result = self._df.to_csv(path_or_buf, **kwargs)

            operation = self.tracker.track_operation(
                "to_csv_file",
                [self.node],
                [file_node],
                {"path": path_or_buf, **kwargs}
            )

            self.tracker.add_edge(self.node, file_node, operation)
            return result
        else:
            # String export
            csv_node = self.tracker.create_node("data", f"{self.name}_csv")
            csv_node.add_metadata("operation", "to_csv")

            result = self._df.to_csv(**kwargs)

            operation = self.tracker.track_operation(
                "to_csv",
                [self.node],
                [csv_node],
                {**kwargs}
            )

            self.tracker.add_edge(self.node, csv_node, operation)
            return result

    def to_excel(self, excel_writer, sheet_name='Sheet1', **kwargs):
        """Export to Excel with lineage tracking."""
        file_node = self.tracker.create_node(
            "file", f"{self.name}_excel_export")
        file_node.add_metadata("file_path", str(excel_writer))
        file_node.add_metadata("file_format", "excel")
        file_node.add_metadata("sheet_name", sheet_name)

        result = self._df.to_excel(
            excel_writer, sheet_name=sheet_name, **kwargs)

        operation = self.tracker.track_operation(
            "to_excel",
            [self.node],
            [file_node],
            {"excel_writer": str(excel_writer),
             "sheet_name": sheet_name, **kwargs}
        )

        self.tracker.add_edge(self.node, file_node, operation)
        return result

    def to_parquet(self, path, **kwargs):
        """Export to Parquet with lineage tracking."""
        file_node = self.tracker.create_node(
            "file", f"{self.name}_parquet_export")
        file_node.add_metadata("file_path", path)
        file_node.add_metadata("file_format", "parquet")

        result = self._df.to_parquet(path, **kwargs)

        operation = self.tracker.track_operation(
            "to_parquet",
            [self.node],
            [file_node],
            {"path": path, **kwargs}
        )

        self.tracker.add_edge(self.node, file_node, operation)
        return result

    def to_sql(self, name, con, **kwargs):
        """Export to SQL database with lineage tracking."""
        db_node = self.tracker.create_node(
            "database", f"{self.name}_sql_export")
        db_node.add_metadata("table_name", name)
        db_node.add_metadata("connection", str(con))

        result = self._df.to_sql(name, con, **kwargs)

        operation = self.tracker.track_operation(
            "to_sql",
            [self.node],
            [db_node],
            {"table_name": name, "connection": str(con), **kwargs}
        )

        self.tracker.add_edge(self.node, db_node, operation)
        return result

    # Enhanced DataFrame operations
    def filter(self, condition):
        """Filter DataFrame with custom condition and lineage tracking."""
        # Create result DataFrame
        if isinstance(condition, str):
            filtered_df = self._df.query(condition)
        else:
            filtered_df = self._df[condition]

        result_name = f"{self.name}_filtered"
        result_ldf = LineageDataFrame(
            filtered_df,
            name=result_name,
            tracker=self.tracker
        )

        # Track the operation
        operation = self.tracker.track_operation(
            "filter",
            [self.node],
            [result_ldf.node],
            {"condition": str(condition), "filtered_rows": len(filtered_df)}
        )

        self.tracker.add_edge(self.node, result_ldf.node, operation)
        return result_ldf

    def aggregate(self, func, **kwargs):
        """Aggregate DataFrame with lineage tracking."""
        if isinstance(func, dict):
            agg_df = self._df.agg(func, **kwargs)
        else:
            agg_df = self._df.agg(func, **kwargs)

        # Convert to DataFrame if Series
        if hasattr(agg_df, 'to_frame'):
            agg_df = agg_df.to_frame().T
        elif not hasattr(agg_df, 'columns'):
            agg_df = pd.DataFrame([agg_df])

        result_name = f"{self.name}_aggregated"
        result_ldf = LineageDataFrame(
            agg_df,
            name=result_name,
            tracker=self.tracker
        )

        operation = self.tracker.track_operation(
            "aggregate",
            [self.node],
            [result_ldf.node],
            {"function": str(func), **kwargs}
        )

        self.tracker.add_edge(self.node, result_ldf.node, operation)
        return result_ldf

    def transform(self, func, **kwargs):
        """Transform DataFrame with lineage tracking."""
        transformed_df = self._df.transform(func, **kwargs)

        result_name = f"{self.name}_transformed"
        result_ldf = LineageDataFrame(
            transformed_df,
            name=result_name,
            tracker=self.tracker
        )

        operation = self.tracker.track_operation(
            "transform",
            [self.node],
            [result_ldf.node],
            {"function": str(func), **kwargs}
        )

        self.tracker.add_edge(self.node, result_ldf.node, operation)
        return result_ldf

    def pivot(self, index=None, columns=None, values=None, **kwargs):
        """Pivot DataFrame with lineage tracking."""
        pivoted_df = self._df.pivot(
            index=index, columns=columns, values=values, **kwargs)

        result_name = f"{self.name}_pivoted"
        result_ldf = LineageDataFrame(
            pivoted_df,
            name=result_name,
            tracker=self.tracker
        )

        operation = self.tracker.track_operation(
            "pivot",
            [self.node],
            [result_ldf.node],
            {"index": index, "columns": columns, "values": values, **kwargs}
        )

        self.tracker.add_edge(self.node, result_ldf.node, operation)
        return result_ldf

    def unpivot(self, id_vars=None, value_vars=None, var_name=None, value_name='value'):
        """Unpivot (melt) DataFrame with lineage tracking."""
        melted_df = pd.melt(self._df, id_vars=id_vars, value_vars=value_vars,
                            var_name=var_name, value_name=value_name)

        result_name = f"{self.name}_unpivoted"
        result_ldf = LineageDataFrame(
            melted_df,
            name=result_name,
            tracker=self.tracker
        )

        operation = self.tracker.track_operation(
            "unpivot",
            [self.node],
            [result_ldf.node],
            {"id_vars": id_vars, "value_vars": value_vars,
             "var_name": var_name, "value_name": value_name}
        )

        self.tracker.add_edge(self.node, result_ldf.node, operation)
        return result_ldf

    def resample(self, rule, **kwargs):
        """Resample time series data with lineage tracking."""
        resampled = self._df.resample(rule, **kwargs)

        # Since resample returns a resampler object, we need to apply an operation
        # This is a placeholder - in practice, user would call .mean(), .sum(), etc.
        result_name = f"{self.name}_resampled"

        # Create a tracked resampler wrapper
        class LineageResampler:
            def __init__(self, resampler, source_ldf, tracker):
                self.resampler = resampler
                self.source_ldf = source_ldf
                self.tracker = tracker

            def mean(self):
                result_df = self.resampler.mean()
                return self._create_result(result_df, "resample_mean")

            def sum(self):
                result_df = self.resampler.sum()
                return self._create_result(result_df, "resample_sum")

            def count(self):
                result_df = self.resampler.count()
                return self._create_result(result_df, "resample_count")

            def _create_result(self, result_df, operation_type):
                result_name = f"{self.source_ldf.name}_{operation_type}"
                result_ldf = LineageDataFrame(
                    result_df,
                    name=result_name,
                    tracker=self.tracker
                )

                operation = self.tracker.track_operation(
                    operation_type,
                    [self.source_ldf.node],
                    [result_ldf.node],
                    {"rule": rule, **kwargs}
                )

                self.tracker.add_edge(
                    self.source_ldf.node, result_ldf.node, operation)
                return result_ldf

        return LineageResampler(resampled, self, self.tracker)

    def rolling(self, window, **kwargs):
        """Rolling window operations with lineage tracking."""
        rolling = self._df.rolling(window, **kwargs)

        class LineageRolling:
            def __init__(self, rolling, source_ldf, tracker, window, kwargs):
                self.rolling = rolling
                self.source_ldf = source_ldf
                self.tracker = tracker
                self.window = window
                self.kwargs = kwargs

            def mean(self):
                result_df = self.rolling.mean()
                return self._create_result(result_df, "rolling_mean")

            def sum(self):
                result_df = self.rolling.sum()
                return self._create_result(result_df, "rolling_sum")

            def std(self):
                result_df = self.rolling.std()
                return self._create_result(result_df, "rolling_std")

            def var(self):
                result_df = self.rolling.var()
                return self._create_result(result_df, "rolling_var")

            def min(self):
                result_df = self.rolling.min()
                return self._create_result(result_df, "rolling_min")

            def max(self):
                result_df = self.rolling.max()
                return self._create_result(result_df, "rolling_max")

            def _create_result(self, result_df, operation_type):
                result_name = f"{self.source_ldf.name}_{operation_type}"
                result_ldf = LineageDataFrame(
                    result_df,
                    name=result_name,
                    tracker=self.tracker
                )

                operation = self.tracker.track_operation(
                    operation_type,
                    [self.source_ldf.node],
                    [result_ldf.node],
                    {"window": self.window, **self.kwargs}
                )

                self.tracker.add_edge(
                    self.source_ldf.node, result_ldf.node, operation)
                return result_ldf

        return LineageRolling(rolling, self, self.tracker, window, kwargs)

    def concatenate(self, other_dataframes, axis=0, **kwargs):
        """Concatenate with other DataFrames with lineage tracking."""
        # Prepare DataFrames for concatenation
        dfs_to_concat = [self._df]
        source_nodes = [self.node]

        for other_df in other_dataframes:
            if isinstance(other_df, LineageDataFrame):
                dfs_to_concat.append(other_df._df)
                source_nodes.append(other_df.node)
            else:
                dfs_to_concat.append(other_df)
                # Create a temporary node for non-LineageDataFrame
                temp_node = self.tracker.create_node(
                    "data", f"temp_concat_{len(source_nodes)}")
                source_nodes.append(temp_node)

        # Perform concatenation
        result_df = pd.concat(dfs_to_concat, axis=axis, **kwargs)

        result_name = f"{self.name}_concatenated"
        result_ldf = LineageDataFrame(
            result_df,
            name=result_name,
            tracker=self.tracker
        )

        # Track the operation
        operation = self.tracker.track_operation(
            "concatenate",
            source_nodes,
            [result_ldf.node],
            {"axis": axis, "num_dataframes": len(dfs_to_concat), **kwargs}
        )

        # Add edges from all source nodes
        for source_node in source_nodes:
            self.tracker.add_edge(source_node, result_ldf.node, operation)

        return result_ldf


def read_csv(filepath: str,
             name: Optional[str] = None,
             tracker=None,
             **kwargs) -> LineageDataFrame:
    """
    Read a CSV file and return a LineageDataFrame with tracked lineage.

    Args:
        filepath: Path to the CSV file
        name: Optional name for the resulting DataFrame
        tracker: LineageTracker instance to use
        **kwargs: Additional arguments passed to pandas.read_csv

    Returns:
        LineageDataFrame with tracked lineage
    """
    # Read the CSV file
    df = pd.read_csv(filepath, **kwargs)

    # Create file node for lineage tracking
    if tracker is None:
        tracker = default_tracker

    file_node = tracker.create_node("file", filepath, {
        'file_path': filepath,
        'file_format': 'csv',
        'operation': 'read_csv'
    })

    # Set schema information
    schema = {col: str(df[col].dtype) for col in df.columns}
    file_node.set_schema(schema)

    # Create LineageDataFrame
    result_name = name or f"csv_data_{filepath.split('/')[-1]}"
    ldf = LineageDataFrame(df, result_name, tracker, file_node)

    return ldf


def read_multiple_files(file_patterns: List[str],
                        file_format: str = 'csv',
                        name: Optional[str] = None,
                        tracker=None,
                        combine_method: str = 'concat',
                        **kwargs) -> LineageDataFrame:
    """
    Read multiple files and combine them with tracked lineage.

    Args:
        file_patterns: List of file paths or glob patterns
        file_format: Format of the files ('csv', 'json', 'parquet')
        name: Optional name for the combined DataFrame
        tracker: LineageTracker instance to use
        combine_method: Method to combine files ('concat', 'merge')
        **kwargs: Additional arguments passed to pandas read functions

    Returns:
        LineageDataFrame with tracked lineage from all source files
    """
    import glob

    if tracker is None:
        tracker = default_tracker

    # Expand file patterns
    all_files = []
    for pattern in file_patterns:
        if '*' in pattern or '?' in pattern:
            all_files.extend(glob.glob(pattern))
        else:
            all_files.append(pattern)

    if not all_files:
        raise ValueError("No files found matching the patterns")

    # Read all files and create lineage nodes
    dataframes = []
    file_nodes = []

    for file_path in all_files:
        # Read file based on format
        if file_format == 'csv':
            df = pd.read_csv(file_path, **kwargs)
        elif file_format == 'json':
            df = pd.read_json(file_path, **kwargs)
        elif file_format == 'parquet':
            df = pd.read_parquet(file_path, **kwargs)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

        # Create file node
        file_node = tracker.create_node("file", file_path, {
            'file_path': file_path,
            'file_format': file_format,
            'operation': f'read_{file_format}'
        })

        # Set schema
        schema = {col: str(df[col].dtype) for col in df.columns}
        file_node.set_schema(schema)

        dataframes.append(df)
        file_nodes.append(file_node)

    # Combine dataframes
    if combine_method == 'concat':
        combined_df = pd.concat(dataframes, ignore_index=True)
    else:
        raise ValueError(f"Unsupported combine method: {combine_method}")

    # Create combined result node
    result_name = name or f"combined_{file_format}_data"
    ldf = LineageDataFrame(combined_df, result_name, tracker)

    # Track the combination operation
    tracker.track_operation(
        f"combine_{file_format}_files",
        file_nodes,
        [ldf.node],
        metadata={
            'combine_method': combine_method,
            'source_files': all_files,
            'file_count': len(all_files)
        }
    )

    return ldf


def read_csv_old(filepath: str,
                 name: Optional[str] = None,
                 tracker=None,
                 **kwargs) -> LineageDataFrame:
    """
    Read CSV file and return LineageDataFrame with automatic lineage tracking.

    Args:
        filepath: Path to CSV file
        name: Optional name for the DataFrame
        tracker: LineageTracker instance to use
        **kwargs: Additional arguments passed to pandas.read_csv

    Returns:
        LineageDataFrame instance
    """
    # Read the CSV file
    df = pd.read_csv(filepath, **kwargs)

    # Create file node
    tracker = tracker or default_tracker
    file_node = tracker.create_node("file", filepath, {
        'file_format': 'csv',
        'file_path': filepath
    })

    # Create LineageDataFrame
    name = name or f"csv_{filepath}"
    ldf = LineageDataFrame(df, name=name, tracker=tracker)

    # Track the read operation
    operation = PandasOperation(
        operation_type="read_csv",
        inputs=[file_node.id],
        outputs=[ldf.node.id],
        method_name="read_csv",
        args=(filepath,),
        kwargs=kwargs
    )

    tracker.operations.append(operation)
    tracker.add_edge(file_node, ldf.node, operation)

    return ldf


def read_json(filepath: str,
              name: Optional[str] = None,
              tracker=None,
              **kwargs) -> LineageDataFrame:
    """
    Read a JSON file and return a LineageDataFrame with tracked lineage.

    Args:
        filepath: Path to the JSON file
        name: Optional name for the resulting DataFrame
        tracker: LineageTracker instance to use
        **kwargs: Additional arguments passed to pandas.read_json

    Returns:
        LineageDataFrame with tracked lineage
    """
    # Read the JSON file
    df = pd.read_json(filepath, **kwargs)

    # Create file node for lineage tracking
    if tracker is None:
        tracker = default_tracker

    file_node = tracker.create_node("file", filepath, {
        'file_path': filepath,
        'file_format': 'json',
        'operation': 'read_json'
    })

    # Set schema information
    schema = {col: str(df[col].dtype) for col in df.columns}
    file_node.set_schema(schema)

    # Create LineageDataFrame
    result_name = name or f"json_data_{filepath.split('/')[-1]}"
    ldf = LineageDataFrame(df, result_name, tracker, file_node)

    return ldf


def read_parquet(filepath: str,
                 name: Optional[str] = None,
                 tracker=None,
                 **kwargs) -> LineageDataFrame:
    """
    Read a Parquet file and return a LineageDataFrame with tracked lineage.

    Args:
        filepath: Path to the Parquet file
        name: Optional name for the resulting DataFrame
        tracker: LineageTracker instance to use
        **kwargs: Additional arguments passed to pandas.read_parquet

    Returns:
        LineageDataFrame with tracked lineage
    """
    # Read the Parquet file
    df = pd.read_parquet(filepath, **kwargs)

    # Create file node for lineage tracking
    if tracker is None:
        tracker = default_tracker

    file_node = tracker.create_node("file", filepath, {
        'file_path': filepath,
        'file_format': 'parquet',
        'operation': 'read_parquet'
    })

    # Set schema information
    schema = {col: str(df[col].dtype) for col in df.columns}
    file_node.set_schema(schema)

    # Create LineageDataFrame
    result_name = name or f"parquet_data_{filepath.split('/')[-1]}"
    ldf = LineageDataFrame(df, result_name, tracker, file_node)

    return ldf


def read_excel(filepath: str,
               name: Optional[str] = None,
               tracker=None,
               **kwargs) -> LineageDataFrame:
    """
    Read an Excel file and return a LineageDataFrame with tracked lineage.

    Args:
        filepath: Path to the Excel file
        name: Optional name for the resulting DataFrame
        tracker: LineageTracker instance to use
        **kwargs: Additional arguments passed to pandas.read_excel

    Returns:
        LineageDataFrame with tracked lineage
    """
    # Read the Excel file
    df = pd.read_excel(filepath, **kwargs)

    # Create file node for lineage tracking
    if tracker is None:
        tracker = default_tracker

    file_node = tracker.create_node("file", filepath, {
        'file_path': filepath,
        'file_format': 'excel',
        'operation': 'read_excel'
    })

    # Set schema information
    schema = {col: str(df[col].dtype) for col in df.columns}
    file_node.set_schema(schema)

    # Create LineageDataFrame
    result_name = name or f"excel_data_{filepath.split('/')[-1]}"
    ldf = LineageDataFrame(df, result_name, tracker, file_node)

    return ldf
