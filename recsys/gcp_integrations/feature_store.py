from typing import List, Tuple, Any, Optional

from google.cloud import aiplatform
from loguru import logger

from recsys.config import settings


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

        # Initialize Vertex AI
        aiplatform.init(project=settings.GCP_PROJECT, location=settings.GCP_LOCATION)

        # Create feature store client
        client = aiplatform.gapic.FeatureOnlineStoreServiceClient()

        # Format the feature store path
        feature_store_path = client.feature_online_store_path(
            project=settings.GCP_PROJECT,
            location=settings.GCP_LOCATION,
            feature_online_store=settings.VERTEX_FEATURE_STORE_ID,
        )

        return client, feature_store_path

    except Exception as e:
        logger.error(f"Error retrieving Feature Store: {str(e)}")
        raise


def read_feature_values(
    client: Any, feature_store_path: str, entity_type: str, entity_ids: List[str]
) -> Any:
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
    try:
        request = aiplatform.gapic.ReadFeatureValuesRequest(
            feature_online_store=feature_store_path,
            entity_type=entity_type,
            entity_ids=entity_ids,
        )
        response = client.read_feature_values(request=request)
        return response

    except Exception as e:
        logger.error(f"Error reading features for {entity_type}: {str(e)}")
        raise
