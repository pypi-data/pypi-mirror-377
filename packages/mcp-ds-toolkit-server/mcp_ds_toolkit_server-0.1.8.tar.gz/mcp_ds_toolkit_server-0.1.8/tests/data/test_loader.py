"""
Tests for the DatasetLoader functionality.

This module tests the comprehensive dataset loading capabilities including:
- Loading built-in sklearn datasets
- Creating sample datasets
- File format detection
- Data type detection
- Error handling
"""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import numpy as np
import pandas as pd
import pytest

from mcp_ds_toolkit_server.data import DataFormat, DatasetInfo, DatasetLoader, DataType
from mcp_ds_toolkit_server.exceptions import DataLoadingError, DatasetNotFoundError


class TestDatasetLoader:
    """Test suite for DatasetLoader class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = TemporaryDirectory()
        self.loader = DatasetLoader(cache_dir=self.temp_dir.name)
    
    def teardown_method(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()
    
    def test_init(self):
        """Test DatasetLoader initialization."""
        assert isinstance(self.loader, DatasetLoader)
        assert self.loader.cache_dir.exists()
        assert len(self.loader.sklearn_datasets) > 0
    
    def test_list_sklearn_datasets(self):
        """Test listing available sklearn datasets."""
        datasets = self.loader.list_sklearn_datasets()
        assert isinstance(datasets, list)
        assert len(datasets) > 0
        assert 'iris' in datasets
        assert 'wine' in datasets
    
    def test_load_sklearn_dataset_iris(self):
        """Test loading iris dataset."""
        df, info = self.loader.load_dataset('iris')
        
        assert isinstance(df, pd.DataFrame)
        assert isinstance(info, DatasetInfo)
        assert info.name == 'iris'
        assert info.data_type == DataType.SKLEARN
        assert info.data_format == DataFormat.SKLEARN
        assert info.target_column == 'target'
        assert df.shape == (150, 5)  # 4 features + 1 target
        assert 'target' in df.columns
    
    def test_load_sklearn_dataset_wine(self):
        """Test loading wine dataset."""
        df, info = self.loader.load_dataset('wine')
        
        assert isinstance(df, pd.DataFrame)
        assert info.name == 'wine'
        assert info.data_type == DataType.SKLEARN
        assert info.target_column == 'target'
        assert df.shape == (178, 14)  # 13 features + 1 target
    
    def test_load_invalid_sklearn_dataset(self):
        """Test loading invalid sklearn dataset."""
        with pytest.raises(DataLoadingError):
            self.loader.load_dataset('invalid_dataset')
    
    def test_create_sample_classification_dataset(self):
        """Test creating sample classification dataset."""
        df, info = self.loader.create_sample_dataset(
            dataset_type="classification",
            n_samples=100,
            n_features=5
        )
        
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (100, 6)  # 5 features + 1 target
        assert info.name == 'sample_classification'
        assert info.data_type == DataType.TABULAR
        assert info.target_column == 'target'
        assert 'target' in df.columns
    
    def test_create_sample_regression_dataset(self):
        """Test creating sample regression dataset."""
        df, info = self.loader.create_sample_dataset(
            dataset_type="regression",
            n_samples=50,
            n_features=3
        )
        
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (50, 4)  # 3 features + 1 target
        assert info.name == 'sample_regression'
        assert info.data_type == DataType.TABULAR
        assert info.target_column == 'target'
    
    def test_create_invalid_sample_dataset(self):
        """Test creating invalid sample dataset."""
        with pytest.raises(DataLoadingError):
            self.loader.create_sample_dataset(dataset_type="invalid")
    
    def test_load_csv_file(self):
        """Test loading CSV file."""
        # Create a temporary CSV file
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("feature1,feature2,target\n")
            f.write("1,2,0\n")
            f.write("3,4,1\n")
            f.write("5,6,0\n")
            temp_path = f.name
        
        try:
            df, info = self.loader.load_dataset(temp_path, target_column='target')
            
            assert isinstance(df, pd.DataFrame)
            assert df.shape == (3, 3)
            assert info.data_format == DataFormat.CSV
            assert info.data_type == DataType.TABULAR
            assert info.target_column == 'target'
            assert Path(temp_path).stem == info.name
        finally:
            Path(temp_path).unlink()
    
    def test_load_json_file(self):
        """Test loading JSON file."""
        # Create a temporary JSON file
        data = [
            {"feature1": 1, "feature2": 2, "target": 0},
            {"feature1": 3, "feature2": 4, "target": 1},
            {"feature1": 5, "feature2": 6, "target": 0}
        ]
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            df, info = self.loader.load_dataset(temp_path)
            
            assert isinstance(df, pd.DataFrame)
            assert df.shape == (3, 3)
            assert info.data_format == DataFormat.JSON
            assert info.data_type == DataType.TABULAR
        finally:
            Path(temp_path).unlink()
    
    def test_load_text_file(self):
        """Test loading text file."""
        # Create a temporary text file
        with NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a sample text file for testing.")
            temp_path = f.name
        
        try:
            df, info = self.loader.load_dataset(temp_path)
            
            assert isinstance(df, pd.DataFrame)
            assert df.shape == (1, 1)
            assert info.data_format == DataFormat.TXT
            assert 'text' in df.columns
        finally:
            Path(temp_path).unlink()
    
    def test_load_nonexistent_file(self):
        """Test loading non-existent file."""
        with pytest.raises(DataLoadingError, match="Could not load dataset"):
            self.loader.load_dataset('/path/to/nonexistent/file.csv')
    
    def test_detect_format(self):
        """Test format detection."""
        assert self.loader._detect_format(Path('test.csv')) == DataFormat.CSV
        assert self.loader._detect_format(Path('test.json')) == DataFormat.JSON
        assert self.loader._detect_format(Path('test.parquet')) == DataFormat.PARQUET
        assert self.loader._detect_format(Path('test.xlsx')) == DataFormat.EXCEL
        assert self.loader._detect_format(Path('test.txt')) == DataFormat.TXT
        assert self.loader._detect_format(Path('test.unknown')) == DataFormat.UNKNOWN
    
    def test_detect_data_type(self):
        """Test data type detection."""
        # Create tabular data
        tabular_df = pd.DataFrame({
            'feature1': [1, 2, 3],
            'feature2': [4.0, 5.0, 6.0]
        })
        assert self.loader._detect_data_type(tabular_df) == DataType.TABULAR
        
        # Create text data
        text_df = pd.DataFrame({
            'text': ['This is a long text sample', 'Another text sample here']
        })
        assert self.loader._detect_data_type(text_df) == DataType.TEXT
    
    def test_is_url(self):
        """Test URL detection."""
        assert self.loader._is_url('https://example.com/data.csv')
        assert self.loader._is_url('http://example.com/data.json')
        assert not self.loader._is_url('/path/to/file.csv')
        assert not self.loader._is_url('file.csv')
        assert not self.loader._is_url('not_a_url')


class TestDatasetInfo:
    """Test suite for DatasetInfo class."""
    
    def test_dataset_info_creation(self):
        """Test DatasetInfo creation."""
        info = DatasetInfo(
            name="test_dataset",
            path="/path/to/dataset.csv",
            data_type=DataType.TABULAR,
            data_format=DataFormat.CSV,
            shape=(100, 5),
            columns=['f1', 'f2', 'f3', 'f4', 'target'],
            target_column='target',
            description="Test dataset",
            source="/path/to/dataset.csv"
        )
        
        assert info.name == "test_dataset"
        assert info.data_type == DataType.TABULAR
        assert info.data_format == DataFormat.CSV
        assert info.shape == (100, 5)
        assert info.target_column == 'target'
    
    def test_dataset_info_str(self):
        """Test DatasetInfo string representation."""
        info = DatasetInfo(
            name="test",
            path=None,
            data_type=DataType.TABULAR,
            data_format=DataFormat.CSV,
            shape=(10, 3),
            columns=None,
            target_column=None,
            description=None,
            source=None
        )
        
        str_repr = str(info)
        assert "Dataset(test, tabular, (10, 3))" == str_repr


class TestDataEnums:
    """Test suite for data enums."""
    
    def test_data_type_enum(self):
        """Test DataType enum."""
        assert DataType.TABULAR.value == "tabular"
        assert DataType.TEXT.value == "text"
        assert DataType.IMAGE.value == "image"
        assert DataType.SKLEARN.value == "sklearn"
    
    def test_data_format_enum(self):
        """Test DataFormat enum."""
        assert DataFormat.CSV.value == "csv"
        assert DataFormat.JSON.value == "json"
        assert DataFormat.PARQUET.value == "parquet"
        assert DataFormat.EXCEL.value == "excel"
        assert DataFormat.SKLEARN.value == "sklearn" 