"""
Base class for model serving in Vertex AI.
"""

from abc import ABC, abstractmethod
from typing import Optional
from loguru import logger
from google.cloud import aiplatform

from recsys.config import settings
from recsys.gcp.vertex_ai.model_registry import (
    initialize_vertex_ai,
    upload_model_to_registry,
)


class BaseGCPModel(ABC):
    """Base class for GCP model integration."""

    def __init__(self, model) -> None:
        self.model = model
        self.local_model_path = None

    @abstractmethod
    def save_to_local(self, output_path: str) -> str:
        """
        Save the model in appropriate format.

        Args:
            output_path: Path to save the model

        Returns:
            Path where model was saved
        """
        pass

    def upload_to_vertex_ai(
        self,
        model_name: str,
        description: str,
        serving_container_image_uri: Optional[str] = None,
    ) -> aiplatform.Model:
        """
        Upload the model to Vertex AI Model Registry.

        Args:
            model_name: Name for the model
            description: Model description
            serving_container_image_uri: URI for serving container

        Returns:
            Uploaded Vertex AI model

        Raises:
            ValueError: If model not saved locally first
        """
        if not self.local_model_path:
            raise ValueError("Model must be saved locally first using save_to_local()")

        initialize_vertex_ai()

        # Use default container if none provided
        if not serving_container_image_uri:
            serving_container_image_uri = (
                f"{settings.GCP_ARTIFACT_REGISTRY}/two-tower:latest"
            )

        return upload_model_to_registry(
            model=self.model,
            model_name=model_name,
            model_display_name=model_name,
            description=description,
            serving_container_image_uri=serving_container_image_uri,
        )

    def deploy_endpoint(
        self,
        model: aiplatform.Model,
        endpoint_id: str,
        machine_type: str = "n1-standard-2",
        min_replica_count: int = 1,
        max_replica_count: int = 1,
    ) -> aiplatform.Endpoint:
        """
        Deploy the model to a Vertex AI endpoint.

        Args:
            model: Model to deploy
            endpoint_id: Endpoint identifier
            machine_type: GCP machine type
            min_replica_count: Minimum replicas
            max_replica_count: Maximum replicas

        Returns:
            Deployed endpoint

        Raises:
            RuntimeError: If endpoint not found or deployment fails
        """
        try:
            # Find existing endpoint
            endpoints = aiplatform.Endpoint.list(filter=f'display_name="{endpoint_id}"')

            if len(endpoints) > 0:
                endpoint = endpoints[0]
                logger.info(f"Found existing endpoint: {endpoint_id}")
            else:
                raise RuntimeError(
                    f"Endpoint {endpoint_id} not found. "
                    "Please ensure it's created in Terraform."
                )

            # Deploy model
            model.deploy(
                endpoint=endpoint,
                machine_type=machine_type,
                min_replica_count=min_replica_count,
                max_replica_count=max_replica_count,
                sync=True,
            )

            logger.info(f"Model deployed to endpoint: {endpoint.resource_name}")
            return endpoint

        except Exception as e:
            logger.error(f"Error deploying model to endpoint {endpoint_id}: {str(e)}")
            raise
