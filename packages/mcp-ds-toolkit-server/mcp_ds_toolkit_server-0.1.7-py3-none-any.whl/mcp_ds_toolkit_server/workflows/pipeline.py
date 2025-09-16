"""
MLOps Pipeline - End-to-end workflow orchestration.

This module provides a unified pipeline that connects all MLOps components:
- Data loading and preprocessing
- Model training and evaluation
- Experiment tracking (when available)
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from mcp_ds_toolkit_server.data import DataProfiler, DatasetLoader, DataValidator, PreprocessingPipeline
from mcp_ds_toolkit_server.exceptions import DataError, TrainingError, ValidationError
from mcp_ds_toolkit_server.training import EvaluationConfig, ModelEvaluator, ModelTrainer, TrainingConfig
from mcp_ds_toolkit_server.utils.config import Settings
from mcp_ds_toolkit_server.utils.logger import make_logger

logger = make_logger(__name__)


@dataclass
class PipelineConfig:
    """Configuration for the complete MLOps pipeline."""

    # Pipeline settings
    pipeline_name: str = "mlops_pipeline"
    description: str = "End-to-end MLOps pipeline"

    # Data settings
    target_column: str = "target"
    feature_columns: Optional[List[str]] = None
    enable_data_validation: bool = True
    enable_data_profiling: bool = True
    enable_preprocessing: bool = True

    # Training settings
    training_config: Optional[TrainingConfig] = None

    # Evaluation settings
    enable_model_evaluation: bool = True
    evaluation_config: Optional[EvaluationConfig] = None

    # Output settings
    save_artifacts: bool = True
    output_dir: Optional[Path] = None


@dataclass
class PipelineResult:
    """Results from the complete MLOps pipeline."""

    pipeline_id: str
    pipeline_name: str

    # Data results
    dataset_info: Dict[str, Any] = field(default_factory=dict)
    data_profile: Optional[Dict[str, Any]] = None
    preprocessing_info: Optional[Dict[str, Any]] = None

    # Training results
    training_results: Optional[Any] = None

    # Evaluation results
    evaluation_results: Optional[Any] = None

    # Preprocessing artifacts
    preprocessor: Optional[Any] = None
    preprocessor_path: Optional[Path] = None

    # Pipeline metadata
    created_at: datetime = field(default_factory=datetime.now)
    duration_seconds: float = 0.0
    status: str = "completed"
    error_message: Optional[str] = None

    # File paths
    output_dir: Optional[Path] = None
    pipeline_metadata_path: Optional[Path] = None


class MLOpsPipeline:
    """End-to-end MLOps pipeline orchestrator."""

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the MLOps pipeline.

        Args:
            settings: Configuration settings.
        """
        self.settings = settings or Settings()
        self.logger = make_logger(__name__)

        # Initialize components
        self.data_loader = DatasetLoader(str(self.settings.data_dir))
        self.data_validator = DataValidator()
        self.data_profiler = DataProfiler()
        self.preprocessor = PreprocessingPipeline()
        self.trainer = ModelTrainer(self.settings)
        self.evaluator = ModelEvaluator(self.settings)

    def run_pipeline(
        self,
        dataset_path: Union[str, Path],
        config: Optional[PipelineConfig] = None,
    ) -> PipelineResult:
        """Run the complete MLOps pipeline.

        Args:
            dataset_path: Path to the input dataset.
            config: Pipeline configuration.

        Returns:
            Pipeline results with all artifacts and metadata.

        Raises:
            ValidationError: If pipeline validation fails.
            DataError: If data processing fails.
            TrainingError: If model training fails.
        """
        config = config or PipelineConfig()
        start_time = datetime.now()

        # Generate pipeline ID
        pipeline_id = f"{config.pipeline_name}_{start_time.strftime('%Y%m%d_%H%M%S')}"

        # Setup output directory
        output_dir = config.output_dir or (self.settings.experiments_dir / pipeline_id)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            self.logger.info(f"Starting MLOps pipeline: {pipeline_id}")

            # Initialize result
            result = PipelineResult(
                pipeline_id=pipeline_id,
                pipeline_name=config.pipeline_name,
                output_dir=output_dir,
            )

            # Step 1: Load and validate data
            self.logger.info("Step 1: Loading and validating data")
            dataset_info, df = self._load_and_validate_data(
                dataset_path, config, output_dir
            )
            result.dataset_info = dataset_info

            # Step 2: Data profiling (optional)
            if config.enable_data_profiling:
                self.logger.info("Step 2: Profiling data")
                result.data_profile = self._profile_data(df, output_dir)

            # Step 3: Prepare features and target (BEFORE preprocessing to avoid data leakage)
            self.logger.info("Step 3: Preparing features and target")
            X, y, feature_names = self._prepare_features_target(df, config)
            
            # Step 4: Split data BEFORE preprocessing to prevent data leakage
            self.logger.info("Step 4: Splitting data into train/test sets")
            # Determine stratify parameter
            should_stratify = (
                len(y.unique()) < 20 and 
                (getattr(config.training_config, 'stratify', True) if config.training_config else True)
            )
            stratify_param = y if should_stratify else None
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, 
                test_size=getattr(config.training_config, 'test_size', 0.2) if config.training_config else 0.2,
                random_state=getattr(config.training_config, 'random_state', 42) if config.training_config else 42,
                stratify=stratify_param
            )
            
            # Step 5: Data preprocessing (optional) - AFTER split to prevent data leakage
            preprocessor = None
            if config.enable_preprocessing:
                self.logger.info("Step 5: Preprocessing data (fit on train, transform train/test)")
                preprocessor, X_train, X_test, preprocessing_info = self._preprocess_data_split(
                    X_train, X_test, y_train, config, output_dir
                )
                result.preprocessing_info = preprocessing_info
                result.preprocessor = preprocessor
                
                # Save preprocessor as artifact
                if config.save_artifacts and preprocessor:
                    preprocessor_path = output_dir / "preprocessor.joblib"
                    preprocessor.save_pipeline(str(preprocessor_path))
                    result.preprocessor_path = preprocessor_path
                    self.logger.info(f"Preprocessor saved to: {preprocessor_path}")

            # Step 6: Train model
            self.logger.info("Step 6: Training model")
            training_results = self._train_model(
                X_train, y_train, feature_names, config, output_dir, 
                preprocessor=result.preprocessor
            )
            # Add preprocessor info to training results
            if hasattr(training_results, 'preprocessor_path'):
                training_results.preprocessor_path = result.preprocessor_path
                training_results.preprocessing_config = result.preprocessing_info
            result.training_results = training_results

            # Step 7: Evaluate model (optional)
            if config.enable_model_evaluation:
                self.logger.info("Step 7: Evaluating model on test data")
                evaluation_results = self._evaluate_model(
                    training_results.model, X_test, y_test, config, output_dir, 
                    preprocessor_path=result.preprocessor_path
                )
                result.evaluation_results = evaluation_results

            # Step 8: Save pipeline metadata
            duration = (datetime.now() - start_time).total_seconds()
            result.duration_seconds = duration

            if config.save_artifacts:
                result.pipeline_metadata_path = self._save_pipeline_metadata(
                    result, config
                )

            self.logger.info(f"Pipeline completed successfully in {duration:.2f}s")
            return result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            result.status = "failed"
            result.error_message = str(e)
            result.duration_seconds = duration

            self.logger.error(f"Pipeline failed after {duration:.2f}s: {str(e)}")

            # Save error information
            if config.save_artifacts:
                result.pipeline_metadata_path = self._save_pipeline_metadata(
                    result, config
                )

            raise

    def _load_and_validate_data(
        self,
        dataset_path: Union[str, Path],
        config: PipelineConfig,
        output_dir: Path,
    ) -> Tuple[Dict[str, Any], pd.DataFrame]:
        """Load and validate the input dataset."""
        # Load dataset
        df, dataset_info_obj = self.data_loader.load_dataset(str(dataset_path))

        # Basic dataset info
        dataset_info = {
            "path": str(dataset_path),
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
        }

        # Validate target column
        if config.target_column not in df.columns:
            raise ValidationError(
                f"Target column '{config.target_column}' not found in dataset"
            )

        # Data validation (optional)
        if config.enable_data_validation:
            validation_results = self.data_validator.validate_dataset(df)
            dataset_info["validation"] = {
                "quality_score": validation_results.quality_score,
                "completeness_score": validation_results.completeness_score,
                "consistency_score": validation_results.consistency_score,
                "validity_score": validation_results.validity_score,
                "total_issues": len(validation_results.issues),
                "critical_issues": len(validation_results.get_critical_issues()),
            }

            # Check for critical issues
            if validation_results.has_critical_issues():
                critical_issues = validation_results.get_critical_issues()
                self.logger.warning(
                    f"Dataset has {len(critical_issues)} critical issues"
                )

        # Save dataset info
        with open(output_dir / "dataset_info.json", "w") as f:
            json.dump(dataset_info, f, indent=2, default=str)

        return dataset_info, df

    def _profile_data(self, df: pd.DataFrame, output_dir: Path) -> Dict[str, Any]:
        """Profile the dataset for insights."""
        profile = self.data_profiler.profile_dataset(df)

        # Save profile
        with open(output_dir / "data_profile.json", "w") as f:
            json.dump(profile, f, indent=2, default=str)

        return profile

    def _preprocess_data(
        self,
        df: pd.DataFrame,
        config: PipelineConfig,
        output_dir: Path,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Preprocess the dataset."""
        # Separate features and target
        target_col = config.target_column
        if config.feature_columns:
            feature_cols = config.feature_columns
        else:
            feature_cols = [col for col in df.columns if col != target_col]

        X = df[feature_cols]
        y = df[target_col]

        # Apply preprocessing
        X_processed = self.preprocessor.fit_transform(X)

        # Handle numpy array output
        if isinstance(X_processed, np.ndarray):
            # Get feature names from preprocessor if available
            try:
                feature_names_out = self.preprocessor.get_feature_names_out(
                    feature_cols
                )
                df_processed = pd.DataFrame(
                    X_processed, columns=feature_names_out, index=df.index
                )
            except (AttributeError, ValueError, TypeError):
                # Fallback to original feature names if get_feature_names_out fails
                df_processed = pd.DataFrame(
                    X_processed, columns=feature_cols, index=df.index
                )
        else:
            df_processed = pd.DataFrame(
                X_processed, columns=feature_cols, index=df.index
            )

        df_processed[target_col] = y

        # Preprocessing info
        preprocessing_info = {
            "original_shape": df.shape,
            "processed_shape": df_processed.shape,
            "feature_columns": feature_cols,
            "target_column": target_col,
            "preprocessing_config": {
                "numeric_scaling": self.preprocessor.config.numeric_scaling.value,
                "categorical_encoding": self.preprocessor.config.categorical_encoding.value,
                "numeric_imputation": self.preprocessor.config.numeric_imputation.value,
                "categorical_imputation": self.preprocessor.config.categorical_imputation.value,
                "feature_selection": self.preprocessor.config.feature_selection.value,
            },
        }

        # Save preprocessing info
        with open(output_dir / "preprocessing_info.json", "w") as f:
            json.dump(preprocessing_info, f, indent=2, default=str)

        return df_processed, preprocessing_info
    
    def _preprocess_data_split(
        self,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame, 
        y_train: pd.Series,
        config: PipelineConfig,
        output_dir: Path,
    ) -> Tuple[PreprocessingPipeline, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        """Preprocess data after train/test split to prevent data leakage.
        
        Args:
            X_train: Training features
            X_test: Test features  
            y_train: Training labels (for supervised preprocessing)
            config: Pipeline configuration
            output_dir: Directory for saving artifacts
            
        Returns:
            Tuple of (fitted_preprocessor, X_train_processed, X_test_processed, preprocessing_info)
        """
        self.logger.info("Fitting preprocessor on training data only (preventing data leakage)")
        
        # Fit preprocessor ONLY on training data  
        fitted_preprocessor = self.preprocessor.fit(X_train, y_train)
        
        # Transform training data
        X_train_processed = fitted_preprocessor.transform(X_train)
        
        # Transform test data using same fitted preprocessor
        X_test_processed = fitted_preprocessor.transform(X_test)
        
        # Handle numpy array output for training data
        if isinstance(X_train_processed, np.ndarray):
            try:
                feature_names_out = fitted_preprocessor.get_feature_names_out(X_train.columns)
                X_train_processed = pd.DataFrame(
                    X_train_processed, columns=feature_names_out, index=X_train.index
                )
                X_test_processed = pd.DataFrame(
                    X_test_processed, columns=feature_names_out, index=X_test.index
                )
            except (AttributeError, ValueError, TypeError):
                # Fallback to original feature names
                X_train_processed = pd.DataFrame(
                    X_train_processed, columns=X_train.columns, index=X_train.index
                )
                X_test_processed = pd.DataFrame(
                    X_test_processed, columns=X_test.columns, index=X_test.index
                )
        
        # Create preprocessing info
        preprocessing_info = {
            "train_original_shape": X_train.shape,
            "train_processed_shape": X_train_processed.shape,
            "test_original_shape": X_test.shape, 
            "test_processed_shape": X_test_processed.shape,
            "feature_columns": list(X_train.columns),
            "preprocessing_fitted_on": "training_data_only",  # Important flag
            "data_leakage_prevented": True,  # Explicit confirmation
            "preprocessing_config": {
                "numeric_scaling": fitted_preprocessor.config.numeric_scaling.value,
                "categorical_encoding": fitted_preprocessor.config.categorical_encoding.value,
                "numeric_imputation": fitted_preprocessor.config.numeric_imputation.value,
                "categorical_imputation": fitted_preprocessor.config.categorical_imputation.value,
                "feature_selection": fitted_preprocessor.config.feature_selection.value,
            },
        }
        
        # Save preprocessing info
        with open(output_dir / "preprocessing_info.json", "w") as f:
            json.dump(preprocessing_info, f, indent=2, default=str)
            
        self.logger.info(f"Preprocessing completed - Train: {X_train_processed.shape}, Test: {X_test_processed.shape}")
        
        return fitted_preprocessor, X_train_processed, X_test_processed, preprocessing_info

    def _prepare_features_target(
        self,
        df: pd.DataFrame,
        config: PipelineConfig,
    ) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
        """Prepare features and target for training."""
        target_col = config.target_column

        if config.feature_columns:
            feature_cols = config.feature_columns
        else:
            feature_cols = [col for col in df.columns if col != target_col]

        X = df[feature_cols]
        y = df[target_col]

        return X, y, feature_cols

    def _train_model(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        feature_names: List[str],
        config: PipelineConfig,
        output_dir: Path,
        preprocessor: Optional[Any] = None,
    ) -> Any:
        """Train the machine learning model."""
        # Use provided training config or create default
        training_config = config.training_config or TrainingConfig()

        # Train model
        training_results = self.trainer.train_model(X, y, training_config, output_dir)

        return training_results

    def _evaluate_model(
        self,
        model: Any,
        X: pd.DataFrame,
        y: pd.Series,
        config: PipelineConfig,
        output_dir: Path,
        preprocessor_path: Optional[Path] = None,
    ) -> Any:
        """Evaluate the trained model."""
        # Load and apply preprocessor if available
        X_processed = X
        if preprocessor_path and preprocessor_path.exists():
            from mcp_mlops_server.data.preprocessing import PreprocessingPipeline
            self.logger.info(f"Loading preprocessor from {preprocessor_path}")
            preprocessor = PreprocessingPipeline.load_pipeline(str(preprocessor_path))
            X_processed = preprocessor.transform(X)
            self.logger.info("Applied saved preprocessor to evaluation data")
        
        # Use provided evaluation config or create default
        evaluation_config = config.evaluation_config or EvaluationConfig()
        evaluation_config.save_results = True

        # Evaluate model
        evaluation_results = self.evaluator.evaluate_model(
            model, X_processed, y, "pipeline_model", evaluation_config
        )

        return evaluation_results

    def _save_pipeline_metadata(
        self,
        result: PipelineResult,
        config: PipelineConfig,
    ) -> Path:
        """Save complete pipeline metadata."""
        metadata = {
            "pipeline_id": result.pipeline_id,
            "pipeline_name": result.pipeline_name,
            "created_at": result.created_at.isoformat(),
            "duration_seconds": result.duration_seconds,
            "status": result.status,
            "error_message": result.error_message,
            # Configuration
            "config": {
                "pipeline_name": config.pipeline_name,
                "description": config.description,
                "target_column": config.target_column,
                "feature_columns": config.feature_columns,
                "enable_data_validation": config.enable_data_validation,
                "enable_data_profiling": config.enable_data_profiling,
                "enable_preprocessing": config.enable_preprocessing,
                "enable_model_evaluation": config.enable_model_evaluation,
            },
            # Results summary
            "results": {
                "dataset_shape": result.dataset_info.get("shape"),
                "training_completed": result.training_results is not None,
                "evaluation_completed": result.evaluation_results is not None,
            },
        }

        # Add training results summary
        if result.training_results:
            metadata["results"]["training"] = {
                "algorithm": result.training_results.algorithm,
                "model_type": result.training_results.model_type,
                "train_score": result.training_results.train_score,
                "test_score": result.training_results.test_score,
                "training_time": result.training_results.training_time,
            }

        # Add evaluation results summary
        if result.evaluation_results:
            metadata["results"]["evaluation"] = {
                "cv_means": result.evaluation_results.cv_means,
                "test_scores": result.evaluation_results.test_scores,
            }

        # Save metadata
        metadata_path = result.output_dir / "pipeline_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)

        self.logger.info(f"Pipeline metadata saved to {metadata_path}")
        return metadata_path

    def create_quick_pipeline(
        self,
        dataset_path: Union[str, Path],
        target_column: str,
        pipeline_name: str = "quick_pipeline",
        algorithm: str = "random_forest",
    ) -> PipelineResult:
        """Create and run a quick pipeline with sensible defaults.

        Args:
            dataset_path: Path to the input dataset.
            target_column: Name of the target column.
            pipeline_name: Name for the pipeline.
            algorithm: ML algorithm to use.

        Returns:
            Pipeline results.
        """
        # Detect if algorithm is for regression (continuous target)
        regression_algorithms = {"linear_regression", "ridge", "lasso", "elastic_net"}
        is_regression = algorithm in regression_algorithms

        # Create configuration with sensible defaults
        config = PipelineConfig(
            pipeline_name=pipeline_name,
            target_column=target_column,
            enable_data_validation=True,
            enable_data_profiling=True,
            enable_preprocessing=True,
            enable_model_evaluation=True,
            training_config=TrainingConfig(
                algorithm=algorithm,
                enable_tuning=False,  # Disable for speed
                cv_folds=3,  # Reduce for speed
                stratify=not is_regression,  # Disable stratification for regression
            ),
            evaluation_config=EvaluationConfig(
                cv_folds=3,  # Reduce for speed
                detailed_metrics=True,
            ),
        )

        return self.run_pipeline(dataset_path, config)
