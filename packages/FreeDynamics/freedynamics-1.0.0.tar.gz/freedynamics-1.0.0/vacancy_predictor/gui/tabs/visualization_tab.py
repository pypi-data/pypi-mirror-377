"""
Visualization tab for data exploration and model evaluation visualizations
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import seaborn as sns
from typing import Optional, Dict, Any, Callable
import logging
import numpy as np

logger = logging.getLogger(__name__)

class VisualizationTab:
    """
    Tab for creating various visualizations of data and model results
    """
    
    def __init__(self, parent, visualizer, get_visualization_data_callback: Callable):
        self.parent = parent
        self.visualizer = visualizer
        self.get_visualization_data_callback = get_visualization_data_callback
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Variables
        self.chart_type_var = tk.StringVar(value="data_overview")
        self.save_path_var = tk.StringVar()
        
        # Current data
        self.current_data = None
        self.current_results = None
        self.current_model = None
        
        # Matplotlib setup
        plt.style.use('default')
        sns.set_palette("husl")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all widgets for the visualization tab"""
        
        # Main container with padding
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        # Controls section
        self.create_controls_section(main_container)
        
        # Visualization display section
        self.create_visualization_section(main_container)
    
    def create_controls_section(self, parent):
        """Create visualization controls section"""
        controls_frame = ttk.LabelFrame(parent, text="Visualization Controls", padding="10")
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Chart type selection
        chart_frame = ttk.Frame(controls_frame)
        chart_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(chart_frame, text="Chart Type:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        # Chart type options in columns
        options_frame = ttk.Frame(chart_frame)
        options_frame.pack(fill="x", pady=(5, 0))
        
        # Data exploration charts
        data_frame = ttk.LabelFrame(options_frame, text="Data Exploration", padding="5")
        data_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        data_charts = [
            ("Data Overview", "data_overview"),
            ("Target Distribution", "target_distribution"),
            ("Feature Correlation", "feature_correlation"),
            ("Missing Values", "missing_values"),
            ("Feature Distributions", "feature_distributions")
        ]
        
        for text, value in data_charts:
            ttk.Radiobutton(data_frame, text=text, variable=self.chart_type_var, 
                           value=value).pack(anchor="w")
        
        # Model evaluation charts
        model_frame = ttk.LabelFrame(options_frame, text="Model Evaluation", padding="5")
        model_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        model_charts = [
            ("Model Performance", "model_performance"),
            ("Feature Importance", "feature_importance"),
            ("Learning Curves", "learning_curves"),
            ("Algorithm Comparison", "algorithm_comparison"),
            ("Prediction vs Actual", "prediction_vs_actual")
        ]
        
        for text, value in model_charts:
            ttk.Radiobutton(model_frame, text=text, variable=self.chart_type_var, 
                           value=value).pack(anchor="w")
        
        # Action buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Generate Visualization", 
                  command=self.generate_visualization,
                  style="Action.TButton").pack(side="left")
        
        ttk.Button(button_frame, text="Save Chart", 
                  command=self.save_chart).pack(side="left", padx=(10, 0))
        
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_visualization).pack(side="left", padx=(10, 0))
        
        # Export options
        ttk.Button(button_frame, text="Export All Charts", 
                  command=self.export_all_charts).pack(side="right")
    
    def create_visualization_section(self, parent):
        """Create visualization display section"""
        viz_frame = ttk.LabelFrame(parent, text="Visualization", padding="10")
        viz_frame.pack(fill="both", expand=True)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add navigation toolbar
        toolbar_frame = ttk.Frame(viz_frame)
        toolbar_frame.pack(fill="x", pady=(5, 0))
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
        
        # Initial message
        self.show_initial_message()
    
    def show_initial_message(self):
        """Show initial message when no visualization is displayed"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, 'Select a chart type and click "Generate Visualization"', 
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        self.canvas.draw()
    
    def generate_visualization(self):
        """Generate the selected visualization"""
        chart_type = self.chart_type_var.get()
        
        # Get data
        viz_data = self.get_visualization_data_callback()
        
        if viz_data is None or viz_data['data'] is None:
            messagebox.showwarning("Warning", "No data available for visualization")
            return
        
        self.current_data = viz_data['data']
        self.current_model = viz_data.get('model')
        data_processor = viz_data.get('processor')
        
        try:
            self.fig.clear()
            
            if chart_type == "data_overview":
                self.create_data_overview()
            elif chart_type == "target_distribution":
                self.create_target_distribution(data_processor)
            elif chart_type == "feature_correlation":
                self.create_feature_correlation()
            elif chart_type == "missing_values":
                self.create_missing_values_chart()
            elif chart_type == "feature_distributions":
                self.create_feature_distributions()
            elif chart_type == "model_performance":
                self.create_model_performance_chart()
            elif chart_type == "feature_importance":
                self.create_feature_importance_chart()
            elif chart_type == "learning_curves":
                self.create_learning_curves()
            elif chart_type == "algorithm_comparison":
                self.create_algorithm_comparison()
            elif chart_type == "prediction_vs_actual":
                self.create_prediction_vs_actual()
            else:
                self.show_not_implemented(chart_type)
            
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate visualization:\n{str(e)}")
            logger.error(f"Visualization error: {str(e)}")
    
    def create_data_overview(self):
        """Create data overview visualization"""
        if self.current_data is None:
            return
        
        # Create 2x2 subplot layout
        fig = self.fig
        
        # 1. Data types distribution
        ax1 = fig.add_subplot(2, 2, 1)
        dtype_counts = self.current_data.dtypes.value_counts()
        ax1.pie(dtype_counts.values, labels=dtype_counts.index, autopct='%1.1f%%')
        ax1.set_title('Data Types Distribution')
        
        # 2. Missing values
        ax2 = fig.add_subplot(2, 2, 2)
        missing_data = self.current_data.isnull().sum()
        missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
        
        if len(missing_data) > 0:
            ax2.bar(range(len(missing_data)), missing_data.values)
            ax2.set_xticks(range(len(missing_data)))
            ax2.set_xticklabels(missing_data.index, rotation=45, ha='right')
            ax2.set_title('Missing Values by Column')
            ax2.set_ylabel('Count')
        else:
            ax2.text(0.5, 0.5, 'No Missing Values', ha='center', va='center', 
                    transform=ax2.transAxes, fontsize=12)
            ax2.set_title('Missing Values by Column')
        
        # 3. Dataset information
        ax3 = fig.add_subplot(2, 2, 3)
        ax3.axis('off')
        info_text = f"""Dataset Information:
        
