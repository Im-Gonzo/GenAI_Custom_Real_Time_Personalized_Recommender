"""Data validation utilities."""

import polars as pl
from typing import List, Dict, Any, Optional
from loguru import logger


def validate_timestamp_range(
    df: pl.DataFrame,
    timestamp_col: str,
    min_timestamp: Optional[int] = None,
    max_timestamp: Optional[int] = None,
) -> bool:
    """Validate that timestamps fall within expected range."""
    if min_timestamp is not None:
        if df[timestamp_col].min() < min_timestamp:
            raise ValueError(f"Found timestamps before {min_timestamp}")

    if max_timestamp is not None:
        if df[timestamp_col].max() > max_timestamp:
            raise ValueError(f"Found timestamps after {max_timestamp}")

    return True


def validate_no_nulls(df: pl.DataFrame, columns: List[str]) -> bool:
    """Validate that specified columns contain no null values."""
    for col in columns:
        if df[col].null_count() > 0:
            raise ValueError(f"Found null values in column {col}")
    return True
