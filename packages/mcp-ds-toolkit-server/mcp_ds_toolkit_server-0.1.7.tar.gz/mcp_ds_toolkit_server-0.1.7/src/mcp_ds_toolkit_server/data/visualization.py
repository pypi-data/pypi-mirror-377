"""
Data Visualization Module

This module provides comprehensive data visualization capabilities for
exploratory data analysis, model evaluation, and reporting.
"""

import base64
import io
import logging
import warnings
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Suppress matplotlib warnings
warnings.filterwarnings("ignore", category=UserWarning, module='matplotlib')

logger = logging.getLogger(__name__)


class PlotType(Enum):
    """Types of plots available."""
    HISTOGRAM = "histogram"
    BOXPLOT = "boxplot"
    SCATTERPLOT = "scatterplot"
    CORRELATION_HEATMAP = "correlation_heatmap"
    PAIRPLOT = "pairplot"
    DISTRIBUTION = "distribution"
    COUNTPLOT = "countplot"
    BARPLOT = "barplot"
    LINEPLOT = "lineplot"
    VIOLIN = "violin"
    CONFUSION_MATRIX = "confusion_matrix"
    ROC_CURVE = "roc_curve"
    LEARNING_CURVE = "learning_curve"
    FEATURE_IMPORTANCE = "feature_importance"


class ColorPalette(Enum):
    """Color palettes for plots."""
    DEFAULT = "default"
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    SEABORN = "Set1"
    COLORBLIND = "colorblind"
    PASTEL = "pastel"


@dataclass
class PlotConfig:
    """Configuration for plots."""
    figsize: Tuple[int, int] = (10, 6)
    dpi: int = 100
    style: str = "whitegrid"
    palette: ColorPalette = ColorPalette.DEFAULT
    title: Optional[str] = None
    xlabel: Optional[str] = None
    ylabel: Optional[str] = None
    save_path: Optional[str] = None
    show_plot: bool = False
    return_base64: bool = True  # Return plot as base64 string for web display


@dataclass
class PlotResult:
    """Result of a plotting operation."""
    plot_type: PlotType
    title: str
    base64_image: Optional[str] = None
    file_path: Optional[str] = None
    description: str = ""
    insights: List[str] = None
    
    def __post_init__(self):
        if self.insights is None:
            self.insights = []


