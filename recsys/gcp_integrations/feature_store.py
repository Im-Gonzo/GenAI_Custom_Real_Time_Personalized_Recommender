import polars as pl
from typing import List, Tuple

from google.cloud import aiplatform
from vertexai.resources.preview.feature_store import FeatureOnlineStore, FeatureView
from loguru import logger

from recsys.features.ranking import fetch_feature_view_data
from recsys.config import settings


aiplatform.init(project=settings.GCP_PROJECT, location=settings.GCP_LOCATION)


def get_feature_store():
    """
    Retrieves the Feature Store client and path.

    Returns:
        Tuple of (client, feature_store_path)
    """
    try:
        logger.info(
            f"Retrieving Feature Store from {settings.GCP_LOCATION}/{settings.GCP_PROJECT}/{settings.VERTEX_FEATURE_STORE_ID}"
        )

        fos = FeatureOnlineStore(settings.VERTEX_FEATURE_STORE_ID)

        return fos

    except Exception as e:
        logger.error(f"Error retrieving Feature Store: {str(e)}")
        raise


def create_retrieval_feature_view(
    fos, fv_ids: List = ["transactions", "articles", "customers"]
) -> Tuple[str]:
    """
    Reads feature values from the online store.

    Args:
        client: Feature Store client
        feature_store_path: Path to feature store
        entity_type: Type of entity to read
        entity_ids: List of entity IDs to retrieve

    Returns:
        Feature values response
    """
    fv_list: list = []

    for id in fv_ids:
        fv = FeatureView(id, fos.name)
        fv_list.append(fv)

    return tuple(fv_list)


def create_training_dataset(
    trans_fv: FeatureView,
    articles_fv: FeatureView,
    customers_fv: FeatureView,
) -> pl.DataFrame:
    trans_df = fetch_feature_view_data(
        trans_fv,
        select_columns=[
            "customer_id",
            "article_id",
            "t_dat",
            "price",
            "month_sin",
            "month_cos",
        ],
    )

    customers_df = fetch_feature_view_data(
        customers_fv,
        select_columns=["customer_id", "age", "club_member_status", "age_group"],
    )

    articles_df = fetch_feature_view_data(
        articles_fv,
        select_columns=["article_id", "garment_group_name", "index_group_name"],
    )

    return trans_df.join(customers_df, on="customer_id").join(
        articles_df, on="article_id"
    )
