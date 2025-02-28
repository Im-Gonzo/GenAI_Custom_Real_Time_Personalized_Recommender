"""
Ranking feature generation and processing.
"""

import time
import polars as pl
from loguru import logger
from typing import List, Optional
from google.cloud import bigquery
from vertexai.resources.preview.feature_store import FeatureView


def fetch_feature_view_data(
    feature_view: FeatureView,
    select_columns: Optional[List[str]] = None,
    except_columns: Optional[List[str]] = None,
) -> pl.DataFrame:
    """
    Fetch data from a feature view.

    Args:
        feature_view: Feature view to query
        select_columns: Columns to include (if None, all columns except except_columns)
        except_columns: Columns to exclude (only used if select_columns is None)

    Returns:
        DataFrame containing feature view data
    """
    client = bigquery.Client()
    table_ref = feature_view.gca_resource.big_query_source.uri.replace("bq://", "")

    if select_columns:
        columns_str = ", ".join(select_columns)
        query = f"SELECT {columns_str} FROM `{table_ref}`"
    elif except_columns:
        query = f"SELECT * EXCEPT({', '.join(except_columns)}) FROM `{table_ref}`"
    else:
        query = f"SELECT * FROM `{table_ref}`"

    query_result = client.query(query)
    return pl.from_pandas(query_result.to_dataframe())


def compute_rankings_dataset(
    trans_fv: FeatureView,
    articles_fv: FeatureView,
    customers_fv: FeatureView,
) -> pl.DataFrame:
    """
    Compute ranking dataset using GCP feature views.

    Args:
        trans_fv: Transactions feature view
        articles_fv: Articles feature view
        customers_fv: Customers feature view

    Returns:
        DataFrame containing ranking dataset
    """
    total_start = time.time()
    logger.info("Computing rankings dataset")

    # Fetch data from feature views
    logger.info("Fetching transactions data...")
    trans_df = fetch_feature_view_data(
        trans_fv, select_columns=["article_id", "customer_id"]
    )

    logger.info("Fetching articles data...")
    articles_df = fetch_feature_view_data(
        articles_fv, except_columns=["article_description", "embeddings", "image_url"]
    )

    logger.info("Fetching customers data...")
    customers_df = fetch_feature_view_data(
        customers_fv, select_columns=["customer_id", "age"]
    )

    # Type casting
    trans_df = trans_df.with_columns(pl.col("article_id").cast(pl.Utf8))
    articles_df = articles_df.with_columns(pl.col("article_id").cast(pl.Utf8))

    # Process unique transactions
    query_features = ["customer_id", "article_id"]
    df = trans_df.select(query_features).unique()

    # Join with customer data
    df = df.join(
        customers_df.select(["customer_id", "age"]), on="customer_id", how="left"
    )

    # Create positive pairs
    positive_pairs = df.clone()

    # Generate negative samples
    logger.info("Generating negative samples...")
    n_neg = len(positive_pairs) * 1

    article_ids = (
        df.select("article_id")
        .unique()
        .sample(n=n_neg, with_replacement=True, seed=2)
        .get_column("article_id")
    )

    customer_ids = (
        df.select("customer_id")
        .sample(n=n_neg, with_replacement=True, seed=3)
        .get_column("customer_id")
    )

    other_features = df.select(["age"]).sample(n=n_neg, with_replacement=True, seed=4)

    # Create negative pairs
    logger.info("Creating negative pairs...")
    negative_pairs = pl.DataFrame(
        {
            "article_id": article_ids,
            "customer_id": customer_ids,
            "age": other_features.get_column("age"),
        }
    )

    # Add labels
    positive_pairs = positive_pairs.with_columns(pl.lit(1).alias("label"))
    negative_pairs = negative_pairs.with_columns(pl.lit(0).alias("label"))

    # Combine positive and negative pairs
    logger.info("Combining positive and negative pairs...")
    ranking_df = pl.concat(
        [positive_pairs, negative_pairs.select(positive_pairs.columns)]
    )

    # Join with item features
    logger.info("Joining with item features...")
    item_df = articles_df.unique(subset=["article_id"])
    ranking_df = ranking_df.join(item_df, on="article_id", how="left")

    total_time = time.time() - total_start
    logger.info(f"Total processing time: {total_time:.2f} seconds")
    logger.info(f"Final DataFrame shape: {ranking_df.shape}")

    return ranking_df
