"""Data Splitting Module

This module provides comprehensive data splitting capabilities for machine learning
workflows with support for stratified, time-series, and cross-validation splits.
"""

import datetime
import logging
import warnings
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.model_selection import (
    GroupKFold,
    GroupShuffleSplit,
    KFold,
    LeaveOneOut,
    LeavePOut,
    ShuffleSplit,
    StratifiedKFold,
    StratifiedShuffleSplit,
    TimeSeriesSplit,
    train_test_split,
)
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)


class SplittingMethod(Enum):
    """Enumeration of data splitting strategies.

    This enum defines the available data splitting methods, each designed
    for specific data characteristics and use cases. The choice of splitting
    method significantly impacts model validation and generalization.

    Attributes:
        RANDOM (str): Random splitting without considering data structure.
            Best for: IID data without temporal or group dependencies.
        STRATIFIED (str): Maintains class distribution across splits.
            Best for: Classification with imbalanced classes.
        TIME_SERIES (str): Respects temporal ordering for time-dependent data.
            Best for: Time series, sequential data, temporal predictions.
        GROUP_BASED (str): Keeps related samples together in same split.
            Best for: Hierarchical data, preventing data leakage.
        CUSTOM (str): User-defined splitting logic.
            Best for: Specialized requirements not covered by standard methods.
        MANUAL (str): Direct specification of split indices.
            Best for: Pre-defined splits, reproducible research setups.

    Example:
        Choosing appropriate splitting method::

            # For balanced classification
            method = SplittingMethod.STRATIFIED

            # For time series forecasting
            method = SplittingMethod.TIME_SERIES

            # For grouped data (e.g., patient data)
            method = SplittingMethod.GROUP_BASED
    """
    RANDOM = "random"
    STRATIFIED = "stratified"
    TIME_SERIES = "time_series"
    GROUP_BASED = "group_based"
    CUSTOM = "custom"
    MANUAL = "manual"


class CrossValidationMethod(Enum):
    """Enumeration of cross-validation strategies.

    This enum defines the available cross-validation methods for robust
    model evaluation. Each method has specific use cases and trade-offs
    between computational cost and evaluation quality.

    Attributes:
        K_FOLD (str): Standard k-fold cross-validation.
            Randomly divides data into k folds. Good general-purpose method.
        STRATIFIED_K_FOLD (str): Maintains class distribution in each fold.
            Essential for imbalanced classification problems.
        GROUP_K_FOLD (str): Ensures groups don't span multiple folds.
            Prevents data leakage in hierarchical or grouped data.
        TIME_SERIES_SPLIT (str): Respects temporal ordering in CV.
            Critical for time series and sequential data validation.
        SHUFFLE_SPLIT (str): Random sampling without exhaustive folding.
            Efficient for large datasets, allows custom test sizes.
        LEAVE_ONE_OUT (str): Extreme case with n_splits = n_samples.
            Maximum use of data but computationally expensive.
        LEAVE_P_OUT (str): Leave p samples out in each iteration.
            Generalization of leave-one-out for larger validation sets.

    Example:
        Cross-validation method selection::

            # For balanced classification
            cv_method = CrossValidationMethod.STRATIFIED_K_FOLD

            # For time series data
            cv_method = CrossValidationMethod.TIME_SERIES_SPLIT

            # For grouped data
            cv_method = CrossValidationMethod.GROUP_K_FOLD
    """
    K_FOLD = "k_fold"
    STRATIFIED_K_FOLD = "stratified_k_fold"
    GROUP_K_FOLD = "group_k_fold"
    TIME_SERIES_SPLIT = "time_series_split"
    SHUFFLE_SPLIT = "shuffle_split"
    LEAVE_ONE_OUT = "leave_one_out"
    LEAVE_P_OUT = "leave_p_out"


