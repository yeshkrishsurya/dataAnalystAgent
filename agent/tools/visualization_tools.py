import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np
import io
import base64
import json
from typing import Dict, List, Any, Union

# Set matplotlib to use non-interactive backend
matplotlib.use('Agg')

class VisualizationTools:
    def __init__(self):
        # Set default style without seaborn
        plt.style.use('default')
        print("VisualizationTools initialized (lightweight version for Vercel)")
    
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
                    ax.plot(df[x_col], df[y_col], marker='o', linewidth=2, markersize=6)
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
            
            elif plot_type == "bar":
                x_col = input_data.get("x_column")
                y_col = input_data.get("y_column")
                if x_col and y_col and x_col in df.columns and y_col in df.columns:
                    ax.bar(df[x_col], df[y_col], alpha=0.7)
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
            
            elif plot_type == "histogram":
                col = input_data.get("column")
                if col and col in df.columns:
                    ax.hist(df[col], bins=20, alpha=0.7, edgecolor='black')
                    ax.set_xlabel(col)
                    ax.set_ylabel("Frequency")
            
            elif plot_type == "scatter":
                x_col = input_data.get("x_column")
                y_col = input_data.get("y_column")
                if x_col and y_col and x_col in df.columns and y_col in df.columns:
                    ax.scatter(df[x_col], df[y_col], alpha=0.6)
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
            
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
        """Create scatterplot with regression line using numpy"""
        try:
            # Parse input JSON
            input_data = json.loads(scatter_input)
            x_data = input_data.get("x_data", [])
            y_data = input_data.get("y_data", [])
            title = input_data.get("title", "Scatterplot")
            x_label = input_data.get("x_label", "X")
            y_label = input_data.get("y_label", "Y")
            
            if not x_data or not y_data:
                return json.dumps({"error": "Both x_data and y_data are required"})
            
            if len(x_data) != len(y_data):
                return json.dumps({"error": "x_data and y_data must have the same length"})
            
            # Convert to numpy arrays
            x = np.array(x_data)
            y = np.array(y_data)
            
            # Remove any NaN values
            mask = ~(np.isnan(x) | np.isnan(y))
            x_clean = x[mask]
            y_clean = y[mask]
            
            if len(x_clean) < 2:
                return json.dumps({"error": "Not enough valid data points for scatterplot"})
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Create scatter plot
            ax.scatter(x_clean, y_clean, alpha=0.6, s=50)
            
            # Add regression line using numpy
            if len(x_clean) >= 2:
                # Calculate regression line
                x_mean = np.mean(x_clean)
                y_mean = np.mean(y_clean)
                
                numerator = np.sum((x_clean - x_mean) * (y_clean - y_mean))
                denominator = np.sum((x_clean - x_mean) ** 2)
                
                if denominator != 0:
                    slope = numerator / denominator
                    intercept = y_mean - slope * x_mean
                    
                    # Plot regression line
                    x_line = np.array([np.min(x_clean), np.max(x_clean)])
                    y_line = slope * x_line + intercept
                    ax.plot(x_line, y_line, 'r-', linewidth=2, label=f'y = {slope:.3f}x + {intercept:.3f}')
                    ax.legend()
            
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
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
            return json.dumps({"error": f"Scatterplot creation failed: {str(e)}"})
    
    def create_from_dataframe(self, df: pd.DataFrame, plot_type: str, x_col: str, y_col: str = None, title: str = "") -> str:
        """Create plot directly from DataFrame"""
        try:
            if df.empty:
                return json.dumps({"error": "DataFrame is empty"})
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if plot_type == "line" and y_col:
                ax.plot(df[x_col], df[y_col], marker='o', linewidth=2)
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
            
            elif plot_type == "bar" and y_col:
                ax.bar(df[x_col], df[y_col], alpha=0.7)
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
            
            elif plot_type == "histogram":
                ax.hist(df[x_col], bins=20, alpha=0.7, edgecolor='black')
                ax.set_xlabel(x_col)
                ax.set_ylabel("Frequency")
            
            elif plot_type == "scatter" and y_col:
                ax.scatter(df[x_col], df[y_col], alpha=0.6)
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
            
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