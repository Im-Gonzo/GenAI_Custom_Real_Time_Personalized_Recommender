"""Data splitting utilities."""

import polars as pl
import numpy as np
from typing import Tuple, Optional


def train_validation_test_split(
    df: pl.DataFrame,
    validation_size: Optional[float] = None,
    test_size: Optional[float] = None,
    train_start: Optional[int] = None,
    train_end: Optional[int] = None,
    validation_start: Optional[int] = None,
    validation_end: Optional[int] = None,
    test_start: Optional[int] = None,
    test_end: Optional[int] = None,
    seed: int = 42,
) -> Tuple[
    pl.DataFrame,
    pl.DataFrame,
    pl.DataFrame,
    Optional[pl.DataFrame],
    Optional[pl.DataFrame],
    Optional[pl.DataFrame],
]:
    """
    Split data into train, validation and test sets using either random or time-based splitting.

    Args:
        df: Input DataFrame
        validation_size: Size of validation set (between 0 and 1)
        test_size: Size of test set (between 0 and 1)
        train_start: Start timestamp for train set
        train_end: End timestamp for train set
        validation_start: Start timestamp for validation set
        validation_end: End timestamp for validation set
        test_start: Start timestamp for test set
        test_end: End timestamp for test set
        seed: Random seed for reproducibility

    Returns:
        Tuple of (train_df, val_df, test_df, train_labels, val_labels, test_labels)
    """
    if train_start is not None:
        # Time-based split
        train_df = df.filter(
            (pl.col("t_dat") >= train_start) & (pl.col("t_dat") < train_end)
        )

        val_df = df.filter(
            (pl.col("t_dat") >= validation_start) & (pl.col("t_dat") < validation_end)
        )

        test_df = df.filter(
            (pl.col("t_dat") >= test_start) & (pl.col("t_dat") < test_end)
        )
    else:
        # Set random seed
        np.random.seed(seed)

        # Generate random values
        random_values = np.random.rand(len(df))

        # Calculate split points
        val_point = 1.0 - (validation_size + test_size)
        test_point = 1.0 - test_size

        # Add random values as a column
        df_with_random = df.with_columns(pl.Series("_random", random_values)).sort(
            "_random"
        )

        # Split based on random values
        train_df = df_with_random.filter(pl.col("_random") <= val_point).drop("_random")

        val_df = df_with_random.filter(
            (pl.col("_random") > val_point) & (pl.col("_random") <= test_point)
        ).drop("_random")

        test_df = df_with_random.filter(pl.col("_random") > test_point).drop("_random")

    # Extract labels if present
    train_labels = None
    val_labels = None
    test_labels = None
    if "label" in df.columns:
        train_labels = train_df.select("label")
        val_labels = val_df.select("label")
        test_labels = test_df.select("label")

    return train_df, val_df, test_df, train_labels, val_labels, test_labels
