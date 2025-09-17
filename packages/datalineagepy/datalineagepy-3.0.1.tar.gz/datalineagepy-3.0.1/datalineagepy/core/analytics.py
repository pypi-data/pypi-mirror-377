"""
Advanced Analytics Module for DataLineagePy
Provides advanced statistical and analytical capabilities with lineage tracking.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import warnings

from .tracker import LineageTracker
from .nodes import DataNode
from .dataframe_wrapper import LineageDataFrame


class DataProfiler:
    """Advanced data profiling with lineage tracking."""

    def __init__(self, tracker: LineageTracker):
        self.tracker = tracker

    def profile_dataset(self, ldf: LineageDataFrame, include_correlations: bool = True) -> Dict[str, Any]:
        """Generate comprehensive data profile with lineage tracking."""
        profile_node = self.tracker.create_node(
            "analysis", f"{ldf.name}_profile")

        profile = {
            'dataset_info': {
                'name': ldf.name,
                'shape': ldf.shape,
                'memory_usage': ldf._df.memory_usage(deep=True).sum(),
                'columns': list(ldf.columns),
                'dtypes': {col: str(dtype) for col, dtype in ldf.dtypes.items()}
            },
            'missing_data': self._analyze_missing_data(ldf._df),
            'column_stats': self._analyze_columns(ldf._df),
            'data_quality': self._assess_data_quality(ldf._df)
        }

        if include_correlations and ldf._df.select_dtypes(include=[np.number]).shape[1] > 1:
            profile['correlations'] = self._calculate_correlations(ldf._df)

        # Track the profiling operation
        operation = self.tracker.track_operation(
            "data_profiling",
            [ldf.node],
            [profile_node],
            {
                "include_correlations": include_correlations,
                "columns_analyzed": len(ldf.columns),
                "rows_analyzed": len(ldf._df)
            }
        )

        self.tracker.add_edge(ldf.node, profile_node, operation)

        # Store profile in node metadata
        profile_node.add_metadata("profile_results", profile)

        return profile

    def _analyze_missing_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze missing data patterns."""
        missing_counts = df.isnull().sum()
        missing_percentages = (missing_counts / len(df)) * 100

        return {
            'total_missing': int(missing_counts.sum()),
            'missing_by_column': {
                col: {
                    'count': int(count),
                    'percentage': float(missing_percentages[col])
                }
                for col, count in missing_counts.items() if count > 0
            },
            'complete_rows': int(len(df) - df.isnull().any(axis=1).sum()),
            'complete_rows_percentage': float(((len(df) - df.isnull().any(axis=1).sum()) / len(df)) * 100)
        }

    def _analyze_columns(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Analyze individual columns."""
        column_stats = {}

        for col in df.columns:
            col_data = df[col]
            stats = {
                'dtype': str(col_data.dtype),
                'unique_count': int(col_data.nunique()),
                'unique_percentage': float((col_data.nunique() / len(col_data)) * 100),
                'missing_count': int(col_data.isnull().sum()),
                'missing_percentage': float((col_data.isnull().sum() / len(col_data)) * 100)
            }

            if pd.api.types.is_numeric_dtype(col_data):
                stats.update(self._numeric_column_stats(col_data))
            elif pd.api.types.is_string_dtype(col_data) or col_data.dtype == 'object':
                stats.update(self._text_column_stats(col_data))
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                stats.update(self._datetime_column_stats(col_data))

            column_stats[col] = stats

        return column_stats

    def _numeric_column_stats(self, series: pd.Series) -> Dict[str, Any]:
        """Calculate statistics for numeric columns."""
        desc = series.describe()
        return {
            'min': float(desc['min']) if not pd.isna(desc['min']) else None,
            'max': float(desc['max']) if not pd.isna(desc['max']) else None,
            'mean': float(desc['mean']) if not pd.isna(desc['mean']) else None,
            'median': float(desc['50%']) if not pd.isna(desc['50%']) else None,
            'std': float(desc['std']) if not pd.isna(desc['std']) else None,
            'q25': float(desc['25%']) if not pd.isna(desc['25%']) else None,
            'q75': float(desc['75%']) if not pd.isna(desc['75%']) else None,
            'zeros_count': int((series == 0).sum()),
            'negative_count': int((series < 0).sum())
        }

    def _text_column_stats(self, series: pd.Series) -> Dict[str, Any]:
        """Calculate statistics for text columns."""
        non_null = series.dropna()
        if len(non_null) == 0:
            return {'avg_length': 0, 'min_length': 0, 'max_length': 0}

        lengths = non_null.astype(str).str.len()
        return {
            'avg_length': float(lengths.mean()),
            'min_length': int(lengths.min()),
            'max_length': int(lengths.max()),
            'empty_strings': int((non_null == '').sum()),
            'most_frequent': non_null.mode().iloc[0] if len(non_null.mode()) > 0 else None,
            'most_frequent_count': int(non_null.value_counts().iloc[0]) if len(non_null) > 0 else 0
        }

    def _datetime_column_stats(self, series: pd.Series) -> Dict[str, Any]:
        """Calculate statistics for datetime columns."""
        non_null = series.dropna()
        if len(non_null) == 0:
            return {'min_date': None, 'max_date': None, 'date_range_days': 0}

        return {
            'min_date': non_null.min().isoformat(),
            'max_date': non_null.max().isoformat(),
            'date_range_days': int((non_null.max() - non_null.min()).days)
        }

    def _calculate_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate correlation matrix for numeric columns."""
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] < 2:
            return {}

        corr_matrix = numeric_df.corr()

        # Find high correlations
        high_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:  # Threshold for high correlation
                    high_correlations.append({
                        'column1': corr_matrix.columns[i],
                        'column2': corr_matrix.columns[j],
                        'correlation': float(corr_value)
                    })

        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'high_correlations': high_correlations
        }

    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess overall data quality."""
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()

        # Check for duplicates
        duplicate_rows = df.duplicated().sum()

        # Check for potential data quality issues
        quality_issues = []

        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                # Check for infinite values
                inf_count = np.isinf(df[col]).sum()
                if inf_count > 0:
                    quality_issues.append(
                        f"Column '{col}' has {inf_count} infinite values")

        quality_score = max(
            0, 100 - (missing_cells / total_cells * 100) - (duplicate_rows / len(df) * 10))

        return {
            'quality_score': float(quality_score),
            'duplicate_rows': int(duplicate_rows),
            'duplicate_percentage': float((duplicate_rows / len(df)) * 100),
            'completeness_percentage': float(((total_cells - missing_cells) / total_cells) * 100),
            'quality_issues': quality_issues
        }


class StatisticalAnalyzer:
    """Advanced statistical analysis with lineage tracking."""

    def __init__(self, tracker: LineageTracker):
        self.tracker = tracker

    def hypothesis_test(self, ldf: LineageDataFrame, test_type: str, **kwargs) -> Dict[str, Any]:
        """Perform statistical hypothesis tests with lineage tracking."""
        test_node = self.tracker.create_node(
            "analysis", f"{ldf.name}_{test_type}_test")

        if test_type == "normality":
            result = self._normality_test(ldf._df, **kwargs)
        elif test_type == "correlation":
            result = self._correlation_test(ldf._df, **kwargs)
        elif test_type == "independence":
            result = self._independence_test(ldf._df, **kwargs)
        else:
            raise ValueError(f"Unknown test type: {test_type}")

        # Track the operation
        operation = self.tracker.track_operation(
            f"hypothesis_test_{test_type}",
            [ldf.node],
            [test_node],
            {"test_type": test_type, **kwargs}
        )

        self.tracker.add_edge(ldf.node, test_node, operation)
        test_node.add_metadata("test_results", result)

        return result

    def _normality_test(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Test for normality using Shapiro-Wilk test."""
        try:
            from scipy import stats
        except ImportError:
            return {"error": "scipy not available for statistical tests"}

        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        results = {}
        for col in columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                data = df[col].dropna()
                if len(data) > 3:  # Minimum for Shapiro-Wilk
                    statistic, p_value = stats.shapiro(data)
                    results[col] = {
                        'statistic': float(statistic),
                        'p_value': float(p_value),
                        'is_normal': p_value > 0.05,
                        'test': 'shapiro_wilk'
                    }

        return results

    def _correlation_test(self, df: pd.DataFrame, column1: str, column2: str) -> Dict[str, Any]:
        """Test correlation significance."""
        try:
            from scipy import stats
        except ImportError:
            return {"error": "scipy not available for statistical tests"}

        if column1 not in df.columns or column2 not in df.columns:
            return {"error": "Specified columns not found"}

        data1 = df[column1].dropna()
        data2 = df[column2].dropna()

        # Align the data
        common_idx = data1.index.intersection(data2.index)
        data1 = data1.loc[common_idx]
        data2 = data2.loc[common_idx]

        if len(data1) < 3:
            return {"error": "Insufficient data for correlation test"}

        # Pearson correlation
        pearson_r, pearson_p = stats.pearsonr(data1, data2)

        # Spearman correlation
        spearman_r, spearman_p = stats.spearmanr(data1, data2)

        return {
            'pearson': {
                'correlation': float(pearson_r),
                'p_value': float(pearson_p),
                'significant': pearson_p < 0.05
            },
            'spearman': {
                'correlation': float(spearman_r),
                'p_value': float(spearman_p),
                'significant': spearman_p < 0.05
            },
            'sample_size': len(data1)
        }

    def _independence_test(self, df: pd.DataFrame, column1: str, column2: str) -> Dict[str, Any]:
        """Chi-square test of independence."""
        try:
            from scipy import stats
        except ImportError:
            return {"error": "scipy not available for statistical tests"}

        if column1 not in df.columns or column2 not in df.columns:
            return {"error": "Specified columns not found"}

        # Create contingency table
        contingency_table = pd.crosstab(df[column1], df[column2])

        if contingency_table.size == 0:
            return {"error": "Empty contingency table"}

        chi2, p_value, dof, expected = stats.chi2_contingency(
            contingency_table)

        return {
            'chi2_statistic': float(chi2),
            'p_value': float(p_value),
            'degrees_of_freedom': int(dof),
            'is_independent': p_value > 0.05,
            'contingency_table': contingency_table.to_dict(),
            'expected_frequencies': expected.tolist()
        }


