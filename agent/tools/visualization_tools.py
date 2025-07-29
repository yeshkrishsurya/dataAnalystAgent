import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import io
import base64
import json
from typing import Dict, List, Any, Union
from sklearn.linear_model import LinearRegression

# Set matplotlib to use non-interactive backend
matplotlib.use('Agg')

class VisualizationTools:
    def __init__(self):
        # Set default style
        plt.style.use('default')
        sns.set_palette("husl")
    
    def create_plot(self, plot_input: str) -> str:
        """Create various types of plots based on input parameters"""
        try:
            # Parse input JSON
            input_data = json.loads(plot_input)
            plot_type = input_data.get("plot_type", "line")
            data = input_data.get("data", [])
            title = input_data.get("title", "")
            x_label = input_data.get("x_label", "X")
            y_label = input_data.get("y_label", "Y")
            
            if not data:
                return json.dumps({"error": "No data provided for plotting"})
            
            df = pd.DataFrame(data)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if plot_type == "line":
                x_col = input_data.get("x_column")
                y_col = input_data.get("y_column")
                if x_col and y_col and x_col in df.columns and y_col in df.columns:
                    ax.plot(df[x_col], df[y_col], marker='o')
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
            
            elif plot_type == "bar":
                x_col = input_data.get("x_column")
                y_col = input_data.get("y_column")
                if x_col and y_col and x_col in df.columns and y_col in df.columns:
                    ax.bar(df[x_col], df[y_col])
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
            
            elif plot_type == "histogram":
                col = input_data.get("column")
                if col and col in df.columns:
                    ax.hist(df[col], bins=20, alpha=0.7)
                    ax.set_xlabel(col)
                    ax.set_ylabel("Frequency")
            
            ax.set_title(title)
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            data_uri = f"data:image/png;base64,{image_base64}"
            
            # Check size limit
            if len(data_uri) > 100000:
                return json.dumps({"error": "Image size exceeds 100,000 bytes limit"})
            
            return json.dumps({
                "success": True,
                "data_uri": data_uri,
                "size": len(data_uri)
            })
            
        except Exception as e:
            return json.dumps({"error": f"Plot creation failed: {str(e)}"})
    
    def create_scatterplot(self, scatter_input: str) -> str:
        """Create scatterplot with regression line"""
        try:
            # Parse input JSON
            input_data = json.loads(scatter_input)
            x_data = input_data.get("x_data", [])
            y_data = input_data.get("y_data", [])
            title = input_data.get("title", "Scatterplot")
            x_label = input_data.get("x_label", "X")
            y_label = input_data.get("y_label", "Y")
            
            if not x_data or not y_data:
                return json.dumps({"error": "No x_data or y_data provided"})
            
            if len(x_data) != len(y_data):
                return json.dumps({"error": "x_data and y_data must have same length"})
            
            # Convert to numpy arrays
            x = np.array(x_data, dtype=float)
            y = np.array(y_data, dtype=float)
            
            # Remove NaN values
            mask = ~(np.isnan(x) | np.isnan(y))
            x = x[mask]
            y = y[mask]
            
            if len(x) < 2:
                return json.dumps({"error": "Need at least 2 valid data points"})
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Create scatterplot
            ax.scatter(x, y, alpha=0.6, s=50)
            
            # Add regression line
            X = x.reshape(-1, 1)
            model = LinearRegression()
            model.fit(X, y)
            
            # Generate line points
            x_line = np.linspace(x.min(), x.max(), 100)
            y_line = model.predict(x_line.reshape(-1, 1))
            
            # Plot regression line (dotted red)
            ax.plot(x_line, y_line, 'r--', linewidth=2, alpha=0.8, label='Regression Line')
            
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title(title)
            ax.legend()
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            data_uri = f"data:image/png;base64,{image_base64}"
            
            # Check size limit
            if len(data_uri) > 100000:
                # Try with lower DPI
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.scatter(x, y, alpha=0.6, s=30)
                ax.plot(x_line, y_line, 'r--', linewidth=2, alpha=0.8)
                ax.set_xlabel(x_label)
                ax.set_ylabel(y_label)
                ax.set_title(title)
                ax.grid(True, alpha=0.3)
                plt.tight_layout()
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=80, bbox_inches='tight')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
                
                data_uri = f"data:image/png;base64,{image_base64}"
                
                if len(data_uri) > 100000:
                    return json.dumps({"error": "Image size still exceeds limit even with compression"})
            
            return json.dumps({
                "success": True,
                "data_uri": data_uri,
                "size": len(data_uri),
                "regression_stats": {
                    "slope": float(model.coef_[0]),
                    "intercept": float(model.intercept_),
                    "data_points": len(x)
                }
            })
            
        except Exception as e:
            return json.dumps({"error": f"Scatterplot creation failed: {str(e)}"})
    
    def create_from_dataframe(self, df: pd.DataFrame, plot_type: str, x_col: str, y_col: str = None, title: str = "") -> str:
        """Create plot directly from DataFrame"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if plot_type == "scatter" and y_col:
                ax.scatter(df[x_col], df[y_col], alpha=0.6)
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
            elif plot_type == "bar":
                df[x_col].value_counts().plot(kind='bar', ax=ax)
                ax.set_xlabel(x_col)
                ax.set_ylabel("Count")
            elif plot_type == "hist":
                ax.hist(df[x_col], bins=20, alpha=0.7)
                ax.set_xlabel(x_col)
                ax.set_ylabel("Frequency")
            
            ax.set_title(title)
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            return f"Error creating plot: {str(e)}"