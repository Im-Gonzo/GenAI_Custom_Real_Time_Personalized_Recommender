import polars as pl
from google.cloud import bigquery
from vertexai.resources.preview.feature_store import FeatureView
from loguru import logger
import time


def compute_rankings_dataset(
    trans_fv: FeatureView,
    articles_fv: FeatureView,
    customers_fv: FeatureView,
) -> pl.DataFrame:
    """Computes ranking dataset using GCP feature views"""

    total_start = time.time()
    logger.info("Starting to compute rankings dataset")

    # Fetch transactions with only needed columns
    logger.info("Fetching transactions data...")
    trans_df = fetch_feature_view_data(
        trans_fv, select_columns=["article_id", "customer_id"]
    )

    # Fetch articles excluding heavy columns
    logger.info("Fetching articles data...")
    articles_df = fetch_feature_view_data(
        articles_fv, except_columns=["article_description", "embeddings", "image_url"]
    )

    # Fetch customers with minimal required columns
    logger.info("Fetching customers data...")
    customers_df = fetch_feature_view_data(
        customers_fv, select_columns=["customer_id", "age"]
    )

    # Type casting
    logger.info("Casting article_id to string...")
    trans_df = trans_df.with_columns(pl.col("article_id").cast(pl.Utf8))
    articles_df = articles_df.with_columns(pl.col("article_id").cast(pl.Utf8))

    # Get unique transactions with query features
    logger.info("Processing unique transactions...")
    query_features = ["customer_id", "article_id"]
    df = trans_df.select(query_features).unique()

    # Join with customers data
    logger.info("Joining with customers data...")
    df = df.join(
        customers_df.select(["customer_id", "age"]), on="customer_id", how="left"
    )

    # Create positive pairs
    logger.info("Creating positive pairs...")
    positive_pairs = df.clone()

    # Negative sampling
    logger.info("Starting negative sampling...")
    n_neg = len(positive_pairs) * 10

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

    # Construct negative pairs
    logger.info("Constructing negative pairs...")
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

    # Concatenate positive and negative pairs
    logger.info("Concatenating pairs...")
    ranking_df = pl.concat(
        [positive_pairs, negative_pairs.select(positive_pairs.columns)]
    )

    # Final join with item features
    logger.info("Performing final join with item features...")
    item_df = articles_df.unique(subset=["article_id"])
    ranking_df = ranking_df.join(item_df, on="article_id", how="left")

    total_time = time.time() - total_start
    logger.info(f"Total processing time: {total_time:.2f} seconds")
    logger.info(f"Final DataFrame shape: {ranking_df.shape}")

    return ranking_df