class TimeSeriesAnalyzer:
    """Time series analysis with lineage tracking."""

    def __init__(self, tracker: LineageTracker):
        self.tracker = tracker

    def decompose_timeseries(self, ldf: LineageDataFrame, value_col: str,
                             date_col: str, model: str = 'additive') -> LineageDataFrame:
        """Decompose time series into trend, seasonal, and residual components."""
        try:
            from statsmodels.tsa.seasonal import seasonal_decompose
        except ImportError:
            raise ImportError(
                "statsmodels required for time series decomposition")

        # Prepare time series data
        ts_df = ldf._df.copy()
        ts_df[date_col] = pd.to_datetime(ts_df[date_col])
        ts_df = ts_df.set_index(date_col).sort_index()

        # Perform decomposition
        decomposition = seasonal_decompose(ts_df[value_col], model=model)

        # Create result DataFrame
        result_df = pd.DataFrame({
            'observed': decomposition.observed,
            'trend': decomposition.trend,
            'seasonal': decomposition.seasonal,
            'residual': decomposition.resid
        })

        # Create LineageDataFrame
        result_name = f"{ldf.name}_decomposed"
        result_ldf = LineageDataFrame(
            result_df.reset_index(),
            name=result_name,
            tracker=self.tracker
        )

        # Track the operation
        operation = self.tracker.track_operation(
            "timeseries_decomposition",
            [ldf.node],
            [result_ldf.node],
            {"value_col": value_col, "date_col": date_col, "model": model}
        )

        self.tracker.add_edge(ldf.node, result_ldf.node, operation)

        return result_ldf

    def detect_anomalies(self, ldf: LineageDataFrame, value_col: str,
                         method: str = 'iqr', threshold: float = 1.5) -> LineageDataFrame:
        """Detect anomalies in time series data."""
        df = ldf._df.copy()

        if method == 'iqr':
            anomalies = self._iqr_anomalies(df[value_col], threshold)
        elif method == 'zscore':
            anomalies = self._zscore_anomalies(df[value_col], threshold)
        elif method == 'isolation_forest':
            anomalies = self._isolation_forest_anomalies(df[value_col])
        else:
            raise ValueError(f"Unknown anomaly detection method: {method}")

        # Add anomaly flag to DataFrame
        df['is_anomaly'] = anomalies
        df['anomaly_score'] = self._calculate_anomaly_scores(
            df[value_col], anomalies)

        # Create result LineageDataFrame
        result_name = f"{ldf.name}_anomalies"
        result_ldf = LineageDataFrame(
            df,
            name=result_name,
            tracker=self.tracker
        )

        # Track the operation
        operation = self.tracker.track_operation(
            "anomaly_detection",
            [ldf.node],
            [result_ldf.node],
            {"value_col": value_col, "method": method, "threshold": threshold}
        )

        self.tracker.add_edge(ldf.node, result_ldf.node, operation)

        return result_ldf

    def _iqr_anomalies(self, series: pd.Series, threshold: float) -> pd.Series:
        """Detect anomalies using IQR method."""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        return (series < lower_bound) | (series > upper_bound)

    def _zscore_anomalies(self, series: pd.Series, threshold: float) -> pd.Series:
        """Detect anomalies using Z-score method."""
        z_scores = np.abs((series - series.mean()) / series.std())
        return z_scores > threshold

    def _isolation_forest_anomalies(self, series: pd.Series) -> pd.Series:
        """Detect anomalies using Isolation Forest."""
        try:
            from sklearn.ensemble import IsolationForest
        except ImportError:
            # Fallback to IQR method
            return self._iqr_anomalies(series, 1.5)

        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        predictions = iso_forest.fit_predict(series.values.reshape(-1, 1))
        return pd.Series(predictions == -1, index=series.index)

    def _calculate_anomaly_scores(self, series: pd.Series, anomalies: pd.Series) -> pd.Series:
        """Calculate anomaly scores."""
        mean_val = series.mean()
        std_val = series.std()
        scores = np.abs((series - mean_val) / std_val)
        return scores


