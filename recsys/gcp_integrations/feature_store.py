from typing import List, Tuple, Any, Optional

from google.cloud import aiplatform
from vertexai.resources.preview.feature_store import FeatureOnlineStore, FeatureView
from loguru import logger

from recsys.config import settings


aiplatform.init(project=settings.GCP_PROJECT, location=settings.GCP_LOCATION)


def get_feature_store() -> Tuple[Any, str]:
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
    fos, fv_ids: list = ["transactions", "articles", "customers"]
) -> tuple:
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
