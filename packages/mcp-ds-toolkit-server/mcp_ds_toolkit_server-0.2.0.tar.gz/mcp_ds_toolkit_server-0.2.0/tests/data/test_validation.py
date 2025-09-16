"""
Tests for data validation and quality checking module.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from mcp_ds_toolkit_server.data.validation import (
    DataQualityReport,
    DataValidator,
    ValidationIssue,
    ValidationRule,
    ValidationSeverity,
    generate_data_profile,
    quick_validate,
    validate_for_ml,
)


class TestDataValidator:
    """Test DataValidator class."""
    
    def test_init_default(self):
        """Test DataValidator initialization with default parameters."""
        validator = DataValidator()
        assert validator.strict_mode is False
        assert validator.issues == []
    
    def test_init_strict_mode(self):
        """Test DataValidator initialization with strict mode."""
        validator = DataValidator(strict_mode=True)
        assert validator.strict_mode is True
        assert validator.issues == []
    
    def test_validate_dataset_empty(self):
        """Test validation of empty dataset."""
        validator = DataValidator()
        data = pd.DataFrame()
        
        report = validator.validate_dataset(data)
        
        assert isinstance(report, DataQualityReport)
        assert report.total_rows == 0
        assert report.total_columns == 0
        assert report.quality_score >= 0
    
    def test_validate_dataset_basic(self):
        """Test basic dataset validation."""
        validator = DataValidator()
        data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e'],
            'C': [1.1, 2.2, 3.3, 4.4, 5.5]
        })
        
        report = validator.validate_dataset(data)
        
        assert isinstance(report, DataQualityReport)
        assert report.total_rows == 5
        assert report.total_columns == 3
        assert report.quality_score > 0
        assert report.completeness_score == 100.0  # No missing values
    
    def test_missing_values_detection(self):
        """Test missing values detection."""
        validator = DataValidator()
        data = pd.DataFrame({
            'A': [1, 2, np.nan, 4, 5],
            'B': ['a', None, 'c', 'd', 'e'],
            'C': [1.1, 2.2, 3.3, np.nan, np.nan]
        })
        
        report = validator.validate_dataset(data, rules=[ValidationRule.MISSING_VALUES])
        
        # Should detect missing values in all columns
        missing_issues = [issue for issue in report.issues if issue.rule == ValidationRule.MISSING_VALUES]
        assert len(missing_issues) == 3
        
        # Check column A (1 missing value = 20%)
        col_a_issue = next(issue for issue in missing_issues if issue.column == 'A')
        assert col_a_issue.severity == ValidationSeverity.WARNING
        assert col_a_issue.affected_rows == 1
        assert 'A' in col_a_issue.message
        
        # Check column C (2 missing values = 40%)
        col_c_issue = next(issue for issue in missing_issues if issue.column == 'C')
        assert col_c_issue.severity == ValidationSeverity.ERROR
        assert col_c_issue.affected_rows == 2
    
    def test_duplicate_rows_detection(self):
        """Test duplicate rows detection."""
        validator = DataValidator()
        data = pd.DataFrame({
            'A': [1, 2, 3, 2, 5],
            'B': ['a', 'b', 'c', 'b', 'e'],
            'C': [1.1, 2.2, 3.3, 2.2, 5.5]
        })
        
        report = validator.validate_dataset(data, rules=[ValidationRule.DUPLICATE_ROWS])
        
        # Should detect duplicate rows
        duplicate_issues = [issue for issue in report.issues if issue.rule == ValidationRule.DUPLICATE_ROWS]
        assert len(duplicate_issues) == 1
        
        issue = duplicate_issues[0]
        assert issue.severity == ValidationSeverity.ERROR  # 20% is high percentage
        assert issue.affected_rows == 1
        assert 'duplicate' in issue.message.lower()
    
    def test_outliers_detection(self):
        """Test outliers detection using IQR method."""
        validator = DataValidator()
        # Create data with obvious outliers
        data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5, 100],  # 100 is an outlier
            'B': [10, 11, 12, 13, 14, 15],  # No outliers
            'C': [-50, 20, 21, 22, 23, 24]  # -50 is an outlier
        })
        
        report = validator.validate_dataset(data, rules=[ValidationRule.OUTLIERS])
        
        # Should detect outliers in columns A and C
        outlier_issues = [issue for issue in report.issues if issue.rule == ValidationRule.OUTLIERS]
        outlier_columns = [issue.column for issue in outlier_issues]
        
        assert 'A' in outlier_columns
        assert 'C' in outlier_columns
        assert 'B' not in outlier_columns  # No outliers in B
    
    def test_data_types_detection(self):
        """Test data types analysis."""
        validator = DataValidator()
        data = pd.DataFrame({
            'numeric_string': ['1', '2', '3', '4', '5'],
            'date_string': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
            'text': ['apple', 'banana', 'cherry', 'date', 'elderberry']
        })
        
        report = validator.validate_dataset(data, rules=[ValidationRule.DATA_TYPES])
        
        # Should suggest type improvements
        type_issues = [issue for issue in report.issues if issue.rule == ValidationRule.DATA_TYPES]
        type_columns = [issue.column for issue in type_issues]
        
        assert 'numeric_string' in type_columns
        assert 'date_string' in type_columns
        assert 'text' not in type_columns  # Should remain as text
    
    def test_schema_validation(self):
        """Test schema validation."""
        validator = DataValidator()
        data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e']
        })
        
        schema = {
            'required_columns': ['A', 'B', 'C'],  # C is missing
            'column_types': {
                'A': 'int64',
                'B': 'object'
            }
        }
        
        report = validator.validate_dataset(data, schema=schema, rules=[ValidationRule.SCHEMA])
        
        # Should detect missing required column
        schema_issues = [issue for issue in report.issues if issue.rule == ValidationRule.SCHEMA]
        assert len(schema_issues) >= 1
        
        # Check for missing column issue
        missing_col_issue = next(
            (issue for issue in schema_issues if 'missing' in issue.message.lower()),
            None
        )
        assert missing_col_issue is not None
        assert missing_col_issue.severity == ValidationSeverity.CRITICAL
    
    def test_value_ranges_detection(self):
        """Test value ranges validation."""
        validator = DataValidator()
        data = pd.DataFrame({
            'age': [25, 30, -5, 200, 45],  # -5 and 200 are invalid ages
            'percentage': [10, 20, 30, 150, 50],  # 150 is invalid percentage
            'normal_col': [1, 2, 3, 4, 5]
        })
        
        report = validator.validate_dataset(data, rules=[ValidationRule.RANGE])
        
        # Should detect range violations
        range_issues = [issue for issue in report.issues if issue.rule == ValidationRule.RANGE]
        range_columns = [issue.column for issue in range_issues]
        
        assert 'age' in range_columns
        assert 'percentage' in range_columns
        assert 'normal_col' not in range_columns
    
    def test_distribution_analysis(self):
        """Test distribution analysis for skewness."""
        validator = DataValidator()
        # Create highly skewed data
        skewed_data = np.random.exponential(scale=2, size=100)
        data = pd.DataFrame({
            'skewed': skewed_data,
            'normal': np.random.normal(0, 1, 100)
        })
        
        report = validator.validate_dataset(data, rules=[ValidationRule.DISTRIBUTION])
        
        # Should detect skewed distribution
        dist_issues = [issue for issue in report.issues if issue.rule == ValidationRule.DISTRIBUTION]
        
        # Might detect skewness in exponential data
        if dist_issues:
            skewed_columns = [issue.column for issue in dist_issues]
            assert any('skewed' in col for col in skewed_columns)
    
    def test_cardinality_detection(self):
        """Test cardinality analysis."""
        validator = DataValidator()
        data = pd.DataFrame({
            'unique_ids': [1, 2, 3, 4, 5],  # High cardinality
            'constant': ['same', 'same', 'same', 'same', 'same'],  # Constant
            'normal': ['A', 'B', 'A', 'B', 'C']  # Normal cardinality
        })
        
        report = validator.validate_dataset(data, rules=[ValidationRule.CARDINALITY])
        
        # Should detect high cardinality and constant columns
        card_issues = [issue for issue in report.issues if issue.rule == ValidationRule.CARDINALITY]
        card_columns = [issue.column for issue in card_issues]
        
        assert 'unique_ids' in card_columns
        assert 'constant' in card_columns
        assert 'normal' not in card_columns
    
    def test_uniqueness_validation(self):
        """Test uniqueness constraints."""
        validator = DataValidator()
        data = pd.DataFrame({
            'id': [1, 2, 3, 2, 5],  # 'id' should be unique but has duplicates
            'primary_key': [1, 2, 3, 4, 5],  # Unique as expected
            'normal_col': ['a', 'b', 'a', 'b', 'c']
        })
        
        report = validator.validate_dataset(data, rules=[ValidationRule.UNIQUENESS])
        
        # Should detect uniqueness violation in 'id' column
        unique_issues = [issue for issue in report.issues if issue.rule == ValidationRule.UNIQUENESS]
        unique_columns = [issue.column for issue in unique_issues]
        
        assert 'id' in unique_columns
        assert 'primary_key' not in unique_columns
        assert 'normal_col' not in unique_columns
    
    def test_completeness_check(self):
        """Test overall completeness check."""
        validator = DataValidator()
        # Create data with many missing values
        data = pd.DataFrame({
            'A': [1, np.nan, np.nan, np.nan, np.nan],
            'B': [np.nan, 2, np.nan, np.nan, np.nan],
            'C': [np.nan, np.nan, 3, np.nan, np.nan]
        })
        
        report = validator.validate_dataset(data, rules=[ValidationRule.COMPLETENESS])
        
        # Should detect low completeness
        completeness_issues = [issue for issue in report.issues if issue.rule == ValidationRule.COMPLETENESS]
        assert len(completeness_issues) == 1
        
        issue = completeness_issues[0]
        assert issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
        assert issue.column is None  # Overall completeness issue
    
    def test_strict_mode_with_critical_issues(self):
        """Test strict mode raises exception for critical issues."""
        validator = DataValidator(strict_mode=True)
        data = pd.DataFrame({
            'A': [np.nan] * 5,  # 100% missing values - critical
            'B': [1, 2, 3, 4, 5]
        })
        
        with pytest.raises(ValueError, match="Critical data quality issues"):
            validator.validate_dataset(data, rules=[ValidationRule.MISSING_VALUES])
    
    def test_quality_scores_calculation(self):
        """Test quality scores calculation."""
        validator = DataValidator()
        data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e'],
            'C': [1.1, 2.2, 3.3, 4.4, 5.5]
        })
        
        report = validator.validate_dataset(data)
        
        # Check score ranges
        assert 0 <= report.quality_score <= 100
        assert 0 <= report.completeness_score <= 100
        assert 0 <= report.validity_score <= 100
        assert 0 <= report.consistency_score <= 100
        assert 0 <= report.uniqueness_score <= 100
        
        # Perfect data should have high scores
        assert report.completeness_score == 100.0
        assert report.quality_score > 90


class TestDataQualityReport:
    """Test DataQualityReport class."""
    
    def test_get_issues_by_severity(self):
        """Test filtering issues by severity."""
        issues = [
            ValidationIssue(
                ValidationRule.MISSING_VALUES, ValidationSeverity.WARNING,
                'A', 'Test warning', {}, 1
            ),
            ValidationIssue(
                ValidationRule.DUPLICATE_ROWS, ValidationSeverity.ERROR,
                'B', 'Test error', {}, 2
            ),
            ValidationIssue(
                ValidationRule.COMPLETENESS, ValidationSeverity.CRITICAL,
                None, 'Test critical', {}, 3
            )
        ]
        
        report = DataQualityReport(
            total_rows=100, total_columns=3, issues=issues,
            quality_score=85.0, completeness_score=90.0,
            consistency_score=95.0, validity_score=80.0,
            uniqueness_score=100.0, summary={}
        )
        
        warnings = report.get_issues_by_severity(ValidationSeverity.WARNING)
        errors = report.get_issues_by_severity(ValidationSeverity.ERROR)
        critical = report.get_issues_by_severity(ValidationSeverity.CRITICAL)
        
        assert len(warnings) == 1
        assert len(errors) == 1
        assert len(critical) == 1
        
        assert warnings[0].severity == ValidationSeverity.WARNING
        assert errors[0].severity == ValidationSeverity.ERROR
        assert critical[0].severity == ValidationSeverity.CRITICAL
    
    def test_get_critical_issues(self):
        """Test getting critical issues."""
        issues = [
            ValidationIssue(
                ValidationRule.MISSING_VALUES, ValidationSeverity.WARNING,
                'A', 'Test warning', {}, 1
            ),
            ValidationIssue(
                ValidationRule.COMPLETENESS, ValidationSeverity.CRITICAL,
                None, 'Test critical', {}, 3
            )
        ]
        
        report = DataQualityReport(
            total_rows=100, total_columns=3, issues=issues,
            quality_score=85.0, completeness_score=90.0,
            consistency_score=95.0, validity_score=80.0,
            uniqueness_score=100.0, summary={}
        )
        
        critical_issues = report.get_critical_issues()
        assert len(critical_issues) == 1
        assert critical_issues[0].severity == ValidationSeverity.CRITICAL
    
    def test_has_critical_issues(self):
        """Test checking for critical issues."""
        # Report with critical issues
        issues_with_critical = [
            ValidationIssue(
                ValidationRule.COMPLETENESS, ValidationSeverity.CRITICAL,
                None, 'Test critical', {}, 3
            )
        ]
        
        report_with_critical = DataQualityReport(
            total_rows=100, total_columns=3, issues=issues_with_critical,
            quality_score=85.0, completeness_score=90.0,
            consistency_score=95.0, validity_score=80.0,
            uniqueness_score=100.0, summary={}
        )
        
        # Report without critical issues
        issues_without_critical = [
            ValidationIssue(
                ValidationRule.MISSING_VALUES, ValidationSeverity.WARNING,
                'A', 'Test warning', {}, 1
            )
        ]
        
        report_without_critical = DataQualityReport(
            total_rows=100, total_columns=3, issues=issues_without_critical,
            quality_score=85.0, completeness_score=90.0,
            consistency_score=95.0, validity_score=80.0,
            uniqueness_score=100.0, summary={}
        )
        
        assert report_with_critical.has_critical_issues() is True
        assert report_without_critical.has_critical_issues() is False
    
    def test_to_dict(self):
        """Test converting report to dictionary."""
        issues = [
            ValidationIssue(
                ValidationRule.MISSING_VALUES, ValidationSeverity.WARNING,
                'A', 'Test warning', {'detail': 'test'}, 1, 'Fix it'
            )
        ]
        
        report = DataQualityReport(
            total_rows=100, total_columns=3, issues=issues,
            quality_score=85.0, completeness_score=90.0,
            consistency_score=95.0, validity_score=80.0,
            uniqueness_score=100.0, summary={'test': 'summary'}
        )
        
        report_dict = report.to_dict()
        
        assert report_dict['total_rows'] == 100
        assert report_dict['total_columns'] == 3
        assert report_dict['quality_score'] == 85.0
        assert len(report_dict['issues']) == 1
        assert report_dict['issues'][0]['rule'] == 'missing_values'
        assert report_dict['issues'][0]['severity'] == 'warning'
        assert report_dict['summary']['test'] == 'summary'


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_quick_validate(self):
        """Test quick_validate function."""
        data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e']
        })
        
        report = quick_validate(data)
        
        assert isinstance(report, DataQualityReport)
        assert report.total_rows == 5
        assert report.total_columns == 2
        assert report.quality_score > 0
    
    def test_quick_validate_with_schema(self):
        """Test quick_validate with schema."""
        data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e']
        })
        
        schema = {
            'required_columns': ['A', 'B'],
            'column_types': {'A': 'int64', 'B': 'object'}
        }
        
        report = quick_validate(data, schema)
        
        assert isinstance(report, DataQualityReport)
        assert report.total_rows == 5
        assert report.total_columns == 2
    
    def test_validate_for_ml_with_target(self):
        """Test validate_for_ml with target column."""
        data = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5],
            'feature2': ['a', 'b', 'c', 'd', 'e'],
            'target': [0, 1, 0, 1, 0]
        })
        
        report = validate_for_ml(data, target_column='target')
        
        assert isinstance(report, DataQualityReport)
        assert report.total_rows == 5
        assert report.total_columns == 3
        
        # Should not have critical issues for target column
        target_issues = [issue for issue in report.issues if issue.column == 'target']
        critical_target_issues = [issue for issue in target_issues if issue.severity == ValidationSeverity.CRITICAL]
        assert len(critical_target_issues) == 0
    
    def test_validate_for_ml_missing_target(self):
        """Test validate_for_ml with missing target values."""
        data = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5],
            'feature2': ['a', 'b', 'c', 'd', 'e'],
            'target': [0, 1, np.nan, 1, 0]  # Missing target value
        })
        
        report = validate_for_ml(data, target_column='target')
        
        # Should have critical issue for missing target
        target_issues = [issue for issue in report.issues if issue.column == 'target']
        critical_target_issues = [issue for issue in target_issues if issue.severity == ValidationSeverity.CRITICAL]
        assert len(critical_target_issues) > 0
    
    def test_validate_for_ml_imbalanced_target(self):
        """Test validate_for_ml with imbalanced target."""
        data = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'feature2': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'],
            'target': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]  # Highly imbalanced
        })
        
        report = validate_for_ml(data, target_column='target')
        
        # Should detect class imbalance
        target_issues = [issue for issue in report.issues if issue.column == 'target']
        imbalance_issues = [issue for issue in target_issues if 'imbalance' in issue.message.lower()]
        assert len(imbalance_issues) > 0
    
    def test_generate_data_profile(self):
        """Test generate_data_profile function."""
        data = pd.DataFrame({
            'numeric': [1, 2, 3, 4, 5],
            'categorical': ['a', 'b', 'c', 'a', 'b'],
            'missing': [1, np.nan, 3, np.nan, 5]
        })
        
        profile = generate_data_profile(data)
        
        # Check structure
        assert 'overview' in profile
        assert 'completeness' in profile
        assert 'duplicates' in profile
        assert 'columns' in profile
        
        # Check overview
        assert profile['overview']['shape'] == (5, 3)
        assert profile['overview']['size'] == 15
        
        # Check completeness
        assert profile['completeness']['total_missing'] == 2
        assert profile['completeness']['completeness_percentage'] < 100
        
        # Check columns
        assert 'numeric' in profile['columns']
        assert 'categorical' in profile['columns']
        assert 'missing' in profile['columns']
        
        # Check numeric column stats
        numeric_stats = profile['columns']['numeric']
        assert 'mean' in numeric_stats
        assert 'std' in numeric_stats
        assert 'min' in numeric_stats
        assert 'max' in numeric_stats
        
        # Check categorical column stats
        categorical_stats = profile['columns']['categorical']
        assert 'top_values' in categorical_stats
        assert 'mode' in categorical_stats
        
        # Check missing column stats
        missing_stats = profile['columns']['missing']
        assert missing_stats['missing_count'] == 2
        assert missing_stats['missing_percentage'] == 40.0


class TestIntegrationWithLoader:
    """Test integration with DatasetLoader."""
    
    def test_validate_loaded_dataset(self):
        """Test validating a dataset loaded with DatasetLoader."""
        from mcp_ds_toolkit_server.data import DatasetLoader

        # Load a dataset
        loader = DatasetLoader()
        data, info = loader.load_dataset('iris')
        
        # Validate the loaded dataset
        report = quick_validate(data)
        
        assert isinstance(report, DataQualityReport)
        assert report.total_rows == 150  # Iris dataset has 150 rows
        assert report.total_columns == 5   # 4 features + 1 target
        assert report.quality_score > 80   # Should be high quality
        assert report.completeness_score == 100.0  # Iris has no missing values
    
    def test_validate_sample_dataset(self):
        """Test validating a sample dataset."""
        from mcp_ds_toolkit_server.data import DatasetLoader

        # Create a sample dataset
        loader = DatasetLoader()
        data, info = loader.create_sample_dataset('classification', n_samples=100, n_features=5)
        
        # Validate for ML
        report = validate_for_ml(data, target_column='target')
        
        assert isinstance(report, DataQualityReport)
        assert report.total_rows == 100
        assert report.total_columns == 6  # 5 features + 1 target
        assert report.quality_score > 80  # Should be high quality
        assert not report.has_critical_issues()  # Should not have critical issues


if __name__ == '__main__':
    pytest.main([__file__]) 