Shape: {self.current_data.shape[0]} rows × {self.current_data.shape[1]} columns

Numeric Columns: {len(self.current_data.select_dtypes(include=[np.number]).columns)}
Categorical Columns: {len(self.current_data.select_dtypes(include=['object']).columns)}

Memory Usage: {self.current_data.memory_usage(deep=True).sum() / 1024**2:.2f} MB"""
        
        ax3.text(0.05, 0.95, info_text, transform=ax3.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace')
        
        # 4. Correlation heatmap for numeric columns
        ax4 = fig.add_subplot(2, 2, 4)
        numeric_data = self.current_data.select_dtypes(include=[np.number])
        
        if len(numeric_data.columns) > 1:
            corr_matrix = numeric_data.corr()
            im = ax4.imshow(corr_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
            ax4.set_xticks(range(len(corr_matrix.columns)))
            ax4.set_yticks(range(len(corr_matrix.columns)))
            ax4.set_xticklabels(corr_matrix.columns, rotation=45, ha='right')
            ax4.set_yticklabels(corr_matrix.columns)
            ax4.set_title('Correlation Matrix')
            
            # Add colorbar
            cbar = fig.colorbar(im, ax=ax4, shrink=0.8)
            cbar.set_label('Correlation')
        else:
            ax4.text(0.5, 0.5, 'Not enough numeric\ncolumns for correlation',
                    ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Correlation Matrix')
        
        fig.suptitle('Dataset Overview', fontsize=16, fontweight='bold')
        fig.tight_layout()
    
    def create_target_distribution(self, data_processor):
        """Create target variable distribution"""
        if data_processor is None or data_processor.target is None:
            self.show_no_target_message()
            return
        
        target = data_processor.target
        target_name = data_processor.target_column or "Target"
        
        fig = self.fig
        
        # Determine if target is numeric or categorical
        if target.dtype in ['int64', 'float64'] and target.nunique() > 10:
            # Numeric target - histogram and box plot
            ax1 = fig.add_subplot(1, 2, 1)
            ax1.hist(target.dropna(), bins=30, alpha=0.7, edgecolor='black', color='skyblue')
            ax1.set_title('Distribution (Histogram)')
            ax1.set_xlabel(target_name)
            ax1.set_ylabel('Frequency')
            
            ax2 = fig.add_subplot(1, 2, 2)
            ax2.boxplot(target.dropna())
            ax2.set_title('Distribution (Box Plot)')
            ax2.set_ylabel(target_name)
        else:
            # Categorical target - bar plot and pie chart
            value_counts = target.value_counts()
            
            # Bar plot
            ax1 = fig.add_subplot(1, 2, 1)
            bars = ax1.bar(range(len(value_counts)), value_counts.values, 
                          color='lightcoral', edgecolor='black')
            ax1.set_xticks(range(len(value_counts)))
            ax1.set_xticklabels(value_counts.index, rotation=45)
            ax1.set_title('Distribution (Bar Plot)')
            ax1.set_xlabel(target_name)
            ax1.set_ylabel('Count')
            
            # Add value labels on bars
            for bar, count in zip(bars, value_counts.values):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(value_counts)*0.01,
                        str(count), ha='center', va='bottom')
            
            # Pie chart
            ax2 = fig.add_subplot(1, 2, 2)
            ax2.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%')
            ax2.set_title('Distribution (Pie Chart)')
        
        fig.suptitle(f'Target Variable: {target_name}', fontsize=16, fontweight='bold')
        fig.tight_layout()
    
    def create_feature_correlation(self):
        """Create feature correlation heatmap"""
        numeric_data = self.current_data.select_dtypes(include=[np.number])
        
        if len(numeric_data.columns) < 2:
            self.show_insufficient_data_message("Need at least 2 numeric columns for correlation")
            return
        
        ax = self.fig.add_subplot(111)
        corr_matrix = numeric_data.corr()
        
        # Create heatmap
        im = ax.imshow(corr_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        
        # Set ticks and labels
        ax.set_xticks(range(len(corr_matrix.columns)))
        ax.set_yticks(range(len(corr_matrix.columns)))
        ax.set_xticklabels(corr_matrix.columns, rotation=45, ha='right')
        ax.set_yticklabels(corr_matrix.columns)
        
        # Add correlation values as text
        for i in range(len(corr_matrix.columns)):
            for j in range(len(corr_matrix.columns)):
                text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                             ha="center", va="center", color="black", fontsize=8)
        
        ax.set_title('Feature Correlation Matrix', fontsize=14, fontweight='bold')
        
        # Add colorbar
        cbar = self.fig.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Correlation Coefficient')
        
        self.fig.tight_layout()
    
    def create_missing_values_chart(self):
        """Create missing values visualization"""
        missing_data = self.current_data.isnull().sum()
        missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
        
        if len(missing_data) == 0:
            self.show_no_missing_data_message()
            return
        
        ax = self.fig.add_subplot(111)
        
        # Create bar chart
        bars = ax.bar(range(len(missing_data)), missing_data.values, 
                     color='orange', edgecolor='black')
        
        ax.set_xticks(range(len(missing_data)))
        ax.set_xticklabels(missing_data.index, rotation=45, ha='right')
        ax.set_title('Missing Values by Column', fontsize=14, fontweight='bold')
        ax.set_ylabel('Number of Missing Values')
        
        # Add percentage labels
        total_rows = len(self.current_data)
        for bar, count in zip(bars, missing_data.values):
            percentage = (count / total_rows) * 100
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(missing_data)*0.01,
                   f'{percentage:.1f}%', ha='center', va='bottom')
        
        self.fig.tight_layout()
    
    def create_feature_distributions(self):
        """Create feature distribution plots"""
        numeric_columns = self.current_data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) == 0:
            self.show_insufficient_data_message("No numeric columns found")
            return
        
        # Show first 6 numeric columns
        columns_to_plot = numeric_columns[:6]
        n_cols = min(3, len(columns_to_plot))
        n_rows = (len(columns_to_plot) + n_cols - 1) // n_cols
        
        for i, col in enumerate(columns_to_plot):
            ax = self.fig.add_subplot(n_rows, n_cols, i + 1)
            
            data = self.current_data[col].dropna()
            ax.hist(data, bins=20, alpha=0.7, edgecolor='black', color='lightgreen')
            ax.set_title(f'{col}')
            ax.set_ylabel('Frequency')
        
        self.fig.suptitle('Feature Distributions', fontsize=16, fontweight='bold')
        self.fig.tight_layout()
    
    def create_model_performance_chart(self):
        """Create model performance visualization"""
        if self.current_results is None:
            self.show_no_model_message()
            return
        
        results = self.current_results
        model_type = results.get('model_type', 'unknown')
        
        if model_type == 'regression':
            self.create_regression_performance_chart(results)
        elif model_type == 'classification':
            self.create_classification_performance_chart(results)
        else:
            self.show_insufficient_data_message(f"Unknown model type: {model_type}")
    
    def create_regression_performance_chart(self, results):
        """Create regression performance chart"""
        fig = self.fig
        
        # R² Score comparison
        ax1 = fig.add_subplot(2, 2, 1)
        scores = [results.get('train_score', 0), results.get('test_score', 0)]
        labels = ['Train', 'Test']
        colors = ['lightblue', 'lightcoral']
        
        bars = ax1.bar(labels, scores, color=colors, edgecolor='black')
        ax1.set_title('R² Score Comparison')
        ax1.set_ylabel('R² Score')
        ax1.set_ylim(0, 1)
        
        for bar, score in zip(bars, scores):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{score:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # RMSE comparison
        ax2 = fig.add_subplot(2, 2, 2)
        rmse_scores = [results.get('train_rmse', 0), results.get('test_rmse', 0)]
        bars = ax2.bar(labels, rmse_scores, color=colors, edgecolor='black')
        ax2.set_title('RMSE Comparison')
        ax2.set_ylabel('RMSE')
        
        for bar, score in zip(bars, rmse_scores):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(rmse_scores)*0.02,
                    f'{score:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # Cross-validation score
        ax3 = fig.add_subplot(2, 2, 3)
        cv_mean = results.get('cv_score_mean', 0)
        cv_std = results.get('cv_score_std', 0)
        
        ax3.bar(['CV Score'], [cv_mean], yerr=[cv_std], 
               color='lightgreen', edgecolor='black', capsize=10)
        ax3.set_title('Cross-Validation Score')
        ax3.set_ylabel('Score')
        ax3.text(0, cv_mean + cv_std + 0.02, f'{cv_mean:.3f} ± {cv_std:.3f}',
                ha='center', va='bottom', fontweight='bold')
        
        # Model information
        ax4 = fig.add_subplot(2, 2, 4)
        ax4.axis('off')
        info_text = f"""Model Performance Summary:

