"""
File Utilities for DataLineagePy
Provides functions for reading multiple files, detecting formats, and file operations.
"""

import os
import glob
import pandas as pd
import json
from pathlib import Path
from typing import List, Union, Optional, Dict, Any
from datalineagepy.core.dataframe_wrapper import LineageDataFrame


def detect_file_format(file_path: str) -> str:
    """
    Detect file format based on file extension.

    Args:
        file_path: Path to the file

    Returns:
        Detected file format (csv, json, excel, parquet, etc.)
    """
    ext = Path(file_path).suffix.lower()

    format_mapping = {
        '.csv': 'csv',
        '.json': 'json',
        '.xlsx': 'excel',
        '.xls': 'excel',
        '.parquet': 'parquet',
        '.txt': 'csv',  # Assume tab/comma separated
        '.tsv': 'csv'
    }

    return format_mapping.get(ext, 'unknown')


def validate_file_path(file_path: str) -> bool:
    """
    Validate if file path exists and is readable.

    Args:
        file_path: Path to validate

    Returns:
        True if file exists and is readable
    """
    try:
        return os.path.exists(file_path) and os.access(file_path, os.R_OK)
    except Exception:
        return False


def read_single_file(file_path: str, file_format: str, **kwargs) -> pd.DataFrame:
    """
    Read a single file into a pandas DataFrame.

    Args:
        file_path: Path to the file
        file_format: Format of the file (csv, json, excel, parquet)
        **kwargs: Additional arguments for pandas readers

    Returns:
        DataFrame containing the file data
    """
    if not validate_file_path(file_path):
        raise FileNotFoundError(f"File not found or not readable: {file_path}")

    try:
        if file_format == 'csv':
            # Default CSV options for better compatibility
            csv_kwargs = {
                'encoding': 'utf-8',
                'sep': ',',
                'header': 0,
                'index_col': None
            }
            csv_kwargs.update(kwargs)
            return pd.read_csv(file_path, **csv_kwargs)

        elif file_format == 'json':
            # Try different JSON orientations
            json_kwargs = {'orient': 'records'}
            json_kwargs.update(kwargs)
            try:
                return pd.read_json(file_path, **json_kwargs)
            except ValueError:
                # Try as lines format
                return pd.read_json(file_path, lines=True)

        elif file_format == 'excel':
            excel_kwargs = {'engine': 'openpyxl'}
            excel_kwargs.update(kwargs)
            return pd.read_excel(file_path, **excel_kwargs)

        elif file_format == 'parquet':
            parquet_kwargs = {'engine': 'pyarrow'}
            parquet_kwargs.update(kwargs)
            return pd.read_parquet(file_path, **parquet_kwargs)

        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    except Exception as e:
        raise RuntimeError(f"Error reading file {file_path}: {str(e)}")


