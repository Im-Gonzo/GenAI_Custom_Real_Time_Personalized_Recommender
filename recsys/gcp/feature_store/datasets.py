"""
Feature Store dataset creation utilities.
"""
import polars as pl
from loguru import logger
from google.cloud import aiplatform
from typing import Dict, List, Optional

from recsys.gcp.bigquery.client import fetch_feature_view_data
from vertexai.resources.preview.feature_store import FeatureView


def create_training_dataset(
    trans_view: FeatureView,
    articles_view: FeatureView,
    customers_view: FeatureView,
    feature_columns: Optional[Dict[str, List[str]]] = None
) -> pl.DataFrame:
    """
    Create training dataset by joining feature views.
    
    Args:
        trans_view: Transactions feature view
        articles_view: Articles feature view
        customers_view: Customers feature view
        feature_columns: Dict mapping view names to columns to select
        
    Returns:
        DataFrame containing joined features
    """
    if feature_columns is None:
        feature_columns = {
            "transactions": [
                "customer_id",
                "article_id",
                "t_dat",
                "price",
                "month_sin",
                "month_cos",
            ],
            "customers": [
                "customer_id",
                "age",
                "club_member_status",
                "age_group"
            ],
            "articles": [
                "article_id",
                "garment_group_name",
                "index_group_name"
            ]
        }

    logger.info("Fetching transactions data...")
    trans_df = fetch_feature_view_data(
        trans_view,
        select_columns=feature_columns["transactions"]
    )

    logger.info("Fetching customer data...")
    customers_df = fetch_feature_view_data(
        customers_view,
        select_columns=feature_columns["customers"]
    )

    logger.info("Fetching article data...")
    articles_df = fetch_feature_view_data(
        articles_view,
        select_columns=feature_columns["articles"]
    )

    logger.info("Joining features...")
    return (
        trans_df.join(customers_df, on="customer_id")
        .join(articles_df, on="article_id")
    )


def create_ranking_dataset(
    trans_view: FeatureView,
    articles_view: FeatureView,
    customers_view: FeatureView,
    feature_columns: Optional[Dict[str, List[str]]] = None
) -> pl.DataFrame:
    """
    Create ranking dataset from feature views.
    
    Args:
        trans_view: Transactions feature view
        articles_view: Articles feature view
        customers_view: Customers feature view
        feature_columns: Dict mapping view names to columns to select
        
    Returns:
        DataFrame prepared for ranking
    """
    if feature_columns is None:
        feature_columns = {
            "transactions": [
                "customer_id",
                "article_id",
                "t_dat"
            ],
            "customers": [
                "customer_id",
                "age"
            ],
            "articles": [
                "article_id",
                "garment_group_name",
                "index_group_name",
                "product_type_name",
                "product_group_name",
                "graphical_appearance_name",
                "colour_group_name",
                "perceived_colour_value_name",
                "perceived_colour_master_name"
            ]
        }

    logger.info("Creating base training dataset...")
    df = create_training_dataset(
        trans_view=trans_view,
        articles_view=articles_view,
        customers_view=customers_view,
        feature_columns=feature_columns
    )

    # Add any ranking-specific transformations here
    logger.info("Applying ranking transformations...")
    
    return df
