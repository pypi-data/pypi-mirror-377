"""Data Validation Module

This module provides comprehensive data validation and quality checking capabilities
for ensuring data integrity and quality before machine learning model training.
"""


import json
import logging
import warnings
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy import stats

# Configure logging
logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationRule(Enum):
    """Types of validation rules."""
    MISSING_VALUES = "missing_values"
    DUPLICATE_ROWS = "duplicate_rows"
    OUTLIERS = "outliers"
    DATA_TYPES = "data_types"
    SCHEMA = "schema"
    RANGE = "range"
    DISTRIBUTION = "distribution"
    CARDINALITY = "cardinality"
    UNIQUENESS = "uniqueness"
    COMPLETENESS = "completeness"


@dataclass
class ValidationIssue:
    """Represents a data validation issue."""
    rule: ValidationRule
    severity: ValidationSeverity
    column: Optional[str]
    message: str
    details: Dict[str, Any]
    affected_rows: Optional[int] = None
    suggested_action: Optional[str] = None


@dataclass
class DataQualityReport:
    """Comprehensive data quality report."""
    total_rows: int
    total_columns: int
    issues: List[ValidationIssue]
    quality_score: float
    completeness_score: float
    consistency_score: float
    validity_score: float
    uniqueness_score: float
    summary: Dict[str, Any]
    
    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[ValidationIssue]:
        """Get issues by severity level."""
        return [issue for issue in self.issues if issue.severity == severity]
    
    def get_critical_issues(self) -> List[ValidationIssue]:
        """Get critical issues that must be addressed."""
        return self.get_issues_by_severity(ValidationSeverity.CRITICAL)
    
    def has_critical_issues(self) -> bool:
        """Check if there are any critical issues."""
        return len(self.get_critical_issues()) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "total_rows": self.total_rows,
            "total_columns": self.total_columns,
            "quality_score": self.quality_score,
            "completeness_score": self.completeness_score,
            "consistency_score": self.consistency_score,
            "validity_score": self.validity_score,
            "uniqueness_score": self.uniqueness_score,
            "summary": self.summary,
            "issues": [
                {
                    "rule": issue.rule.value,
                    "severity": issue.severity.value,
                    "column": issue.column,
                    "message": issue.message,
                    "details": issue.details,
                    "affected_rows": issue.affected_rows,
                    "suggested_action": issue.suggested_action
                }
                for issue in self.issues
            ]
        }


