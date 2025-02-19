"""
H&M dataset loading utilities.
"""
import polars as pl
from recsys.config import settings


def extract_articles_df() -> pl.DataFrame:
    """
    Extract articles data from GCS bucket.
    
    Returns:
        DataFrame containing article information
    """
    return pl.read_csv(
        f"gs://{settings.GCS_DATA_BUCKET}/articles.csv",
        try_parse_dates=True,
    )


def extract_customers_df() -> pl.DataFrame:
    """
    Extract customers data from GCS bucket.
    
    Returns:
        DataFrame containing customer information
    """
    return pl.read_csv(
        f"gs://{settings.GCS_DATA_BUCKET}/customers.csv",
        try_parse_dates=True,
    )


def extract_transactions_df() -> pl.DataFrame:
    """
    Extract transactions data from GCS bucket.
    
    Returns:
        DataFrame containing transaction information
    """
    return pl.read_csv(
        f"gs://{settings.GCS_DATA_BUCKET}/transactions_train.csv",
        try_parse_dates=True,
    )
