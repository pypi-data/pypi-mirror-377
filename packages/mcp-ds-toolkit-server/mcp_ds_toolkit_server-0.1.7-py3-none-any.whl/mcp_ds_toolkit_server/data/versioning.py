"""Data Versioning Module

This module provides comprehensive dataset versioning capabilities with data drift
detection and automated version tracking for machine learning workflows.
"""

import hashlib
import json
import logging
import os
import shutil
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import yaml

try:
    import git
    from git.exc import InvalidGitRepositoryError
    HAS_GIT = True
except ImportError:
    HAS_GIT = False

# DVC imports
try:
    import dvc.api
    import dvc.repo
    from dvc.exceptions import DvcException
    from dvc.repo import Repo as DVCRepo
except ImportError:
    dvc = None
    DVCRepo = None
    DvcException = Exception

# Cloud storage imports - optional dependencies
try:
    import boto3
    from botocore.exceptions import ClientError
    HAS_AWS = True
except ImportError:
    HAS_AWS = False

try:
    from google.cloud import storage as gcs
    HAS_GCS = True
except ImportError:
    HAS_GCS = False

try:
    from azure.storage.blob import BlobServiceClient
    HAS_AZURE = True
except ImportError:
    HAS_AZURE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RemoteStorageType(Enum):
    """Enumeration of supported remote storage backends.

    This enum defines the available storage backends for dataset versioning
    and remote synchronization. Each storage type has specific configuration
    requirements and capabilities.

    Attributes:
        LOCAL (str): Local filesystem storage.
        S3 (str): Amazon S3 bucket storage.
        GCS (str): Google Cloud Storage bucket.
        AZURE (str): Azure Blob Storage container.
        GDRIVE (str): Google Drive folder (experimental).
        SSH (str): SSH/SFTP remote server storage.
        HDFS (str): Hadoop Distributed File System.

    Example:
        Storage backend selection::

            # For cloud storage
            storage_type = RemoteStorageType.S3

            # For local development
            storage_type = RemoteStorageType.LOCAL
    """
    LOCAL = "local"
    S3 = "s3"
    GCS = "gs"
    AZURE = "azure"
    GDRIVE = "gdrive"
    SSH = "ssh"
    HDFS = "hdfs"


class VersioningStrategy(Enum):
    """Enumeration of dataset versioning strategies.

    This enum defines different approaches to version naming and tracking.
    Each strategy has different use cases and trade-offs between human
    readability and automation.

    Attributes:
        HASH_BASED (str): Content-based versioning using file hashes.
            Automatic, deterministic, but not human-readable.
        TIMESTAMP_BASED (str): Time-based versioning with ISO timestamps.
            Automatic, chronological, readable but not semantic.
        SEMANTIC_VERSIONING (str): Manual semantic versioning (major.minor.patch).
            Human-readable, semantic meaning, requires manual management.
        INCREMENTAL (str): Simple incremental numbering (v1, v2, v3...).
            Simple, readable, but no semantic meaning.

    Example:
        Version strategy selection::

            # For production datasets
            strategy = VersioningStrategy.SEMANTIC_VERSIONING

            # For automated pipelines
            strategy = VersioningStrategy.HASH_BASED
    """
    HASH_BASED = "hash_based"
    TIMESTAMP_BASED = "timestamp_based"
    SEMANTIC_VERSIONING = "semantic"
    INCREMENTAL = "incremental"


