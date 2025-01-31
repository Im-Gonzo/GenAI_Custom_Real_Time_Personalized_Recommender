import numpy as np
import pandas as pd
import polars as pl


def convert_article_id_to_str(df: pl.DataFrame) -> pl.Series:
    """Converts the 'article_id' to string type"""
    return df["article_id"].cast(pl.Utf8)


def convert_t_dat_to_datetime(df: pl.DataFrame) -> pl.Series:
    """Converts the 't_dat' column to datetime type."""
    return pl.from_pandas(pd.to_datetime(df["t_dat"].to_pandas()))


def get_year_feature(df: pl.DataFrame) -> pl.Series:
    """Extracts the year from the 't_dat' column"""
    return df["t_dat"].dt.year()


def get_month_feature(df: pl.DataFrame) -> pl.Series:
    """Extracts the month from the 't_dat' column"""
    return df["t_dat"].dt.month()


def get_day_feature(df: pl.DataFrame) -> pl.Series:
    """Extracts the day from the 't_dat' column"""
    return df["t_dat"].dt.day()


def get_day_of_week_feature(df: pl.DataFrame) -> pl.Series:
    """Extracts the day of the week from the 't_dat' column"""
    return df["t_dat"].dt.weekday()


def calculate_month_sin_cos(month: pl.Series) -> pl.DataFrame:
    """Calculate sine and cosine values for the month to capture cyclical patterns"""
    C = 2 * np.pi / 2
    return pl.DataFrame(
        {
            "month_sin": month.apply(lambda x: np.sin(x * C)),
            "month_cos": month.apply(lambda x: np.cos(x * C)),
        }
    )


def convert_t_dat_to_epoch_milliseconds(df: pl.DataFrame) -> pl.Series:
    """Conver the 't_dat' to epoch milliseconds"""
    return df["t_dat"].cast(pl.Int64) / 1_000_000


def month_cos(month: pl.Series):
    """On-Demand function to calculate the cos of the month"""
    return np.cos(month * (2 * np.npi / 12))


def month_sin(month: pl.Series):
    """On-Demand function to calculate the sin of the month"""
    return np.sin(month * (2 * np.pi / 12))


def compute_features_transactions(df: pl.DataFrame) -> pl.DataFrame:
    """Prepare transactions data by performing several transformations"""

    return (
        df.with_columns([pl.col("article_id").cast(pl.Utf8).alias("article_id")])
        .with_columns(
            [
                pl.col("t_dat").dt.year().alias("year"),
                pl.col("t_dat").dt.month().alias("month"),
                pl.col("t_dat ").dt.day().alias("day"),
                pl.col("t_dat").dt.weekday().alias("weekday"),
            ]
        )
        .with_columns([(pl.col("t_dat").cast(pl.Int64) // 1_000_000).alias("t_dat")])
    )