Algorithm: {results.get('algorithm', 'Unknown')}

Training Samples: {results.get('train_samples', 'Unknown')}
Test Samples: {results.get('test_samples', 'Unknown')}
Features: {results.get('feature_count', 'Unknown')}

Train R²: {results.get('train_score', 0):.4f}
Test R²: {results.get('test_score', 0):.4f}

CV Score: {results.get('cv_score_mean', 0):.4f} ± {results.get('cv_score_std', 0):.4f}"""
        
        ax4.text(0.05, 0.95, info_text, transform=ax4.transAxes, fontsize=9,
                verticalalignment='top', fontfamily='monospace')
        
        fig.suptitle(f'Regression Model Performance: {results["algorithm"]}', 
                    fontsize=14, fontweight='bold')
        fig.tight_layout()
    
    def create_classification_performance_chart(self, results):
        """Create classification performance chart"""
        fig = self.fig
        
        # Accuracy comparison
        ax1 = fig.add_subplot(2, 2, 1)
        scores = [results.get('train_score', 0), results.get('test_score', 0)]
        labels = ['Train', 'Test']
        colors = ['lightblue', 'lightcoral']
        
        bars = ax1.bar(labels, scores, color=colors, edgecolor='black')
        ax1.set_title('Accuracy Comparison')
        ax1.set_ylabel('Accuracy')
        ax1.set_ylim(0, 1)
        
        for bar, score in zip(bars, scores):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{score:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # Precision, Recall, F1-Score
        ax2 = fig.add_subplot(2, 2, 2)
        metrics = ['Precision', 'Recall', 'F1-Score']
        values = [results.get('precision', 0), results.get('recall', 0), results.get('f1_score', 0)]
        
        bars = ax2.bar(metrics, values, color='lightgreen', edgecolor='black')
        ax2.set_title('Performance Metrics')
        ax2.set_ylabel('Score')
        ax2.set_ylim(0, 1)
        
        for bar, value in zip(bars, values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # Cross-validation score
        ax3 = fig.add_subplot(2, 2, 3)
        cv_mean = results.get('cv_score_mean', 0)
        cv_std = results.get('cv_score_std', 0)
        
        ax3.bar(['CV Accuracy'], [cv_mean], yerr=[cv_std], 
               color='lightyellow', edgecolor='black', capsize=10)
        ax3.set_title('Cross-Validation Accuracy')
        ax3.set_ylabel('Accuracy')
        ax3.text(0, cv_mean + cv_std + 0.02, f'{cv_mean:.3f} ± {cv_std:.3f}',
                ha='center', va='bottom', fontweight='bold')
        
        # Model information
        ax4 = fig.add_subplot(2, 2, 4)
        ax4.axis('off')
        info_text = f"""Model Performance Summary:

