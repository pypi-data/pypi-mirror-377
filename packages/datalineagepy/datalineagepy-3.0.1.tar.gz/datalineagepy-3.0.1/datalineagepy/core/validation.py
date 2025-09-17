"""
Data Validation Module for DataLineagePy
Comprehensive data quality and validation checks with lineage tracking.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime
import re

from .tracker import LineageTracker
from .nodes import DataNode
from .dataframe_wrapper import LineageDataFrame


class DataValidator:
    """Comprehensive data validation with lineage tracking."""

    def __init__(self, tracker: LineageTracker):
        self.tracker = tracker
        self.validation_rules = {}
        self.validation_history = []

    def add_validation_rule(self, rule_name: str, rule_function: Callable,
                            description: str = "", severity: str = "error"):
        """Add a custom validation rule."""
        self.validation_rules[rule_name] = {
            'function': rule_function,
            'description': description,
            'severity': severity
        }

    def validate_dataframe(self, ldf: LineageDataFrame,
                           rules: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run comprehensive validation on a LineageDataFrame."""
        validation_node = self.tracker.create_node(
            "validation", f"{ldf.name}_validation")

        # Default validation rules if none specified
        if rules is None:
            rules = ['completeness', 'uniqueness',
                     'data_types', 'ranges', 'patterns']

        validation_results = {
            'dataset_name': ldf.name,
            'validation_timestamp': datetime.now().isoformat(),
            'total_rows': len(ldf._df),
            'total_columns': len(ldf._df.columns),
            'rules_applied': rules,
            'validation_summary': {
                'passed': 0,
                'warnings': 0,
                'errors': 0
            },
            'rule_results': {}
        }

        # Apply validation rules
        for rule in rules:
            if rule == 'completeness':
                result = self._validate_completeness(ldf._df)
            elif rule == 'uniqueness':
                result = self._validate_uniqueness(ldf._df)
            elif rule == 'data_types':
                result = self._validate_data_types(ldf._df)
            elif rule == 'ranges':
                result = self._validate_ranges(ldf._df)
            elif rule == 'patterns':
                result = self._validate_patterns(ldf._df)
            elif rule in self.validation_rules:
                result = self.validation_rules[rule]['function'](ldf._df)
            else:
                result = {'status': 'skipped',
                          'message': f'Unknown rule: {rule}'}

            validation_results['rule_results'][rule] = result

            # Update summary counts
            if result.get('status') == 'passed':
                validation_results['validation_summary']['passed'] += 1
            elif result.get('status') == 'warning':
                validation_results['validation_summary']['warnings'] += 1
            elif result.get('status') == 'error':
                validation_results['validation_summary']['errors'] += 1

        # Calculate overall validation score
        total_rules = len(rules)
        passed_rules = validation_results['validation_summary']['passed']
        validation_results['validation_score'] = (
            passed_rules / total_rules * 100) if total_rules > 0 else 0

        # Track the validation operation
        operation = self.tracker.track_operation(
            "data_validation",
            [ldf.node],
            [validation_node],
            {
                "rules_applied": rules,
                "validation_score": validation_results['validation_score'],
                "total_issues": validation_results['validation_summary']['errors'] +
                validation_results['validation_summary']['warnings']
            }
        )

        self.tracker.add_edge(ldf.node, validation_node, operation)
        validation_node.add_metadata("validation_results", validation_results)

        # Store in validation history
        self.validation_history.append(validation_results)

        return validation_results

    def _validate_completeness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate data completeness (missing values)."""
        missing_counts = df.isnull().sum()
        total_cells = len(df) * len(df.columns)
        total_missing = missing_counts.sum()

        completeness_percentage = (
            (total_cells - total_missing) / total_cells) * 100

        issues = []
        for col, missing_count in missing_counts.items():
            if missing_count > 0:
                missing_percentage = (missing_count / len(df)) * 100
                issues.append({
                    'column': col,
                    'missing_count': int(missing_count),
                    'missing_percentage': round(missing_percentage, 2)
                })

        if completeness_percentage >= 95:
            status = 'passed'
        elif completeness_percentage >= 80:
            status = 'warning'
        else:
            status = 'error'

        return {
            'status': status,
            'completeness_percentage': round(completeness_percentage, 2),
            'total_missing_values': int(total_missing),
            'columns_with_missing': issues,
            'message': f"Data is {completeness_percentage:.1f}% complete"
        }

    def _validate_uniqueness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate uniqueness constraints."""
        uniqueness_issues = []

        for col in df.columns:
            total_values = len(df[col].dropna())
            unique_values = df[col].nunique()

            if total_values > 0:
                uniqueness_ratio = unique_values / total_values
                duplicate_count = total_values - unique_values

                if duplicate_count > 0:
                    uniqueness_issues.append({
                        'column': col,
                        'total_values': total_values,
                        'unique_values': unique_values,
                        'duplicate_count': duplicate_count,
                        'uniqueness_ratio': round(uniqueness_ratio, 3)
                    })

        if not uniqueness_issues:
            status = 'passed'
            message = "No uniqueness issues found"
        elif len(uniqueness_issues) <= len(df.columns) * 0.2:  # Less than 20% of columns
            status = 'warning'
            message = f"Minor uniqueness issues in {len(uniqueness_issues)} columns"
        else:
            status = 'error'
            message = f"Significant uniqueness issues in {len(uniqueness_issues)} columns"

        return {
            'status': status,
            'uniqueness_issues': uniqueness_issues,
            'columns_with_duplicates': len(uniqueness_issues),
            'message': message
        }

    def _validate_data_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate data types and detect inconsistencies."""
        type_issues = []

        for col in df.columns:
            col_data = df[col].dropna()

            if len(col_data) == 0:
                continue

            # Check for mixed types in object columns
            if col_data.dtype == 'object':
                # Sample first 100
                types_found = set(
                    type(val).__name__ for val in col_data.iloc[:100])

                if len(types_found) > 1:
                    type_issues.append({
                        'column': col,
                        'issue': 'mixed_types',
                        'types_found': list(types_found),
                        'current_dtype': str(col_data.dtype)
                    })

            # Check numeric columns for non-numeric values
            elif pd.api.types.is_numeric_dtype(col_data):
                try:
                    pd.to_numeric(col_data, errors='raise')
                except (ValueError, TypeError):
                    type_issues.append({
                        'column': col,
                        'issue': 'invalid_numeric_values',
                        'current_dtype': str(col_data.dtype)
                    })

        if not type_issues:
            status = 'passed'
            message = "All data types are consistent"
        elif len(type_issues) <= 2:
            status = 'warning'
            message = f"Minor data type issues in {len(type_issues)} columns"
        else:
            status = 'error'
            message = f"Significant data type issues in {len(type_issues)} columns"

        return {
            'status': status,
            'type_issues': type_issues,
            'columns_with_issues': len(type_issues),
            'message': message
        }

    def _validate_ranges(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate numeric ranges and detect outliers."""
        range_issues = []

        numeric_columns = df.select_dtypes(include=[np.number]).columns

        for col in numeric_columns:
            col_data = df[col].dropna()

            if len(col_data) == 0:
                continue

            # Detect outliers using IQR method
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = col_data[(col_data < lower_bound) |
                                (col_data > upper_bound)]

            if len(outliers) > 0:
                range_issues.append({
                    'column': col,
                    'outlier_count': len(outliers),
                    'outlier_percentage': round((len(outliers) / len(col_data)) * 100, 2),
                    'range': {
                        'min': float(col_data.min()),
                        'max': float(col_data.max()),
                        'q1': float(Q1),
                        'q3': float(Q3)
                    },
                    'expected_range': {
                        'lower_bound': float(lower_bound),
                        'upper_bound': float(upper_bound)
                    }
                })

        if not range_issues:
            status = 'passed'
            message = "No significant outliers detected"
        else:
            total_outlier_percentage = sum(
                issue['outlier_percentage'] for issue in range_issues) / len(range_issues)
            if total_outlier_percentage <= 5:
                status = 'warning'
                message = f"Minor outliers detected in {len(range_issues)} columns"
            else:
                status = 'error'
                message = f"Significant outliers detected in {len(range_issues)} columns"

        return {
            'status': status,
            'range_issues': range_issues,
            'columns_with_outliers': len(range_issues),
            'message': message
        }

    def _validate_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate common data patterns (emails, phones, etc.)."""
        pattern_issues = []

        # Common patterns to validate
        patterns = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$',
            'url': r'^https?://[^\s/$.?#].[^\s]*$',
            'ip_address': r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
        }

        text_columns = df.select_dtypes(include=['object']).columns

        for col in text_columns:
            col_data = df[col].dropna().astype(str)

            if len(col_data) == 0:
                continue

            # Try to detect pattern type based on column name
            col_lower = col.lower()
            detected_pattern = None

            for pattern_name in patterns.keys():
                if pattern_name in col_lower:
                    detected_pattern = pattern_name
                    break

            if detected_pattern:
                pattern_regex = patterns[detected_pattern]
                valid_values = col_data.str.match(pattern_regex, na=False)
                invalid_count = len(col_data) - valid_values.sum()

                if invalid_count > 0:
                    pattern_issues.append({
                        'column': col,
                        'expected_pattern': detected_pattern,
                        'invalid_count': invalid_count,
                        'invalid_percentage': round((invalid_count / len(col_data)) * 100, 2),
                        'sample_invalid_values': col_data[~valid_values].head(3).tolist()
                    })

        if not pattern_issues:
            status = 'passed'
            message = "All detected patterns are valid"
        elif len(pattern_issues) == 1:
            status = 'warning'
            message = "Minor pattern validation issues detected"
        else:
            status = 'error'
            message = f"Pattern validation issues in {len(pattern_issues)} columns"

        return {
            'status': status,
            'pattern_issues': pattern_issues,
            'columns_with_pattern_issues': len(pattern_issues),
            'message': message
        }

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of all validation history."""
        if not self.validation_history:
            return {"message": "No validation history available"}

        total_validations = len(self.validation_history)
        avg_score = sum(v['validation_score']
                        for v in self.validation_history) / total_validations

        recent_validations = sorted(self.validation_history,
                                    key=lambda x: x['validation_timestamp'],
                                    reverse=True)[:5]

        return {
            'total_validations_run': total_validations,
            'average_validation_score': round(avg_score, 2),
            'recent_validations': recent_validations,
            'available_rules': list(self.validation_rules.keys()) +
            ['completeness', 'uniqueness', 'data_types', 'ranges', 'patterns']
        }


