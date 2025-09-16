"""
MCP Data Science Toolkit - Custom Exceptions

This module defines a comprehensive hierarchy of custom exceptions for the
MCP Data Science Toolkit, providing detailed error handling and debugging
capabilities across all toolkit components.

The exception hierarchy is designed to provide granular error categorization
while maintaining a consistent interface for error handling throughout the
data science workflow.

Exception Hierarchy:
    DataScienceError: Base exception for all toolkit errors
    ├── ConfigurationError: Configuration and settings errors
    ├── DataError: Data-related error base class
    │   ├── DataValidationError: Data validation failures
    │   ├── DataLoadingError: Data loading and I/O errors
    │   ├── DatasetNotFoundError: Missing dataset errors
    │   └── DataProcessingError: Data processing failures
    ├── VersionControlError: Version control operation errors
    ├── RemoteStorageError: Remote storage operation errors
    ├── ValidationError: General input validation errors
    ├── FeatureNotImplementedError: Not-yet-implemented features
    ├── TrainingError: Model training failures
    ├── EvaluationError: Model evaluation failures
    └── TrackingError: Experiment tracking errors

Example:
    Handling toolkit exceptions::

        from mcp_ds_toolkit_server.exceptions import DataLoadingError

        try:
            data = loader.load_dataset('data.csv')
        except DataLoadingError as e:
            print(f"Failed to load data: {e.message}")
            print(f"File: {e.file_path}")
            print(f"Details: {e.details}")
"""


class DataScienceError(Exception):
    """Base exception for all MCP Data Science Toolkit errors.

    This is the root exception class for all toolkit-specific errors, providing
    a consistent interface for error handling with additional context information
    including error codes and detailed debugging information.

    Args:
        message (str): Human-readable error description
        error_code (str, optional): Machine-readable error code. Defaults to "GENERAL_ERROR"
        details (dict, optional): Additional error context and debugging information

    Attributes:
        message (str): The error message
        error_code (str): Error categorization code
        details (dict): Additional error details and context

    Example:
        Creating a custom data science error::

            raise DataScienceError(
                "Failed to process dataset",
                error_code="PROCESSING_FAILED",
                details={"dataset_size": 1000, "memory_available": "2GB"}
            )
    """

    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "GENERAL_ERROR"
        self.details = details or {}


# Backwards compatibility alias
MLOpsError = DataScienceError


class ConfigurationError(DataScienceError):
    """Raised when there's an issue with configuration or settings.

    This exception is raised when the toolkit encounters problems with
    configuration files, environment variables, or settings validation.

    Args:
        message (str): Description of the configuration error
        config_key (str, optional): The specific configuration key that caused the error
        details (dict, optional): Additional context about the configuration issue

    Attributes:
        config_key (str): The problematic configuration key
    """

    def __init__(self, message: str, config_key: str = None, details: dict = None):
        super().__init__(message, "CONFIG_ERROR", details)
        self.config_key = config_key


class DataError(DataScienceError):
    """Base exception for data-related errors.

    This is the parent class for all data-related errors in the toolkit,
    including loading, validation, processing, and transformation errors.

    Args:
        message (str): Description of the data error
        data_source (str, optional): The data source that caused the error
        details (dict, optional): Additional context about the data error

    Attributes:
        data_source (str): The problematic data source identifier
    """

    def __init__(self, message: str, data_source: str = None, details: dict = None):
        super().__init__(message, "DATA_ERROR", details)
        self.data_source = data_source


class DataValidationError(DataError):
    """Raised when data validation fails.

    This exception occurs when data doesn't meet expected validation criteria,
    such as schema validation, data type checks, or business rule validation.

    Args:
        message (str): Description of the validation failure
        validation_rule (str, optional): The specific validation rule that failed
        details (dict, optional): Additional validation context and failed values

    Attributes:
        validation_rule (str): The validation rule that was violated
    """

    def __init__(self, message: str, validation_rule: str = None, details: dict = None):
        super().__init__(message, None, details)
        self.error_code = "VALIDATION_ERROR"
        self.validation_rule = validation_rule


class DataLoadingError(DataError):
    """Raised when there's an issue loading data.

    This exception occurs during data loading operations from various sources
    including files, databases, APIs, or remote storage systems.

    Args:
        message (str): Description of the loading failure
        file_path (str, optional): The file path that failed to load
        details (dict, optional): Additional context about the loading error

    Attributes:
        file_path (str): The problematic file path or data source location
    """

    def __init__(self, message: str, file_path: str = None, details: dict = None):
        super().__init__(message, None, details)
        self.error_code = "LOADING_ERROR"
        self.file_path = file_path