Algorithm: {results.get('algorithm', 'Unknown')}

Training Samples: {results.get('train_samples', 'Unknown')}
Test Samples: {results.get('test_samples', 'Unknown')}
Features: {results.get('feature_count', 'Unknown')}

Test Accuracy: {results.get('test_score', 0):.4f}
Precision: {results.get('precision', 0):.4f}
Recall: {results.get('recall', 0):.4f}
F1-Score: {results.get('f1_score', 0):.4f}"""
        
        ax4.text(0.05, 0.95, info_text, transform=ax4.transAxes, fontsize=9,
                verticalalignment='top', fontfamily='monospace')
        
        fig.suptitle(f'Classification Model Performance: {results["algorithm"]}', 
                    fontsize=14, fontweight='bold')
        fig.tight_layout()
    
    def create_feature_importance_chart(self):
        """Create feature importance chart"""
        if self.current_results is None or 'feature_importance' not in self.current_results:
            self.show_no_feature_importance_message()
            return
        
        feature_importance = self.current_results['feature_importance']
        
        if not feature_importance:
            self.show_no_feature_importance_message()
            return
        
        # Get top 15 features
        top_features = feature_importance[:15]
        
        ax = self.fig.add_subplot(111)
        
        features = [item['feature'] for item in top_features]
        importances = [item['importance'] for item in top_features]
        
        # Horizontal bar plot
        bars = ax.barh(range(len(features)), importances, 
                      color='lightcoral', edgecolor='black')
        
        ax.set_yticks(range(len(features)))
        ax.set_yticklabels(features)
        ax.set_xlabel('Importance Score')
        ax.set_title('Feature Importance', fontsize=14, fontweight='bold')
        ax.invert_yaxis()  # Highest importance at top
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + max(importances)*0.01, bar.get_y() + bar.get_height()/2, 
                   f'{width:.3f}', ha='left', va='center', fontsize=9)
        
        self.fig.tight_layout()
    
    def show_not_implemented(self, chart_type):
        """Show not implemented message"""
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, f'Chart type "{chart_type}" not yet implemented', 
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
    
    def show_no_target_message(self):
        """Show no target selected message"""
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, 'No target variable selected.\nPlease select a target in the Data tab.', 
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
    
    def show_no_model_message(self):
        """Show no model message"""
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, 'No model results available.\nPlease train a model in the Training tab.', 
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
    
    def show_no_feature_importance_message(self):
        """Show no feature importance message"""
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, 'No feature importance data available.\nTrain a model that supports feature importance.', 
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
    
    def show_insufficient_data_message(self, message):
        """Show insufficient data message"""
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
    
    def show_no_missing_data_message(self):
        """Show no missing data message"""
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, 'No missing values found in the dataset!', 
                ha='center', va='center', fontsize=14, transform=ax.transAxes,
                color='green', fontweight='bold')
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
    
    def save_chart(self):
        """Save current chart to file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Chart",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg"),
                ("JPG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Chart saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save chart:\n{str(e)}")
    
    def clear_visualization(self):
        """Clear current visualization"""
        self.show_initial_message()
    
    def export_all_charts(self):
        """Export all available charts"""
        directory = filedialog.askdirectory(title="Select directory to save all charts")
        
        if not directory:
            return
        
        directory = Path(directory)
        
        try:
            charts_to_export = [
                ("data_overview", "Data Overview"),
                ("target_distribution", "Target Distribution"),
                ("feature_correlation", "Feature Correlation"),
                ("missing_values", "Missing Values"),
                ("feature_distributions", "Feature Distributions")
            ]
            
            # Add model charts if model is available
            if self.current_results:
                charts_to_export.extend([
                    ("model_performance", "Model Performance"),
                    ("feature_importance", "Feature Importance")
                ])
            
            exported_count = 0
            
            for chart_type, chart_name in charts_to_export:
                try:
                    # Generate chart
                    original_type = self.chart_type_var.get()
                    self.chart_type_var.set(chart_type)
                    self.generate_visualization()
                    
                    # Save chart
                    filename = f"{chart_name.replace(' ', '_').lower()}.png"
                    filepath = directory / filename
                    self.fig.savefig(filepath, dpi=300, bbox_inches='tight')
                    
                    exported_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to export {chart_name}: {str(e)}")
                    continue
            
            # Restore original chart type
            self.chart_type_var.set(original_type)
            self.generate_visualization()
            
            messagebox.showinfo("Export Complete", 
                               f"Exported {exported_count} charts to:\n{directory}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export charts:\n{str(e)}")
    
    def update_data(self, data):
        """Update when new data is loaded"""
        self.current_data = data
    
    def update_model_results(self, results):
        """Update when model results are available"""
        self.current_results = results
    
    def reset(self):
        """Reset the tab to initial state"""
        self.current_data = None
        self.current_results = None
        self.current_model = None
        self.chart_type_var.set("data_overview")
        self.show_initial_message()