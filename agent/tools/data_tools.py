import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any, Union

class DataTools:
    def __init__(self):
        # Remove DuckDB dependency for Vercel deployment
        self.conn = None
        print("DataTools initialized (lightweight version for Vercel)")
    
    def query_duckdb(self, query: str) -> str:
        """Placeholder for DuckDB queries - not available in lightweight deployment"""
        return json.dumps({
            "error": "DuckDB queries not available in this deployment",
            "message": "Use local deployment for database functionality"
        })
    
    def analyze_data(self, data_input: str) -> str:
        """Perform statistical analysis on data using pandas and numpy only"""
        try:
            # Parse input JSON
            input_data = json.loads(data_input)
            data = input_data.get("data", [])
            analysis_type = input_data.get("analysis_type", "describe")
            
            if not data:
                return json.dumps({"error": "No data provided"})
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            results = {}
            
            if analysis_type == "describe":
                # Basic descriptive statistics
                desc = df.describe()
                results["description"] = {}
                for col in desc.columns:
                    results["description"][col] = {}
                    for stat in desc.index:
                        value = desc.loc[stat, col]
                        if pd.isna(value):
                            results["description"][col][stat] = None
                        else:
                            results["description"][col][stat] = float(value) if isinstance(value, (np.integer, np.floating)) else str(value)
                
                results["info"] = {
                    "shape": list(df.shape),
                    "columns": list(df.columns),
                    "dtypes": df.dtypes.astype(str).to_dict()
                }
            
            elif analysis_type == "correlation":
                # Correlation analysis using pandas
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) >= 2:
                    corr_matrix = df[numeric_cols].corr()
                    results["correlation_matrix"] = {}
                    for col1 in corr_matrix.columns:
                        results["correlation_matrix"][col1] = {}
                        for col2 in corr_matrix.columns:
                            value = corr_matrix.loc[col1, col2]
                            results["correlation_matrix"][col1][col2] = float(value) if not pd.isna(value) else None
                else:
                    results["error"] = "Need at least 2 numeric columns for correlation"
            
            elif analysis_type == "regression":
                # Simple linear regression using numpy
                x_col = input_data.get("x_column")
                y_col = input_data.get("y_column")
                
                if not x_col or not y_col:
                    return json.dumps({"error": "Need x_column and y_column for regression"})
                
                if x_col not in df.columns or y_col not in df.columns:
                    return json.dumps({"error": "Specified columns not found in data"})
                
                # Clean data (remove NaN values)
                clean_data = df[[x_col, y_col]].dropna()
                
                if len(clean_data) < 2:
                    return json.dumps({"error": "Not enough data points for regression"})
                
                x = clean_data[x_col].values
                y = clean_data[y_col].values
                
                # Simple linear regression using numpy
                n = len(x)
                x_mean = np.mean(x)
                y_mean = np.mean(y)
                
                # Calculate coefficients
                numerator = np.sum((x - x_mean) * (y - y_mean))
                denominator = np.sum((x - x_mean) ** 2)
                
                if denominator == 0:
                    return json.dumps({"error": "Cannot perform regression: x values are all the same"})
                
                slope = numerator / denominator
                intercept = y_mean - slope * x_mean
                
                # Calculate R-squared
                y_pred = slope * x + intercept
                ss_res = np.sum((y - y_pred) ** 2)
                ss_tot = np.sum((y - y_mean) ** 2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                
                results["regression"] = {
                    "slope": float(slope),
                    "intercept": float(intercept),
                    "r_squared": float(r_squared),
                    "equation": f"y = {slope:.4f}x + {intercept:.4f}",
                    "data_points": int(n)
                }
            
            elif analysis_type == "summary":
                # Summary statistics
                results["summary"] = {
                    "total_rows": int(len(df)),
                    "total_columns": int(len(df.columns)),
                    "missing_values": df.isnull().sum().to_dict(),
                    "data_types": df.dtypes.astype(str).to_dict()
                }
                
                # Add basic stats for numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    results["summary"]["numeric_stats"] = {}
                    for col in numeric_cols:
                        col_data = df[col].dropna()
                        if len(col_data) > 0:
                            results["summary"]["numeric_stats"][col] = {
                                "mean": float(np.mean(col_data)),
                                "median": float(np.median(col_data)),
                                "std": float(np.std(col_data)),
                                "min": float(np.min(col_data)),
                                "max": float(np.max(col_data)),
                                "count": int(len(col_data))
                            }
            
            else:
                return json.dumps({"error": f"Unknown analysis type: {analysis_type}"})
            
            return json.dumps({
                "success": True,
                "analysis_type": analysis_type,
                "results": results
            })
            
        except Exception as e:
            return json.dumps({"error": f"Analysis failed: {str(e)}"})
    
    def filter_data(self, data: List[Dict], filters: Dict) -> List[Dict]:
        """Filter data based on conditions"""
        try:
            df = pd.DataFrame(data)
            
            for column, condition in filters.items():
                if column in df.columns:
                    if isinstance(condition, dict):
                        if 'min' in condition:
                            df = df[df[column] >= condition['min']]
                        if 'max' in condition:
                            df = df[df[column] <= condition['max']]
                        if 'equals' in condition:
                            df = df[df[column] == condition['equals']]
                        if 'contains' in condition:
                            df = df[df[column].astype(str).str.contains(condition['contains'], na=False)]
                    else:
                        # Simple equality filter
                        df = df[df[column] == condition]
            
            return df.to_dict('records')
        except Exception as e:
            print(f"Error filtering data: {e}")
            return data
    
    def clean_numeric_data(self, data: List[Dict], columns: List[str]) -> List[Dict]:
        """Clean numeric data by removing outliers and handling missing values"""
        try:
            df = pd.DataFrame(data)
            
            for column in columns:
                if column in df.columns:
                    # Convert to numeric, coercing errors to NaN
                    df[column] = pd.to_numeric(df[column], errors='coerce')
                    
                    # Remove outliers using IQR method
                    Q1 = df[column].quantile(0.25)
                    Q3 = df[column].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    # Replace outliers with NaN
                    df.loc[(df[column] < lower_bound) | (df[column] > upper_bound), column] = np.nan
                    
                    # Fill missing values with median
                    median_val = df[column].median()
                    df[column].fillna(median_val, inplace=True)
            
            return df.to_dict('records')
        except Exception as e:
            print(f"Error cleaning numeric data: {e}")
            return data