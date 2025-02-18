"""Data splitting utilities."""

import polars as pl
import numpy as np
from typing import Tuple, Optional, Union
from datetime import datetime, date


def train_test_split(
    df: pl.DataFrame,
    test_size: Optional[float] = None,
    train_start: Optional[Union[str, int, datetime, date]] = None,
    train_end: Optional[Union[str, int, datetime, date]] = None,
    test_start: Optional[Union[str, int, datetime, date]] = None,
    test_end: Optional[Union[str, int, datetime, date]] = None,
    description: str = "",
    extra_filter: Optional[pl.Expr] = None,
    seed: int = 42,
) -> Tuple[pl.DataFrame, pl.DataFrame, Optional[pl.DataFrame], Optional[pl.DataFrame]]:
    """
    Split data into train and test sets using either random or time-based splitting.
    Similar to hsfs feature view train_test_split but adapted for polars DataFrame.

    Args:
        df: Input DataFrame
        test_size: Size of test set (between 0 and 1)
        train_start: Start event time for the train split query, inclusive
        train_end: End event time for the train split query, exclusive
        test_start: Start event time for the test split query, inclusive
        test_end: End event time for the test split query, exclusive
        description: A string describing the contents of the training dataset
        extra_filter: Additional filter expression to be applied to the DataFrame
        seed: Random seed for reproducibility

    Returns:
        Tuple of (X_train, X_test, y_train, y_test)
        If no label column is present, y_train and y_test will be None
    """
    # Apply extra filter if provided
    if extra_filter is not None:
        df = df.filter(extra_filter)

    # Convert string dates to timestamps if necessary
    def _convert_to_timestamp(time_val):
        if isinstance(time_val, str):
            return int(datetime.strptime(time_val, "%Y-%m-%d %H:%M:%S").timestamp())
        elif isinstance(time_val, (datetime, date)):
            return int(time_val.timestamp())
        return time_val

    if train_start is not None:
        # Time-based split
        train_start = _convert_to_timestamp(train_start)
        train_end = _convert_to_timestamp(train_end)
        test_start = _convert_to_timestamp(test_start)
        test_end = _convert_to_timestamp(test_end)

        train_df = df.filter(
            (pl.col("t_dat") >= train_start) & (pl.col("t_dat") < train_end)
        )
        test_df = df.filter(
            (pl.col("t_dat") >= test_start) & (pl.col("t_dat") < test_end)
        )
    else:
        # Random split
        if test_size is None:
            raise ValueError("test_size must be provided for random splitting")

        if not 0 < test_size < 1:
            raise ValueError("test_size should be between 0 and 1")

        # Set random seed
        np.random.seed(seed)

        # Generate random values
        random_values = np.random.rand(len(df))

        # Calculate split point
        split_point = 1.0 - test_size

        # Add random values as a column
        df_with_random = df.with_columns(pl.Series("_random", random_values)).sort(
            "_random"
        )

        # Split based on random values
        train_df = df_with_random.filter(pl.col("_random") <= split_point).drop("_random")
        test_df = df_with_random.filter(pl.col("_random") > split_point).drop("_random")

    # Extract features and labels
    if "label" in df.columns:
        y_train = train_df.select("label")
        y_test = test_df.select("label")
        X_train = train_df.drop("label")
        X_test = test_df.drop("label")
    else:
        X_train = train_df
        X_test = test_df
        y_train = None
        y_test = None

    return X_train, X_test, y_train, y_test


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