"""
Schema validation utilities for recommendation data.
"""

import polars as pl
from typing import Dict, List, Union, Any, Optional
from loguru import logger


def validate_column_types(df: pl.DataFrame, expected_schema: Dict[str, Any]) -> bool:
    """
    Validate that DataFrame columns match expected data types.

    Args:
        df: DataFrame to validate
        expected_schema: Dict mapping column names to expected types

    Returns:
        True if validation passes, False otherwise
    """
    valid = True

    for col_name, expected_type in expected_schema.items():
        if col_name not in df.columns:
            logger.error(f"Missing column: {col_name}")
            valid = False
            continue

        # Map polars types to Python types for comparison
        type_mapping = {
            pl.Int8: int,
            pl.Int16: int,
            pl.Int32: int,
            pl.Int64: int,
            pl.UInt8: int,
            pl.UInt16: int,
            pl.UInt32: int,
            pl.UInt64: int,
            pl.Float32: float,
            pl.Float64: float,
            pl.Boolean: bool,
            pl.Utf8: str,
            pl.Date: "date",
            pl.Datetime: "datetime",
        }

        actual_type = df.schema[col_name]
        mapped_type = None

        for pl_type, py_type in type_mapping.items():
            if isinstance(actual_type, pl_type):
                mapped_type = py_type
                break

        if mapped_type != expected_type:
            logger.error(
                f"Column {col_name}: expected {expected_type}, got {actual_type}"
            )
            valid = False

    return valid


def validate_required_columns(df: pl.DataFrame, required_columns: List[str]) -> bool:
    """
    Validate that DataFrame contains all required columns.

    Args:
        df: DataFrame to validate
        required_columns: List of required column names

    Returns:
        True if validation passes, False otherwise
    """
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        logger.error(f"Missing required columns: {missing_columns}")
        return False

    return True


def validate_unique_constraints(
    df: pl.DataFrame, unique_columns: List[Union[str, List[str]]]
) -> bool:
    """
    Validate uniqueness constraints on DataFrame columns.

    Args:
        df: DataFrame to validate
        unique_columns: List of column names or column groups that should be unique

    Returns:
        True if validation passes, False otherwise
    """
    valid = True

    for constraint in unique_columns:
        if isinstance(constraint, str):
            constraint = [constraint]

        n_total = df.shape[0]
        n_unique = df.unique(subset=constraint).shape[0]

        if n_unique < n_total:
            duplicates = n_total - n_unique
            logger.error(
                f"Uniqueness constraint violated: {constraint}, found {duplicates} duplicates"
            )
            valid = False

    return valid
