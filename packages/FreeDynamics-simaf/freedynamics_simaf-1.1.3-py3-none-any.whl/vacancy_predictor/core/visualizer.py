"""
Visualization module for data analysis and model evaluation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Visualizer:
    """
    Handles all visualization tasks for data exploration and model evaluation
    """
    
    def __init__(self, style: str = 'seaborn-v0_8', figsize: Tuple[int, int] = (10, 6)):
        self.style = style
        self.figsize = figsize
        plt.style.use('default')  # Fallback to default if seaborn not available
        sns.set_palette("husl")
        
    def plot_data_overview(self, data: pd.DataFrame, save_path: Optional[str] = None) -> None:
        """
        Create an overview of the dataset
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Dataset Overview', fontsize=16, fontweight='bold')
        
        # 1. Data types distribution
        dtype_counts = data.dtypes.value_counts()
        axes[0, 0].pie(dtype_counts.values, labels=dtype_counts.index, autopct='%1.1f%%')
        axes[0, 0].set_title('Data Types Distribution')
        
        # 2. Missing values heatmap
        missing_data = data.isnull().sum()
        missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
        if len(missing_data) > 0:
            axes[0, 1].bar(range(len(missing_data)), missing_data.values)
            axes[0, 1].set_xticks(range(len(missing_data)))
            axes[0, 1].set_xticklabels(missing_data.index, rotation=45)
            axes[0, 1].set_title('Missing Values by Column')
            axes[0, 1].set_ylabel('Count')
        else:
            axes[0, 1].text(0.5, 0.5, 'No Missing Values', ha='center', va='center', 
                           transform=axes[0, 1].transAxes, fontsize=14)
            axes[0, 1].set_title('Missing Values by Column')
        
        # 3. Dataset shape and basic info
        info_text = f"""
        Dataset Shape: {data.shape[0]} rows × {data.shape[1]} columns
        
        Numeric Columns: {len(data.select_dtypes(include=[np.number]).columns)}
        Categorical Columns: {len(data.select_dtypes(include=['object']).columns)}
        
        Memory Usage: {data.memory_usage(deep=True).sum() / 1024**2:.2f} MB
        """
        axes[1, 0].text(0.05, 0.95, info_text, transform=axes[1, 0].transAxes,
                       fontsize=11, verticalalignment='top', fontfamily='monospace')
        axes[1, 0].set_title('Dataset Information')
        axes[1, 0].axis('off')
        
        # 4. Correlation heatmap for numeric columns
        numeric_data = data.select_dtypes(include=[np.number])
        if len(numeric_data.columns) > 1:
            corr_matrix = numeric_data.corr()
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                       square=True, ax=axes[1, 1], fmt='.2f')
            axes[1, 1].set_title('Correlation Matrix (Numeric Columns)')
        else:
            axes[1, 1].text(0.5, 0.5, 'Not enough numeric\ncolumns for correlation',
                           ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Correlation Matrix')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Data overview plot saved to: {save_path}")
        
        plt.show()
    
    def plot_target_distribution(self, target: pd.Series, target_name: str, 
                                save_path: Optional[str] = None) -> None:
        """
        Plot target variable distribution
        """
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle(f'Target Variable: {target_name}', fontsize=16, fontweight='bold')
        
        # Determine if target is numeric or categorical
        if target.dtype in ['int64', 'float64'] and target.nunique() > 10:
            # Numeric target - histogram and box plot
            axes[0].hist(target.dropna(), bins=30, alpha=0.7, edgecolor='black')
            axes[0].set_title('Distribution (Histogram)')
            axes[0].set_xlabel(target_name)
            axes[0].set_ylabel('Frequency')
            
            axes[1].boxplot(target.dropna())
            axes[1].set_title('Distribution (Box Plot)')
            axes[1].set_ylabel(target_name)
        else:
            # Categorical target - bar plot and pie chart
            value_counts = target.value_counts()
            
            # Bar plot
            value_counts.plot(kind='bar', ax=axes[0], color='skyblue', edgecolor='black')
            axes[0].set_title('Distribution (Bar Plot)')
            axes[0].set_xlabel(target_name)
            axes[0].set_ylabel('Count')
            axes[0].tick_params(axis='x', rotation=45)
            
            # Pie chart
            axes[1].pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%')
            axes[1].set_title('Distribution (Pie Chart)')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Target distribution plot saved to: {save_path}")
        
        plt.show()
    
    def plot_feature_importance(self, feature_importance: List[Dict], 
                               top_n: int = 15, save_path: Optional[str] = None) -> None:
        """
        Plot feature importance from model
        """
        if not feature_importance:
            logger.warning("No feature importance data provided")
            return
        
        # Convert to DataFrame and get top features
        importance_df = pd.DataFrame(feature_importance)
        importance_df = importance_df.head(top_n)
        
        plt.figure(figsize=(12, 8))
        
        # Horizontal bar plot
        bars = plt.barh(range(len(importance_df)), importance_df['importance'], 
                       color='lightcoral', edgecolor='black')
        
        plt.yticks(range(len(importance_df)), importance_df['feature'])
        plt.xlabel('Importance Score')
        plt.title(f'Top {top_n} Feature Importance', fontsize=16, fontweight='bold')
        plt.gca().invert_yaxis()  # Highest importance at top
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(width + 0.001, bar.get_y() + bar.get_height()/2, 
                    f'{width:.3f}', ha='left', va='center', fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Feature importance plot saved to: {save_path}")
        
        plt.show()
    
    def plot_model_performance(self, results: Dict[str, Any], 
                              save_path: Optional[str] = None) -> None:
        """
        Plot model performance metrics
        """
        model_type = results.get('model_type', 'unknown')
        
        if model_type == 'regression':
            self._plot_regression_performance(results, save_path)
        elif model_type == 'classification':
            self._plot_classification_performance(results, save_path)
        else:
            logger.warning(f"Unknown model type: {model_type}")
    
    def _plot_regression_performance(self, results: Dict[str, Any], 
                                   save_path: Optional[str] = None) -> None:
        """
        Plot regression model performance
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Regression Model Performance: {results["algorithm"]}', 
                    fontsize=16, fontweight='bold')
        
        # 1. R² Score comparison
        scores = [results.get('train_score', 0), results.get('test_score', 0)]
        score_labels = ['Train', 'Test']
        colors = ['lightblue', 'lightcoral']
        
        bars = axes[0, 0].bar(score_labels, scores, color=colors, edgecolor='black')
        axes[0, 0].set_title('R² Score Comparison')
        axes[0, 0].set_ylabel('R² Score')
        axes[0, 0].set_ylim(0, 1)
        
        # Add value labels
        for bar, score in zip(bars, scores):
            axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                           f'{score:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # 2. RMSE comparison
        rmse_scores = [results.get('train_rmse', 0), results.get('test_rmse', 0)]
        bars = axes[0, 1].bar(score_labels, rmse_scores, color=colors, edgecolor='black')
        axes[0, 1].set_title('RMSE Comparison')
        axes[0, 1].set_ylabel('RMSE')
        
        for bar, score in zip(bars, rmse_scores):
            axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(rmse_scores)*0.02,
                           f'{score:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # 3. Cross-validation scores
        cv_mean = results.get('cv_score_mean', 0)
        cv_std = results.get('cv_score_std', 0)
        
        axes[1, 0].bar(['CV Score'], [cv_mean], yerr=[cv_std], 
                      color='lightgreen', edgecolor='black', capsize=10)
        axes[1, 0].set_title('Cross-Validation Score')
        axes[1, 0].set_ylabel('Score')
        axes[1, 0].text(0, cv_mean + cv_std + 0.02, f'{cv_mean:.3f} ± {cv_std:.3f}',
                       ha='center', va='bottom', fontweight='bold')
        
        # 4. Model information
        info_text = f"""
        Algorithm: {results.get('algorithm', 'Unknown')}
        
        Training Samples: {results.get('train_samples', 'Unknown')}
        Test Samples: {results.get('test_samples', 'Unknown')}
        Features: {results.get('feature_count', 'Unknown')}
        
        Train R²: {results.get('train_score', 0):.4f}
        Test R²: {results.get('test_score', 0):.4f}
        
        Train RMSE: {results.get('train_rmse', 0):.4f}
        Test RMSE: {results.get('test_rmse', 0):.4f}
        
        CV Score: {results.get('cv_score_mean', 0):.4f} ± {results.get('cv_score_std', 0):.4f}
        """
        
        axes[1, 1].text(0.05, 0.95, info_text, transform=axes[1, 1].transAxes,
                       fontsize=11, verticalalignment='top', fontfamily='monospace')
        axes[1, 1].set_title('Model Summary')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Regression performance plot saved to: {save_path}")
        
        plt.show()
    
    def _plot_classification_performance(self, results: Dict[str, Any], 
                                       save_path: Optional[str] = None) -> None:
        """
        Plot classification model performance
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Classification Model Performance: {results["algorithm"]}', 
                    fontsize=16, fontweight='bold')
        
        # 1. Accuracy comparison
        scores = [results.get('train_score', 0), results.get('test_score', 0)]
        score_labels = ['Train', 'Test']
        colors = ['lightblue', 'lightcoral']
        
        bars = axes[0, 0].bar(score_labels, scores, color=colors, edgecolor='black')
        axes[0, 0].set_title('Accuracy Comparison')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].set_ylim(0, 1)
        
        for bar, score in zip(bars, scores):
            axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                           f'{score:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # 2. Precision, Recall, F1-Score
        metrics = ['Precision', 'Recall', 'F1-Score']
        values = [results.get('precision', 0), results.get('recall', 0), results.get('f1_score', 0)]
        
        bars = axes[0, 1].bar(metrics, values, color='lightgreen', edgecolor='black')
        axes[0, 1].set_title('Performance Metrics')
        axes[0, 1].set_ylabel('Score')
        axes[0, 1].set_ylim(0, 1)
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        for bar, value in zip(bars, values):
            axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                           f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # 3. Cross-validation scores
        cv_mean = results.get('cv_score_mean', 0)
        cv_std = results.get('cv_score_std', 0)
        
        axes[1, 0].bar(['CV Accuracy'], [cv_mean], yerr=[cv_std], 
                      color='lightyellow', edgecolor='black', capsize=10)
        axes[1, 0].set_title('Cross-Validation Accuracy')
        axes[1, 0].set_ylabel('Accuracy')
        axes[1, 0].text(0, cv_mean + cv_std + 0.02, f'{cv_mean:.3f} ± {cv_std:.3f}',
                       ha='center', va='bottom', fontweight='bold')
        
        # 4. Model information
        info_text = f"""
        Algorithm: {results.get('algorithm', 'Unknown')}
        
        Training Samples: {results.get('train_samples', 'Unknown')}
        Test Samples: {results.get('test_samples', 'Unknown')}
        Features: {results.get('feature_count', 'Unknown')}
        
        Train Accuracy: {results.get('train_score', 0):.4f}
        Test Accuracy: {results.get('test_score', 0):.4f}
        
        Precision: {results.get('precision', 0):.4f}
        Recall: {results.get('recall', 0):.4f}
        F1-Score: {results.get('f1_score', 0):.4f}
        
        CV Accuracy: {results.get('cv_score_mean', 0):.4f} ± {results.get('cv_score_std', 0):.4f}
        """
        
        axes[1, 1].text(0.05, 0.95, info_text, transform=axes[1, 1].transAxes,
                       fontsize=11, verticalalignment='top', fontfamily='monospace')
        axes[1, 1].set_title('Model Summary')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Classification performance plot saved to: {save_path}")
        
        plt.show()
    
    def plot_algorithm_comparison(self, comparison_df: pd.DataFrame, 
                                 save_path: Optional[str] = None) -> None:
        """
        Plot comparison of different algorithms
        """
        if comparison_df.empty:
            logger.warning("No comparison data provided")
            return
        
        plt.figure(figsize=(14, 8))
        
        # Sort by test score
        comparison_df_sorted = comparison_df.sort_values('test_score', ascending=True)
        
        # Create horizontal bar plot
        bars = plt.barh(range(len(comparison_df_sorted)), 
                       comparison_df_sorted['test_score'],
                       color='skyblue', edgecolor='black')
        
        plt.yticks(range(len(comparison_df_sorted)), comparison_df_sorted['algorithm'])
        plt.xlabel('Test Score')
        plt.title('Algorithm Performance Comparison', fontsize=16, fontweight='bold')
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(width + 0.005, bar.get_y() + bar.get_height()/2, 
                    f'{width:.3f}', ha='left', va='center', fontweight='bold')
        
        # Add vertical line for average performance
        avg_score = comparison_df_sorted['test_score'].mean()
        plt.axvline(x=avg_score, color='red', linestyle='--', alpha=0.7, 
                   label=f'Average: {avg_score:.3f}')
        plt.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Algorithm comparison plot saved to: {save_path}")
        
        plt.show()
    
    def plot_learning_curves(self, model, X, y, save_path: Optional[str] = None) -> None:
        """
        Plot learning curves to analyze model performance vs training size
        """
        from sklearn.model_selection import learning_curve
        
        plt.figure(figsize=(12, 6))
        
        train_sizes, train_scores, val_scores = learning_curve(
            model, X, y, cv=5, n_jobs=-1, 
            train_sizes=np.linspace(0.1, 1.0, 10),
            scoring='r2' if hasattr(model, 'predict') else 'accuracy'
        )
        
        # Calculate mean and std
        train_mean = np.mean(train_scores, axis=1)
        train_std = np.std(train_scores, axis=1)
        val_mean = np.mean(val_scores, axis=1)
        val_std = np.std(val_scores, axis=1)
        
        # Plot learning curves
        plt.plot(train_sizes, train_mean, 'o-', color='blue', label='Training Score')
        plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, 
                        alpha=0.1, color='blue')
        
        plt.plot(train_sizes, val_mean, 'o-', color='red', label='Validation Score')
        plt.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, 
                        alpha=0.1, color='red')
        
        plt.xlabel('Training Set Size')
        plt.ylabel('Score')
        plt.title('Learning Curves', fontsize=16, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Learning curves plot saved to: {save_path}")
        
        plt.show()
    
    def create_model_report(self, results: Dict[str, Any], 
                           feature_importance: Optional[List[Dict]] = None,
                           save_path: Optional[str] = None) -> None:
        """
        Create a comprehensive model report with multiple visualizations
        """
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 16))
        
        # Plot model performance
        self.plot_model_performance(results)
        
        # Plot feature importance if available
        if feature_importance:
            self.plot_feature_importance(feature_importance)
        
        logger.info("Model report generated successfully")