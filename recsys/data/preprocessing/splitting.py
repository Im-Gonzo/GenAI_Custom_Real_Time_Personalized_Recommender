"""
Train-test and validation split utilities for recommendation datasets.
"""

import polars as pl
import numpy as np
from typing import Tuple, Optional, Union, List, Dict, Any
from datetime import datetime, date
from loguru import logger


def train_test_split(
    df: pl.DataFrame,
    test_size: Optional[float] = None,
    train_start: Optional[Union[str, datetime, date]] = None,
    train_end: Optional[Union[str, datetime, date]] = None,
    test_start: Optional[Union[str, datetime, date]] = None,
    test_end: Optional[Union[str, datetime, date]] = None,
    time_column: str = "t_dat",
    stratify_column: Optional[str] = None,
    extra_filter: Optional[pl.Expr] = None,
    seed: int = 12,
) -> Tuple[pl.DataFrame, pl.DataFrame, Optional[pl.DataFrame], Optional[pl.DataFrame]]:
    """
    Split data into train and test sets using either random or time-based splitting.

    Args:
        df: Input DataFrame
        test_size: Size of test set (between 0 and 1)
        train_start: Start time for the train split, inclusive
        train_end: End time for the train split, exclusive
        test_start: Start time for the test split, inclusive
        test_end: End time for the test split, exclusive
        time_column: Column containing timestamps for time-based splits
        stratify_column: Column to use for stratified splitting
        extra_filter: Additional filter expression to apply
        seed: Random seed for reproducibility

    Returns:
        Tuple of (X_train, X_test, y_train, y_test)
        If no label column is present, y_train and y_test will be None
    """
    # Apply extra filter if provided
    if extra_filter is not None:
        df = df.filter(extra_filter)

    # Convert string dates to datetime objects if necessary
    def _convert_datetime(time_val):
        if isinstance(time_val, str):
            try:
                return datetime.strptime(time_val, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    return datetime.strptime(time_val, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(f"Could not parse date string: {time_val}")
        return time_val

    # Perform time-based split if time parameters are provided
    if train_start is not None:
        if time_column not in df.columns:
            raise ValueError(f"Time column '{time_column}' not found in DataFrame")

        train_start = _convert_datetime(train_start)
        train_end = _convert_datetime(train_end)
        test_start = _convert_datetime(test_start)
        test_end = _convert_datetime(test_end)

        train_df = df.filter(
            (pl.col(time_column) >= train_start) & (pl.col(time_column) < train_end)
        )

        test_df = df.filter(
            (pl.col(time_column) >= test_start) & (pl.col(time_column) < test_end)
        )

        logger.info(
            f"Time-based split: train={train_df.shape[0]} rows "
            f"({train_start} to {train_end}), "
            f"test={test_df.shape[0]} rows ({test_start} to {test_end})"
        )

    else:
        if test_size is None:
            raise ValueError("test_size must be provided for random splitting")
        if not 0 < test_size < 1:
            raise ValueError("test_size should be between 0 and 1")

        # Set random seed
        np.random.seed(seed)

        if stratify_column is not None:
            # Perform stratified split
            if stratify_column not in df.columns:
                raise ValueError(
                    f"Stratify column '{stratify_column}' not found in DataFrame"
                )

            strata = df[stratify_column].unique().to_list()
            train_indices = []
            test_indices = []

            for stratum in strata:
                stratum_indices = df.filter(
                    pl.col(stratify_column) == stratum
                ).row_indices()
                n_stratum = len(stratum_indices)
                n_test = int(n_stratum * test_size)

                # Shuffle indices
                np.random.shuffle(stratum_indices)

                # Split indices
                test_indices.extend(stratum_indices[:n_test])
                train_indices.extend(stratum_indices[n_test:])

            train_df = df.filter(pl.col("index").is_in(train_indices))
            test_df = df.filter(pl.col("index").is_in(test_indices))

        else:
            # Simple random split
            random_values = np.random.rand(len(df))
            split_point = 1.0 - test_size

            df_with_random = df.with_columns(pl.Series("_random", random_values))

            train_df = df_with_random.filter(pl.col("_random") <= split_point).drop(
                "_random"
            )
            test_df = df_with_random.filter(pl.col("_random") > split_point).drop(
                "_random"
            )

        logger.info(
            f"Random split: train={train_df.shape[0]} rows ({(1 - test_size) * 100:.1f}%), "
            f"test={test_df.shape[0]} rows ({test_size * 100:.1f}%)"
        )

    # Extract features and labels if needed
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
    validation_size: float = 0.1,
    test_size: float = 0.1,
    time_ranges: Optional[
        Dict[str, Tuple[Union[str, datetime, date], Union[str, datetime, date]]]
    ] = None,
    time_column: str = "t_dat",
    stratify_column: Optional[str] = None,
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
    Split data into train, validation, and test sets.

    Args:
        df: Input DataFrame
        validation_size: Size of validation set (between 0 and 1)
        test_size: Size of test set (between 0 and 1)
        time_ranges: Dictionary with time ranges for each split:
                     {'train': (start, end), 'validation': (start, end), 'test': (start, end)}
        time_column: Column containing timestamps for time-based splits
        stratify_column: Column to use for stratified splitting
        seed: Random seed for reproducibility

    Returns:
        Tuple of (X_train, X_val, X_test, y_train, y_val, y_test)
        If no label column is present, y_* values will be None
    """
    if time_ranges is not None:
        # Time-based split
        if time_column not in df.columns:
            raise ValueError(f"Time column '{time_column}' not found in DataFrame")

        # Convert string dates to datetime objects if necessary
        def _convert_datetime(time_val):
            if isinstance(time_val, str):
                try:
                    return datetime.strptime(time_val, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        return datetime.strptime(time_val, "%Y-%m-%d")
                    except ValueError:
                        raise ValueError(f"Could not parse date string: {time_val}")
            return time_val

        required_keys = ["train", "validation", "test"]
        if not all(k in time_ranges for k in required_keys):
            raise ValueError(f"time_ranges must contain all keys: {required_keys}")

        # Process time ranges
        ranges = {}
        for key, (start, end) in time_ranges.items():
            ranges[key] = (_convert_datetime(start), _convert_datetime(end))

        # Create splits
        train_df = df.filter(
            (pl.col(time_column) >= ranges["train"][0])
            & (pl.col(time_column) < ranges["train"][1])
        )

        val_df = df.filter(
            (pl.col(time_column) >= ranges["validation"][0])
            & (pl.col(time_column) < ranges["validation"][1])
        )

        test_df = df.filter(
            (pl.col(time_column) >= ranges["test"][0])
            & (pl.col(time_column) < ranges["test"][1])
        )

    else:
        # Random split
        if not (
            0 < validation_size < 1
            and 0 < test_size < 1
            and validation_size + test_size < 1
        ):
            raise ValueError(
                "validation_size and test_size must be between 0 and 1, "
                "and their sum must be less than 1"
            )

        # Set random seed for reproducibility
        np.random.seed(seed)

        if stratify_column is not None:
            # Stratified split
            if stratify_column not in df.columns:
                raise ValueError(
                    f"Stratify column '{stratify_column}' not found in DataFrame"
                )

            strata = df[stratify_column].unique().to_list()
            train_indices = []
            val_indices = []
            test_indices = []

            for stratum in strata:
                stratum_indices = df.filter(
                    pl.col(stratify_column) == stratum
                ).row_indices()
                n_stratum = len(stratum_indices)
                n_test = int(n_stratum * test_size)
                n_val = int(n_stratum * validation_size)

                # Shuffle indices
                np.random.shuffle(stratum_indices)

                # Split indices
                test_indices.extend(stratum_indices[:n_test])
                val_indices.extend(stratum_indices[n_test : n_test + n_val])
                train_indices.extend(stratum_indices[n_test + n_val :])

            train_df = df.filter(pl.col("index").is_in(train_indices))
            val_df = df.filter(pl.col("index").is_in(val_indices))
            test_df = df.filter(pl.col("index").is_in(test_indices))

        else:
            # Random split
            random_values = np.random.rand(len(df))

            val_threshold = 1.0 - (validation_size + test_size)
            test_threshold = 1.0 - test_size

            df_with_random = df.with_columns(pl.Series("_random", random_values))

            train_df = df_with_random.filter(pl.col("_random") <= val_threshold).drop(
                "_random"
            )
            val_df = df_with_random.filter(
                (pl.col("_random") > val_threshold)
                & (pl.col("_random") <= test_threshold)
            ).drop("_random")
            test_df = df_with_random.filter(pl.col("_random") > test_threshold).drop(
                "_random"
            )

    # Extract labels if present
    if "label" in df.columns:
        y_train = train_df.select("label")
        y_val = val_df.select("label")
        y_test = test_df.select("label")
        X_train = train_df.drop("label")
        X_val = val_df.drop("label")
        X_test = test_df.drop("label")
    else:
        X_train = train_df
        X_val = val_df
        X_test = test_df
        y_train = None
        y_val = None
        y_test = None

    logger.info(
        f"Split complete: train={X_train.shape[0]} rows, "
        f"validation={X_val.shape[0]} rows, "
        f"test={X_test.shape[0]} rows"
    )

    return X_train, X_val, X_test, y_train, y_val, y_test


def temporal_split(
    df: pl.DataFrame,
    n_splits: int = 5,
    gap: int = 0,
    time_column: str = "t_dat",
) -> List[Tuple[np.ndarray, np.ndarray]]:
    """
    Create temporal cross-validation splits for time series data.

    Args:
        df: Input DataFrame
        n_splits: Number of splits to create
        gap: Number of samples to exclude between train and test
        time_column: Column containing timestamps

    Returns:
        List of (train_indices, test_indices) tuples
    """
    if time_column not in df.columns:
        raise ValueError(f"Time column '{time_column}' not found in DataFrame")

    # Sort by time
    df = df.sort(time_column)

    # Get unique timestamps
    timestamps = df[time_column].unique().sort()
    n_samples = len(timestamps)

    # Calculate test size
    test_size = n_samples // (n_splits + 1)

    splits = []
    for i in range(n_splits):
        # Calculate indices
        test_end = n_samples - i * test_size
        test_start = test_end - test_size
        train_end = test_start - gap

        if train_end <= 0:
            logger.warning(f"Not enough data for {n_splits} splits with gap={gap}")
            break

        # Get timestamps for this split
        train_times = timestamps[:train_end]
        test_times = timestamps[test_start:test_end]

        # Get indices
        train_indices = df.filter(pl.col(time_column).is_in(train_times)).row_indices()
        test_indices = df.filter(pl.col(time_column).is_in(test_times)).row_indices()

        splits.append((train_indices, test_indices))

    return splits


def grouped_split(
    df: pl.DataFrame,
    group_column: str,
    test_size: float = 0.2,
    validation_size: Optional[float] = None,
    seed: int = 42,
) -> Union[
    Tuple[pl.DataFrame, pl.DataFrame], Tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]
]:
    """
    Split data ensuring that all rows with the same group value stay together.
    Useful for user-based or item-based splitting in recommendation systems.

    Args:
        df: Input DataFrame
        group_column: Column to group by (e.g., 'user_id', 'item_id')
        test_size: Proportion of groups to use for testing
        validation_size: Proportion of groups to use for validation
        seed: Random seed for reproducibility

    Returns:
        Tuple of DataFrames: (train_df, test_df) or (train_df, val_df, test_df)
    """
    if group_column not in df.columns:
        raise ValueError(f"Group column '{group_column}' not found in DataFrame")

    # Get unique groups
    groups = df[group_column].unique()
    n_groups = len(groups)

    # Set random seed
    np.random.seed(seed)

    # Shuffle groups
    shuffled_groups = groups.to_list()
    np.random.shuffle(shuffled_groups)

    if validation_size is None:
        # Two-way split
        n_test = int(n_groups * test_size)

        test_groups = shuffled_groups[:n_test]
        train_groups = shuffled_groups[n_test:]

        train_df = df.filter(pl.col(group_column).is_in(train_groups))
        test_df = df.filter(pl.col(group_column).is_in(test_groups))

        logger.info(
            f"Grouped split: train={train_df.shape[0]} rows ({len(train_groups)} groups), "
            f"test={test_df.shape[0]} rows ({len(test_groups)} groups)"
        )

        return train_df, test_df

    else:
        # Three-way split
        n_test = int(n_groups * test_size)
        n_val = int(n_groups * validation_size)

        test_groups = shuffled_groups[:n_test]
        val_groups = shuffled_groups[n_test : n_test + n_val]
        train_groups = shuffled_groups[n_test + n_val :]

        train_df = df.filter(pl.col(group_column).is_in(train_groups))
        val_df = df.filter(pl.col(group_column).is_in(val_groups))
        test_df = df.filter(pl.col(group_column).is_in(test_groups))

        logger.info(
            f"Grouped split: train={train_df.shape[0]} rows ({len(train_groups)} groups), "
            f"validation={val_df.shape[0]} rows ({len(val_groups)} groups), "
            f"test={test_df.shape[0]} rows ({len(test_groups)} groups)"
        )

        return train_df, val_df, test_df
