"""Dataset Loader Module

This module provides comprehensive dataset loading capabilities supporting various
data formats, sources, and types with automatic format detection and type inference.
"""

import json
import logging
import os
import warnings
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse
from urllib.request import urlopen

import numpy as np
import pandas as pd

# Suppress pandas warnings
warnings.filterwarnings("ignore", category=FutureWarning, module='pandas')

logger = logging.getLogger(__name__)
from sklearn.datasets import (
    load_breast_cancer,
    load_diabetes,
    load_digits,
    load_iris,
    load_wine,
    make_classification,
    make_regression,
)

from mcp_ds_toolkit_server.exceptions import DataLoadingError, DatasetNotFoundError
from mcp_ds_toolkit_server.utils.common import ensure_directory, validate_path

logger = logging.getLogger(__name__)


class DataType(Enum):
    """Enumeration of supported data types for dataset classification.
    
    This enum defines the primary data types that can be automatically
    detected and handled by the dataset loader.
    
    Attributes:
        TABULAR (str): Structured tabular data (CSV, Excel, etc.)
        TEXT (str): Text data for NLP tasks
        IMAGE (str): Image data for computer vision
        AUDIO (str): Audio data for speech/sound processing
        VIDEO (str): Video data for video analysis
        SKLEARN (str): Built-in scikit-learn datasets
        UNKNOWN (str): Unknown or undetected data type
    """
    TABULAR = "tabular"
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    SKLEARN = "sklearn"
    UNKNOWN = "unknown"


class DataFormat(Enum):
    """Enumeration of supported data formats for file loading.
    
    This enum defines the file formats that can be automatically
    detected and loaded by the dataset loader.
    
    Attributes:
        CSV (str): Comma-separated values format
        JSON (str): JavaScript Object Notation format
        PARQUET (str): Apache Parquet columnar format
        EXCEL (str): Microsoft Excel format
        TXT (str): Plain text format
        NUMPY (str): NumPy binary format
        PICKLE (str): Python pickle format
        SKLEARN (str): Built-in scikit-learn format
        UNKNOWN (str): Unknown or undetected format
    """
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"
    EXCEL = "excel"
    TXT = "txt"
    NUMPY = "numpy"
    PICKLE = "pickle"
    SKLEARN = "sklearn"
    UNKNOWN = "unknown"


@dataclass
class DatasetInfo:
    """Comprehensive metadata information about a loaded dataset.
    
    This dataclass contains all relevant metadata about a dataset including
    its structure, source, format, and content characteristics. Used throughout
    the system to maintain dataset context and enable informed processing decisions.
    
    Attributes:
        name (str): Human-readable name of the dataset
        path (Optional[str]): File system path to the dataset (if applicable)
        data_type (DataType): Detected or specified data type classification
        data_format (DataFormat): File format used for storage
        shape (Tuple[int, ...]): Dimensions of the dataset (rows, columns, etc.)
        columns (Optional[List[str]]): Column names for tabular data
        target_column (Optional[str]): Name of target variable for supervised learning
        description (Optional[str]): Human-readable description of the dataset
        source (Optional[str]): Original source location (file path, URL, etc.)
    
    Example:
        Creating dataset info for a classification dataset::
        
            info = DatasetInfo(
                name="iris",
                path="/data/iris.csv",
                data_type=DataType.TABULAR,
                data_format=DataFormat.CSV,
                shape=(150, 5),
                columns=["sepal_length", "sepal_width", "petal_length", 
                        "petal_width", "species"],
                target_column="species",
                description="Famous iris flower classification dataset",
                source="/data/iris.csv"
            )
    """
    name: str
    path: Optional[str]
    data_type: DataType
    data_format: DataFormat
    shape: Tuple[int, ...]
    columns: Optional[List[str]]
    target_column: Optional[str]
    description: Optional[str]
    source: Optional[str]
    
    def __str__(self) -> str:
        """Return a concise string representation of the dataset.
        
        Returns:
            str: String representation in format "Dataset(name, type, shape)"
        """
        return f"Dataset({self.name}, {self.data_type.value}, {self.shape})"


