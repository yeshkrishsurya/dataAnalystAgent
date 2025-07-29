import duckdb
import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any, Union
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

class DataTools:
    def __init__(self):
        self.conn = duckdb.connect()
        # Install and load required extensions
        self._setup_duckdb()
    
    def _setup_duckdb(self):
        """Setup DuckDB with required extensions"""
        try:
            self.conn.execute("INSTALL httpfs")
            self.conn.execute("LOAD httpfs")
            self.conn.execute("INSTALL parquet")
            self.conn.execute("LOAD parquet")
        except Exception as e:
            print(f"Warning: Failed to setup DuckDB extensions: {e}")
    
    def query_duckdb(self, query: str) -> str:
        """Execute SQL query on DuckDB and return results as JSON"""
        try:
            result = self.conn.execute(query).fetchall()
            columns = [desc[0] for desc in self.conn.description]
            
            # Convert to list of dictionaries
            data = []
            for row in result:
                row_dict = {}
                for i, value in enumerate(row):
                    # Handle various data types
                    if isinstance(value, (np.integer, np.floating)):
                        value = value.item()
                    elif pd.isna(value):
                        value = None
                    row_dict[columns[i]] = value
                data.append(row_dict)
            
            return json.dumps({
                "success": True,
                "data": data,
                "columns": columns,
                "row_count": len(data)
            })
        except Exception as e:
            return json.dumps({"error": f"SQL query failed: {str(e)}"})
    
    def analyze_data(self, data_input: str) -> str:
        """Perform statistical analysis on data"""
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
                results["description"] = df.describe().to_dict()
                results["info"] = {
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "dtypes": df.dtypes.astype(str).to_dict()
                }
            
            elif analysis_type == "correlation":
                # Correlation analysis
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) >= 2:
                    corr_matrix = df[numeric_cols].corr()
                    results["correlation_matrix"] = corr_matrix.to_dict()
                else:
                    results["error"] = "Need at least 2 numeric columns for correlation"
            
            elif analysis_type == "regression":
                # Linear regression analysis
                x_col = input_data.get("x_column")
                y_col = input_data.get("y_column")
                
                if not x_col or not y_col:
                    return json.dumps({"error": "Need x_column and y_column for regression"})
                
                if x_col not in df.columns or y_col not in df.columns:
                    return json.dumps({"error": "Specified columns not found in data"})
                
                # Clean data (remove NaN values)
                clean_data = df[[x_col, y_col]].dropna()
                
                if len(clean_data) < 2:
                    return json.dumps({"error": "Insufficient data for regression"})
                
                X = clean_data[x_col].values.reshape(-1, 1)
                y = clean_data[y_col].values
                
                # Perform linear regression
                model = LinearRegression()
                model.fit(X, y)
                
                y_pred = model.predict(X)
                r2 = r2_score(y, y_pred)
                
                # Calculate correlation coefficient
                correlation = np.corrcoef(clean_data[x_col], clean_data[y_col])[0, 1]
                
                results["regression"] = {
                    "slope": float(model.coef_[0]),
                    "intercept": float(model.intercept_),
                    "r_squared": float(r2),
                    "correlation": float(correlation),
                    "data_points": len(clean_data)
                }
            
            elif analysis_type == "count":
                # Count specific conditions
                condition = input_data.get("condition", {})
                if condition:
                    filtered_df = df
                    for col, value in condition.items():
                        if col in df.columns:
                            filtered_df = filtered_df[filtered_df[col] == value]
                    results["count"] = len(filtered_df)
                else:
                    results["total_count"] = len(df)
            
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
                if column not in df.columns:
                    continue
                
                if isinstance(condition, dict):
                    # Handle complex conditions
                    if "gt" in condition:
                        df = df[df[column] > condition["gt"]]
                    if "lt" in condition:
                        df = df[df[column] < condition["lt"]]
                    if "eq" in condition:
                        df = df[df[column] == condition["eq"]]
                    if "contains" in condition:
                        df = df[df[column].str.contains(condition["contains"], na=False)]
                else:
                    # Simple equality filter
                    df = df[df[column] == condition]
            
            return df.to_dict('records')
        except Exception as e:
            return []
    
    def clean_numeric_data(self, data: List[Dict], columns: List[str]) -> List[Dict]:
        """Clean and convert data to numeric formats"""
        try:
            df = pd.DataFrame(data)
            
            for col in columns:
                if col in df.columns:
                    # Remove common formatting characters
                    df[col] = df[col].astype(str)
                    df[col] = df[col].str.replace(',', '')
                    df[col] = df[col].str.replace('$', '')
                    df[col] = df[col].str.replace('%', '')
                    df[col] = df[col].str.extract(r'(\d+\.?\d*)').astype(float)
            
            return df.to_dict('records')
        except Exception as e:
            return data