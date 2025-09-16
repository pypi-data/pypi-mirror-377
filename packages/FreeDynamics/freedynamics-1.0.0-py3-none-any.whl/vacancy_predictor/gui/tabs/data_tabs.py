"""
Data tab for loading and exploring data
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from typing import Callable, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DataTab:
    """
    Tab for data loading, exploration and preprocessing
    """
    
    def __init__(self, parent, data_processor, data_loaded_callback: Callable):
        self.parent = parent
        self.data_processor = data_processor
        self.data_loaded_callback = data_loaded_callback
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Variables
        self.file_path_var = tk.StringVar()
        self.data_info_var = tk.StringVar()
        self.data_info_var.set("No data loaded")
        
        # Current data reference
        self.current_data = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all widgets for the data tab"""
        
        # Main container with padding
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        # File loading section
        self.create_file_section(main_container)
        
        # Data information section
        self.create_info_section(main_container)
        
        # Data preview section
        self.create_preview_section(main_container)
        
        # Column selection section
        self.create_column_section(main_container)
    
    def create_file_section(self, parent):
        """Create file loading section"""
        file_frame = ttk.LabelFrame(parent, text="Load Data File", padding="10")
        file_frame.pack(fill="x", pady=(0, 10))
        
        # File path frame
        path_frame = ttk.Frame(file_frame)
        path_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(path_frame, text="File:").pack(side="left")
        
        file_entry = ttk.Entry(path_frame, textvariable=self.file_path_var, state="readonly")
        file_entry.pack(side="left", fill="x", expand=True, padx=(5, 5))
        
        ttk.Button(path_frame, text="Browse", command=self.browse_file).pack(side="right")
        
        # File info and actions
        action_frame = ttk.Frame(file_frame)
        action_frame.pack(fill="x")
        
        ttk.Button(action_frame, text="Load Data", 
                  command=self.load_data, style="Action.TButton").pack(side="left")
        
        ttk.Button(action_frame, text="Convert Dump to CSV", 
                  command=self.convert_dump_to_csv).pack(side="left", padx=(10, 0))
        
        # Supported formats info
        formats_text = "Supported formats: .csv, .xlsx, .xls, .json, .jsonl, .pkl, .dump"
        ttk.Label(file_frame, text=formats_text, font=("Arial", 8), 
                 foreground="gray").pack(anchor="w", pady=(5, 0))
    
    def create_info_section(self, parent):
        """Create data information section"""
        info_frame = ttk.LabelFrame(parent, text="Data Information", padding="10")
        info_frame.pack(fill="x", pady=(0, 10))
        
        # Data info display
        info_text = tk.Text(info_frame, height=6, wrap="word", state="disabled")
        info_text.pack(fill="x")
        
        self.info_text = info_text
        
        # Action buttons
        button_frame = ttk.Frame(info_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="Refresh Info", 
                  command=self.refresh_data_info).pack(side="left")
        
        ttk.Button(button_frame, text="Validate Data", 
                  command=self.validate_data).pack(side="left", padx=(10, 0))
        
        ttk.Button(button_frame, text="Export to CSV", 
                  command=self.export_to_csv).pack(side="right")
    
    def create_preview_section(self, parent):
        """Create data preview section"""
        preview_frame = ttk.LabelFrame(parent, text="Data Preview", padding="10")
        preview_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create treeview for data preview
        columns = ("Column 1", "Column 2", "Column 3", "Column 4", "Column 5")
        
        self.tree = ttk.Treeview(preview_frame, columns=columns, show="headings", height=8)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(preview_frame, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack everything
        self.tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
    
    def create_column_section(self, parent):
        """Create column selection section"""
        column_frame = ttk.LabelFrame(parent, text="Feature & Target Selection", padding="10")
        column_frame.pack(fill="x")
        
        # Split into two columns
        left_frame = ttk.Frame(column_frame)
        left_frame.pack(side="left", fill="both", expand=True)
        
        right_frame = ttk.Frame(column_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(20, 0))
        
        # Features selection
        ttk.Label(left_frame, text="Select Features:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        # Features listbox with scrollbar
        features_frame = ttk.Frame(left_frame)
        features_frame.pack(fill="both", expand=True, pady=(5, 0))
        
        self.features_listbox = tk.Listbox(features_frame, selectmode="multiple", height=6)
        features_scroll = ttk.Scrollbar(features_frame, orient="vertical")
        
        self.features_listbox.configure(yscrollcommand=features_scroll.set)
        features_scroll.configure(command=self.features_listbox.yview)
        
        self.features_listbox.pack(side="left", fill="both", expand=True)
        features_scroll.pack(side="right", fill="y")
        
        # Features buttons
        features_btn_frame = ttk.Frame(left_frame)
        features_btn_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Button(features_btn_frame, text="Select All", 
                  command=self.select_all_features).pack(side="left")
        ttk.Button(features_btn_frame, text="Clear All", 
                  command=self.clear_all_features).pack(side="left", padx=(5, 0))
        
        # Target selection
        ttk.Label(right_frame, text="Select Target:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.target_var = tk.StringVar()
        self.target_combo = ttk.Combobox(right_frame, textvariable=self.target_var, 
                                        state="readonly", width=25)
        self.target_combo.pack(anchor="w", pady=(5, 10))
        
        # Action buttons
        action_btn_frame = ttk.Frame(right_frame)
        action_btn_frame.pack(anchor="w")
        
        ttk.Button(action_btn_frame, text="Set Features & Target", 
                  command=self.set_features_target, 
                  style="Success.TButton").pack(anchor="w")
        
        ttk.Button(action_btn_frame, text="Preprocess Data", 
                  command=self.preprocess_data).pack(anchor="w", pady=(5, 0))
    
    def browse_file(self):
        """Browse for data file"""
        file_types = [
            ("All supported", "*.csv *.xlsx *.xls *.json *.jsonl *.pkl *.dump"),
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx *.xls"),
            ("JSON files", "*.json *.jsonl"),
            ("Pickle files", "*.pkl"),
            ("Dump files", "*.dump"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select data file",
            filetypes=file_types
        )
        
        if file_path:
            self.file_path_var.set(file_path)
    
    def load_data(self):
        """Load data from selected file"""
        file_path = self.file_path_var.get()
        
        if not file_path:
            messagebox.showwarning("Warning", "Please select a file first")
            return
        
        if not Path(file_path).exists():
            messagebox.showerror("Error", "File not found")
            return
        
        try:
            # Load data using data processor
            self.current_data = self.data_processor.load_data(file_path)
            
            # Update displays
            self.update_data_display(self.current_data)
            self.update_column_lists(self.current_data)
            self.refresh_data_info()
            
            # Notify parent
            self.data_loaded_callback(self.current_data)
            
            messagebox.showinfo("Success", f"Data loaded successfully!\n"
                               f"Shape: {self.current_data.shape[0]} rows × {self.current_data.shape[1]} columns")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data:\n{str(e)}")
            logger.error(f"Error loading data: {str(e)}")
    
    def convert_dump_to_csv(self):
        """Convert dump file to CSV"""
        dump_path = filedialog.askopenfilename(
            title="Select dump file to convert",
            filetypes=[("Dump files", "*.dump"), ("Pickle files", "*.pkl"), ("All files", "*.*")]
        )
        
        if not dump_path:
            return
        
        csv_path = filedialog.asksaveasfilename(
            title="Save CSV as",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not csv_path:
            return
        
        try:
            from ..utils.file_handlers import FileHandler
            file_handler = FileHandler()
            
            conversion_info = file_handler.convert_dump_to_csv(dump_path, csv_path)
            
            message = f"Conversion successful!\n\n" \
                     f"Original file: {conversion_info['original_size_mb']:.2f} MB\n" \
                     f"Converted file: {conversion_info['converted_size_mb']:.2f} MB\n" \
                     f"Rows: {conversion_info['rows']}\n" \
                     f"Columns: {conversion_info['columns']}"
            
            messagebox.showinfo("Conversion Complete", message)
            
            # Ask if user wants to load the converted file
            if messagebox.askyesno("Load Data", "Do you want to load the converted CSV file?"):
                self.file_path_var.set(csv_path)
                self.load_data()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert file:\n{str(e)}")
    
    def update_data_display(self, data):
        """Update the data preview treeview"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if data is None or data.empty:
            return
        
        # Update column headers
        columns = list(data.columns[:5])  # Show first 5 columns
        self.tree["columns"] = columns
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="w")
        
        # Add data rows (first 100 rows for performance)
        max_rows = min(100, len(data))
        for i in range(max_rows):
            row_data = []
            for col in columns:
                value = data.iloc[i][col]
                # Format value for display
                if pd.isna(value):
                    formatted_value = "NaN"
                elif isinstance(value, float):
                    formatted_value = f"{value:.3f}"
                else:
                    formatted_value = str(value)[:20]  # Truncate long strings
                row_data.append(formatted_value)
            
            self.tree.insert("", "end", values=row_data)
        
        # Add info if data was truncated
        if len(data) > 100:
            self.tree.insert("", "end", values=["...", "...", "...", "...", "..."])
    
    def update_column_lists(self, data):
        """Update features and target selection lists"""
        if data is None:
            return
        
        columns = list(data.columns)
        
        # Update features listbox
        self.features_listbox.delete(0, tk.END)
        for col in columns:
            self.features_listbox.insert(tk.END, col)
        
        # Update target combobox
        self.target_combo["values"] = columns
        if columns:
            self.target_combo.set(columns[-1])  # Default to last column
    
    def refresh_data_info(self):
        """Refresh data information display"""
        if self.current_data is None:
            info_text = "No data loaded"
        else:
            # Get data summary
            summary = self.data_processor.get_data_summary()
            column_info = self.data_processor.get_column_info()
            
            info_lines = [
                f"Dataset Shape: {summary['shape'][0]} rows × {summary['shape'][1]} columns",
                f"Memory Usage: {summary['memory_usage_mb']:.2f} MB",
                "",
                f"Data Types:",
                f"  Numeric: {len(summary['numeric_columns'])}",
                f"  Categorical: {len(summary['categorical_columns'])}",
                "",
                f"Missing Values:",
            ]
            
            # Add missing values info
            missing_info = summary['missing_data_pct']
            has_missing = any(pct > 0 for pct in missing_info.values())
            
            if has_missing:
                for col, pct in missing_info.items():
                    if pct > 0:
                        info_lines.append(f"  {col}: {pct:.1f}%")
            else:
                info_lines.append("  No missing values")
            
            info_text = "\n".join(info_lines)
        
        # Update text widget
        self.info_text.config(state="normal")
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_text)
        self.info_text.config(state="disabled")
    
    def validate_data(self):
        """Validate current data"""
        if self.current_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
        
        try:
            from ..utils.validators import DataValidator
            validator = DataValidator()
            
            results = validator.validate_dataframe(self.current_data)
            suggestions = validator.suggest_preprocessing(self.current_data)
            
            # Create validation report
            report_lines = []
            
            if results['is_valid']:
                report_lines.append("✓ Data validation passed")
            else:
                report_lines.append("✗ Data validation failed")
            
            if results['errors']:
                report_lines.append("\nErrors:")
                for error in results['errors']:
                    report_lines.append(f"  • {error}")
            
            if results['warnings']:
                report_lines.append("\nWarnings:")
                for warning in results['warnings']:
                    report_lines.append(f"  • {warning}")
            
            if suggestions:
                report_lines.append("\nSuggested preprocessing steps:")
                for suggestion in suggestions:
                    report_lines.append(f"  • {suggestion}")
            
            report_text = "\n".join(report_lines)
            
            # Show validation results
            validation_window = tk.Toplevel(self.frame)
            validation_window.title("Data Validation Report")
            validation_window.geometry("600x400")
            
            text_widget = tk.Text(validation_window, wrap="word", padx=10, pady=10)
            text_widget.pack(fill="both", expand=True)
            text_widget.insert(1.0, report_text)
            text_widget.config(state="disabled")
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(validation_window, command=text_widget.yview)
            scrollbar.pack(side="right", fill="y")
            text_widget.config(yscrollcommand=scrollbar.set)
            
        except Exception as e:
            messagebox.showerror("Error", f"Validation failed:\n{str(e)}")
    
    def export_to_csv(self):
        """Export current data to CSV"""
        if self.current_data is None:
            messagebox.showwarning("Warning", "No data to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.current_data.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Data exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export:\n{str(e)}")
    
    def select_all_features(self):
        """Select all features"""
        self.features_listbox.selection_set(0, tk.END)
    
    def clear_all_features(self):
        """Clear all feature selections"""
        self.features_listbox.selection_clear(0, tk.END)
    
    def set_features_target(self):
        """Set selected features and target"""
        if self.current_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
        
        # Get selected features
        selected_indices = self.features_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select at least one feature")
            return
        
        feature_columns = [self.features_listbox.get(i) for i in selected_indices]
        
        # Get target
        target_column = self.target_var.get()
        if not target_column:
            messagebox.showwarning("Warning", "Please select a target column")
            return
        
        try:
            # Set features and target in data processor
            self.data_processor.select_features(feature_columns)
            self.data_processor.set_target(target_column)
            
            message = f"Features and target set successfully!\n\n" \
                     f"Features ({len(feature_columns)}):\n" + \
                     "\n".join(f"  • {col}" for col in feature_columns[:10]) + \
                     (f"\n  ... and {len(feature_columns)-10} more" if len(feature_columns) > 10 else "") + \
                     f"\n\nTarget: {target_column}"
            
            messagebox.showinfo("Success", message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set features and target:\n{str(e)}")
    
    def preprocess_data(self):
        """Open preprocessing dialog"""
        if self.data_processor.features is None or self.data_processor.target is None:
            messagebox.showwarning("Warning", "Please set features and target first")
            return
        
        # Create preprocessing dialog
        preprocessing_window = tk.Toplevel(self.frame)
        preprocessing_window.title("Data Preprocessing")
        preprocessing_window.geometry("400x300")
        preprocessing_window.transient(self.frame)
        preprocessing_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(preprocessing_window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Missing values handling
        ttk.Label(main_frame, text="Missing Values:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        missing_var = tk.StringVar(value="drop")
        missing_options = [
            ("Drop rows with missing values", "drop"),
            ("Fill with mean (numeric)", "fill_mean"),
            ("Fill with median (numeric)", "fill_median"),
            ("Fill with mode (most frequent)", "fill_mode")
        ]
        
        for text, value in missing_options:
            ttk.Radiobutton(main_frame, text=text, variable=missing_var, 
                           value=value).pack(anchor="w", padx=20)
        
        # Categorical encoding
        ttk.Label(main_frame, text="Categorical Variables:", 
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=(20, 0))
        
        encode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Encode categorical variables", 
                       variable=encode_var).pack(anchor="w", padx=20)
        
        # Scaling
        ttk.Label(main_frame, text="Feature Scaling:", 
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=(20, 0))
        
        scale_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(main_frame, text="Scale numeric features", 
                       variable=scale_var).pack(anchor="w", padx=20)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(20, 0))
        
        def apply_preprocessing():
            try:
                self.data_processor.preprocess_data(
                    handle_missing=missing_var.get(),
                    encode_categorical=encode_var.get(),
                    scale_numeric=scale_var.get()
                )
                messagebox.showinfo("Success", "Data preprocessing completed!")
                preprocessing_window.destroy()
                self.refresh_data_info()
                
            except Exception as e:
                messagebox.showerror("Error", f"Preprocessing failed:\n{str(e)}")
        
        ttk.Button(button_frame, text="Apply", command=apply_preprocessing,
                  style="Success.TButton").pack(side="left", padx=(0, 10))
        
        ttk.Button(button_frame, text="Cancel", 
                  command=preprocessing_window.destroy).pack(side="left")
    
    def reset(self):
        """Reset the tab to initial state"""
        self.file_path_var.set("")
        self.current_data = None
        
        # Clear displays
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.features_listbox.delete(0, tk.END)
        self.target_combo.set("")
        self.target_combo["values"] = []
        
        self.info_text.config(state="normal")
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "No data loaded")
        self.info_text.config(state="disabled")