"""
Vertex AI model registry and deployment utilities.
"""

import os
import shutil
import tensorflow as tf
import xgboost as xgb
from xgboost import XGBModel
from loguru import logger
from typing import Union
from google.cloud.aiplatform import Model, init, Endpoint

from recsys.config import settings


def initialize_vertex_ai():
    """Initialize Vertex AI with project settings."""
    init(project=settings.GCP_PROJECT, location=settings.GCP_LOCATION)


def upload_model_to_registry(
    model: Union[tf.keras.Model, XGBModel],
    model_name: str,
    model_display_name: str,
    description: str,
    serving_container_image_uri: str,
) -> Model:
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
    uploaded_model = Model.upload(
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
    model: Model,
    endpoint_name: str,
    machine_type: str = "n1-standard-2",
    min_replica_count: int = 1,
    max_replica_count: int = 1,
) -> Endpoint:
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
    return Model.list(filter=filter_expression, order_by=order_by)


def get_model(
    model_name: str,
    model_version: str = "latest",
    download_model: bool = False,
    model_type: str = "auto",
) -> Union[tuple[Union[tf.keras.Model, xgb.Booster], list], Model]:
    """
    Get a specific model from Vertex AI, optionally downloading and extracting features.

    Args:
        model_name: Name of the model
        model_version: Version to retrieve (default: latest)
        download_model: Whether to download and load the model (default: False)
        model_type: Type of model to load ("tf", "xgboost", or "auto" for automatic detection)

    Returns:
        If download_model is True:
            Tuple of (loaded model, list of features/input names)
        If download_model is False:
            Vertex AI model reference

    Raises:
        RuntimeError: If model not found or can't be loaded
    """

    initialize_vertex_ai()

    models = list_models(
        filter_expression=f'display_name="{model_name}"', order_by="create_time desc"
    )

    if not models:
        raise RuntimeError(f"No model found with name: {model_name}")

    vertex_model: Model = None
    if model_version == "latest":
        vertex_model = models[0]
    else:
        for model in models:
            if model.version == model_version:
                vertex_model = model
                break

        if vertex_model is None:
            raise RuntimeError(
                f"Version {model_version} not found for model: {model_name}"
            )

    if not download_model:
        return vertex_model

    model_uri = vertex_model.uri
    logger.info(f"Model URI: {model_uri}")

    if model_type == "auto":
        if (
            "xgboost" in vertex_model.container_spec.image_uri.lower()
            or model_name.lower().startswith("ranking")
        ):
            model_type = "xgboost"
        else:
            model_type = "tf"

    logger.info(f"Loading {model_type} model from {model_uri}")

    if model_type == "tf":
        loaded_model = tf.saved_model.load(vertex_model.uri)
        features = []
        try:
            features = [
                *loaded_model.signatures["serving_default"]
                .structured_input_signature[-1]
                .keys()
            ]
            logger.info(f"Extracted {len(features)} input features from model")
        except (KeyError, AttributeError, IndexError) as e:
            logger.warning(f"Could not extract features from model signature: {e}")
    elif model_type == "xgboost":
        import tempfile
        from google.cloud import storage

        gcs_path = model_uri.replace("gs://", "")
        bucket_name = gcs_path.split("/")[0]
        prefix = "/".join(gcs_path.split("/")[1:])

        temp_dir = tempfile.mkdtemp()
        local_model_path = os.path.join(temp_dir, "model.bst")

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        model_blob_path = os.path.join(prefix, "model.bst")
        blob = bucket.blob(model_blob_path)

        logger.info(f"Downloading from GCS: {model_blob_path} to {local_model_path}")
        blob.download_to_filename(local_model_path)

        # Load to XGBooster
        loaded_model = xgb.Booster()
        loaded_model.load_model(local_model_path)
        logger.info("XGBoost model loaded")

        try:
            os.remove(local_model_path)
            os.rmdir(temp_dir)
        except:
            pass

        try:
            features = loaded_model.feature_names
            if not features:
                logger.warning("XGBoost model has no feature names")
                features = []
        except AttributeError:
            logger.warning("Could not extract feature names from XGBoost model")
            features = []
    else:
        raise ValueError(f"Unsupported model_type: {model_type}")

    return loaded_model, features
