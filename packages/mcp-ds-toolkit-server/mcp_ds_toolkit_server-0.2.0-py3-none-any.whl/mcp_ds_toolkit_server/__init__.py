"""
MCP Data Science Toolkit - Comprehensive Data Science Platform

This package provides a comprehensive, self-contained data science platform that
integrates with the Model Context Protocol (MCP) for natural language
interaction with ML workflows and data science operations.

The MCP Data Science Toolkit enables data scientists and ML engineers to perform
complete data science workflows through natural language commands, from data
ingestion and preprocessing to model training, evaluation, and deployment.

Key Features:
    - **Data Management**: Comprehensive data loading, validation, cleaning, and preprocessing
    - **Model Training**: Support for multiple ML algorithms with hyperparameter tuning
    - **Experiment Tracking**: Local SQLite-based experiment tracking with versioning
    - **Model Evaluation**: Automated model performance assessment and comparison
    - **Natural Language Interface**: Full MCP integration for conversational data science
    - **Zero Dependencies**: Self-contained platform that works immediately after installation

Architecture:
    The toolkit is organized into focused modules:

    - :mod:`mcp_ds_toolkit.data`: Data management and preprocessing capabilities
    - :mod:`mcp_ds_toolkit.training`: Model training and evaluation functionality
    - :mod:`mcp_ds_toolkit.tracking`: Experiment tracking and versioning
    - :mod:`mcp_ds_toolkit.tools`: MCP tool integrations
    - :mod:`mcp_ds_toolkit.workflows`: End-to-end workflow orchestration
    - :mod:`mcp_ds_toolkit.utils`: Common utilities and configurations

Example:
    Basic usage of the toolkit::

        from mcp_ds_toolkit_server.data import DatasetLoader, DataProfiler
        from mcp_ds_toolkit_server.training import ModelTrainer

        # Load and profile data
        loader = DatasetLoader()
        data = loader.load_csv("data.csv")
        profiler = DataProfiler()
        profile = profiler.profile_dataset(data)

        # Train a model
        trainer = ModelTrainer()
        model = trainer.train_model(data, target_column="target")

Note:
    This package requires Python 3.8+ and uses SQLite for local persistence.
    All machine learning operations use scikit-learn as the core ML library.
"""

# Exceptions
from mcp_ds_toolkit_server.exceptions import FeatureNotImplementedError

# Core data management
from mcp_ds_toolkit_server.data import (
    CleaningConfig,
    CleaningReport,
    ColumnProfile,
    CorrelationAnalysis,
    CrossValidationConfig,
    CrossValidationMethod,
    CustomTransformer,
    DataCleaner,
    DataDriftMetric,
    DataFormat,
    DataProfile,
    DataProfiler,
    DataQualityReport,
    DatasetInfo,
    DatasetLoader,
    DatasetVersion,
    DataSplitter,
    DataType,
    DataValidator,
    DistributionType,
    DriftReport,
    EncodingMethod,
    FeatureImportanceAnalysis,
    ImputationMethod,
    MissingDataConfig,
    MissingDataHandler,
    MissingDataMethod,
    MissingDataReport,
    OutlierAction,
    OutlierConfig,
    OutlierDetector,
    OutlierMethod,
    OutlierReport,
    PipelineConfig,
    PreprocessingConfig,
    PreprocessingPipeline,
    PreprocessingReport,
    ProfileType,
    RemoteConfig,
    RemoteStorageType,
    ScalingMethod,
    SelectionMethod,
    SplitMetrics,
    SplittingConfig,
    SplittingMethod,
    SplittingReport,
    ValidationIssue,
    ValidationRule,
    ValidationSeverity,
    VersioningConfig,
    VersioningStrategy,
)
from mcp_ds_toolkit_server.data.cleaning import (
    analyze_missing_data,
    clean_dataset,
    detect_outliers,
)
from mcp_ds_toolkit_server.data.splitting import (
    create_stratified_splits,
    create_time_series_splits,
    split_dataset,
)

# Utility functions
# Versioning functionality removed - using local storage only

__version__ = "0.1.0"

# Clean, organized exports grouped by functionality
__all__ = [
    # Core data classes
    "DatasetLoader",
    "DatasetInfo",
    "DataType",
    "DataFormat",
    # Data validation
    "DataValidator",
    "DataQualityReport",
    "ValidationIssue",
    "ValidationRule",
    "ValidationSeverity",
    # Data profiling
    "DataProfiler",
    "DataProfile",
    "ColumnProfile",
    "CorrelationAnalysis",
    "FeatureImportanceAnalysis",
    "ProfileType",
    "DistributionType",
    # Data preprocessing
    "PreprocessingPipeline",
    "PreprocessingConfig",
    "PreprocessingReport",
    "CustomTransformer",
    "ScalingMethod",
    "EncodingMethod",
    "SelectionMethod",
    "ImputationMethod",
    # Data cleaning
    "DataCleaner",
    "MissingDataHandler",
    "OutlierDetector",
    "CleaningConfig",
    "MissingDataConfig",
    "OutlierConfig",
    "CleaningReport",
    "MissingDataReport",
    "OutlierReport",
    "MissingDataMethod",
    "OutlierMethod",
    "OutlierAction",
    "analyze_missing_data",
    "detect_outliers",
    "clean_dataset",
    # Data splitting
    "DataSplitter",
    "SplittingConfig",
    "CrossValidationConfig",
    "SplittingReport",
    "SplitMetrics",
    "SplittingMethod",
    "CrossValidationMethod",
    "split_dataset",
    "create_time_series_splits",
    "create_stratified_splits",
    # Data versioning
    "RemoteStorageType",
    "VersioningStrategy",
    "DataDriftMetric",
    "RemoteConfig",
    "VersioningConfig",
    "DatasetVersion",
    "DriftReport",
    "PipelineConfig",
# Versioning functions removed - using local storage only
    # Exceptions
    "FeatureNotImplementedError",
]