class DataValidator:
    """Comprehensive data validation and quality checking."""
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize data validator.
        
        Args:
            strict_mode: If True, raises exceptions for critical issues
        """
        self.strict_mode = strict_mode
        self.issues = []
        
    def validate_dataset(
        self,
        data: pd.DataFrame,
        schema: Optional[Dict[str, Any]] = None,
        rules: Optional[List[ValidationRule]] = None
    ) -> DataQualityReport:
        """
        Perform comprehensive data validation.
        
        Args:
            data: DataFrame to validate
            schema: Optional schema definition for validation
            rules: Optional list of specific rules to apply
            
        Returns:
            DataQualityReport with validation results
        """
        logger.info(f"Starting data validation for dataset with shape {data.shape}")
        
        # Reset issues
        self.issues = []
        
        # Default rules if none specified
        if rules is None:
            rules = list(ValidationRule)
        
        # Apply validation rules
        for rule in rules:
            try:
                if rule == ValidationRule.MISSING_VALUES:
                    self._check_missing_values(data)
                elif rule == ValidationRule.DUPLICATE_ROWS:
                    self._check_duplicate_rows(data)
                elif rule == ValidationRule.OUTLIERS:
                    self._check_outliers(data)
                elif rule == ValidationRule.DATA_TYPES:
                    self._check_data_types(data)
                elif rule == ValidationRule.SCHEMA:
                    if schema:
                        self._validate_schema(data, schema)
                elif rule == ValidationRule.RANGE:
                    self._check_value_ranges(data)
                elif rule == ValidationRule.DISTRIBUTION:
                    self._check_distributions(data)
                elif rule == ValidationRule.CARDINALITY:
                    self._check_cardinality(data)
                elif rule == ValidationRule.UNIQUENESS:
                    self._check_uniqueness(data)
                elif rule == ValidationRule.COMPLETENESS:
                    self._check_completeness(data)
                    
            except Exception as e:
                logger.error(f"Error applying validation rule {rule.value}: {e}")
                self.issues.append(ValidationIssue(
                    rule=rule,
                    severity=ValidationSeverity.ERROR,
                    column=None,
                    message=f"Validation rule {rule.value} failed: {str(e)}",
                    details={"error": str(e)}
                ))
        
        # Calculate quality scores
        quality_scores = self._calculate_quality_scores(data)
        
        # Create report
        report = DataQualityReport(
            total_rows=len(data),
            total_columns=len(data.columns),
            issues=self.issues,
            quality_score=quality_scores["overall"],
            completeness_score=quality_scores["completeness"],
            consistency_score=quality_scores["consistency"],
            validity_score=quality_scores["validity"],
            uniqueness_score=quality_scores["uniqueness"],
            summary=self._generate_summary(data)
        )
        
        # Handle strict mode
        if self.strict_mode and report.has_critical_issues():
            critical_issues = report.get_critical_issues()
            raise ValueError(f"Critical data quality issues found: {len(critical_issues)} issues")
        
        logger.info(f"Data validation completed. Quality score: {quality_scores['overall']:.2f}")
        return report
    
    def _check_missing_values(self, data: pd.DataFrame) -> None:
        """Check for missing values."""
        missing_stats = data.isnull().sum()
        total_rows = len(data)
        
        for column in data.columns:
            missing_count = missing_stats[column]
            if missing_count > 0:
                missing_pct = (missing_count / total_rows) * 100
                
                if missing_pct > 50:
                    severity = ValidationSeverity.CRITICAL
                    action = "Consider removing column or imputing values"
                elif missing_pct > 20:
                    severity = ValidationSeverity.ERROR
                    action = "Implement imputation strategy"
                elif missing_pct > 5:
                    severity = ValidationSeverity.WARNING
                    action = "Consider imputation or removal"
                else:
                    severity = ValidationSeverity.INFO
                    action = "Minor missing values, consider simple imputation"
                
                self.issues.append(ValidationIssue(
                    rule=ValidationRule.MISSING_VALUES,
                    severity=severity,
                    column=column,
                    message=f"Column '{column}' has {missing_count} missing values ({missing_pct:.1f}%)",
                    details={
                        "missing_count": int(missing_count),
                        "missing_percentage": round(missing_pct, 2),
                        "total_rows": total_rows
                    },
                    affected_rows=int(missing_count),
                    suggested_action=action
                ))
    
    def _check_duplicate_rows(self, data: pd.DataFrame) -> None:
        """Check for duplicate rows."""
        duplicates = data.duplicated()
        duplicate_count = duplicates.sum()
        
        if duplicate_count > 0:
            duplicate_pct = (duplicate_count / len(data)) * 100
            
            if duplicate_pct > 10:
                severity = ValidationSeverity.ERROR
                action = "Remove duplicate rows"
            elif duplicate_pct > 5:
                severity = ValidationSeverity.WARNING
                action = "Consider removing duplicates"
            else:
                severity = ValidationSeverity.INFO
                action = "Minor duplicates, verify if intentional"
            
            self.issues.append(ValidationIssue(
                rule=ValidationRule.DUPLICATE_ROWS,
                severity=severity,
                column=None,
                message=f"Found {duplicate_count} duplicate rows ({duplicate_pct:.1f}%)",
                details={
                    "duplicate_count": int(duplicate_count),
                    "duplicate_percentage": round(duplicate_pct, 2),
                    "duplicate_indices": duplicates[duplicates].index.tolist()
                },
                affected_rows=int(duplicate_count),
                suggested_action=action
            ))
    
    def _check_outliers(self, data: pd.DataFrame) -> None:
        """Check for outliers using IQR method."""
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            if data[column].nunique() < 2:  # Skip constant columns
                continue
                
            Q1 = data[column].quantile(0.25)
            Q3 = data[column].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = data[(data[column] < lower_bound) | (data[column] > upper_bound)]
            outlier_count = len(outliers)
            
            if outlier_count > 0:
                outlier_pct = (outlier_count / len(data)) * 100
                
                if outlier_pct > 10:
                    severity = ValidationSeverity.WARNING
                    action = "Investigate outliers, consider transformation or removal"
                elif outlier_pct > 5:
                    severity = ValidationSeverity.INFO
                    action = "Consider outlier treatment methods"
                else:
                    severity = ValidationSeverity.INFO
                    action = "Minor outliers, monitor but may be valid"
                
                self.issues.append(ValidationIssue(
                    rule=ValidationRule.OUTLIERS,
                    severity=severity,
                    column=column,
                    message=f"Column '{column}' has {outlier_count} outliers ({outlier_pct:.1f}%)",
                    details={
                        "outlier_count": int(outlier_count),
                        "outlier_percentage": round(outlier_pct, 2),
                        "lower_bound": float(lower_bound),
                        "upper_bound": float(upper_bound),
                        "Q1": float(Q1),
                        "Q3": float(Q3),
                        "IQR": float(IQR)
                    },
                    affected_rows=int(outlier_count),
                    suggested_action=action
                ))
    
    def _check_data_types(self, data: pd.DataFrame) -> None:
        """Check data types and suggest improvements."""
        for column in data.columns:
            dtype = data[column].dtype
            
            # Check for potential type improvements
            if dtype == 'object':
                # Check if could be numeric
                try:
                    pd.to_numeric(data[column], errors='raise')
                    self.issues.append(ValidationIssue(
                        rule=ValidationRule.DATA_TYPES,
                        severity=ValidationSeverity.INFO,
                        column=column,
                        message=f"Column '{column}' is object type but could be numeric",
                        details={"current_dtype": str(dtype), "suggested_dtype": "numeric"},
                        suggested_action="Convert to numeric type for better performance"
                    ))
                except (ValueError, TypeError):
                    # Check if could be datetime
                    try:
                        pd.to_datetime(data[column], errors='raise')
                        self.issues.append(ValidationIssue(
                            rule=ValidationRule.DATA_TYPES,
                            severity=ValidationSeverity.INFO,
                            column=column,
                            message=f"Column '{column}' could be datetime type",
                            details={"current_dtype": str(dtype), "suggested_dtype": "datetime"},
                            suggested_action="Convert to datetime type for temporal analysis"
                        ))
                    except (ValueError, TypeError):
                        pass
    
    def _validate_schema(self, data: pd.DataFrame, schema: Dict[str, Any]) -> None:
        """Validate data against schema."""
        # Check required columns
        required_columns = schema.get('required_columns', [])
        missing_columns = set(required_columns) - set(data.columns)
        
        if missing_columns:
            self.issues.append(ValidationIssue(
                rule=ValidationRule.SCHEMA,
                severity=ValidationSeverity.CRITICAL,
                column=None,
                message=f"Missing required columns: {list(missing_columns)}",
                details={"missing_columns": list(missing_columns)},
                suggested_action="Add missing columns to dataset"
            ))
        
        # Check column types
        column_types = schema.get('column_types', {})
        for column, expected_type in column_types.items():
            if column in data.columns:
                actual_type = str(data[column].dtype)
                if actual_type != expected_type:
                    self.issues.append(ValidationIssue(
                        rule=ValidationRule.SCHEMA,
                        severity=ValidationSeverity.ERROR,
                        column=column,
                        message=f"Column '{column}' type mismatch: expected {expected_type}, got {actual_type}",
                        details={"expected_type": expected_type, "actual_type": actual_type},
                        suggested_action=f"Convert column to {expected_type} type"
                    ))
    
    def _check_value_ranges(self, data: pd.DataFrame) -> None:
        """Check for values outside expected ranges."""
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            col_min = data[column].min()
            col_max = data[column].max()
            
            # Check for common range violations
            if column.lower() in ['age', 'years']:
                if col_min < 0 or col_max > 150:
                    self.issues.append(ValidationIssue(
                        rule=ValidationRule.RANGE,
                        severity=ValidationSeverity.ERROR,
                        column=column,
                        message=f"Column '{column}' has values outside expected age range (0-150)",
                        details={"min_value": float(col_min), "max_value": float(col_max)},
                        suggested_action="Verify age values and correct outliers"
                    ))
            
            elif column.lower() in ['percentage', 'percent', 'pct']:
                if col_min < 0 or col_max > 100:
                    self.issues.append(ValidationIssue(
                        rule=ValidationRule.RANGE,
                        severity=ValidationSeverity.ERROR,
                        column=column,
                        message=f"Column '{column}' has values outside percentage range (0-100)",
                        details={"min_value": float(col_min), "max_value": float(col_max)},
                        suggested_action="Verify percentage values are in correct range"
                    ))
    
    def _check_distributions(self, data: pd.DataFrame) -> None:
        """Check data distributions for anomalies."""
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            if data[column].nunique() < 2:  # Skip constant columns
                continue
            
            # Check skewness
            try:
                skewness = stats.skew(data[column].dropna())
                if abs(skewness) > 2:
                    severity = ValidationSeverity.WARNING if abs(skewness) < 3 else ValidationSeverity.ERROR
                    self.issues.append(ValidationIssue(
                        rule=ValidationRule.DISTRIBUTION,
                        severity=severity,
                        column=column,
                        message=f"Column '{column}' is highly skewed (skewness: {skewness:.2f})",
                        details={"skewness": float(skewness)},
                        suggested_action="Consider applying transformation (log, sqrt, etc.)"
                    ))
            except Exception as e:
                logger.warning(f"Could not calculate skewness for column {column}: {e}")
    
    def _check_cardinality(self, data: pd.DataFrame) -> None:
        """Check cardinality of categorical columns."""
        for column in data.columns:
            unique_count = data[column].nunique()
            total_count = len(data)
            
            if unique_count == total_count:
                # High cardinality - every value is unique
                self.issues.append(ValidationIssue(
                    rule=ValidationRule.CARDINALITY,
                    severity=ValidationSeverity.WARNING,
                    column=column,
                    message=f"Column '{column}' has very high cardinality (all values unique)",
                    details={"unique_count": unique_count, "total_count": total_count},
                    suggested_action="Consider if this column should be an identifier or needs grouping"
                ))
            elif unique_count == 1:
                # Constant column
                self.issues.append(ValidationIssue(
                    rule=ValidationRule.CARDINALITY,
                    severity=ValidationSeverity.WARNING,
                    column=column,
                    message=f"Column '{column}' has only one unique value (constant)",
                    details={"unique_count": unique_count, "constant_value": data[column].iloc[0]},
                    suggested_action="Consider removing constant column as it provides no information"
                ))
    
    def _check_uniqueness(self, data: pd.DataFrame) -> None:
        """Check uniqueness constraints."""
        for column in data.columns:
            if column.lower() in ['id', 'identifier', 'key', 'primary_key', 'pk']:
                unique_count = data[column].nunique()
                total_count = len(data)
                
                if unique_count != total_count:
                    self.issues.append(ValidationIssue(
                        rule=ValidationRule.UNIQUENESS,
                        severity=ValidationSeverity.ERROR,
                        column=column,
                        message=f"Column '{column}' should be unique but has duplicates",
                        details={
                            "unique_count": unique_count,
                            "total_count": total_count,
                            "duplicate_count": total_count - unique_count
                        },
                        suggested_action="Ensure identifier columns have unique values"
                    ))
    
    def _check_completeness(self, data: pd.DataFrame) -> None:
        """Check overall data completeness."""
        total_cells = data.shape[0] * data.shape[1]
        missing_cells = data.isnull().sum().sum()
        completeness_pct = ((total_cells - missing_cells) / total_cells) * 100 if total_cells > 0 else 100.0
        
        if completeness_pct < 80:
            severity = ValidationSeverity.CRITICAL
            action = "Dataset has too many missing values - consider data collection improvement"
        elif completeness_pct < 90:
            severity = ValidationSeverity.ERROR
            action = "Implement comprehensive imputation strategy"
        elif completeness_pct < 95:
            severity = ValidationSeverity.WARNING
            action = "Consider imputation for missing values"
        else:
            return  # Good completeness, no issue
        
        self.issues.append(ValidationIssue(
            rule=ValidationRule.COMPLETENESS,
            severity=severity,
            column=None,
            message=f"Dataset completeness is {completeness_pct:.1f}%",
            details={
                "completeness_percentage": round(completeness_pct, 2),
                "total_cells": total_cells,
                "missing_cells": int(missing_cells)
            },
            suggested_action=action
        ))
    
    def _calculate_quality_scores(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate various quality scores."""
        # Completeness score
        total_cells = data.shape[0] * data.shape[1]
        missing_cells = data.isnull().sum().sum()
        completeness = ((total_cells - missing_cells) / total_cells) * 100 if total_cells > 0 else 100.0
        
        # Validity score (based on error/critical issues)
        error_issues = len([i for i in self.issues if i.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]])
        validity = max(0, 100 - (error_issues * 10))
        
        # Consistency score (based on data types and ranges)
        consistency_issues = len([i for i in self.issues if i.rule in [ValidationRule.DATA_TYPES, ValidationRule.RANGE]])
        consistency = max(0, 100 - (consistency_issues * 5))
        
        # Uniqueness score
        duplicate_issues = len([i for i in self.issues if i.rule == ValidationRule.DUPLICATE_ROWS])
        uniqueness = max(0, 100 - (duplicate_issues * 15))
        
        # Overall score (weighted average)
        overall = (completeness * 0.3 + validity * 0.4 + consistency * 0.2 + uniqueness * 0.1)
        
        return {
            "overall": round(overall, 2),
            "completeness": round(completeness, 2),
            "validity": round(validity, 2),
            "consistency": round(consistency, 2),
            "uniqueness": round(uniqueness, 2)
        }
    
    def _generate_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics."""
        summary = {
            "shape": data.shape,
            "memory_usage": data.memory_usage(deep=True).sum(),
            "dtypes": {str(k): int(v) for k, v in data.dtypes.value_counts().to_dict().items()},
            "missing_values_total": data.isnull().sum().sum(),
            "duplicate_rows": data.duplicated().sum(),
            "numeric_columns": len(data.select_dtypes(include=[np.number]).columns),
            "categorical_columns": len(data.select_dtypes(include=['object', 'category']).columns),
            "datetime_columns": len(data.select_dtypes(include=['datetime', 'datetimetz']).columns),
        }
        
        # Add column-wise statistics
        summary["column_stats"] = {}
        for column in data.columns:
            stats = {
                "dtype": str(data[column].dtype),
                "missing_count": data[column].isnull().sum(),
                "unique_count": data[column].nunique(),
            }
            
            if pd.api.types.is_numeric_dtype(data[column]):
                stats.update({
                    "mean": data[column].mean(),
                    "std": data[column].std(),
                    "min": data[column].min(),
                    "max": data[column].max(),
                    "median": data[column].median(),
                })
            
            summary["column_stats"][column] = stats
        
        return summary


# Utility functions
def quick_validate(data: pd.DataFrame, schema: Optional[Dict[str, Any]] = None) -> DataQualityReport:
    """
    Quick validation with default settings.
    
    Args:
        data: DataFrame to validate
        schema: Optional schema for validation
        
    Returns:
        DataQualityReport
    """
    validator = DataValidator(strict_mode=False)
    return validator.validate_dataset(data, schema)


def validate_for_ml(data: pd.DataFrame, target_column: Optional[str] = None) -> DataQualityReport:
    """
    Validate data specifically for ML model training.
    
    Args:
        data: DataFrame to validate
        target_column: Name of target column for ML
        
    Returns:
        DataQualityReport
    """
    validator = DataValidator(strict_mode=False)
    
    # ML-specific validation rules
    ml_rules = [
        ValidationRule.MISSING_VALUES,
        ValidationRule.DUPLICATE_ROWS,
        ValidationRule.OUTLIERS,
        ValidationRule.DATA_TYPES,
        ValidationRule.CARDINALITY,
        ValidationRule.COMPLETENESS
    ]
    
    report = validator.validate_dataset(data, rules=ml_rules)
    
    # Add ML-specific checks
    if target_column and target_column in data.columns:
        # Check target distribution
        target_nunique = data[target_column].nunique()
        target_missing = data[target_column].isnull().sum()
        
        if target_missing > 0:
            validator.issues.append(ValidationIssue(
                rule=ValidationRule.MISSING_VALUES,
                severity=ValidationSeverity.CRITICAL,
                column=target_column,
                message=f"Target column '{target_column}' has {target_missing} missing values",
                details={"missing_count": int(target_missing)},
                suggested_action="Target column must not have missing values"
            ))
        
        # Check for binary classification
        if target_nunique == 2:
            value_counts = data[target_column].value_counts()
            min_class_pct = (value_counts.min() / len(data)) * 100
            if min_class_pct < 15:
                validator.issues.append(ValidationIssue(
                    rule=ValidationRule.DISTRIBUTION,
                    severity=ValidationSeverity.WARNING,
                    column=target_column,
                    message=f"Target column has class imbalance: {min_class_pct:.1f}% minority class",
                    details={"class_distribution": value_counts.to_dict()},
                    suggested_action="Consider class balancing techniques"
                ))
        
        # Create new report with all issues (including ML-specific ones)
        scores = validator._calculate_quality_scores(data)
        summary = validator._generate_summary(data)
        
        report = DataQualityReport(
            total_rows=data.shape[0],
            total_columns=data.shape[1],
            issues=validator.issues,
            quality_score=scores["overall"],
            completeness_score=scores["completeness"],
            consistency_score=scores["consistency"],
            validity_score=scores["validity"],
            uniqueness_score=scores["uniqueness"],
            summary=summary
        )
    
    return report


def generate_data_profile(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate comprehensive data profile.
    
    Args:
        data: DataFrame to profile
        
    Returns:
        Dictionary containing detailed data profile
    """
    profile = {
        "overview": {
            "shape": data.shape,
            "size": data.size,
            "memory_usage": data.memory_usage(deep=True).sum(),
            "dtypes": data.dtypes.value_counts().to_dict()
        },
        "completeness": {
            "total_missing": data.isnull().sum().sum(),
            "completeness_percentage": ((data.size - data.isnull().sum().sum()) / data.size) * 100,
            "missing_by_column": data.isnull().sum().to_dict()
        },
        "duplicates": {
            "duplicate_rows": data.duplicated().sum(),
            "duplicate_percentage": (data.duplicated().sum() / len(data)) * 100
        },
        "columns": {}
    }
    
    # Column-wise profiling
    for column in data.columns:
        col_profile = {
            "dtype": str(data[column].dtype),
            "missing_count": data[column].isnull().sum(),
            "missing_percentage": (data[column].isnull().sum() / len(data)) * 100,
            "unique_count": data[column].nunique(),
            "unique_percentage": (data[column].nunique() / len(data)) * 100
        }
        
        if pd.api.types.is_numeric_dtype(data[column]):
            col_profile.update({
                "mean": data[column].mean(),
                "std": data[column].std(),
                "min": data[column].min(),
                "max": data[column].max(),
                "median": data[column].median(),
                "q25": data[column].quantile(0.25),
                "q75": data[column].quantile(0.75),
                "skewness": stats.skew(data[column].dropna()) if data[column].nunique() > 1 else 0,
                "kurtosis": stats.kurtosis(data[column].dropna()) if data[column].nunique() > 1 else 0
            })
        elif pd.api.types.is_categorical_dtype(data[column]) or data[column].dtype == 'object':
            value_counts = data[column].value_counts()
            col_profile.update({
                "top_values": value_counts.head(10).to_dict(),
                "mode": data[column].mode().iloc[0] if not data[column].mode().empty else None,
                "mode_frequency": value_counts.iloc[0] if len(value_counts) > 0 else 0
            })
        
        profile["columns"][column] = col_profile
    
    return profile 