class SchemaValidator:
    """Validate data against predefined schemas."""

    def __init__(self, tracker: LineageTracker):
        self.tracker = tracker
        self.schemas = {}

    def register_schema(self, schema_name: str, schema_definition: Dict[str, Any]):
        """Register a schema for validation."""
        self.schemas[schema_name] = {
            'definition': schema_definition,
            'created_at': datetime.now().isoformat()
        }

    def validate_against_schema(self, ldf: LineageDataFrame,
                                schema_name: str) -> Dict[str, Any]:
        """Validate DataFrame against a registered schema."""
        if schema_name not in self.schemas:
            return {'error': f'Schema {schema_name} not found'}

        schema = self.schemas[schema_name]['definition']
        schema_node = self.tracker.create_node("schema_validation",
                                               f"{ldf.name}_{schema_name}_validation")

        validation_results = {
            'dataset_name': ldf.name,
            'schema_name': schema_name,
            'validation_timestamp': datetime.now().isoformat(),
            'schema_compliance': True,
            'issues': []
        }

        # Validate required columns
        required_columns = schema.get('required_columns', [])
        missing_columns = set(required_columns) - set(ldf.columns)

        if missing_columns:
            validation_results['schema_compliance'] = False
            validation_results['issues'].append({
                'type': 'missing_columns',
                'columns': list(missing_columns)
            })

        # Validate column data types
        column_types = schema.get('column_types', {})
        for col, expected_type in column_types.items():
            if col in ldf.columns:
                actual_type = str(ldf._df[col].dtype)
                if expected_type not in actual_type:
                    validation_results['schema_compliance'] = False
                    validation_results['issues'].append({
                        'type': 'type_mismatch',
                        'column': col,
                        'expected': expected_type,
                        'actual': actual_type
                    })

        # Validate constraints
        constraints = schema.get('constraints', {})
        for constraint_name, constraint_def in constraints.items():
            constraint_result = self._validate_constraint(
                ldf._df, constraint_def)
            if not constraint_result['valid']:
                validation_results['schema_compliance'] = False
                validation_results['issues'].append({
                    'type': 'constraint_violation',
                    'constraint': constraint_name,
                    'details': constraint_result
                })

        # Track schema validation
        operation = self.tracker.track_operation(
            "schema_validation",
            [ldf.node],
            [schema_node],
            {
                "schema_name": schema_name,
                "compliance": validation_results['schema_compliance'],
                "issues_count": len(validation_results['issues'])
            }
        )

        self.tracker.add_edge(ldf.node, schema_node, operation)
        schema_node.add_metadata(
            "schema_validation_results", validation_results)

        return validation_results

    def _validate_constraint(self, df: pd.DataFrame, constraint: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a specific constraint."""
        constraint_type = constraint.get('type')

        if constraint_type == 'range':
            column = constraint['column']
            min_val = constraint.get('min')
            max_val = constraint.get('max')

            if column not in df.columns:
                return {'valid': False, 'error': f'Column {column} not found'}

            col_data = df[column].dropna()
            violations = []

            if min_val is not None:
                violations.extend(col_data[col_data < min_val].index.tolist())

            if max_val is not None:
                violations.extend(col_data[col_data > max_val].index.tolist())

            return {
                'valid': len(violations) == 0,
                'violations': len(violations),
                'violation_rows': violations[:10]  # First 10 violations
            }

        elif constraint_type == 'unique':
            column = constraint['column']

            if column not in df.columns:
                return {'valid': False, 'error': f'Column {column} not found'}

            duplicates = df[column].duplicated().sum()

            return {
                'valid': duplicates == 0,
                'duplicate_count': duplicates
            }

        return {'valid': True, 'message': 'Constraint type not implemented'}

    def create_schema_from_dataframe(self, ldf: LineageDataFrame,
                                     schema_name: str) -> Dict[str, Any]:
        """Create a schema definition from an existing DataFrame."""
        schema_definition = {
            'name': schema_name,
            'created_from': ldf.name,
            'created_at': datetime.now().isoformat(),
            'required_columns': list(ldf.columns),
            'column_types': {col: str(dtype) for col, dtype in ldf.dtypes.items()},
            'shape': {
                'min_rows': len(ldf._df),
                'columns': len(ldf.columns)
            },
            'constraints': {}
        }

        # Auto-generate some basic constraints
        for col in ldf.columns:
            if pd.api.types.is_numeric_dtype(ldf._df[col]):
                col_data = ldf._df[col].dropna()
                if len(col_data) > 0:
                    schema_definition['constraints'][f'{col}_range'] = {
                        'type': 'range',
                        'column': col,
                        'min': float(col_data.min()),
                        'max': float(col_data.max())
                    }

        self.register_schema(schema_name, schema_definition)
        return schema_definition