def read_multiple_files(
    file_patterns: List[str],
    file_format: str,
    tracker,
    combine_method: str = 'concat',
    **kwargs
) -> LineageDataFrame:
    """
    Read multiple files and combine them into a single DataFrame with lineage tracking.

    Args:
        file_patterns: List of file patterns (supports glob patterns)
        file_format: Format of the files (csv, json, excel, parquet)
        tracker: LineageTracker instance for lineage tracking
        combine_method: How to combine files ('concat', 'merge')
        **kwargs: Additional arguments for pandas readers

    Returns:
        LineageDataFrame containing combined data with lineage tracking
    """
    if not file_patterns:
        raise ValueError("No file patterns provided")

    # Expand file patterns to actual file paths
    all_files = []
    for pattern in file_patterns:
        if '*' in pattern or '?' in pattern:
            # Glob pattern
            matched_files = glob.glob(pattern)
            all_files.extend(matched_files)
        else:
            # Direct file path
            if validate_file_path(pattern):
                all_files.append(pattern)

    if not all_files:
        raise FileNotFoundError(
            f"No files found matching patterns: {file_patterns}")

    # Auto-detect format if not provided
    if file_format == 'auto':
        if all_files:
            file_format = detect_file_format(all_files[0])

    # Read all files and track lineage
    dataframes = []
    source_nodes = []

    for file_path in all_files:
        try:
            # Create a source node for each file
            file_name = os.path.basename(file_path)
            source_node = tracker.create_node('file', f'source_{file_name}')
            source_node.add_metadata('file_path', file_path)
            source_node.add_metadata('file_format', file_format)
            source_node.add_metadata('file_size', os.path.getsize(file_path))
            source_nodes.append(source_node)

            # Read the file
            df = read_single_file(file_path, file_format, **kwargs)
            dataframes.append(df)

            # Add schema information to the node
            schema = {col: str(dtype) for col, dtype in df.dtypes.items()}
            source_node.set_schema(schema)
            source_node.add_metadata('rows', len(df))
            source_node.add_metadata('columns', list(df.columns))

        except Exception as e:
            # Track error but continue with other files
            error_node = tracker.create_node('error', f'error_{file_name}')
            tracker.track_error(error_node.id, str(e), 'file_read_error')
            continue

    if not dataframes:
        raise RuntimeError("No files could be read successfully")

    # Combine dataframes
    if combine_method == 'concat':
        combined_df = pd.concat(dataframes, ignore_index=True, sort=False)
    elif combine_method == 'merge':
        # For merge, we need a common column - use the first column
        combined_df = dataframes[0]
        for df in dataframes[1:]:
            # Simple merge on index or first common column
            common_cols = list(set(combined_df.columns) & set(df.columns))
            if common_cols:
                combined_df = pd.merge(
                    combined_df, df, on=common_cols[0], how='outer')
            else:
                # Fallback to concat if no common columns
                combined_df = pd.concat(
                    [combined_df, df], ignore_index=True, sort=False)
    else:
        raise ValueError(f"Unsupported combine method: {combine_method}")

    # Create combined result node
    result_node = tracker.create_node('data', 'combined_files')
    result_node.add_metadata(
        'source_files', [os.path.basename(f) for f in all_files])
    result_node.add_metadata('combine_method', combine_method)
    result_node.add_metadata('total_files', len(all_files))
    result_node.add_metadata('successful_files', len(dataframes))

    # Set schema for combined data
    combined_schema = {col: str(dtype)
                       for col, dtype in combined_df.dtypes.items()}
    result_node.set_schema(combined_schema)
    result_node.add_metadata('final_rows', len(combined_df))
    result_node.add_metadata('final_columns', list(combined_df.columns))

    # Track the combination operation
    operation = tracker.track_operation(
        f'combine_files_{combine_method}',
        source_nodes,
        [result_node],
        {
            'file_patterns': file_patterns,
            'file_format': file_format,
            'combine_method': combine_method,
            'files_processed': len(all_files)
        }
    )

    # Add operation metadata
    operation.add_metadata('execution_context', {
        'function': 'read_multiple_files',
        'timestamp': pd.Timestamp.now().isoformat(),
        'file_patterns': file_patterns,
        'total_rows': len(combined_df),
        'total_columns': len(combined_df.columns)
    })

    # Create edges from source nodes to result node
    for source_node in source_nodes:
        tracker.add_edge(source_node, result_node, 'file_combine')

        # Create LineageDataFrame with lineage
    wrapper = LineageDataFrame(
        combined_df, name='combined_files', tracker=tracker, source_node=result_node)

    return wrapper


