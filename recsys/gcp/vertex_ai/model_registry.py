"""
Vertex AI model registry and deployment utilities.
"""

import shutil
import tensorflow as tf
import os
from xgboost import XGBModel
from loguru import logger
from typing import Union
from google.cloud import aiplatform

from recsys.config import settings


def initialize_vertex_ai():
    """Initialize Vertex AI with project settings."""
    aiplatform.init(project=settings.GCP_PROJECT, location=settings.GCP_LOCATION)


def upload_model_to_registry(
    model: Union[tf.keras.Model, XGBModel],
    model_name: str,
    model_display_name: str,
    description: str,
    serving_container_image_uri: str,
) -> aiplatform.Model:
    """
    Upload a model to Vertex AI Model Registry.

    Args:
        model: Model to upload (TensorFlow or XGBoost)
        model_name: Name for local model storage
        model_display_name: Display name in Vertex AI
        description: Model description
        serving_container_image_uri: URI for serving container

    Returns:
        Uploaded Vertex AI model
    """
    initialize_vertex_ai()

    model_dir = f"/tmp/{model_name}"
    logger.info(f"Saving model into: {model_dir}")

    if os.path.exists(model_dir):
        shutil.rmtree(model_dir)

    os.makedirs(model_dir, exist_ok=True)

    # Handle different model types
    if isinstance(model, XGBModel):
        model_path = os.path.join(model_dir, "model.bst")
        model.save_model(model_path)
    elif hasattr(model, "save"):
        model.save(model_dir)
    else:
        raise ValueError(f"Unsupported model type: {type(model)}")

    logger.info(f"Uploading model to {model_display_name} to Vertex AI")
    uploaded_model = aiplatform.Model.upload(
        display_name=model_display_name,
        artifact_uri=model_dir,
        serving_container_image_uri=serving_container_image_uri,
        description=description,
        serving_container_predict_route="/v1/predict",
        serving_container_health_route="/v1/health",
    )

    logger.info(f"Model uploaded with resource name: {uploaded_model.resource_name}")
    return uploaded_model


def deploy_model_to_endpoint(
    model: aiplatform.Model,
    endpoint_name: str,
    machine_type: str = "n1-standard-2",
    min_replica_count: int = 1,
    max_replica_count: int = 1,
) -> aiplatform.Endpoint:
    """
    Deploy a model to a Vertex AI Model Endpoint.

    Args:
        model: Model to deploy
        endpoint_name: Name for the endpoint
        machine_type: GCP machine type
        min_replica_count: Minimum number of replicas
        max_replica_count: Maximum number of replicas

    Returns:
        Deployed endpoint
    """
    initialize_vertex_ai()

    logger.info(f"Deploying model to {endpoint_name}")
    endpoint = model.deploy(
        deployed_model_display_name=endpoint_name,
        machine_type=machine_type,
        min_replica_count=min_replica_count,
        max_replica_count=max_replica_count,
        sync=True,
    )
    logger.info(f"Model deployed to endpoint: {endpoint.resource_name}")
    return endpoint


def list_models(
    filter_expression: str = None, order_by: str = "create_time desc"
) -> list:
    """
    List models in Vertex AI Model Registry.

    Args:
        filter_expression: Filter for models
        order_by: Ordering expression

    Returns:
        List of matching models
    """
    initialize_vertex_ai()
    return aiplatform.Model.list(filter=filter_expression, order_by=order_by)


def get_model(model_name: str, model_version: str = "latest") -> aiplatform.Model:
    """
    Get a specific model from Vertex AI.

    Args:
        model_name: Name of the model
        model_version: Version to retrieve (default: latest)

    Returns:
        Retrieved model

    Raises:
        RuntimeError: If model not found
    """
    initialize_vertex_ai()

    models = list_models(
        filter_expression=f'display_name="{model_name}"', order_by="create_time desc"
    )

    if not models:
        raise RuntimeError(f"No model found with name: {model_name}")

    if model_version == "latest":
        return models[0]

    for model in models:
        if model.version == model_version:
            return model

    raise RuntimeError(f"Version {model_version} not found for model: {model_name}")
