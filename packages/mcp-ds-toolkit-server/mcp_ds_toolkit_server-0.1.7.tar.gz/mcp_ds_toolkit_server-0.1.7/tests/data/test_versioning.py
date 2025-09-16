"""
Tests for DVC versioning module.
"""

import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from mcp_ds_toolkit_server.data.versioning import (
    DataDriftMetric,
    DatasetVersion,
    DriftReport,
    DVCManager,
    HAS_GIT,
    PipelineConfig,
    RemoteConfig,
    RemoteStorageType,
    VersioningConfig,
    VersioningStrategy,
    compare_dataset_versions,
    configure_remote_storage,
    create_versioning_config,
    initialize_dvc_repo,
    track_dataset,
)


def conditional_git_patch(test_func):
    """Decorator to conditionally patch Git based on availability."""
    if HAS_GIT:
        return patch('mcp_mlops_server.data.versioning.git.Repo')(test_func)
    else:
        # If Git is not available, just run the test without Git patching
        return test_func


# Skip DVC tests when Git is not available since they rely on Git mocking
skip_if_no_git = pytest.mark.skipif(not HAS_GIT, reason="Git not available - required for DVC tests")


class TestRemoteConfig:
    """Tests for RemoteConfig class."""
    
    def test_remote_config_creation(self):
        """Test creating remote configuration."""
        config = RemoteConfig(
            storage_type=RemoteStorageType.S3,
            url="s3://my-bucket/data",
            access_key_id="key",
            secret_access_key="secret",
            region="us-west-2"
        )
        
        assert config.storage_type == RemoteStorageType.S3
        assert config.url == "s3://my-bucket/data"
        assert config.access_key_id == "key"
        assert config.secret_access_key == "secret"
        assert config.region == "us-west-2"
        assert config.use_ssl is True
    
    def test_remote_config_defaults(self):
        """Test remote configuration with defaults."""
        config = RemoteConfig(
            storage_type=RemoteStorageType.LOCAL,
            url="/local/path"
        )
        
        assert config.storage_type == RemoteStorageType.LOCAL
        assert config.url == "/local/path"
        assert config.access_key_id is None
        assert config.region is None
        assert config.use_ssl is True


class TestVersioningConfig:
    """Tests for VersioningConfig class."""
    
    def test_versioning_config_creation(self):
        """Test creating versioning configuration."""
        config = VersioningConfig(
            strategy=VersioningStrategy.HASH_BASED,
            include_metadata=True,
            track_lineage=True,
            auto_stage=True,
            tags=["v1", "production"]
        )
        
        assert config.strategy == VersioningStrategy.HASH_BASED
        assert config.include_metadata is True
        assert config.track_lineage is True
        assert config.auto_stage is True
        assert config.tags == ["v1", "production"]
    
    def test_versioning_config_defaults(self):
        """Test versioning configuration with defaults."""
        config = VersioningConfig()
        
        assert config.strategy == VersioningStrategy.HASH_BASED
        assert config.include_metadata is True
        assert config.track_lineage is True
        assert config.auto_stage is True
        assert config.tags == []
        assert config.description is None


class TestDatasetVersion:
    """Tests for DatasetVersion class."""
    
    def test_dataset_version_creation(self):
        """Test creating dataset version."""
        version = DatasetVersion(
            version="v1.0.0",
            hash="abc123",
            timestamp=datetime.now(),
            size=1024,
            path="/data/dataset.csv",
            tags=["production"],
            description="Production dataset"
        )
        
        assert version.version == "v1.0.0"
        assert version.hash == "abc123"
        assert version.size == 1024
        assert version.path == "/data/dataset.csv"
        assert version.tags == ["production"]
        assert version.description == "Production dataset"


class TestDriftReport:
    """Tests for DriftReport class."""
    
    def test_drift_report_creation(self):
        """Test creating drift report."""
        report = DriftReport(
            source_version="v1.0.0",
            target_version="v1.1.0",
            drift_detected=True,
            drift_score=0.75,
            drift_metrics={"feature1": {"p_value": 0.01}},
            drifted_features=["feature1"],
            recommendations=["Retrain model"]
        )
        
        assert report.source_version == "v1.0.0"
        assert report.target_version == "v1.1.0"
        assert report.drift_detected is True
        assert report.drift_score == 0.75
        assert report.drift_metrics == {"feature1": {"p_value": 0.01}}
        assert report.drifted_features == ["feature1"]
        assert report.recommendations == ["Retrain model"]