class DataDriftMetric(Enum):
    """Enumeration of data drift detection metrics.

    This enum defines statistical and ML-based metrics for detecting
    changes in data distribution between dataset versions. Each metric
    has different sensitivity and computational requirements.

    Attributes:
        KOLMOGOROV_SMIRNOV (str): K-S test for distribution differences.
            Non-parametric test, works for any distribution shape.
        JENSEN_SHANNON (str): JS divergence for probability distributions.
            Symmetric, bounded metric good for discrete distributions.
        WASSERSTEIN (str): Earth mover's distance between distributions.
            Considers distance between distribution modes.
        POPULATION_STABILITY (str): Population Stability Index for monitoring.
            Industry-standard metric for model monitoring.
        FEATURE_IMPORTANCE (str): ML-based drift using feature importance.
            Model-based approach for complex, multivariate drift.

    Example:
        Drift metric selection::

            # For continuous variables
            metric = DataDriftMetric.KOLMOGOROV_SMIRNOV

            # For model monitoring
            metric = DataDriftMetric.POPULATION_STABILITY
    """
    KOLMOGOROV_SMIRNOV = "ks_test"
    JENSEN_SHANNON = "js_divergence"
    WASSERSTEIN = "wasserstein"
    POPULATION_STABILITY = "psi"
    FEATURE_IMPORTANCE = "feature_importance"


@dataclass
class RemoteConfig:
    """Configuration for remote storage."""
    storage_type: RemoteStorageType
    url: str
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    region: Optional[str] = None
    bucket: Optional[str] = None
    prefix: Optional[str] = None
    endpoint_url: Optional[str] = None
    profile: Optional[str] = None
    use_ssl: bool = True
    additional_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VersioningConfig:
    """Configuration for dataset versioning."""
    strategy: VersioningStrategy = VersioningStrategy.HASH_BASED
    include_metadata: bool = True
    track_lineage: bool = True
    auto_stage: bool = True
    compression: Optional[str] = None
    cache_dir: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    description: Optional[str] = None


@dataclass
class DatasetVersion:
    """Information about a dataset version."""
    version: str
    hash: str
    timestamp: datetime
    size: int
    path: str
    tags: List[str]
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    lineage: Dict[str, Any] = field(default_factory=dict)
    drift_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class DriftReport:
    """Report of data drift analysis."""
    source_version: str
    target_version: str
    drift_detected: bool
    drift_score: float
    drift_metrics: Dict[str, Dict[str, float]]
    drifted_features: List[str]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PipelineConfig:
    """Configuration for DVC pipeline."""
    stages: List[Dict[str, Any]] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    metrics: List[str] = field(default_factory=list)
    plots: List[str] = field(default_factory=list)