class DataTransformer:
    """Advanced data transformation operations with lineage tracking."""

    def __init__(self, tracker: LineageTracker):
        self.tracker = tracker

    def standardize(self, ldf: LineageDataFrame, columns: Optional[List[str]] = None) -> LineageDataFrame:
        """Standardize numeric columns (z-score normalization)."""
        df = ldf._df.copy()

        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        for col in columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                df[col] = (df[col] - df[col].mean()) / df[col].std()

        result_name = f"{ldf.name}_standardized"
        result_ldf = LineageDataFrame(
            df, name=result_name, tracker=self.tracker)

        operation = self.tracker.track_operation(
            "standardization",
            [ldf.node],
            [result_ldf.node],
            {"columns": columns, "method": "z_score"}
        )

        self.tracker.add_edge(ldf.node, result_ldf.node, operation)
        return result_ldf

    def normalize(self, ldf: LineageDataFrame, columns: Optional[List[str]] = None,
                  method: str = 'min_max') -> LineageDataFrame:
        """Normalize numeric columns."""
        df = ldf._df.copy()

        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        for col in columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                if method == 'min_max':
                    min_val = df[col].min()
                    max_val = df[col].max()
                    df[col] = (df[col] - min_val) / (max_val - min_val)
                elif method == 'robust':
                    median = df[col].median()
                    mad = np.median(np.abs(df[col] - median))
                    df[col] = (df[col] - median) / mad

        result_name = f"{ldf.name}_normalized"
        result_ldf = LineageDataFrame(
            df, name=result_name, tracker=self.tracker)

        operation = self.tracker.track_operation(
            "normalization",
            [ldf.node],
            [result_ldf.node],
            {"columns": columns, "method": method}
        )

        self.tracker.add_edge(ldf.node, result_ldf.node, operation)
        return result_ldf

    def encode_categorical(self, ldf: LineageDataFrame, columns: Optional[List[str]] = None,
                           method: str = 'one_hot') -> LineageDataFrame:
        """Encode categorical variables."""
        df = ldf._df.copy()

        if columns is None:
            columns = df.select_dtypes(
                include=['object', 'category']).columns.tolist()

        if method == 'one_hot':
            df = pd.get_dummies(df, columns=columns, prefix=columns)
        elif method == 'label':
            for col in columns:
                if col in df.columns:
                    df[col] = pd.Categorical(df[col]).codes

        result_name = f"{ldf.name}_encoded"
        result_ldf = LineageDataFrame(
            df, name=result_name, tracker=self.tracker)

        operation = self.tracker.track_operation(
            "categorical_encoding",
            [ldf.node],
            [result_ldf.node],
            {"columns": columns, "method": method}
        )

        self.tracker.add_edge(ldf.node, result_ldf.node, operation)
        return result_ldf
