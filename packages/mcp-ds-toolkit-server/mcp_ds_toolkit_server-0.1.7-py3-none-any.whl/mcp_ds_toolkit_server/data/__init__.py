"""
Data Management Module

This module provides comprehensive data management capabilities for
machine learning workflows, including dataset loading, validation, profiling,
preprocessing, cleaning, splitting, and visualization.
"""

import logging
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

# Suppress common warnings
warnings.filterwarnings("ignore", category=UserWarning, module='sklearn')
warnings.filterwarnings("ignore", category=FutureWarning, module='pandas')

logger = logging.getLogger(__name__)

from mcp_ds_toolkit_server.data.cleaning import (
    CleaningConfig,
    CleaningReport,
    DataCleaner,
    MissingDataConfig,
    MissingDataHandler,
    MissingDataMethod,
    MissingDataReport,
    OutlierAction,
    OutlierConfig,
    OutlierDetector,
    OutlierMethod,
    OutlierReport,
    analyze_missing_data,
    clean_dataset,
    detect_outliers,
)
from mcp_ds_toolkit_server.data.loader import DataFormat, DatasetInfo, DatasetLoader, DataType

from mcp_ds_toolkit_server.data.model_evaluation import (
    CrossValidationConfig,
    CrossValidationMethod,
    HyperparameterTuningConfig,
    HyperparameterTuningMethod,
    ModelEvaluator,
    ModelPerformanceReport,
    TaskType,
    get_default_param_grids,
    quick_model_comparison,
)

from mcp_ds_toolkit_server.data.preprocessing import (
    CustomTransformer,
    EncodingMethod,
    ImputationMethod,
    PreprocessingConfig,
    PreprocessingPipeline,
    PreprocessingReport,
    ScalingMethod,
    SelectionMethod,
)
from mcp_ds_toolkit_server.data.profiling import (
    ColumnProfile,
    CorrelationAnalysis,
    DataProfile,
    DataProfiler,
    DistributionType,
    FeatureImportanceAnalysis,
    ProfileType,
)
from mcp_ds_toolkit_server.data.splitting import (
    CrossValidationConfig,
    CrossValidationMethod,
    DataSplitter,
    SplitMetrics,
    SplittingConfig,
    SplittingMethod,
    SplittingReport,
    create_stratified_splits,
    create_time_series_splits,
    split_dataset,
)
from mcp_ds_toolkit_server.data.validation import (
    DataQualityReport,
    DataValidator,
    ValidationIssue,
    ValidationRule,
    ValidationSeverity,
)
from mcp_ds_toolkit_server.data.versioning import (
    DataDriftMetric,
    DatasetVersion,
    DriftReport,
    PipelineConfig,
    RemoteConfig,
    RemoteStorageType,
    VersioningConfig,
    VersioningStrategy,
)
from mcp_ds_toolkit_server.data.visualization import (
    ColorPalette,
    DataVisualizer,
    PlotConfig,
    PlotResult,
    PlotType,
    quick_eda,
    save_plots_to_html,
)

__all__ = [
    # Dataset loading
    "DatasetLoader",
    "DatasetInfo", 
    "DataType",
    "DataFormat",
    # Validation
    "DataValidator",
    "DataQualityReport",
    "ValidationIssue",
    "ValidationRule",
    "ValidationSeverity",
    # Profiling
    "DataProfiler",
    "DataProfile",
    "ColumnProfile",
    "CorrelationAnalysis",
    "FeatureImportanceAnalysis",
    "ProfileType",
    "DistributionType",
    # Preprocessing
    "PreprocessingPipeline",
    "PreprocessingConfig", 
    "PreprocessingReport",
    "CustomTransformer",
    "ScalingMethod",
    "EncodingMethod",
    "SelectionMethod",
    "ImputationMethod",
    # Cleaning
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
    # Splitting
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
    # Versioning
    "RemoteStorageType",
    "VersioningStrategy",
    "DataDriftMetric",
    "RemoteConfig",
    "VersioningConfig",
    "DatasetVersion",
    "DriftReport",
    "PipelineConfig",
    # Model evaluation
    "ModelEvaluator",
    "TaskType",
    "CrossValidationMethod",
    "HyperparameterTuningMethod",
    "CrossValidationConfig", 
    "HyperparameterTuningConfig",
    "ModelPerformanceReport",
    "get_default_param_grids",
    "quick_model_comparison",
    # Visualization
    "DataVisualizer",
    "PlotType",
    "ColorPalette",
    "PlotConfig",
    "PlotResult",
    "quick_eda",
    "save_plots_to_html",
]