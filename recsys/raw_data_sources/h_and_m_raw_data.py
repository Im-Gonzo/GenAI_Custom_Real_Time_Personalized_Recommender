import polars as pl
from recsys.config import settings


def extract_articles_df() -> pl.DataFrame:
    return pl.read_csv(
        f"gs://{settings.GCS_DATA_BUCKET}/h-and-m/articles.csv",
        try_parse_dates=True,
    )


def extract_customers_df() -> pl.DataFrame:
    return pl.read_csv(
        f"gs://{settings.GCS_DATA_BUCKET}/h-and-m/customers.csv",
        try_parse_dates=True,
    )


def extract_transactions_df() -> pl.DataFrame:
    return pl.read_csv(
        f"gs://{settings.GCS_DATA_BUCKET}/h-and-m/transactions_train.csv",
        try_parse_dates=True,
    )