def save_dataframe_with_lineage(
    df_wrapper: LineageDataFrame,
    file_path: str,
    file_format: Optional[str] = None,
    **kwargs
) -> None:
    """
    Save a LineageDataFrame to file and track the lineage.

    Args:
        df_wrapper: LineageDataFrame to save
        file_path: Output file path
        file_format: Output format (auto-detected if None)
        **kwargs: Additional arguments for pandas writers
    """
    if file_format is None:
        file_format = detect_file_format(file_path)

    # Create output node
    file_name = os.path.basename(file_path)
    output_node = df_wrapper.tracker.create_node('file', f'output_{file_name}')
    output_node.add_metadata('file_path', file_path)
    output_node.add_metadata('file_format', file_format)

    # Save the file
    try:
        if file_format == 'csv':
            csv_kwargs = {'index': False}
            csv_kwargs.update(kwargs)
            df_wrapper._df.to_csv(file_path, **csv_kwargs)

        elif file_format == 'json':
            json_kwargs = {'orient': 'records'}
            json_kwargs.update(kwargs)
            df_wrapper._df.to_json(file_path, **json_kwargs)

        elif file_format == 'excel':
            excel_kwargs = {'index': False}
            excel_kwargs.update(kwargs)
            df_wrapper._df.to_excel(file_path, **excel_kwargs)

        elif file_format == 'parquet':
            parquet_kwargs = {'index': False}
            parquet_kwargs.update(kwargs)
            df_wrapper._df.to_parquet(file_path, **parquet_kwargs)

        else:
            raise ValueError(f"Unsupported output format: {file_format}")

        # Add file size and success metadata
        output_node.add_metadata('file_size', os.path.getsize(file_path))
        output_node.add_metadata('save_success', True)

    except Exception as e:
        output_node.add_metadata('save_success', False)
        df_wrapper.tracker.track_error(
            output_node.id, str(e), 'file_write_error')
        raise

    # Track the save operation
    operation = df_wrapper.tracker.track_operation(
        'save_file',
        [df_wrapper.node],
        [output_node],
        {
            'file_path': file_path,
            'file_format': file_format,
            'rows_saved': len(df_wrapper._df),
            'columns_saved': len(df_wrapper._df.columns)
        }
    )

    # Add edge
    df_wrapper.tracker.add_edge(
        df_wrapper.node, output_node, 'file_save')


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get comprehensive information about a file.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary containing file information
    """
    if not validate_file_path(file_path):
        return {'exists': False, 'error': 'File not found or not readable'}

    try:
        stat = os.stat(file_path)
        file_format = detect_file_format(file_path)

        info = {
            'exists': True,
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'modified': pd.Timestamp.fromtimestamp(stat.st_mtime).isoformat(),
            'format': file_format,
            'extension': Path(file_path).suffix,
            'readable': True
        }

        # Try to get data information
        try:
            if file_format in ['csv', 'json', 'excel', 'parquet']:
                df = read_single_file(file_path, file_format)
                info.update({
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': list(df.columns),
                    'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                    'memory_usage': df.memory_usage(deep=True).sum()
                })
        except Exception as e:
            info['data_read_error'] = str(e)

        return info

    except Exception as e:
        return {'exists': True, 'error': str(e)}


def batch_file_operations(
    operations: List[Dict[str, Any]],
    tracker,
    continue_on_error: bool = True
) -> Dict[str, Any]:
    """
    Perform batch file operations with lineage tracking.

    Args:
        operations: List of operation dictionaries
        tracker: LineageTracker instance
        continue_on_error: Whether to continue on individual operation errors

    Returns:
        Results summary
    """
    results = {
        'total_operations': len(operations),
        'successful_operations': 0,
        'failed_operations': 0,
        'operation_results': [],
        'errors': []
    }

    for i, operation in enumerate(operations):
        try:
            op_type = operation.get('type')
            op_id = f"batch_op_{i}_{op_type}"

            if op_type == 'read_multiple':
                result = read_multiple_files(
                    operation['file_patterns'],
                    operation.get('file_format', 'auto'),
                    tracker,
                    **operation.get('kwargs', {})
                )
                results['operation_results'].append({
                    'operation_id': op_id,
                    'type': op_type,
                    'success': True,
                    'result_shape': result._df.shape,
                    'result_node_id': result.node.id
                })
                results['successful_operations'] += 1

            elif op_type == 'save':
                save_dataframe_with_lineage(
                    operation['df_wrapper'],
                    operation['file_path'],
                    operation.get('file_format'),
                    **operation.get('kwargs', {})
                )
                results['operation_results'].append({
                    'operation_id': op_id,
                    'type': op_type,
                    'success': True,
                    'file_path': operation['file_path']
                })
                results['successful_operations'] += 1

            else:
                raise ValueError(f"Unsupported operation type: {op_type}")

        except Exception as e:
            error_msg = f"Operation {i} failed: {str(e)}"
            results['errors'].append(error_msg)
            results['failed_operations'] += 1

            results['operation_results'].append({
                'operation_id': op_id,
                'type': operation.get('type', 'unknown'),
                'success': False,
                'error': str(e)
            })

            if not continue_on_error:
                break

    return results