class DatasetNotFoundError(DataError):
    """Raised when a requested dataset doesn't exist.

    This exception is raised when attempting to access a dataset that
    is not available in the expected location or registry.

    Args:
        message (str): Description of the missing dataset error
        dataset_name (str, optional): The name of the missing dataset
        details (dict, optional): Additional context about the search locations

    Attributes:
        dataset_name (str): The name of the dataset that couldn't be found
    """

    def __init__(self, message: str, dataset_name: str = None, details: dict = None):
        super().__init__(message, None, details)
        self.error_code = "DATASET_NOT_FOUND"
        self.dataset_name = dataset_name


class DataProcessingError(DataError):
    """Raised when data processing fails.

    This exception occurs during data transformation, cleaning, preprocessing,
    or any other data manipulation operations.

    Args:
        message (str): Description of the processing failure
        processing_step (str, optional): The specific processing step that failed
        details (dict, optional): Additional context about the processing error

    Attributes:
        processing_step (str): The processing step that encountered the error
    """

    def __init__(self, message: str, processing_step: str = None, details: dict = None):
        super().__init__(message, None, details)
        self.error_code = "PROCESSING_ERROR"
        self.processing_step = processing_step


class VersionControlError(DataScienceError):
    """Raised when there's an issue with version control operations.

    This exception occurs during data versioning, model versioning,
    or experiment versioning operations.

    Args:
        message (str): Description of the version control error
        operation (str, optional): The specific version control operation that failed
        details (dict, optional): Additional context about the version control error

    Attributes:
        operation (str): The version control operation that encountered the error
    """

    def __init__(self, message: str, operation: str = None, details: dict = None):
        super().__init__(message, "VERSION_CONTROL_ERROR", details)
        self.operation = operation




class RemoteStorageError(DataScienceError):
    """Raised when remote storage operations fail.

    This exception occurs during operations with remote storage systems
    such as cloud storage, distributed file systems, or remote databases.

    Args:
        message (str): Description of the storage operation failure
        storage_type (str, optional): The type of storage system that failed
        details (dict, optional): Additional context about the storage error

    Attributes:
        storage_type (str): The storage system type that encountered the error
    """

    def __init__(self, message: str, storage_type: str = None, details: dict = None):
        super().__init__(message, "STORAGE_ERROR", details)
        self.storage_type = storage_type


class ValidationError(DataScienceError):
    """Raised when input validation fails.

    This is a general-purpose validation exception for input parameter
    validation, API argument validation, and other non-data validation errors.

    Args:
        message (str): Description of the validation failure
        field (str, optional): The specific field or parameter that failed validation
        details (dict, optional): Additional validation context and constraints

    Attributes:
        field (str): The field or parameter that failed validation
    """

    def __init__(self, message: str, field: str = None, details: dict = None):
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field


class FeatureNotImplementedError(DataScienceError):
    """Raised when a feature is not yet implemented.

    This exception is used to indicate functionality that is planned
    but not yet available in the current toolkit version.

    Args:
        message (str): Description of the unimplemented feature
        feature (str, optional): The specific feature that is not implemented
        details (dict, optional): Additional context about the feature

    Attributes:
        feature (str): The feature name that is not yet implemented
    """

    def __init__(self, message: str, feature: str = None, details: dict = None):
        super().__init__(message, "FEATURE_NOT_IMPLEMENTED", details)
        self.feature = feature


class TrainingError(DataScienceError):
    """Raised when model training fails.

    This exception occurs during machine learning model training operations,
    including hyperparameter optimization, model fitting, and validation.

    Args:
        message (str): Description of the training failure
        model_type (str, optional): The type of model that failed to train
        details (dict, optional): Additional context about the training error

    Attributes:
        model_type (str): The model type that encountered the training error
    """

    def __init__(self, message: str, model_type: str = None, details: dict = None):
        super().__init__(message, "TRAINING_ERROR", details)
        self.model_type = model_type


class EvaluationError(DataScienceError):
    """Raised when model evaluation fails.

    This exception occurs during model performance evaluation, including
    metric calculation, cross-validation, and model comparison operations.

    Args:
        message (str): Description of the evaluation failure
        evaluation_type (str, optional): The type of evaluation that failed
        details (dict, optional): Additional context about the evaluation error

    Attributes:
        evaluation_type (str): The evaluation type that encountered the error
    """

    def __init__(self, message: str, evaluation_type: str = None, details: dict = None):
        super().__init__(message, "EVALUATION_ERROR", details)
        self.evaluation_type = evaluation_type


class TrackingError(DataScienceError):
    """Raised when experiment tracking fails.

    This exception occurs during experiment logging, metric tracking,
    artifact storage, or other experiment management operations.

    Args:
        message (str): Description of the tracking failure
        tracking_operation (str, optional): The specific tracking operation that failed
        details (dict, optional): Additional context about the tracking error

    Attributes:
        tracking_operation (str): The tracking operation that encountered the error
    """

    def __init__(
        self, message: str, tracking_operation: str = None, details: dict = None
    ):
        super().__init__(message, "TRACKING_ERROR", details)
        self.tracking_operation = tracking_operation
