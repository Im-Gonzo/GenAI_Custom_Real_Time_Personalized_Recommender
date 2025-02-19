import shutil
import tensorflow as tf
import os
from xgboost import XGBModel

from loguru import logger
from typing import Union
from google.cloud import aiplatform
from recsys.config import settings


aiplatform.init(project=settings.GCP_PROJECT, location=settings.GCP_LOCATION)


def upload_model_to_registry(
    model: Union[tf.keras.Model, XGBModel],
    model_name: str,
    model_display_name: str,
    description: str,
    serving_container_image_uri: str,
) -> aiplatform.Model:
    """Upload a model to Vertex AI Model Registry"""

    model_dir = f"/tmp/{model_name}"
    logger.info(f"Saving model into: {model_dir}")

    if os.path.exists(model_dir):
        shutil.rmtree(model_dir)

    # Create directory if it doesn't exist
    os.makedirs(model_dir, exist_ok=True)

    # Handle different model types
    if isinstance(model, XGBModel):
        # Save XGBoost model in its native format
        model_path = os.path.join(model_dir, "model.bst")
        model.save_model(model_path)
    elif hasattr(model, "save"):  # TensorFlow models
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
    """Deploys a model to a Vertex AI Model Endpoint"""
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
