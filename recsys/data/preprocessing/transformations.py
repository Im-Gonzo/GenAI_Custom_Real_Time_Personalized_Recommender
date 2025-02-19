"""
Data transformation utilities for recommendation datasets.
"""
import polars as pl
from typing import List, Dict, Any, Optional, Union
import numpy as np


def normalize_numeric_features(
    df: pl.DataFrame,
    columns: Optional[List[str]] = None,
    method: str = "minmax"
) -> pl.DataFrame:
    """
    Normalize numeric features in a DataFrame.
    
    Args:
        df: Input DataFrame
        columns: List of columns to normalize (None = all numeric)
        method: Normalization method ('minmax', 'standard', 'robust')
        
    Returns:
        DataFrame with normalized features
    """
    if columns is None:
        numeric_dtypes = [pl.Float32, pl.Float64, pl.Int32, pl.Int64]
        columns = [
            col for col in df.columns 
            if any(isinstance(df.schema[col], dtype) for dtype in numeric_dtypes)
        ]
    
    result = df.clone()
    
    for col in columns:
        if col not in df.columns:
            continue
            
        if method == "minmax":
            min_val = df[col].min()
            max_val = df[col].max()
            if max_val > min_val:
                result = result.with_columns([
                    ((pl.col(col) - min_val) / (max_val - min_val)).alias(f"{col}_norm")
                ])
            else:
                # If min == max, set normalized value to 0.5
                result = result.with_columns([
                    pl.lit(0.5).alias(f"{col}_norm")
                ])
                
        elif method == "standard":
            mean_val = df[col].mean()
            std_val = df[col].std()
            if std_val > 0:
                result = result.with_columns([
                    ((pl.col(col) - mean_val) / std_val).alias(f"{col}_norm")
                ])
            else:
                # If std == 0, set normalized value to 0
                result = result.with_columns([
                    pl.lit(0.0).alias(f"{col}_norm")
                ])
                
        elif method == "robust":
            q25 = df[col].quantile(0.25)
            q75 = df[col].quantile(0.75)
            iqr = q75 - q25
            if iqr > 0:
                result = result.with_columns([
                    ((pl.col(col) - q25) / iqr).alias(f"{col}_norm")
                ])
            else:
                # If IQR == 0, use standard method
                mean_val = df[col].mean()
                std_val = df[col].std()
                if std_val > 0:
                    result = result.with_columns([
                        ((pl.col(col) - mean_val) / std_val).alias(f"{col}_norm")
                    ])
                else:
                    # Last resort - set to 0
                    result = result.with_columns([
                        pl.lit(0.0).alias(f"{col}_norm")
                    ])
    
    return result


def encode_categorical_features(
    df: pl.DataFrame,
    columns: Optional[List[str]] = None,
    method: str = "one_hot"
) -> pl.DataFrame:
    """
    Encode categorical features in a DataFrame.
    
    Args:
        df: Input DataFrame
        columns: List of categorical columns to encode
        method: Encoding method ('one_hot', 'label', 'target')
        
    Returns:
        DataFrame with encoded features
    """
    # Example implementation - adapt to your needs
    return df