class DataVisualizer:
    """Comprehensive data visualization toolkit."""
    
    def __init__(self, style: str = "whitegrid", palette: str = "Set1"):
        """Initialize visualizer with style settings.
        
        Args:
            style: Seaborn style (whitegrid, darkgrid, white, dark, ticks)
            palette: Color palette
        """
        self.style = style
        self.palette = palette
        
        # Set default style
        sns.set_style(style)
        sns.set_palette(palette)
        
        # Configure matplotlib for better quality
        plt.rcParams['figure.dpi'] = 100
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['font.size'] = 10
        
        logger.info("DataVisualizer initialized")
    
    def _setup_plot(self, config: PlotConfig) -> plt.Figure:
        """Set up plot with configuration."""
        if config.style != self.style:
            sns.set_style(config.style)
        
        fig, ax = plt.subplots(figsize=config.figsize, dpi=config.dpi)
        
        if config.title:
            ax.set_title(config.title, fontsize=14, fontweight='bold')
        if config.xlabel:
            ax.set_xlabel(config.xlabel)
        if config.ylabel:
            ax.set_ylabel(config.ylabel)
        
        return fig
    
    def _finalize_plot(self, fig: plt.Figure, config: PlotConfig, plot_type: PlotType) -> PlotResult:
        """Finalize plot and return result."""
        plt.tight_layout()
        
        base64_image = None
        file_path = None
        
        # Save or convert to base64
        if config.return_base64:
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', bbox_inches='tight', dpi=config.dpi)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            base64_image = f"data:image/png;base64,{image_base64}"
            buffer.close()
        
        if config.save_path:
            fig.savefig(config.save_path, bbox_inches='tight', dpi=config.dpi)
            file_path = config.save_path
        
        if config.show_plot:
            plt.show()
        else:
            plt.close(fig)
        
        return PlotResult(
            plot_type=plot_type,
            title=config.title or plot_type.value.replace('_', ' ').title(),
            base64_image=base64_image,
            file_path=file_path
        )
    
    def plot_histogram(
        self, 
        data: pd.Series, 
        bins: int = 30, 
        config: PlotConfig = None
    ) -> PlotResult:
        """Create histogram plot."""
        if config is None:
            config = PlotConfig()
        
        fig = self._setup_plot(config)
        
        plt.hist(data.dropna(), bins=bins, alpha=0.7, edgecolor='black')
        
        # Add statistics
        mean_val = data.mean()
        median_val = data.median()
        plt.axvline(mean_val, color='red', linestyle='--', label=f'Mean: {mean_val:.2f}')
        plt.axvline(median_val, color='green', linestyle='--', label=f'Median: {median_val:.2f}')
        plt.legend()
        
        result = self._finalize_plot(fig, config, PlotType.HISTOGRAM)
        result.insights = [
            f"Mean: {mean_val:.2f}",
            f"Median: {median_val:.2f}",
            f"Standard deviation: {data.std():.2f}",
            f"Skewness: {data.skew():.2f}"
        ]
        
        return result
    
    def plot_boxplot(
        self, 
        data: Union[pd.Series, pd.DataFrame], 
        groupby: Optional[str] = None,
        config: PlotConfig = None
    ) -> PlotResult:
        """Create box plot."""
        if config is None:
            config = PlotConfig()
        
        fig = self._setup_plot(config)
        
        if isinstance(data, pd.DataFrame) and groupby:
            sns.boxplot(data=data, y=data.columns[0], x=groupby)
        else:
            sns.boxplot(y=data)
        
        result = self._finalize_plot(fig, config, PlotType.BOXPLOT)
        
        if isinstance(data, pd.Series):
            q1 = data.quantile(0.25)
            q3 = data.quantile(0.75)
            iqr = q3 - q1
            outliers = data[(data < q1 - 1.5*iqr) | (data > q3 + 1.5*iqr)]
            
            result.insights = [
                f"Q1 (25th percentile): {q1:.2f}",
                f"Q3 (75th percentile): {q3:.2f}",
                f"IQR: {iqr:.2f}",
                f"Number of outliers: {len(outliers)}"
            ]
        
        return result
    
    def plot_correlation_heatmap(
        self, 
        data: pd.DataFrame, 
        method: str = "pearson",
        config: PlotConfig = None
    ) -> PlotResult:
        """Create correlation heatmap."""
        if config is None:
            config = PlotConfig(figsize=(12, 8))
        
        fig = self._setup_plot(config)
        
        # Calculate correlation matrix
        numeric_data = data.select_dtypes(include=[np.number])
        corr_matrix = numeric_data.corr(method=method)
        
        # Create heatmap
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(
            corr_matrix, 
            mask=mask, 
            annot=True, 
            cmap='coolwarm', 
            center=0,
            square=True,
            fmt='.2f'
        )
        
        result = self._finalize_plot(fig, config, PlotType.CORRELATION_HEATMAP)
        
        # Find strong correlations
        strong_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    strong_corr.append(f"{corr_matrix.columns[i]} - {corr_matrix.columns[j]}: {corr_val:.2f}")
        
        result.insights = [
            f"Correlation method: {method}",
            f"Number of numeric variables: {len(numeric_data.columns)}",
            f"Strong correlations (|r| > 0.7): {len(strong_corr)}"
        ] + strong_corr[:5]  # Show top 5 strong correlations
        
        return result
    
    def plot_scatterplot(
        self, 
        data: pd.DataFrame, 
        x: str, 
        y: str, 
        hue: Optional[str] = None,
        config: PlotConfig = None
    ) -> PlotResult:
        """Create scatter plot."""
        if config is None:
            config = PlotConfig()
        
        fig = self._setup_plot(config)
        
        sns.scatterplot(data=data, x=x, y=y, hue=hue, alpha=0.7)
        
        # Add regression line if no hue
        if hue is None:
            sns.regplot(data=data, x=x, y=y, scatter=False, color='red')
        
        result = self._finalize_plot(fig, config, PlotType.SCATTERPLOT)
        
        # Calculate correlation
        if hue is None:
            correlation = data[x].corr(data[y])
            result.insights = [
                f"Correlation between {x} and {y}: {correlation:.3f}",
                f"Sample size: {len(data)}",
                f"Relationship strength: {'Strong' if abs(correlation) > 0.7 else 'Moderate' if abs(correlation) > 0.3 else 'Weak'}"
            ]
        
        return result
    
    def plot_distribution(
        self, 
        data: pd.Series, 
        plot_type: str = "hist",
        config: PlotConfig = None
    ) -> PlotResult:
        """Create distribution plot."""
        if config is None:
            config = PlotConfig()
        
        fig = self._setup_plot(config)
        
        if plot_type == "hist":
            sns.histplot(data=data, kde=True)
        elif plot_type == "kde":
            sns.kdeplot(data=data, fill=True)
        elif plot_type == "box":
            sns.boxplot(y=data)
        else:
            sns.histplot(data=data, kde=True)
        
        result = self._finalize_plot(fig, config, PlotType.DISTRIBUTION)
        
        result.insights = [
            f"Mean: {data.mean():.2f}",
            f"Median: {data.median():.2f}",
            f"Standard deviation: {data.std():.2f}",
            f"Skewness: {data.skew():.2f}",
            f"Kurtosis: {data.kurtosis():.2f}"
        ]
        
        return result
    
    def plot_feature_importance(
        self, 
        importance_dict: Dict[str, float], 
        top_n: int = 15,
        config: PlotConfig = None
    ) -> PlotResult:
        """Create feature importance plot."""
        if config is None:
            config = PlotConfig(figsize=(10, 8))
        
        fig = self._setup_plot(config)
        
        # Sort by importance
        sorted_features = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
        top_features = dict(list(sorted_features.items())[:top_n])
        
        # Create horizontal bar plot
        features = list(top_features.keys())
        importances = list(top_features.values())
        
        plt.barh(range(len(features)), importances)
        plt.yticks(range(len(features)), features)
        plt.xlabel('Importance')
        plt.gca().invert_yaxis()  # Highest importance at top
        
        result = self._finalize_plot(fig, config, PlotType.FEATURE_IMPORTANCE)
        
        result.insights = [
            f"Most important feature: {features[0]} ({importances[0]:.3f})",
            f"Least important (in top {top_n}): {features[-1]} ({importances[-1]:.3f})",
            f"Total features shown: {len(features)}",
            f"Importance range: {min(importances):.3f} - {max(importances):.3f}"
        ]
        
        return result
    
    def plot_confusion_matrix(
        self, 
        cm: np.ndarray, 
        class_names: List[str] = None,
        config: PlotConfig = None
    ) -> PlotResult:
        """Create confusion matrix heatmap."""
        if config is None:
            config = PlotConfig(figsize=(8, 6))
        
        fig = self._setup_plot(config)
        
        # Create heatmap
        sns.heatmap(
            cm, 
            annot=True, 
            fmt='d', 
            cmap='Blues',
            xticklabels=class_names if class_names else range(cm.shape[1]),
            yticklabels=class_names if class_names else range(cm.shape[0])
        )
        
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        
        result = self._finalize_plot(fig, config, PlotType.CONFUSION_MATRIX)
        
        # Calculate metrics
        total = cm.sum()
        accuracy = np.trace(cm) / total
        
        result.insights = [
            f"Total predictions: {total}",
            f"Accuracy: {accuracy:.3f}",
            f"Number of classes: {cm.shape[0]}"
        ]
        
        return result
    
    def create_dashboard(
        self, 
        data: pd.DataFrame, 
        target_column: Optional[str] = None,
        save_path: Optional[str] = None
    ) -> List[PlotResult]:
        """Create a comprehensive data dashboard."""
        logger.info("Creating comprehensive data dashboard")
        
        plots = []
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Remove target from feature lists
        if target_column:
            if target_column in numeric_cols:
                numeric_cols.remove(target_column)
            if target_column in categorical_cols:
                categorical_cols.remove(target_column)
        
        # 1. Dataset overview (correlation heatmap)
        if len(numeric_cols) > 1:
            plots.append(self.plot_correlation_heatmap(
                data[numeric_cols], 
                config=PlotConfig(title="Feature Correlation Matrix")
            ))
        
        # 2. Target distribution (if provided)
        if target_column and target_column in data.columns:
            if data[target_column].dtype in ['object', 'category'] or data[target_column].nunique() < 10:
                # Categorical target
                target_counts = data[target_column].value_counts()
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.bar(target_counts.index, target_counts.values)
                ax.set_title(f'Distribution of {target_column}')
                ax.set_ylabel('Count')
                plots.append(self._finalize_plot(fig, PlotConfig(), PlotType.COUNTPLOT))
            else:
                # Numeric target
                plots.append(self.plot_distribution(
                    data[target_column], 
                    config=PlotConfig(title=f'Distribution of {target_column}')
                ))
        
        # 3. Feature distributions (top 4 numeric features)
        for col in numeric_cols[:4]:
            plots.append(self.plot_histogram(
                data[col], 
                config=PlotConfig(title=f'Distribution of {col}')
            ))
        
        # 4. Feature relationships with target (if numeric)
        if target_column and target_column in numeric_cols + [target_column]:
            for col in numeric_cols[:3]:
                plots.append(self.plot_scatterplot(
                    data, 
                    x=col, 
                    y=target_column,
                    config=PlotConfig(title=f'{col} vs {target_column}')
                ))
        
        logger.info(f"Dashboard created with {len(plots)} plots")
        return plots