class DatasetLoader:
    """Core dataset loader with comprehensive multi-format and multi-source support.
    
    The DatasetLoader provides a unified interface for loading datasets from various
    sources including local files, URLs, and built-in datasets. It automatically
    detects file formats and data types, handles caching for remote resources, and
    provides consistent output format regardless of input source.
    
    This class supports a wide range of data formats and provides robust error
    handling, validation, and metadata extraction for all loaded datasets.
    
    Attributes:
        cache_dir (Path): Directory used for caching downloaded datasets
        sklearn_datasets (Dict[str, Callable]): Registry of built-in sklearn datasets
    
    Supported Operations:
        * Load from local files (CSV, JSON, Parquet, Excel, TXT, NumPy, Pickle)
        * Load from URLs with automatic caching
        * Load built-in scikit-learn datasets
        * Create synthetic datasets for testing
        * Automatic format and type detection
        * Comprehensive metadata extraction
    
    Example:
        Basic usage with different data sources::
        
            # Initialize with custom cache directory
            loader = DatasetLoader(cache_dir="./my_cache")
            
            # Load local file
            df, info = loader.load_dataset("./data/train.csv", target_column="target")
            
            # Load from URL (cached automatically)
            df, info = loader.load_dataset("https://example.com/data.csv")
            
            # Load built-in dataset
            df, info = loader.load_dataset("iris")
            
            # Create synthetic dataset
            df, info = loader.create_sample_dataset("classification", n_samples=1000)
    
    Note:
        Downloaded datasets are cached to avoid repeated downloads. The cache
        directory defaults to a project-relative location but can be customized
        or set to use temporary storage if needed.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize the dataset loader with optional cache directory.
        
        Sets up the loader with caching capabilities and initializes the registry
        of built-in datasets. Creates the cache directory if it doesn't exist,
        with fallback to temporary storage if creation fails.
        
        Args:
            cache_dir (Optional[str]): Directory to cache downloaded datasets.
                If None, uses a project-relative default path with temp fallback.
        
        Raises:
            OSError: If cache directory cannot be created and fallback fails.
        
        Example:
            Initialize with different cache configurations::
            
                # Use default cache location
                loader = DatasetLoader()
                
                # Use custom cache directory
                loader = DatasetLoader(cache_dir="/path/to/cache")
                
                # Use temporary cache (auto-cleanup)
                import tempfile
                loader = DatasetLoader(cache_dir=tempfile.mkdtemp())
        """
        if cache_dir:
            cache_path = Path(cache_dir)
        else:
            # Use project-relative path instead of absolute cwd
            project_root = Path(__file__).parent.parent.parent.parent
            cache_path = project_root / "data"
        
        # Use robust directory creation with fallback to temp
        self.cache_dir = ensure_directory(cache_path, fallback_to_temp=True)
        
        # Built-in sklearn datasets (excluding deprecated ones)
        self.sklearn_datasets = {
            'iris': load_iris,
            'wine': load_wine,
            'breast_cancer': load_breast_cancer,
            'diabetes': load_diabetes,
            'digits': load_digits,
            # Note: load_boston was removed in scikit-learn 1.2
        }
        
        logger.info(f"DatasetLoader initialized with cache_dir: {self.cache_dir}")
    
    def load_dataset(
        self,
        path_or_name: str,
        target_column: Optional[str] = None,
        **kwargs
    ) -> Tuple[pd.DataFrame, DatasetInfo]:
        """Load a dataset from various sources with automatic format detection.
        
        This is the main entry point for dataset loading. It automatically detects
        the source type (file, URL, or built-in dataset) and delegates to the
        appropriate loading method. Provides consistent output format regardless
        of input source.
        
        The method handles:
        * Local file paths with automatic format detection
        * URLs with caching and download management
        * Built-in scikit-learn dataset names
        * Comprehensive error handling and validation
        
        Args:
            path_or_name (str): Source identifier - can be:
                * Local file path (e.g., "./data/train.csv")
                * URL (e.g., "https://example.com/data.csv") 
                * Built-in dataset name (e.g., "iris", "wine", "breast_cancer")
            target_column (Optional[str]): Name of the target column for supervised
                learning tasks. If specified, this column will be marked in the
                metadata for downstream processing.
            **kwargs: Additional arguments passed to format-specific loaders:
                * For pandas.read_csv: sep, encoding, header, etc.
                * For pandas.read_json: orient, lines, etc.
                * For pandas.read_excel: sheet_name, header, etc.
                
        Returns:
            Tuple[pd.DataFrame, DatasetInfo]: A tuple containing:
                * pd.DataFrame: The loaded dataset as a pandas DataFrame
                * DatasetInfo: Comprehensive metadata about the dataset including
                  shape, columns, data type, format, source, and target information
            
        Raises:
            DataLoadingError: If the dataset cannot be loaded due to format issues,
                network problems, or other loading-related errors.
            DatasetNotFoundError: If a built-in dataset name is not recognized.
            FileNotFoundError: If a local file path does not exist.
            ValueError: If the dataset source cannot be determined or is invalid.
            
        Example:
            Load different types of datasets::
            
                loader = DatasetLoader()
                
                # Load local CSV with target column
                df, info = loader.load_dataset(
                    "train.csv", 
                    target_column="price",
                    sep=",",
                    encoding="utf-8"
                )
                
                # Load built-in dataset
                iris_df, iris_info = loader.load_dataset("iris")
                
                # Load from URL
                web_df, web_info = loader.load_dataset(
                    "https://example.com/data.json",
                    orient="records"
                )
                
                # Check loaded dataset
                print(f"Loaded {info.name}: {info.shape}")
                print(f"Columns: {info.columns}")
                print(f"Target: {info.target_column}")
        
        Note:
            URLs are automatically cached to avoid repeated downloads. The cache
            behavior can be influenced by the cache_dir parameter during
            DatasetLoader initialization.
        """
        try:
            # Check if it's a built-in sklearn dataset
            if path_or_name in self.sklearn_datasets:
                return self._load_sklearn_dataset(path_or_name, **kwargs)
            
            # Check if it's a URL
            if self._is_url(path_or_name):
                return self._load_from_url(path_or_name, target_column, **kwargs)
            
            # Load from file path
            return self._load_from_file(path_or_name, target_column, **kwargs)
            
        except Exception as e:
            logger.error(f"Failed to load dataset {path_or_name}: {str(e)}")
            raise DataLoadingError(f"Could not load dataset {path_or_name}: {str(e)}")
    
    def _load_sklearn_dataset(self, name: str, **kwargs) -> Tuple[pd.DataFrame, DatasetInfo]:
        """Load a built-in sklearn dataset."""
        logger.info(f"Loading sklearn dataset: {name}")
        
        loader_func = self.sklearn_datasets[name]
        
        try:
            # Handle deprecated boston dataset
            if name == 'boston':
                import warnings
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=FutureWarning)
                    dataset = loader_func()
            else:
                dataset = loader_func()
                
            # Convert to DataFrame
            if hasattr(dataset, 'data') and hasattr(dataset, 'target'):
                # Standard sklearn dataset format
                df = pd.DataFrame(dataset.data, columns=dataset.feature_names)
                df['target'] = dataset.target
                target_column = 'target'
            else:
                # Handle other formats
                df = pd.DataFrame(dataset)
                target_column = None
            
            info = DatasetInfo(
                name=name,
                path=None,
                data_type=DataType.SKLEARN,
                data_format=DataFormat.SKLEARN,
                shape=df.shape,
                columns=df.columns.tolist(),
                target_column=target_column,
                description=getattr(dataset, 'DESCR', f"Built-in {name} dataset"),
                source="sklearn"
            )
            
            logger.info(f"Successfully loaded sklearn dataset {name}: {info}")
            return df, info
            
        except Exception as e:
            logger.error(f"Failed to load sklearn dataset {name}: {str(e)}")
            raise ValueError(f"Could not load sklearn dataset {name}: {str(e)}")
    
    def _load_from_file(
        self,
        file_path: str,
        target_column: Optional[str] = None,
        **kwargs
    ) -> Tuple[pd.DataFrame, DatasetInfo]:
        """Load dataset from a file."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Loading dataset from file: {file_path}")
        
        # Determine format from file extension
        data_format = self._detect_format(path)
        
        # Load based on format
        if data_format == DataFormat.CSV:
            df = pd.read_csv(file_path, **kwargs)
        elif data_format == DataFormat.JSON:
            df = pd.read_json(file_path, **kwargs)
        elif data_format == DataFormat.PARQUET:
            df = pd.read_parquet(file_path, **kwargs)
        elif data_format == DataFormat.EXCEL:
            df = pd.read_excel(file_path, **kwargs)
        elif data_format == DataFormat.TXT:
            # Load as text data
            with open(file_path, 'r', encoding='utf-8') as f:
                text_data = f.read()
            df = pd.DataFrame({'text': [text_data]})
        elif data_format == DataFormat.NUMPY:
            data = np.load(file_path)
            df = pd.DataFrame(data)
        elif data_format == DataFormat.PICKLE:
            df = pd.read_pickle(file_path)
        else:
            raise DataLoadingError(f"Unsupported file format: {path.suffix}")
        
        # Detect data type
        data_type = self._detect_data_type(df)
        
        info = DatasetInfo(
            name=path.stem,
            path=str(path.absolute()),
            data_type=data_type,
            data_format=data_format,
            shape=df.shape,
            columns=df.columns.tolist(),
            target_column=target_column,
            description=f"Dataset loaded from {file_path}",
            source=str(path.absolute())
        )
        
        logger.info(f"Successfully loaded dataset from file: {info}")
        return df, info
    
    def _load_from_url(
        self,
        url: str,
        target_column: Optional[str] = None,
        **kwargs
    ) -> Tuple[pd.DataFrame, DatasetInfo]:
        """Load dataset from a URL."""
        logger.info(f"Loading dataset from URL: {url}")
        
        # Create cache filename
        parsed_url = urlparse(url)
        cache_filename = Path(parsed_url.path).name
        if not cache_filename:
            cache_filename = "dataset"
        
        cache_path = self.cache_dir / cache_filename
        
        # Download if not cached
        if not cache_path.exists():
            logger.info(f"Downloading dataset from {url} to {cache_path}")
            try:
                with urlopen(url) as response:
                    cache_path.write_bytes(response.read())
            except Exception as e:
                logger.error(f"Failed to download dataset from {url}: {str(e)}")
                raise ValueError(f"Could not download dataset from {url}: {str(e)}")
        
        # Load the cached file
        df, info = self._load_from_file(str(cache_path), target_column, **kwargs)
        
        # Update info with URL source
        info.source = url
        info.description = f"Dataset downloaded from {url}"
        
        logger.info(f"Successfully loaded dataset from URL: {info}")
        return df, info
    
    def _detect_format(self, path: Path) -> DataFormat:
        """Detect data format from file extension."""
        extension = path.suffix.lower()
        
        format_map = {
            '.csv': DataFormat.CSV,
            '.json': DataFormat.JSON,
            '.parquet': DataFormat.PARQUET,
            '.pq': DataFormat.PARQUET,
            '.xlsx': DataFormat.EXCEL,
            '.xls': DataFormat.EXCEL,
            '.txt': DataFormat.TXT,
            '.npy': DataFormat.NUMPY,
            '.npz': DataFormat.NUMPY,
            '.pkl': DataFormat.PICKLE,
            '.pickle': DataFormat.PICKLE,
        }
        
        return format_map.get(extension, DataFormat.UNKNOWN)
    
    def _detect_data_type(self, df: pd.DataFrame) -> DataType:
        """Detect data type from DataFrame content."""
        # Check if it's primarily text data
        text_columns = 0
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if contains mostly text
                sample = df[col].dropna().head(10)
                if sample.apply(lambda x: isinstance(x, str) and len(x) > 10).sum() > len(sample) * 0.5:
                    text_columns += 1
        
        if text_columns > len(df.columns) * 0.5:
            return DataType.TEXT
        
        # Default to tabular for structured data
        return DataType.TABULAR
    
    def _is_url(self, path: str) -> bool:
        """Check if path is a URL."""
        try:
            result = urlparse(path)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def list_sklearn_datasets(self) -> List[str]:
        """List all available built-in scikit-learn datasets.
        
        Returns a list of dataset names that can be used with the load_dataset
        method to load built-in datasets for experimentation and testing.
        
        Returns:
            List[str]: List of available dataset names including:
                * 'iris': Multi-class classification (150 samples, 4 features)
                * 'wine': Multi-class classification (178 samples, 13 features)
                * 'breast_cancer': Binary classification (569 samples, 30 features)
                * 'diabetes': Regression (442 samples, 10 features)
                * 'digits': Multi-class classification (1797 samples, 64 features)
        
        Example:
            Discover and load available datasets::
            
                loader = DatasetLoader()
                
                # List available datasets
                datasets = loader.list_sklearn_datasets()
                print(f"Available datasets: {datasets}")
                
                # Load each dataset
                for name in datasets:
                    df, info = loader.load_dataset(name)
                    print(f"{name}: {info.shape}")
        
        Note:
            The boston housing dataset was deprecated in scikit-learn 1.2 and
            is not included in the available datasets.
        """
        return list(self.sklearn_datasets.keys())
    
    def create_sample_dataset(
        self,
        dataset_type: str = "classification",
        n_samples: int = 1000,
        n_features: int = 20,
        **kwargs
    ) -> Tuple[pd.DataFrame, DatasetInfo]:
        """Create a synthetic dataset for testing and experimentation.
        
        Generates synthetic datasets using scikit-learn's dataset generation
        functions. Useful for testing algorithms, prototyping, and educational
        purposes when real data is not available.
        
        Args:
            dataset_type (str): Type of machine learning task. Supported values:
                * 'classification': Multi-class classification dataset
                * 'regression': Continuous target regression dataset
            n_samples (int): Number of samples (data points) to generate.
                Default is 1000.
            n_features (int): Number of input features to generate.
                Default is 20.
            **kwargs: Additional arguments for dataset generation:
                
                For classification:
                    * n_classes (int): Number of target classes. Default is 2.
                    * n_clusters_per_class (int): Number of clusters per class.
                    * random_state (int): Random seed for reproducibility.
                    
                For regression:
                    * noise (float): Standard deviation of Gaussian noise.
                      Default is 0.1.
                    * random_state (int): Random seed for reproducibility.
                
        Returns:
            Tuple[pd.DataFrame, DatasetInfo]: A tuple containing:
                * pd.DataFrame: Generated dataset with feature columns and target
                * DatasetInfo: Metadata describing the synthetic dataset
                
        Raises:
            DataLoadingError: If an unsupported dataset_type is specified.
            
        Example:
            Generate different types of synthetic datasets::
            
                loader = DatasetLoader()
                
                # Binary classification dataset
                df, info = loader.create_sample_dataset(
                    dataset_type="classification",
                    n_samples=500,
                    n_features=10,
                    n_classes=2,
                    random_state=42
                )
                
                # Multi-class classification dataset
                df, info = loader.create_sample_dataset(
                    dataset_type="classification",
                    n_samples=1000,
                    n_features=15,
                    n_classes=5,
                    random_state=42
                )
                
                # Regression dataset
                df, info = loader.create_sample_dataset(
                    dataset_type="regression",
                    n_samples=800,
                    n_features=12,
                    noise=0.2,
                    random_state=42
                )
                
                print(f"Generated {info.name}: {info.shape}")
                print(f"Target column: {info.target_column}")
        
        Note:
            The generated datasets are purely synthetic and may not reflect
            real-world data distributions. They are intended for testing and
            educational purposes only.
        """
        logger.info(f"Creating sample {dataset_type} dataset")
        
        if dataset_type == "classification":
            X, y = make_classification(
                n_samples=n_samples,
                n_features=n_features,
                n_classes=kwargs.get('n_classes', 2),
                random_state=kwargs.get('random_state', 42)
            )
        elif dataset_type == "regression":
            X, y = make_regression(
                n_samples=n_samples,
                n_features=n_features,
                noise=kwargs.get('noise', 0.1),
                random_state=kwargs.get('random_state', 42)
            )
        else:
            raise DataLoadingError(f"Unsupported dataset type: {dataset_type}")
        
        # Create DataFrame
        feature_names = [f"feature_{i}" for i in range(n_features)]
        df = pd.DataFrame(X, columns=feature_names)
        df['target'] = y
        
        info = DatasetInfo(
            name=f"sample_{dataset_type}",
            path=None,
            data_type=DataType.TABULAR,
            data_format=DataFormat.SKLEARN,
            shape=df.shape,
            columns=df.columns.tolist(),
            target_column='target',
            description=f"Sample {dataset_type} dataset with {n_samples} samples and {n_features} features",
            source="generated"
        )
        
        logger.info(f"Successfully created sample dataset: {info}")
        return df, info 