class DVCManager:
    """
    DVC Manager for dataset versioning and tracking.
    
    This class provides comprehensive DVC integration including:
    - Dataset versioning with multiple strategies
    - Remote storage configuration
    - Data drift detection
    - Pipeline management
    - Version comparison and lineage tracking
    """
    
    def __init__(self, 
                 repo_path: str = ".",
                 versioning_config: VersioningConfig = None,
                 remote_config: RemoteConfig = None):
        """
        Initialize DVC Manager.
        
        Args:
            repo_path: Path to the repository
            versioning_config: Configuration for versioning
            remote_config: Configuration for remote storage
        """
        self.repo_path = Path(repo_path)
        self.versioning_config = versioning_config or VersioningConfig()
        self.remote_config = remote_config
        self.dvc_repo = None
        self.git_repo = None
        self.versions = {}
        self.pipeline_config = PipelineConfig()
        
        # Initialize repository
        self.initialize_repo()
    
    def initialize_repo(self):
        """Initialize Git and DVC repositories."""
        try:
            # Initialize Git repository if Git is available
            if HAS_GIT:
                if not (self.repo_path / ".git").exists():
                    logger.info("Initializing Git repository...")
                    self.git_repo = git.Repo.init(str(self.repo_path))
                else:
                    self.git_repo = git.Repo(str(self.repo_path))
            else:
                logger.warning("Git not available - DVC versioning will work without Git integration")
            
            # Initialize DVC repository if DVC is available
            if dvc and DVCRepo:
                if not (self.repo_path / ".dvc").exists():
                    logger.info("Initializing DVC repository...")
                    self.dvc_repo = DVCRepo.init(str(self.repo_path))
                else:
                    self.dvc_repo = DVCRepo(str(self.repo_path))
                
                # Configure remote storage if provided
                if self.remote_config:
                    self._configure_remote_storage()
            else:
                logger.warning("DVC not available - versioning features will be disabled")
                
        except Exception as e:
            logger.error(f"Failed to initialize repository: {e}")
            # Don't raise - allow graceful fallback
    
    def _configure_remote_storage(self):
        """Configure remote storage for DVC."""
        try:
            remote_name = "origin"
            
            # Remove existing remote if it exists
            try:
                with self.dvc_repo.config.edit() as conf:
                    if f"remote \"{remote_name}\"" in conf:
                        del conf[f"remote \"{remote_name}\""]
            except:
                pass
            
            # Add new remote configuration
            remote_config = {
                "url": self.remote_config.url
            }
            
            # Add storage-specific configuration
            if self.remote_config.storage_type == RemoteStorageType.S3:
                if self.remote_config.access_key_id:
                    remote_config["access_key_id"] = self.remote_config.access_key_id
                if self.remote_config.secret_access_key:
                    remote_config["secret_access_key"] = self.remote_config.secret_access_key
                if self.remote_config.region:
                    remote_config["region"] = self.remote_config.region
                if self.remote_config.endpoint_url:
                    remote_config["endpoint_url"] = self.remote_config.endpoint_url
                if self.remote_config.profile:
                    remote_config["profile"] = self.remote_config.profile
                remote_config["use_ssl"] = self.remote_config.use_ssl
            
            # Add additional configuration
            remote_config.update(self.remote_config.additional_config)
            
            # Configure remote in DVC
            with self.dvc_repo.config.edit() as conf:
                conf[f"remote \"{remote_name}\""] = remote_config
            
            # Set as default remote
            with self.dvc_repo.config.edit() as conf:
                conf["core"]["remote"] = remote_name
            
            logger.info(f"Configured remote storage: {self.remote_config.storage_type.value}")
            
        except Exception as e:
            logger.error(f"Failed to configure remote storage: {e}")
            raise
    
    def add_dataset(self, 
                   data_path: str,
                   version: Optional[str] = None,
                   tags: Optional[List[str]] = None,
                   description: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> DatasetVersion:
        """
        Add a dataset to DVC tracking.
        
        Args:
            data_path: Path to the dataset
            version: Version identifier (auto-generated if not provided)
            tags: Tags for the dataset
            description: Description of the dataset
            metadata: Additional metadata
            
        Returns:
            DatasetVersion object with version information
        """
        try:
            if self.dvc_repo is None:
                raise RuntimeError("DVC repository not initialized. Use initialize_repo() first.")
                
            data_path = Path(data_path)
            
            if not data_path.exists():
                raise FileNotFoundError(f"Dataset not found: {data_path}")
            
            # Generate version if not provided
            if version is None:
                version = self._generate_version(data_path)
            
            # Add to DVC tracking
            logger.info(f"Adding dataset to DVC: {data_path}")
            self.dvc_repo.add(str(data_path))
            
            # Calculate file hash and size
            file_hash = self._calculate_file_hash(data_path)
            file_size = self._get_file_size(data_path)
            
            # Create version information
            dataset_version = DatasetVersion(
                version=version,
                hash=file_hash,
                timestamp=datetime.now(),
                size=file_size,
                path=str(data_path),
                tags=tags or [],
                description=description,
                metadata=metadata or {},
                lineage=self._extract_lineage(data_path)
            )
            
            # Store version information
            self.versions[version] = dataset_version
            self._save_version_info(dataset_version)
            
            # Stage changes if configured
            if self.versioning_config.auto_stage:
                self._stage_changes(data_path, version)
            
            logger.info(f"Dataset added with version: {version}")
            return dataset_version
            
        except Exception as e:
            logger.error(f"Failed to add dataset: {e}")
            raise
    
    def get_dataset(self, 
                   version: str,
                   output_path: Optional[str] = None) -> str:
        """
        Get a specific version of a dataset.
        
        Args:
            version: Version identifier
            output_path: Path to save the dataset (optional)
            
        Returns:
            Path to the retrieved dataset
        """
        try:
            if version not in self.versions:
                raise ValueError(f"Version not found: {version}")
            
            version_info = self.versions[version]
            
            # Get dataset using DVC
            if output_path:
                dvc.api.get(version_info.path, output_path, repo=str(self.repo_path))
                return output_path
            else:
                return dvc.api.get_url(version_info.path, repo=str(self.repo_path))
                
        except Exception as e:
            logger.error(f"Failed to get dataset: {e}")
            raise
    
    def list_versions(self, 
                     dataset_path: Optional[str] = None) -> List[DatasetVersion]:
        """
        List all versions of datasets.
        
        Args:
            dataset_path: Filter by dataset path (optional)
            
        Returns:
            List of DatasetVersion objects
        """
        if dataset_path:
            return [v for v in self.versions.values() if v.path == dataset_path]
        else:
            return list(self.versions.values())
    
    def compare_versions(self, 
                        version1: str,
                        version2: str) -> DriftReport:
        """
        Compare two dataset versions and detect data drift.
        
        Args:
            version1: First version identifier
            version2: Second version identifier
            
        Returns:
            DriftReport with comparison results
        """
        try:
            if version1 not in self.versions or version2 not in self.versions:
                raise ValueError("One or both versions not found")
            
            v1_info = self.versions[version1]
            v2_info = self.versions[version2]
            
            # Load datasets
            df1 = self._load_dataset(v1_info.path)
            df2 = self._load_dataset(v2_info.path)
            
            # Calculate drift metrics
            drift_metrics = self._calculate_drift_metrics(df1, df2)
            
            # Determine if drift is detected
            drift_detected = any(
                metric_values.get('p_value', 1.0) < 0.05 
                for metric_values in drift_metrics.values()
            )
            
            # Calculate overall drift score
            drift_score = np.mean([
                1 - metric_values.get('p_value', 1.0)
                for metric_values in drift_metrics.values()
            ])
            
            # Identify drifted features
            drifted_features = [
                feature for feature, metric_values in drift_metrics.items()
                if metric_values.get('p_value', 1.0) < 0.05
            ]
            
            # Generate recommendations
            recommendations = self._generate_drift_recommendations(
                drift_detected, drifted_features, drift_score
            )
            
            return DriftReport(
                source_version=version1,
                target_version=version2,
                drift_detected=drift_detected,
                drift_score=drift_score,
                drift_metrics=drift_metrics,
                drifted_features=drifted_features,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to compare versions: {e}")
            raise
    
    def create_pipeline(self, 
                       pipeline_config: PipelineConfig) -> str:
        """
        Create a DVC pipeline.
        
        Args:
            pipeline_config: Configuration for the pipeline
            
        Returns:
            Path to the created pipeline file
        """
        try:
            pipeline_file = self.repo_path / "dvc.yaml"
            
            # Create pipeline configuration
            pipeline_data = {
                "stages": {},
                "params": pipeline_config.parameters,
                "metrics": pipeline_config.metrics,
                "plots": pipeline_config.plots
            }
            
            # Add stages
            for stage in pipeline_config.stages:
                stage_name = stage["name"]
                pipeline_data["stages"][stage_name] = {
                    "cmd": stage["cmd"],
                    "deps": stage.get("deps", []),
                    "outs": stage.get("outs", []),
                    "params": stage.get("params", []),
                    "metrics": stage.get("metrics", []),
                    "plots": stage.get("plots", [])
                }
            
            # Write pipeline file
            with open(pipeline_file, 'w') as f:
                yaml.dump(pipeline_data, f, default_flow_style=False)
            
            logger.info(f"Created DVC pipeline: {pipeline_file}")
            return str(pipeline_file)
            
        except Exception as e:
            logger.error(f"Failed to create pipeline: {e}")
            raise
    
    def run_pipeline(self, 
                    stage: Optional[str] = None,
                    force: bool = False) -> bool:
        """
        Run DVC pipeline.
        
        Args:
            stage: Specific stage to run (optional)
            force: Force execution even if unchanged
            
        Returns:
            True if successful
        """
        try:
            if stage:
                self.dvc_repo.reproduce(stage, force=force)
            else:
                self.dvc_repo.reproduce(force=force)
            
            logger.info("Pipeline execution completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            raise
    
    def push_to_remote(self, 
                      version: Optional[str] = None) -> bool:
        """
        Push dataset(s) to remote storage.
        
        Args:
            version: Specific version to push (optional)
            
        Returns:
            True if successful
        """
        try:
            if version:
                if version not in self.versions:
                    raise ValueError(f"Version not found: {version}")
                
                version_info = self.versions[version]
                self.dvc_repo.push([version_info.path])
            else:
                self.dvc_repo.push()
            
            logger.info("Successfully pushed to remote storage")
            return True
            
        except Exception as e:
            logger.error(f"Failed to push to remote: {e}")
            raise
    
    def pull_from_remote(self, 
                        version: Optional[str] = None) -> bool:
        """
        Pull dataset(s) from remote storage.
        
        Args:
            version: Specific version to pull (optional)
            
        Returns:
            True if successful
        """
        try:
            if version:
                if version not in self.versions:
                    raise ValueError(f"Version not found: {version}")
                
                version_info = self.versions[version]
                self.dvc_repo.pull([version_info.path])
            else:
                self.dvc_repo.pull()
            
            logger.info("Successfully pulled from remote storage")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pull from remote: {e}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get DVC repository status.
        
        Returns:
            Dictionary with status information
        """
        try:
            status = self.dvc_repo.status()
            
            return {
                "tracked_files": len(status.get("committed", {})),
                "modified_files": len(status.get("modified", {})),
                "new_files": len(status.get("new", {})),
                "deleted_files": len(status.get("deleted", {})),
                "versions": len(self.versions),
                "remote_configured": self.remote_config is not None
            }
            
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {}
    
    def _generate_version(self, data_path: Path) -> str:
        """Generate version identifier based on strategy."""
        if self.versioning_config.strategy == VersioningStrategy.HASH_BASED:
            return self._calculate_file_hash(data_path)[:8]
        elif self.versioning_config.strategy == VersioningStrategy.TIMESTAMP_BASED:
            return datetime.now().strftime("%Y%m%d_%H%M%S")
        elif self.versioning_config.strategy == VersioningStrategy.INCREMENTAL:
            return f"v{len(self.versions) + 1}"
        else:
            return f"v{len(self.versions) + 1}"
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate hash of a file."""
        hasher = hashlib.sha256()
        
        if file_path.is_file():
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
        elif file_path.is_dir():
            for root, dirs, files in os.walk(file_path):
                for file in sorted(files):
                    file_path_full = Path(root) / file
                    with open(file_path_full, 'rb') as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def _get_file_size(self, file_path: Path) -> int:
        """Get size of a file or directory."""
        if file_path.is_file():
            return file_path.stat().st_size
        elif file_path.is_dir():
            total_size = 0
            for root, dirs, files in os.walk(file_path):
                for file in files:
                    file_path_full = Path(root) / file
                    total_size += file_path_full.stat().st_size
            return total_size
        return 0
    
    def _extract_lineage(self, data_path: Path) -> Dict[str, Any]:
        """Extract lineage information for a dataset."""
        lineage = {
            "created_at": datetime.now().isoformat(),
            "source_path": str(data_path),
            "git_commit": None,
            "git_branch": None
        }
        
        try:
            if self.git_repo:
                lineage["git_commit"] = self.git_repo.head.commit.hexsha
                lineage["git_branch"] = self.git_repo.active_branch.name
        except:
            pass
        
        return lineage
    
    def _save_version_info(self, version: DatasetVersion):
        """Save version information to disk."""
        version_dir = self.repo_path / ".dvc" / "versions"
        version_dir.mkdir(exist_ok=True)
        
        version_file = version_dir / f"{version.version}.json"
        
        version_data = {
            "version": version.version,
            "hash": version.hash,
            "timestamp": version.timestamp.isoformat(),
            "size": version.size,
            "path": version.path,
            "tags": version.tags,
            "description": version.description,
            "metadata": version.metadata,
            "lineage": version.lineage,
            "drift_metrics": version.drift_metrics
        }
        
        with open(version_file, 'w') as f:
            json.dump(version_data, f, indent=2)
    
    def _stage_changes(self, data_path: Path, version: str):
        """Stage changes in Git."""
        try:
            # Stage .dvc file
            dvc_file = data_path.with_suffix(data_path.suffix + '.dvc')
            if dvc_file.exists():
                self.git_repo.index.add([str(dvc_file)])
            
            # Stage .gitignore changes
            gitignore_file = data_path.parent / ".gitignore"
            if gitignore_file.exists():
                self.git_repo.index.add([str(gitignore_file)])
            
            logger.info(f"Staged changes for version: {version}")
            
        except Exception as e:
            logger.warning(f"Failed to stage changes: {e}")
    
    def _load_dataset(self, path: str) -> pd.DataFrame:
        """Load dataset from path."""
        path = Path(path)
        
        if path.suffix.lower() == '.csv':
            return pd.read_csv(path)
        elif path.suffix.lower() in ['.json', '.jsonl']:
            return pd.read_json(path)
        elif path.suffix.lower() in ['.parquet', '.pq']:
            return pd.read_parquet(path)
        elif path.suffix.lower() in ['.xlsx', '.xls']:
            return pd.read_excel(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    
    def _calculate_drift_metrics(self, df1: pd.DataFrame, df2: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Calculate drift metrics between two datasets."""
        from scipy import stats
        
        drift_metrics = {}
        
        # Get common columns
        common_cols = set(df1.columns) & set(df2.columns)
        
        for col in common_cols:
            if df1[col].dtype in ['int64', 'float64'] and df2[col].dtype in ['int64', 'float64']:
                # Numerical columns
                col_metrics = {}
                
                # Kolmogorov-Smirnov test
                ks_stat, ks_pvalue = stats.ks_2samp(df1[col].dropna(), df2[col].dropna())
                col_metrics['ks_statistic'] = ks_stat
                col_metrics['p_value'] = ks_pvalue
                
                # Wasserstein distance
                wasserstein_dist = stats.wasserstein_distance(df1[col].dropna(), df2[col].dropna())
                col_metrics['wasserstein_distance'] = wasserstein_dist
                
                # Mean and std comparison
                col_metrics['mean_diff'] = abs(df1[col].mean() - df2[col].mean())
                col_metrics['std_diff'] = abs(df1[col].std() - df2[col].std())
                
                drift_metrics[col] = col_metrics
            
            elif df1[col].dtype == 'object' and df2[col].dtype == 'object':
                # Categorical columns
                col_metrics = {}
                
                # Chi-square test
                try:
                    # Get value counts
                    values1 = df1[col].value_counts()
                    values2 = df2[col].value_counts()
                    
                    # Align categories
                    all_categories = set(values1.index) | set(values2.index)
                    freq1 = [values1.get(cat, 0) for cat in all_categories]
                    freq2 = [values2.get(cat, 0) for cat in all_categories]
                    
                    # Chi-square test
                    chi2_stat, chi2_pvalue = stats.chisquare(freq1, freq2)
                    col_metrics['chi2_statistic'] = chi2_stat
                    col_metrics['p_value'] = chi2_pvalue
                    
                    # Jensen-Shannon divergence
                    p1 = np.array(freq1) / sum(freq1)
                    p2 = np.array(freq2) / sum(freq2)
                    js_div = self._jensen_shannon_divergence(p1, p2)
                    col_metrics['js_divergence'] = js_div
                    
                    drift_metrics[col] = col_metrics
                    
                except Exception as e:
                    logger.warning(f"Failed to calculate drift metrics for {col}: {e}")
        
        return drift_metrics
    
    def _jensen_shannon_divergence(self, p: np.ndarray, q: np.ndarray) -> float:
        """Calculate Jensen-Shannon divergence."""
        # Ensure probabilities sum to 1
        p = p / np.sum(p)
        q = q / np.sum(q)
        
        # Calculate m
        m = (p + q) / 2
        
        # Calculate KL divergences
        kl_pm = np.sum(p * np.log(p / m + 1e-10))
        kl_qm = np.sum(q * np.log(q / m + 1e-10))
        
        # Jensen-Shannon divergence
        js_div = (kl_pm + kl_qm) / 2
        
        return js_div
    
    def _generate_drift_recommendations(self, 
                                      drift_detected: bool,
                                      drifted_features: List[str],
                                      drift_score: float) -> List[str]:
        """Generate recommendations based on drift analysis."""
        recommendations = []
        
        if not drift_detected:
            recommendations.append("No significant data drift detected. Data appears stable.")
        else:
            recommendations.append(f"Data drift detected in {len(drifted_features)} features.")
            
            if drift_score > 0.8:
                recommendations.append("High drift detected. Consider retraining models.")
            elif drift_score > 0.5:
                recommendations.append("Moderate drift detected. Monitor closely.")
            else:
                recommendations.append("Low drift detected. Continue monitoring.")
            
            if len(drifted_features) > 0:
                recommendations.append(f"Features showing drift: {', '.join(drifted_features)}")
                recommendations.append("Consider feature engineering or data preprocessing adjustments.")
        
        return recommendations


# Utility functions
def initialize_dvc_repo(repo_path: str = ".") -> DVCManager:
    """
    Initialize a DVC repository.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        DVCManager instance
    """
    return DVCManager(repo_path)


def configure_remote_storage(storage_type: str,
                           url: str,
                           **kwargs) -> RemoteConfig:
    """
    Configure remote storage for DVC.
    
    Args:
        storage_type: Type of remote storage
        url: Storage URL
        **kwargs: Additional configuration parameters
        
    Returns:
        RemoteConfig instance
    """
    return RemoteConfig(
        storage_type=RemoteStorageType(storage_type),
        url=url,
        **kwargs
    )


def create_versioning_config(strategy: str = "hash_based",
                           **kwargs) -> VersioningConfig:
    """
    Create versioning configuration.
    
    Args:
        strategy: Versioning strategy
        **kwargs: Additional configuration parameters
        
    Returns:
        VersioningConfig instance
    """
    return VersioningConfig(
        strategy=VersioningStrategy(strategy),
        **kwargs
    )


def track_dataset(data_path: str,
                 repo_path: str = ".",
                 version: Optional[str] = None,
                 **kwargs) -> DatasetVersion:
    """
    Track a dataset with DVC.
    
    Args:
        data_path: Path to the dataset
        repo_path: Path to the repository
        version: Version identifier
        **kwargs: Additional parameters
        
    Returns:
        DatasetVersion instance
    """
    manager = DVCManager(repo_path)
    return manager.add_dataset(data_path, version=version, **kwargs)


def compare_dataset_versions(version1: str,
                           version2: str,
                           repo_path: str = ".") -> DriftReport:
    """
    Compare two dataset versions.
    
    Args:
        version1: First version identifier
        version2: Second version identifier
        repo_path: Path to the repository
        
    Returns:
        DriftReport with comparison results
    """
    manager = DVCManager(repo_path)
    return manager.compare_versions(version1, version2) 