class TestPipelineConfig:
    """Tests for PipelineConfig class."""
    
    def test_pipeline_config_creation(self):
        """Test creating pipeline configuration."""
        config = PipelineConfig(
            stages=[
                {
                    "name": "prepare",
                    "cmd": "python prepare.py",
                    "deps": ["data/raw"],
                    "outs": ["data/processed"]
                }
            ],
            parameters={"train_size": 0.8},
            metrics=["accuracy", "f1_score"],
            plots=["confusion_matrix"]
        )
        
        assert len(config.stages) == 1
        assert config.stages[0]["name"] == "prepare"
        assert config.parameters == {"train_size": 0.8}
        assert config.metrics == ["accuracy", "f1_score"]
        assert config.plots == ["confusion_matrix"]
    
    def test_pipeline_config_defaults(self):
        """Test pipeline configuration with defaults."""
        config = PipelineConfig()
        
        assert config.stages == []
        assert config.parameters == {}
        assert config.metrics == []
        assert config.plots == []


@skip_if_no_git
class TestDVCManager:
    """Tests for DVCManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir)
        
        # Create test data
        self.test_data = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'target': np.random.randint(0, 2, 100)
        })
        
        self.test_file = self.repo_path / "test_data.csv"
        self.test_data.to_csv(self.test_file, index=False)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('mcp_mlops_server.data.versioning.git.Repo')
    @patch('mcp_mlops_server.data.versioning.DVCRepo')
    def test_dvc_manager_initialization(self, mock_dvc_repo, mock_git_repo):
        """Test DVCManager initialization."""
        self.setUp()
        
        try:
            # Mock the repository initialization
            mock_git_repo.init.return_value = MagicMock()
            mock_dvc_repo.init.return_value = MagicMock()
            
            config = VersioningConfig(strategy=VersioningStrategy.HASH_BASED)
            manager = DVCManager(str(self.repo_path), versioning_config=config)
            
            assert manager.repo_path == self.repo_path
            assert manager.versioning_config.strategy == VersioningStrategy.HASH_BASED
            assert manager.remote_config is None
            assert manager.versions == {}
            
        finally:
            self.tearDown()
    
    @patch('mcp_mlops_server.data.versioning.git.Repo')
    @patch('mcp_mlops_server.data.versioning.DVCRepo')
    def test_dvc_manager_with_remote_config(self, mock_dvc_repo, mock_git_repo):
        """Test DVCManager with remote configuration."""
        self.setUp()
        
        try:
            # Mock the repository initialization
            mock_git_repo.init.return_value = MagicMock()
            mock_dvc_repo.init.return_value = MagicMock()
            
            remote_config = RemoteConfig(
                storage_type=RemoteStorageType.S3,
                url="s3://test-bucket/data"
            )
            
            manager = DVCManager(str(self.repo_path), remote_config=remote_config)
            
            assert manager.remote_config == remote_config
            assert manager.remote_config.storage_type == RemoteStorageType.S3
            
        finally:
            self.tearDown()
    
    @patch('mcp_mlops_server.data.versioning.git.Repo')
    @patch('mcp_mlops_server.data.versioning.DVCRepo')
    def test_version_generation_hash_based(self, mock_dvc_repo, mock_git_repo):
        """Test hash-based version generation."""
        self.setUp()
        
        try:
            # Mock the repository initialization
            mock_git_repo.init.return_value = MagicMock()
            mock_dvc_repo.init.return_value = MagicMock()
            
            config = VersioningConfig(strategy=VersioningStrategy.HASH_BASED)
            manager = DVCManager(str(self.repo_path), versioning_config=config)
            
            version = manager._generate_version(self.test_file)
            
            assert isinstance(version, str)
            assert len(version) == 8  # First 8 characters of hash
            
        finally:
            self.tearDown()
    
    @patch('mcp_mlops_server.data.versioning.git.Repo')
    @patch('mcp_mlops_server.data.versioning.DVCRepo')
    def test_version_generation_timestamp_based(self, mock_dvc_repo, mock_git_repo):
        """Test timestamp-based version generation."""
        self.setUp()
        
        try:
            # Mock the repository initialization
            mock_git_repo.init.return_value = MagicMock()
            mock_dvc_repo.init.return_value = MagicMock()
            
            config = VersioningConfig(strategy=VersioningStrategy.TIMESTAMP_BASED)
            manager = DVCManager(str(self.repo_path), versioning_config=config)
            
            version = manager._generate_version(self.test_file)
            
            assert isinstance(version, str)
            assert len(version) == 15  # YYYYMMDD_HHMMSS format
            
        finally:
            self.tearDown()
    
    @patch('mcp_mlops_server.data.versioning.git.Repo')
    @patch('mcp_mlops_server.data.versioning.DVCRepo')
    def test_version_generation_incremental(self, mock_dvc_repo, mock_git_repo):
        """Test incremental version generation."""
        self.setUp()
        
        try:
            # Mock the repository initialization
            mock_git_repo.init.return_value = MagicMock()
            mock_dvc_repo.init.return_value = MagicMock()
            
            config = VersioningConfig(strategy=VersioningStrategy.INCREMENTAL)
            manager = DVCManager(str(self.repo_path), versioning_config=config)
            
            version = manager._generate_version(self.test_file)
            
            assert version == "v1"  # First version
            
        finally:
            self.tearDown()
    
    @patch('mcp_mlops_server.data.versioning.git.Repo')
    @patch('mcp_mlops_server.data.versioning.DVCRepo')
    def test_file_hash_calculation(self, mock_dvc_repo, mock_git_repo):
        """Test file hash calculation."""
        self.setUp()
        
        try:
            # Mock the repository initialization
            mock_git_repo.init.return_value = MagicMock()
            mock_dvc_repo.init.return_value = MagicMock()
            
            manager = DVCManager(str(self.repo_path))
            
            hash1 = manager._calculate_file_hash(self.test_file)
            hash2 = manager._calculate_file_hash(self.test_file)
            
            assert isinstance(hash1, str)
            assert len(hash1) == 64  # SHA256 hash length
            assert hash1 == hash2  # Same file should have same hash
            
        finally:
            self.tearDown()
    
    @patch('mcp_mlops_server.data.versioning.git.Repo')
    @patch('mcp_mlops_server.data.versioning.DVCRepo')
    def test_file_size_calculation(self, mock_dvc_repo, mock_git_repo):
        """Test file size calculation."""
        self.setUp()
        
        try:
            # Mock the repository initialization
            mock_git_repo.init.return_value = MagicMock()
            mock_dvc_repo.init.return_value = MagicMock()
            
            manager = DVCManager(str(self.repo_path))
            
            size = manager._get_file_size(self.test_file)
            
            assert isinstance(size, int)
            assert size > 0
            
        finally:
            self.tearDown()
    
    @patch('mcp_mlops_server.data.versioning.git.Repo')
    @patch('mcp_mlops_server.data.versioning.DVCRepo')
    def test_lineage_extraction(self, mock_dvc_repo, mock_git_repo):
        """Test lineage extraction."""
        self.setUp()
        
        try:
            # Mock the repository initialization
            mock_git_repo.init.return_value = MagicMock()
            mock_dvc_repo.init.return_value = MagicMock()
            
            manager = DVCManager(str(self.repo_path))
            
            lineage = manager._extract_lineage(self.test_file)
            
            assert isinstance(lineage, dict)
            assert "created_at" in lineage
            assert "source_path" in lineage
            assert "git_commit" in lineage
            assert "git_branch" in lineage
            
        finally:
            self.tearDown()
    
    @patch('mcp_mlops_server.data.versioning.git.Repo')
    @patch('mcp_mlops_server.data.versioning.DVCRepo')
    def test_dataset_loading(self, mock_dvc_repo, mock_git_repo):
        """Test dataset loading."""
        self.setUp()
        
        try:
            # Mock the repository initialization
            mock_git_repo.init.return_value = MagicMock()
            mock_dvc_repo.init.return_value = MagicMock()
            
            manager = DVCManager(str(self.repo_path))
            
            df = manager._load_dataset(str(self.test_file))
            
            assert isinstance(df, pd.DataFrame)
            assert df.shape == (100, 3)
            assert list(df.columns) == ['feature1', 'feature2', 'target']
            
        finally:
            self.tearDown()
    
    @patch('mcp_mlops_server.data.versioning.git.Repo')
    @patch('mcp_mlops_server.data.versioning.DVCRepo')
    def test_drift_metrics_calculation(self, mock_dvc_repo, mock_git_repo):
        """Test drift metrics calculation."""
        self.setUp()
        
        try:
            # Mock the repository initialization
            mock_git_repo.init.return_value = MagicMock()
            mock_dvc_repo.init.return_value = MagicMock()
            
            manager = DVCManager(str(self.repo_path))
            
            # Create two datasets with different distributions
            df1 = pd.DataFrame({
                'feature1': np.random.normal(0, 1, 100),
                'feature2': np.random.normal(0, 1, 100),
                'category': np.random.choice(['A', 'B'], 100)
            })
            
            df2 = pd.DataFrame({
                'feature1': np.random.normal(1, 1, 100),  # Different mean
                'feature2': np.random.normal(0, 1, 100),
                'category': np.random.choice(['A', 'B'], 100)
            })
            
            drift_metrics = manager._calculate_drift_metrics(df1, df2)
            
            assert isinstance(drift_metrics, dict)
            assert 'feature1' in drift_metrics
            assert 'feature2' in drift_metrics
            assert 'category' in drift_metrics
            
            # Check that drift metrics contain expected keys
            for feature, metrics in drift_metrics.items():
                assert isinstance(metrics, dict)
                if feature in ['feature1', 'feature2']:
                    assert 'ks_statistic' in metrics
                    assert 'p_value' in metrics
                    assert 'wasserstein_distance' in metrics
                elif feature == 'category':
                    assert 'chi2_statistic' in metrics
                    assert 'p_value' in metrics
                    assert 'js_divergence' in metrics
                    
        finally:
            self.tearDown()
    
    @patch('mcp_mlops_server.data.versioning.git.Repo')
    @patch('mcp_mlops_server.data.versioning.DVCRepo')
    def test_jensen_shannon_divergence(self, mock_dvc_repo, mock_git_repo):
        """Test Jensen-Shannon divergence calculation."""
        self.setUp()
        
        try:
            # Mock the repository initialization
            mock_git_repo.init.return_value = MagicMock()
            mock_dvc_repo.init.return_value = MagicMock()
            
            manager = DVCManager(str(self.repo_path))
            
            # Test with identical distributions
            p1 = np.array([0.5, 0.5])
            p2 = np.array([0.5, 0.5])
            js_div = manager._jensen_shannon_divergence(p1, p2)
            
            assert js_div == pytest.approx(0.0, abs=1e-8)
            
            # Test with different distributions
            p1 = np.array([1.0, 0.0])
            p2 = np.array([0.0, 1.0])
            js_div = manager._jensen_shannon_divergence(p1, p2)
            
            assert js_div > 0
            
        finally:
            self.tearDown()
    
    @patch('mcp_mlops_server.data.versioning.git.Repo')
    @patch('mcp_mlops_server.data.versioning.DVCRepo')
    def test_drift_recommendations(self, mock_dvc_repo, mock_git_repo):
        """Test drift recommendations generation."""
        self.setUp()
        
        try:
            # Mock the repository initialization
            mock_git_repo.init.return_value = MagicMock()
            mock_dvc_repo.init.return_value = MagicMock()
            
            manager = DVCManager(str(self.repo_path))
            
            # Test no drift
            recommendations = manager._generate_drift_recommendations(
                drift_detected=False,
                drifted_features=[],
                drift_score=0.1
            )
            
            assert isinstance(recommendations, list)
            assert len(recommendations) > 0
            assert any("no significant" in rec.lower() for rec in recommendations)
            
            # Test high drift
            recommendations = manager._generate_drift_recommendations(
                drift_detected=True,
                drifted_features=['feature1', 'feature2'],
                drift_score=0.9
            )
            
            assert isinstance(recommendations, list)
            assert len(recommendations) > 0
            assert any("high drift" in rec.lower() for rec in recommendations)
            assert any("retraining" in rec.lower() for rec in recommendations)
            
        finally:
            self.tearDown()


class TestUtilityFunctions:
    """Tests for utility functions."""
    
    def test_initialize_dvc_repo(self):
        """Test DVC repository initialization."""
        with patch('mcp_mlops_server.data.versioning.DVCManager') as mock_manager:
            mock_manager.return_value = MagicMock()
            
            result = initialize_dvc_repo("/test/path")
            
            mock_manager.assert_called_once_with("/test/path")
            assert result is not None
    
    def test_configure_remote_storage(self):
        """Test remote storage configuration."""
        config = configure_remote_storage(
            storage_type="s3",
            url="s3://test-bucket/data",
            access_key_id="test_key",
            region="us-west-2"
        )
        
        assert isinstance(config, RemoteConfig)
        assert config.storage_type == RemoteStorageType.S3
        assert config.url == "s3://test-bucket/data"
        assert config.access_key_id == "test_key"
        assert config.region == "us-west-2"
    
    def test_create_versioning_config(self):
        """Test versioning configuration creation."""
        config = create_versioning_config(
            strategy="timestamp_based",
            include_metadata=True,
            auto_stage=False,
            tags=["test"]
        )
        
        assert isinstance(config, VersioningConfig)
        assert config.strategy == VersioningStrategy.TIMESTAMP_BASED
        assert config.include_metadata is True
        assert config.auto_stage is False
        assert config.tags == ["test"]
    
    @patch('mcp_mlops_server.data.versioning.DVCManager')
    def test_track_dataset(self, mock_manager_class):
        """Test dataset tracking."""
        mock_manager = MagicMock()
        mock_version = MagicMock()
        mock_manager.add_dataset.return_value = mock_version
        mock_manager_class.return_value = mock_manager
        
        result = track_dataset(
            data_path="/test/data.csv",
            repo_path="/test/repo",
            version="v1.0.0",
            tags=["test"]
        )
        
        mock_manager_class.assert_called_once_with("/test/repo")
        mock_manager.add_dataset.assert_called_once_with(
            "/test/data.csv",
            version="v1.0.0",
            tags=["test"]
        )
        assert result == mock_version
    
    @patch('mcp_mlops_server.data.versioning.DVCManager')
    def test_compare_dataset_versions(self, mock_manager_class):
        """Test dataset version comparison."""
        mock_manager = MagicMock()
        mock_report = MagicMock()
        mock_manager.compare_versions.return_value = mock_report
        mock_manager_class.return_value = mock_manager
        
        result = compare_dataset_versions(
            version1="v1.0.0",
            version2="v1.1.0",
            repo_path="/test/repo"
        )
        
        mock_manager_class.assert_called_once_with("/test/repo")
        mock_manager.compare_versions.assert_called_once_with("v1.0.0", "v1.1.0")
        assert result == mock_report


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_remote_config_invalid_storage_type(self):
        """Test remote config with invalid storage type."""
        # Note: Dataclasses don't validate enum values automatically
        # This test verifies that the dataclass accepts the value
        config = RemoteConfig(
            storage_type="invalid_type",
            url="test://url"
        )
        assert config.storage_type == "invalid_type"
    
    def test_versioning_config_invalid_strategy(self):
        """Test versioning config with invalid strategy."""
        # Note: Dataclasses don't validate enum values automatically
        # This test verifies that the dataclass accepts the value
        config = VersioningConfig(strategy="invalid_strategy")
        assert config.strategy == "invalid_strategy"
    
    def test_create_versioning_config_invalid_strategy(self):
        """Test utility function with invalid strategy."""
        with pytest.raises(ValueError):
            create_versioning_config(strategy="invalid_strategy")
    
    def test_configure_remote_storage_invalid_type(self):
        """Test utility function with invalid storage type."""
        with pytest.raises(ValueError):
            configure_remote_storage(
                storage_type="invalid_type",
                url="test://url"
            )


if __name__ == "__main__":
    pytest.main([__file__]) 