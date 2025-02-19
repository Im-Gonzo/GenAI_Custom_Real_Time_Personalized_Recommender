"""
Data quality check utilities for recommendation data.
"""

import polars as pl
from typing import Dict, List, Optional, Tuple, Any
from loguru import logger


def check_missing_values(df: pl.DataFrame, threshold: float = 0.1) -> Dict[str, float]:
    """
    Check for missing values in DataFrame columns.

    Args:
        df: DataFrame to check
        threshold: Maximum acceptable proportion of missing values

    Returns:
        Dictionary mapping columns to proportion of missing values
    """
    result = {}

    for col in df.columns:
        null_count = df[col].null_count()
        missing_ratio = null_count / df.shape[0]

        if missing_ratio > 0:
            result[col] = missing_ratio

            if missing_ratio > threshold:
                logger.warning(
                    f"Column {col} has {missing_ratio:.2%} missing values, exceeding threshold of {threshold:.2%}"
                )

    return result


def check_value_distributions(
    df: pl.DataFrame, expected_stats: Dict[str, Dict[str, Any]]
) -> Dict[str, Dict[str, Tuple[Any, Any]]]:
    """
    Check that column distributions match expected statistics.

    Args:
        df: DataFrame to check
        expected_stats: Dictionary mapping columns to expected statistics

    Returns:
        Dictionary mapping columns to tuples of (expected, actual) values
    """
    result = {}

    for col, stats in expected_stats.items():
        if col not in df.columns:
            logger.error(f"Column {col} not found in DataFrame")
            continue

        column_results = {}

        for stat_name, expected_value in stats.items():
            actual_value = None

            if stat_name == "min":
                actual_value = df[col].min()
            elif stat_name == "max":
                actual_value = df[col].max()
            elif stat_name == "mean":
                actual_value = df[col].mean()
            elif stat_name == "median":
                actual_value = df[col].median()
            elif stat_name == "std":
                actual_value = df[col].std()
            elif stat_name.startswith("quantile_"):
                q = float(stat_name.split("_")[1]) / 100
                actual_value = df[col].quantile(q)

            if actual_value is not None:
                column_results[stat_name] = (expected_value, actual_value)

                # Check if values are significantly different
                if isinstance(expected_value, (int, float)) and isinstance(
                    actual_value, (int, float)
                ):
                    rel_diff = abs(expected_value - actual_value) / max(
                        abs(expected_value), 1e-10
                    )
                    if rel_diff > 0.1:  # 10% difference threshold
                        logger.warning(
                            f"Column {col} {stat_name} differs significantly: "
                            f"expected {expected_value}, got {actual_value} (diff: {rel_diff:.2%})"
                        )

        if column_results:
            result[col] = column_results

    return result


def check_data_freshness(df: pl.DataFrame, date_column: str, max_age_days: int) -> bool:
    """
    Check that data is not too old.

    Args:
        df: DataFrame to check
        date_column: Name of date column to check
        max_age_days: Maximum acceptable age in days

    Returns:
        True if data is fresh, False otherwise
    """
    if date_column not in df.columns:
        logger.error(f"Date column {date_column} not found in DataFrame")
        return False

    latest_date = df[date_column].max()

    if latest_date is None:
        logger.error(f"No valid dates found in {date_column}")
        return False

    import datetime

    today = datetime.datetime.now().date()

    if isinstance(latest_date, datetime.datetime):
        latest_date = latest_date.date()

    age_days = (today - latest_date).days

    if age_days > max_age_days:
        logger.warning(
            f"Data is {age_days} days old, exceeding maximum age of {max_age_days} days"
        )
        return False

    return True