# Utility functions
def quick_eda(data: pd.DataFrame, target_column: Optional[str] = None) -> List[PlotResult]:
    """Quick exploratory data analysis with essential plots.
    
    Args:
        data: DataFrame to analyze
        target_column: Target variable name
        
    Returns:
        List of plot results
    """
    visualizer = DataVisualizer()
    return visualizer.create_dashboard(data, target_column)


def save_plots_to_html(plots: List[PlotResult], output_path: str) -> None:
    """Save multiple plots to an HTML report.
    
    Args:
        plots: List of plot results
        output_path: Path to save HTML file
    """
    html_content = """
    <html>
    <head>
        <title>Data Analysis Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .plot-container { margin: 20px 0; text-align: center; }
            .plot-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; }
            .plot-insights { text-align: left; margin: 10px 0; }
            .insights-list { padding-left: 20px; }
        </style>
    </head>
    <body>
        <h1>Data Analysis Report</h1>
    """
    
    for plot in plots:
        if plot.base64_image:
            html_content += f"""
            <div class="plot-container">
                <div class="plot-title">{plot.title}</div>
                <img src="{plot.base64_image}" alt="{plot.title}" style="max-width: 100%; height: auto;">
                <div class="plot-insights">
                    <strong>Insights:</strong>
                    <ul class="insights-list">
            """
            
            for insight in plot.insights:
                html_content += f"<li>{insight}</li>\n"
            
            html_content += "</ul></div></div>\n"
    
    html_content += """
    </body>
    </html>
    """
    
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    logger.info(f"HTML report saved to {output_path}")