@dataclass
class SplittingConfig:
    """Configuration class for data splitting parameters.

    This dataclass encapsulates all parameters needed to configure data splitting
    operations. It provides validation, sensible defaults, and support for
    advanced splitting scenarios.

    Attributes:
        method (SplittingMethod): Splitting strategy to use.
            Determines the core splitting algorithm and validation approach.
        train_size (float): Proportion of data for training (0.0 to 1.0).
            Should be largest split for sufficient learning data.
        validation_size (float): Proportion of data for validation (0.0 to 1.0).
            Used for hyperparameter tuning and model selection.
        test_size (float): Proportion of data for testing (0.0 to 1.0).
            Reserved for final unbiased performance evaluation.
        random_state (int): Random seed for reproducible splits.
            Set to None for non-deterministic behavior.
        shuffle (bool): Whether to shuffle data before splitting.
            Recommended True except for time series data.
        stratify_column (Optional[str]): Column for stratified splitting.
            Required for stratified method, maintains class distribution.
        group_column (Optional[str]): Column for group-based splitting.
            Required for group-based method, prevents data leakage.
        time_column (Optional[str]): Column for time-aware splitting.
            Required for time series method, maintains temporal order.
        sort_by_time (bool): Whether to sort by time column.
            Only applies to time series splitting method.
        min_samples_per_class (int): Minimum samples required per class.
            Validation constraint for stratified splitting.
        preserve_order (bool): Whether to preserve original data order.
            Overrides shuffle when True.
        custom_indices (Optional[Dict[str, List[int]]]): Pre-defined split indices.
            Required for manual splitting method.

    Raises:
        ValueError: If split sizes don't sum to 1.0 or are non-positive.

    Example:
        Various splitting configurations::

            # Basic random splitting
            config = SplittingConfig()

            # Stratified splitting for classification
            config = SplittingConfig(
                method=SplittingMethod.STRATIFIED,
                stratify_column='target',
                train_size=0.8,
                validation_size=0.1,
                test_size=0.1
            )

            # Time series splitting
            config = SplittingConfig(
                method=SplittingMethod.TIME_SERIES,
                time_column='timestamp',
                shuffle=False,
                sort_by_time=True
            )

            # Group-based splitting
            config = SplittingConfig(
                method=SplittingMethod.GROUP_BASED,
                group_column='patient_id',
                train_size=0.7,
                validation_size=0.2,
                test_size=0.1
            )
    """
    method: SplittingMethod = SplittingMethod.RANDOM
    train_size: float = 0.7
    validation_size: float = 0.15
    test_size: float = 0.15
    random_state: int = 42
    shuffle: bool = True
    stratify_column: Optional[str] = None
    group_column: Optional[str] = None
    time_column: Optional[str] = None
    sort_by_time: bool = True

    # Advanced options
    min_samples_per_class: int = 1
    preserve_order: bool = False
    custom_indices: Optional[Dict[str, List[int]]] = None

    def __post_init__(self):
        """Validate configuration parameters.

        Raises:
            ValueError: If split sizes don't sum to 1.0 or are non-positive.
        """
        if abs(self.train_size + self.validation_size + self.test_size - 1.0) > 1e-6:
            raise ValueError("Train, validation, and test sizes must sum to 1.0")

        if any(size <= 0 for size in [self.train_size, self.validation_size, self.test_size]):
            raise ValueError("All split sizes must be positive")


@dataclass
class CrossValidationConfig:
    """Configuration for cross-validation."""
    method: CrossValidationMethod = CrossValidationMethod.K_FOLD
    n_splits: int = 5
    random_state: int = 42
    shuffle: bool = True
    group_column: Optional[str] = None
    stratify_column: Optional[str] = None
    test_size: float = 0.2
    n_repeats: int = 1
    p: int = 1  # For leave-p-out
    
    def __post_init__(self):
        """Validate configuration."""
        if self.n_splits <= 1:
            raise ValueError("n_splits must be greater than 1")
        if self.test_size <= 0 or self.test_size >= 1:
            raise ValueError("test_size must be between 0 and 1")


@dataclass
class SplitMetrics:
    """Metrics for a single split."""
    size: int
    percentage: float
    class_distribution: Optional[Dict[str, int]] = None
    group_distribution: Optional[Dict[str, int]] = None
    time_range: Optional[Tuple[Any, Any]] = None
    missing_values: int = 0


@dataclass
class SplittingReport:
    """Report of data splitting results."""
    method: str
    total_samples: int
    train_metrics: SplitMetrics
    validation_metrics: SplitMetrics
    test_metrics: SplitMetrics
    splitting_config: SplittingConfig
    stratification_quality: Optional[float] = None
    time_overlap: bool = False
    group_overlap: bool = False
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


