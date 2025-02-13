"""General data manipulation utilities."""

import polars as pl
from typing import List, Dict, Any


def check_required_columns(df: pl.DataFrame, required_columns: List[str]) -> bool:
    """Check if DataFrame contains all required columns."""
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    return True


def safe_cast_columns(df: pl.DataFrame, type_mapping: Dict[str, Any]) -> pl.DataFrame:
    """Safely cast DataFrame columns to specified types."""
    for col, dtype in type_mapping.items():
        if col in df.columns:
            df = df.with_columns(pl.col(col).cast(dtype))
    return df
