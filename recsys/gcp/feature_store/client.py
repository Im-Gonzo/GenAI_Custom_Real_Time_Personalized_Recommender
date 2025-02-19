"""
Feature Store client and management utilities.
"""

from typing import List, Tuple, Optional
from google.cloud import aiplatform
from loguru import logger

from recsys.config import settings
from recsys.gcp.bigquery.client import fetch_feature_view_data
from vertexai.resources.preview.feature_store import FeatureOnlineStore, FeatureView


def initialize() -> None:
    """Initialize Vertex AI with project settings."""
    aiplatform.init(project=settings.GCP_PROJECT, location=settings.GCP_LOCATION)


def get_client() -> FeatureOnlineStore:
    """
    Get the Feature Store client.

    Returns:
        Feature Store client

    Raises:
        RuntimeError: If feature store cannot be accessed
    """
    try:
        logger.info(
            f"Retrieving Feature Store from "
            f"{settings.GCP_LOCATION}/{settings.GCP_PROJECT}/"
            f"{settings.VERTEX_FEATURE_STORE_ID}"
        )

        initialize()
        return FeatureOnlineStore(settings.VERTEX_FEATURE_STORE_ID)

    except Exception as e:
        logger.error(f"Error retrieving Feature Store: {str(e)}")
        raise


def get_feature_views(
    feature_store: FeatureOnlineStore, view_ids: Optional[List[str]] = None
) -> Tuple[FeatureView]:
    """
    Get feature views from the feature store.

    Args:
        feature_store: Feature store client
        view_ids: List of view IDs to retrieve (default: standard views)

    Returns:
        List of feature views
    """
    if view_ids is None:
        view_ids = ["transactions", "articles", "customers", "rankings"]

    views = []
    for view_id in view_ids:
        view = FeatureView(view_id, feature_store.name)
        views.append(view)

    return tuple(views)
