"""
Data cleaning utilities for recommendation datasets.
"""
import polars as pl
from typing import List, Dict, Optional, Union, Tuple
import numpy as np


def remove_duplicates(
    df: pl.DataFrame,
    subset: Optional[List[str]] = None,
    keep: str = "first"
) -> pl.DataFrame:
    """
    Remove duplicate rows from a DataFrame.
    
    Args:
        df: Input DataFrame
        subset: Column subset to consider for duplicates
        keep: Which duplicates to keep ('first', 'last', None)
        
    Returns:
        DataFrame with duplicates removed
    """
    return df.unique(subset=subset, keep=keep)


def handle_missing_values(
    df: pl.DataFrame,
    strategy: Dict[str, str] = None
) -> pl.DataFrame:
    """
    Handle missing values in a DataFrame.
    
    Args:
        df: Input DataFrame
        strategy: Dictionary mapping column names to strategies
                 ('drop', 'mean', 'median', 'mode', 'constant:value')
                 
    Returns:
        DataFrame with missing values handled
    """
    if strategy is None:
        strategy = {}
        
    result = df.clone()
    
    # Apply default strategy to columns not specified
    default_strategy = strategy.get('__default__', 'drop')
    
    # First handle any row-wise drops
    if default_strategy == 'drop':
        cols_without_strategy = [col for col in df.columns if col not in strategy]
        if cols_without_strategy:
            result = result.drop_nulls(subset=cols_without_strategy)
    
    # Then handle column-specific strategies
    for col, strat in strategy.items():
        if col == '__default__' or col not in df.columns:
            continue
            
        if strat == 'drop':
            result = result.drop_nulls(subset=[col])
        elif strat == 'mean':
            mean_val = df[col].mean()
            result = result.with_columns([
                pl.col(col).fill_null(mean_val)
            ])
        elif strat == 'median':
            median_val = df[col].median()
            result = result.with_columns([
                pl.col(col).fill_null(median_val)
            ])
        elif strat == 'mode':
            # Simple mode implementation (first most common value)
            mode_val = df[col].value_counts().filter(pl.col(col).is_not_null()).head(1)[col][0]
            result = result.with_columns([
                pl.col(col).fill_null(mode_val)
            ])
        elif strat.startswith('constant:'):
            constant_val = strat.split(':', 1)[1]
            # Try to convert to appropriate type
            try:
                if '.' in constant_val:
                    constant_val = float(constant_val)
                else:
                    constant_val = int(constant_val)
            except ValueError:
                # Keep as string if conversion fails
                pass
                
            result = result.with_columns([
                pl.col(col).fill_null(constant_val)
            ])
    
    return result


def filter_outliers(
    df: pl.DataFrame,
    numeric_columns: Optional[List[str]] = None,
    method: str = "iqr",
    threshold: float = 1.5
) -> pl.DataFrame:
    """
    Filter outliers from numeric columns.
    
    Args:
        df: Input DataFrame
        numeric_columns: List of numeric columns to check
        method: Detection method ('iqr', 'zscore', 'percentile')
        threshold: Threshold for outlier detection
        
    Returns:
        DataFrame with outliers removed
    """
    # Implementation example - adapt to your needs
    return df
