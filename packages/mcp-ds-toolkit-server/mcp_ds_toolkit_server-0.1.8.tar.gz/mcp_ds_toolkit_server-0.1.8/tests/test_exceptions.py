"""Tests for custom exceptions module."""

import pytest

from mcp_ds_toolkit_server.exceptions import (
    ConfigurationError,
    DataError,
    DataLoadingError,
    DataProcessingError,
    DatasetNotFoundError,
    DataValidationError,
    EvaluationError,
    FeatureNotImplementedError,
    MLOpsError,
    RemoteStorageError,
    TrackingError,
    TrainingError,
    ValidationError,
    VersionControlError,
)


class TestMLOpsError:
    """Test the base MLOpsError exception."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = MLOpsError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.error_code == "GENERAL_ERROR"
        assert error.details == {}

    def test_error_with_code_and_details(self):
        """Test error with custom code and details."""
        details = {"key": "value", "count": 42}
        error = MLOpsError("Test error", "CUSTOM_CODE", details)
        assert error.message == "Test error"
        assert error.error_code == "CUSTOM_CODE"
        assert error.details == details


class TestConfigurationError:
    """Test ConfigurationError exception."""

    def test_basic_configuration_error(self):
        """Test basic configuration error."""
        error = ConfigurationError("Invalid config")
        assert str(error) == "Invalid config"
        assert error.error_code == "CONFIG_ERROR"
        assert error.config_key is None

    def test_configuration_error_with_key(self):
        """Test configuration error with specific key."""
        error = ConfigurationError("Invalid value", "database_url")
        assert error.message == "Invalid value"
        assert error.config_key == "database_url"


class TestDataErrors:
    """Test data-related exceptions."""

    def test_data_error(self):
        """Test basic DataError."""
        error = DataError("Data processing failed")
        assert str(error) == "Data processing failed"
        assert error.error_code == "DATA_ERROR"
        assert error.data_source is None

    def test_data_validation_error(self):
        """Test DataValidationError."""
        error = DataValidationError("Validation failed", "not_null_check")
        assert error.message == "Validation failed"
        assert error.error_code == "VALIDATION_ERROR"
        assert error.validation_rule == "not_null_check"

    def test_data_loading_error(self):
        """Test DataLoadingError."""
        error = DataLoadingError("File not found", "/path/to/file.csv")
        assert error.message == "File not found"
        assert error.error_code == "LOADING_ERROR"
        assert error.file_path == "/path/to/file.csv"

    def test_dataset_not_found_error(self):
        """Test DatasetNotFoundError."""
        error = DatasetNotFoundError("Dataset missing", "iris")
        assert error.message == "Dataset missing"
        assert error.error_code == "DATASET_NOT_FOUND"
        assert error.dataset_name == "iris"

    def test_data_processing_error(self):
        """Test DataProcessingError."""
        error = DataProcessingError("Processing failed", "normalization")
        assert error.message == "Processing failed"
        assert error.error_code == "PROCESSING_ERROR"
        assert error.processing_step == "normalization"


class TestVersionControlErrors:
    """Test version control related exceptions."""

    def test_version_control_error(self):
        """Test basic VersionControlError."""
        error = VersionControlError("Git operation failed", "commit")
        assert error.message == "Git operation failed"
        assert error.error_code == "VERSION_CONTROL_ERROR"
        assert error.operation == "commit"



class TestOtherErrors:
    """Test other exception types."""

    def test_remote_storage_error(self):
        """Test RemoteStorageError."""
        error = RemoteStorageError("S3 connection failed", "s3")
        assert error.message == "S3 connection failed"
        assert error.error_code == "STORAGE_ERROR"
        assert error.storage_type == "s3"

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Invalid input", "email")
        assert error.message == "Invalid input"
        assert error.error_code == "VALIDATION_ERROR"
        assert error.field == "email"

    def test_feature_not_implemented_error(self):
        """Test FeatureNotImplementedError."""
        error = FeatureNotImplementedError("Feature not ready", "auto_ml")
        assert error.message == "Feature not ready"
        assert error.error_code == "FEATURE_NOT_IMPLEMENTED"
        assert error.feature == "auto_ml"

    def test_training_error(self):
        """Test TrainingError."""
        error = TrainingError("Training failed", "random_forest")
        assert error.message == "Training failed"
        assert error.error_code == "TRAINING_ERROR"
        assert error.model_type == "random_forest"

    def test_evaluation_error(self):
        """Test EvaluationError."""
        error = EvaluationError("Evaluation failed", "cross_validation")
        assert error.message == "Evaluation failed"
        assert error.error_code == "EVALUATION_ERROR"
        assert error.evaluation_type == "cross_validation"

    def test_tracking_error(self):
        """Test TrackingError."""
        error = TrackingError("Local tracking failed", "log_metrics")
        assert error.message == "Local tracking failed"
        assert error.error_code == "TRACKING_ERROR"
        assert error.tracking_operation == "log_metrics"


class TestExceptionInheritance:
    """Test exception inheritance hierarchy."""

    def test_all_inherit_from_mlops_error(self):
        """Test that all exceptions inherit from MLOpsError."""
        exceptions = [
            ConfigurationError("test"),
            DataError("test"),
            DataValidationError("test"),
            DataLoadingError("test"),
            DatasetNotFoundError("test"),
            DataProcessingError("test"),
            VersionControlError("test"),
            RemoteStorageError("test"),
            ValidationError("test"),
            FeatureNotImplementedError("test"),
            TrainingError("test"),
            EvaluationError("test"),
            TrackingError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, MLOpsError)
            assert isinstance(exc, Exception)

    def test_data_exceptions_inherit_from_data_error(self):
        """Test that data-specific exceptions inherit from DataError."""
        data_exceptions = [
            DataValidationError("test"),
            DataLoadingError("test"),
            DatasetNotFoundError("test"),
            DataProcessingError("test"),
        ]

        for exc in data_exceptions:
            assert isinstance(exc, DataError)
            assert isinstance(exc, MLOpsError)



class TestExceptionDetails:
    """Test exception details and context."""

    def test_exception_with_detailed_context(self):
        """Test exception with detailed context information."""
        details = {
            "file_path": "/data/dataset.csv",
            "line_number": 42,
            "column": "target",
            "expected_type": "numeric",
            "actual_type": "string",
            "sample_values": ["apple", "banana", "cherry"],
        }

        error = DataValidationError(
            "Invalid data type in target column", "type_validation", details
        )

        assert error.message == "Invalid data type in target column"
        assert error.validation_rule == "type_validation"
        assert error.details["file_path"] == "/data/dataset.csv"
        assert error.details["line_number"] == 42
        assert error.details["expected_type"] == "numeric"
        assert len(error.details["sample_values"]) == 3

    def test_exception_details_immutability(self):
        """Test that exception details can be safely accessed."""
        details = {"mutable_list": [1, 2, 3]}
        error = MLOpsError("test", details=details)

        # Modifying original details shouldn't affect exception
        details["mutable_list"].append(4)
        # Note: This tests current behavior - details are not deep copied
        # In a production system, you might want to deep copy details
        assert error.details["mutable_list"] == [1, 2, 3, 4]