class DataSplitter:
    """Advanced data splitting with multiple strategies."""
    
    def __init__(self, config: SplittingConfig = None):
        self.config = config or SplittingConfig()
        self.label_encoders = {}
        self.split_indices = {}
        self._split_data = {}
        
    def split_data(
        self, 
        df: pd.DataFrame, 
        target_column: Optional[str] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, SplittingReport]:
        """
        Split data into train, validation, and test sets.
        
        Args:
            df: Input DataFrame
            target_column: Target column name for stratification
            
        Returns:
            Tuple of (train_df, val_df, test_df, splitting_report)
        """
        logger.info(f"Splitting data with method: {self.config.method.value}")
        
        if len(df) == 0:
            raise ValueError("Cannot split empty DataFrame")
        
        # Validate configuration against data
        self._validate_config_against_data(df, target_column)
        
        # Perform splitting based on method
        if self.config.method == SplittingMethod.RANDOM:
            train_df, val_df, test_df = self._random_split(df)
        elif self.config.method == SplittingMethod.STRATIFIED:
            train_df, val_df, test_df = self._stratified_split(df, target_column)
        elif self.config.method == SplittingMethod.TIME_SERIES:
            train_df, val_df, test_df = self._time_series_split(df)
        elif self.config.method == SplittingMethod.GROUP_BASED:
            train_df, val_df, test_df = self._group_based_split(df)
        elif self.config.method == SplittingMethod.CUSTOM:
            train_df, val_df, test_df = self._custom_split(df)
        elif self.config.method == SplittingMethod.MANUAL:
            train_df, val_df, test_df = self._manual_split(df)
        else:
            raise ValueError(f"Unknown splitting method: {self.config.method}")
        
        # Store split indices
        self.split_indices = {
            'train': train_df.index.tolist(),
            'validation': val_df.index.tolist(),
            'test': test_df.index.tolist()
        }
        
        # Store split data
        self._split_data = {
            'train': train_df,
            'validation': val_df,
            'test': test_df
        }
        
        # Generate report
        report = self._generate_splitting_report(
            df, train_df, val_df, test_df, target_column
        )
        
        return train_df, val_df, test_df, report
    
    def create_cross_validation_splits(
        self, 
        df: pd.DataFrame, 
        cv_config: CrossValidationConfig,
        target_column: Optional[str] = None
    ) -> Generator[Tuple[pd.DataFrame, pd.DataFrame], None, None]:
        """
        Create cross-validation splits.
        
        Args:
            df: Input DataFrame
            cv_config: Cross-validation configuration
            target_column: Target column for stratification
            
        Yields:
            Tuple of (train_df, val_df) for each fold
        """
        logger.info(f"Creating CV splits with method: {cv_config.method.value}")
        
        # Get the appropriate CV splitter
        cv_splitter = self._get_cv_splitter(cv_config, df, target_column)
        
        # Prepare data for splitting
        X = df.drop(columns=[target_column] if target_column else [])
        y = df[target_column] if target_column else None
        groups = df[cv_config.group_column] if cv_config.group_column else None
        
        # Generate splits
        for train_idx, val_idx in cv_splitter.split(X, y, groups):
            train_df = df.iloc[train_idx]
            val_df = df.iloc[val_idx]
            yield train_df, val_df
    
    def _validate_config_against_data(self, df: pd.DataFrame, target_column: Optional[str]):
        """Validate configuration against actual data."""
        if self.config.method == SplittingMethod.STRATIFIED:
            if target_column is None and self.config.stratify_column is None:
                raise ValueError("Stratified splitting requires a target column")
            
            stratify_col = target_column or self.config.stratify_column
            if stratify_col not in df.columns:
                raise ValueError(f"Stratification column '{stratify_col}' not found")
            
            # Check minimum samples per class
            class_counts = df[stratify_col].value_counts()
            min_count = class_counts.min()
            if min_count < self.config.min_samples_per_class:
                raise ValueError(f"Minimum samples per class ({min_count}) is less than required ({self.config.min_samples_per_class})")
        
        elif self.config.method == SplittingMethod.TIME_SERIES:
            if self.config.time_column is None:
                raise ValueError("Time series splitting requires a time column")
            if self.config.time_column not in df.columns:
                raise ValueError(f"Time column '{self.config.time_column}' not found")
        
        elif self.config.method == SplittingMethod.GROUP_BASED:
            if self.config.group_column is None:
                raise ValueError("Group-based splitting requires a group column")
            if self.config.group_column not in df.columns:
                raise ValueError(f"Group column '{self.config.group_column}' not found")
        
        elif self.config.method == SplittingMethod.MANUAL:
            if self.config.custom_indices is None:
                raise ValueError("Manual splitting requires custom indices")
    
    def _random_split(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Perform random splitting."""
        # First split: train vs (val + test)
        train_df, temp_df = train_test_split(
            df,
            train_size=self.config.train_size,
            random_state=self.config.random_state,
            shuffle=self.config.shuffle
        )
        
        # Second split: val vs test
        val_size_adjusted = self.config.validation_size / (self.config.validation_size + self.config.test_size)
        val_df, test_df = train_test_split(
            temp_df,
            train_size=val_size_adjusted,
            random_state=self.config.random_state,
            shuffle=self.config.shuffle
        )
        
        return train_df, val_df, test_df
    
    def _stratified_split(self, df: pd.DataFrame, target_column: Optional[str]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Perform stratified splitting."""
        stratify_col = target_column or self.config.stratify_column
        
        # Encode target if necessary
        if df[stratify_col].dtype == 'object':
            if stratify_col not in self.label_encoders:
                self.label_encoders[stratify_col] = LabelEncoder()
                encoded_target = self.label_encoders[stratify_col].fit_transform(df[stratify_col])
            else:
                encoded_target = self.label_encoders[stratify_col].transform(df[stratify_col])
        else:
            encoded_target = df[stratify_col]
        
        # First split: train vs (val + test)
        train_df, temp_df = train_test_split(
            df,
            train_size=self.config.train_size,
            stratify=encoded_target,
            random_state=self.config.random_state,
            shuffle=self.config.shuffle
        )
        
        # Update encoded target for temp data
        temp_encoded = encoded_target[temp_df.index]
        
        # Second split: val vs test
        val_size_adjusted = self.config.validation_size / (self.config.validation_size + self.config.test_size)
        val_df, test_df = train_test_split(
            temp_df,
            train_size=val_size_adjusted,
            stratify=temp_encoded,
            random_state=self.config.random_state,
            shuffle=self.config.shuffle
        )
        
        return train_df, val_df, test_df
    
    def _time_series_split(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Perform time-series aware splitting."""
        time_col = self.config.time_column
        
        # Sort by time if requested
        if self.config.sort_by_time:
            df_sorted = df.sort_values(time_col)
        else:
            df_sorted = df.copy()
        
        # Calculate split points
        n_samples = len(df_sorted)
        train_end = int(n_samples * self.config.train_size)
        val_end = int(n_samples * (self.config.train_size + self.config.validation_size))
        
        # Split data
        train_df = df_sorted.iloc[:train_end]
        val_df = df_sorted.iloc[train_end:val_end]
        test_df = df_sorted.iloc[val_end:]
        
        return train_df, val_df, test_df
    
    def _group_based_split(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Perform group-based splitting."""
        group_col = self.config.group_column
        unique_groups = df[group_col].unique()
        
        # Split groups
        train_groups, temp_groups = train_test_split(
            unique_groups,
            train_size=self.config.train_size,
            random_state=self.config.random_state,
            shuffle=self.config.shuffle
        )
        
        val_size_adjusted = self.config.validation_size / (self.config.validation_size + self.config.test_size)
        val_groups, test_groups = train_test_split(
            temp_groups,
            train_size=val_size_adjusted,
            random_state=self.config.random_state,
            shuffle=self.config.shuffle
        )
        
        # Filter data by groups
        train_df = df[df[group_col].isin(train_groups)]
        val_df = df[df[group_col].isin(val_groups)]
        test_df = df[df[group_col].isin(test_groups)]
        
        return train_df, val_df, test_df
    
    def _custom_split(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Perform custom splitting using user-defined logic."""
        # This is a placeholder for custom splitting logic
        # Users can override this method for specific needs
        logger.warning("Custom splitting method not implemented, falling back to random split")
        return self._random_split(df)
    
    def _manual_split(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Perform manual splitting using provided indices."""
        indices = self.config.custom_indices
        
        train_df = df.iloc[indices['train']]
        val_df = df.iloc[indices['validation']]
        test_df = df.iloc[indices['test']]
        
        return train_df, val_df, test_df
    
    def _get_cv_splitter(self, cv_config: CrossValidationConfig, df: pd.DataFrame, target_column: Optional[str]):
        """Get appropriate cross-validation splitter."""
        if cv_config.method == CrossValidationMethod.K_FOLD:
            return KFold(
                n_splits=cv_config.n_splits,
                shuffle=cv_config.shuffle,
                random_state=cv_config.random_state
            )
        elif cv_config.method == CrossValidationMethod.STRATIFIED_K_FOLD:
            return StratifiedKFold(
                n_splits=cv_config.n_splits,
                shuffle=cv_config.shuffle,
                random_state=cv_config.random_state
            )
        elif cv_config.method == CrossValidationMethod.GROUP_K_FOLD:
            return GroupKFold(n_splits=cv_config.n_splits)
        elif cv_config.method == CrossValidationMethod.TIME_SERIES_SPLIT:
            return TimeSeriesSplit(n_splits=cv_config.n_splits)
        elif cv_config.method == CrossValidationMethod.SHUFFLE_SPLIT:
            return ShuffleSplit(
                n_splits=cv_config.n_splits,
                test_size=cv_config.test_size,
                random_state=cv_config.random_state
            )
        elif cv_config.method == CrossValidationMethod.LEAVE_ONE_OUT:
            return LeaveOneOut()
        elif cv_config.method == CrossValidationMethod.LEAVE_P_OUT:
            return LeavePOut(p=cv_config.p)
        else:
            raise ValueError(f"Unknown CV method: {cv_config.method}")
    
    def _calculate_split_metrics(self, df: pd.DataFrame, target_column: Optional[str]) -> SplitMetrics:
        """Calculate metrics for a data split."""
        size = len(df)
        percentage = (size / len(df)) * 100 if len(df) > 0 else 0.0
        
        # Class distribution
        class_distribution = None
        if target_column and target_column in df.columns:
            class_distribution = df[target_column].value_counts().to_dict()
        
        # Group distribution
        group_distribution = None
        if self.config.group_column and self.config.group_column in df.columns:
            group_distribution = df[self.config.group_column].value_counts().to_dict()
        
        # Time range
        time_range = None
        if self.config.time_column and self.config.time_column in df.columns:
            time_range = (df[self.config.time_column].min(), df[self.config.time_column].max())
        
        # Missing values
        missing_values = df.isnull().sum().sum()
        
        return SplitMetrics(
            size=size,
            percentage=percentage,
            class_distribution=class_distribution,
            group_distribution=group_distribution,
            time_range=time_range,
            missing_values=missing_values
        )
    
    def _generate_splitting_report(
        self, 
        original_df: pd.DataFrame, 
        train_df: pd.DataFrame, 
        val_df: pd.DataFrame, 
        test_df: pd.DataFrame,
        target_column: Optional[str]
    ) -> SplittingReport:
        """Generate comprehensive splitting report."""
        total_samples = len(original_df)
        
        # Calculate metrics for each split
        train_metrics = self._calculate_split_metrics(train_df, target_column)
        val_metrics = self._calculate_split_metrics(val_df, target_column)
        test_metrics = self._calculate_split_metrics(test_df, target_column)
        
        # Fix percentage calculation
        train_metrics.percentage = (train_metrics.size / total_samples) * 100
        val_metrics.percentage = (val_metrics.size / total_samples) * 100
        test_metrics.percentage = (test_metrics.size / total_samples) * 100
        
        # Calculate stratification quality
        stratification_quality = None
        if target_column and target_column in original_df.columns:
            stratification_quality = self._calculate_stratification_quality(
                original_df, train_df, val_df, test_df, target_column
            )
        
        # Check for overlaps
        time_overlap = False
        group_overlap = False
        
        if self.config.time_column and self.config.time_column in original_df.columns:
            time_overlap = self._check_time_overlap(train_df, val_df, test_df)
        
        if self.config.group_column and self.config.group_column in original_df.columns:
            group_overlap = self._check_group_overlap(train_df, val_df, test_df)
        
        # Generate recommendations
        recommendations = self._generate_splitting_recommendations(
            train_metrics, val_metrics, test_metrics, stratification_quality, time_overlap, group_overlap
        )
        
        return SplittingReport(
            method=self.config.method.value,
            total_samples=total_samples,
            train_metrics=train_metrics,
            validation_metrics=val_metrics,
            test_metrics=test_metrics,
            splitting_config=self.config,
            stratification_quality=stratification_quality,
            time_overlap=time_overlap,
            group_overlap=group_overlap,
            recommendations=recommendations
        )
    
    def _calculate_stratification_quality(
        self, 
        original_df: pd.DataFrame, 
        train_df: pd.DataFrame, 
        val_df: pd.DataFrame, 
        test_df: pd.DataFrame,
        target_column: str
    ) -> float:
        """Calculate how well the stratification preserved class distribution."""
        original_dist = original_df[target_column].value_counts(normalize=True)
        
        # Calculate distribution for each split
        train_dist = train_df[target_column].value_counts(normalize=True)
        val_dist = val_df[target_column].value_counts(normalize=True)
        test_dist = test_df[target_column].value_counts(normalize=True)
        
        # Calculate average absolute difference from original distribution
        total_diff = 0
        count = 0
        
        for class_name in original_dist.index:
            if class_name in train_dist.index:
                total_diff += abs(original_dist[class_name] - train_dist[class_name])
                count += 1
            if class_name in val_dist.index:
                total_diff += abs(original_dist[class_name] - val_dist[class_name])
                count += 1
            if class_name in test_dist.index:
                total_diff += abs(original_dist[class_name] - test_dist[class_name])
                count += 1
        
        # Return quality score (1.0 = perfect, 0.0 = worst)
        if count > 0:
            avg_diff = total_diff / count
            return max(0.0, 1.0 - avg_diff)
        return 0.0
    
    def _check_time_overlap(self, train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame) -> bool:
        """Check for time overlap between splits."""
        time_col = self.config.time_column
        
        train_max = train_df[time_col].max()
        val_min = val_df[time_col].min()
        val_max = val_df[time_col].max()
        test_min = test_df[time_col].min()
        
        return train_max >= val_min or val_max >= test_min
    
    def _check_group_overlap(self, train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame) -> bool:
        """Check for group overlap between splits."""
        group_col = self.config.group_column
        
        train_groups = set(train_df[group_col].unique())
        val_groups = set(val_df[group_col].unique())
        test_groups = set(test_df[group_col].unique())
        
        return bool(train_groups & val_groups) or bool(val_groups & test_groups) or bool(train_groups & test_groups)
    
    def _generate_splitting_recommendations(
        self, 
        train_metrics: SplitMetrics, 
        val_metrics: SplitMetrics, 
        test_metrics: SplitMetrics,
        stratification_quality: Optional[float],
        time_overlap: bool,
        group_overlap: bool
    ) -> List[str]:
        """Generate recommendations based on splitting results."""
        recommendations = []
        
        # Check split sizes
        if train_metrics.size < 100:
            recommendations.append("Training set is very small (<100 samples) - consider collecting more data")
        elif train_metrics.size < 1000:
            recommendations.append("Training set is small (<1000 samples) - use cross-validation")
        
        if val_metrics.size < 50:
            recommendations.append("Validation set is very small (<50 samples) - consider k-fold CV")
        
        if test_metrics.size < 50:
            recommendations.append("Test set is very small (<50 samples) - results may not be reliable")
        
        # Check stratification quality
        if stratification_quality is not None:
            if stratification_quality < 0.8:
                recommendations.append("Poor stratification quality - consider larger dataset or different split ratios")
            elif stratification_quality > 0.95:
                recommendations.append("Excellent stratification quality maintained")
        
        # Check for overlaps
        if time_overlap:
            recommendations.append("Time overlap detected - ensure chronological order for time series data")
        
        if group_overlap:
            recommendations.append("Group overlap detected - this may cause data leakage")
        
        # Check missing values
        total_missing = train_metrics.missing_values + val_metrics.missing_values + test_metrics.missing_values
        if total_missing > 0:
            recommendations.append(f"Missing values detected ({total_missing}) - consider imputation before splitting")
        
        return recommendations
    
    def get_split_indices(self) -> Dict[str, List[int]]:
        """Get indices for each split."""
        return self.split_indices.copy()
    
    def get_split_data(self) -> Dict[str, pd.DataFrame]:
        """Get data for each split."""
        return self._split_data.copy()
    
    def save_splits(self, output_dir: str, prefix: str = "split"):
        """Save splits to files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for split_name, split_df in self._split_data.items():
            filename = f"{prefix}_{split_name}.csv"
            filepath = output_path / filename
            split_df.to_csv(filepath, index=False)
            logger.info(f"Saved {split_name} split to {filepath}")


# Utility functions
def split_dataset(
    df: pd.DataFrame,
    method: Union[str, SplittingMethod] = SplittingMethod.RANDOM,
    target_column: Optional[str] = None,
    train_size: float = 0.7,
    validation_size: float = 0.15,
    test_size: float = 0.15,
    **kwargs
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, SplittingReport]:
    """
    Quick utility function for data splitting.
    
    Args:
        df: Input DataFrame
        method: Splitting method
        target_column: Target column for stratification
        train_size: Training set size
        validation_size: Validation set size
        test_size: Test set size
        **kwargs: Additional configuration parameters
        
    Returns:
        Tuple of (train_df, val_df, test_df, splitting_report)
    """
    # Convert string method to enum
    if isinstance(method, str):
        method = SplittingMethod(method)
    
    # Create configuration
    config = SplittingConfig(
        method=method,
        train_size=train_size,
        validation_size=validation_size,
        test_size=test_size,
        **kwargs
    )
    
    # Create splitter and split data
    splitter = DataSplitter(config)
    return splitter.split_data(df, target_column)


def create_time_series_splits(
    df: pd.DataFrame,
    time_column: str,
    n_splits: int = 5,
    test_size: float = 0.2
) -> Generator[Tuple[pd.DataFrame, pd.DataFrame], None, None]:
    """
    Create time series cross-validation splits.
    
    Args:
        df: Input DataFrame
        time_column: Time column name
        n_splits: Number of splits
        test_size: Test size for each split (as percentage of data)
        
    Yields:
        Tuple of (train_df, val_df) for each fold
    """
    # Sort by time
    df_sorted = df.sort_values(time_column)
    
    # Calculate test size as integer
    test_size_int = max(1, int(len(df) * test_size))
    
    # Create time series split - use None for test_size to let it auto-calculate
    tss = TimeSeriesSplit(n_splits=n_splits)
    
    for train_idx, val_idx in tss.split(df_sorted):
        train_df = df_sorted.iloc[train_idx]
        val_df = df_sorted.iloc[val_idx]
        yield train_df, val_df


def create_stratified_splits(
    df: pd.DataFrame,
    target_column: str,
    n_splits: int = 5,
    test_size: float = 0.2,
    random_state: int = 42
) -> Generator[Tuple[pd.DataFrame, pd.DataFrame], None, None]:
    """
    Create stratified cross-validation splits.
    
    Args:
        df: Input DataFrame
        target_column: Target column for stratification
        n_splits: Number of splits
        test_size: Test size for each split
        random_state: Random state for reproducibility
        
    Yields:
        Tuple of (train_df, val_df) for each fold
    """
    # Create stratified split
    sss = StratifiedShuffleSplit(
        n_splits=n_splits,
        test_size=test_size,
        random_state=random_state
    )
    
    # Prepare target
    y = df[target_column]
    if y.dtype == 'object':
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
    else:
        y_encoded = y
    
    for train_idx, val_idx in sss.split(df, y_encoded):
        train_df = df.iloc[train_idx]
        val_df = df.iloc[val_idx]
        yield train_df, val_df 