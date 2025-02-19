import tensorflow as tf
from loguru import logger
from recsys.config import settings
from typing import Optional, Tuple
from abc import ABC, abstractmethod
from google.cloud import aiplatform
from recsys.gcp_integrations.model_registry import (
    upload_model_to_registry,
    deploy_model_to_endpoint,
)


class BaseGCPModel(ABC):
    """Base class for GCP model integration."""

    def __init__(self, model) -> None:
        self.model = model
        self.local_model_path = None

    @abstractmethod
    def save_to_local(self, output_path: str) -> str:
        """Save the model in TensorFlow SavedModel format."""
        pass

    def upload_to_vertex_ai(
        self,
        model_name: str,
        description: str,
        serving_container_image_uri: Optional[str] = None,
    ) -> aiplatform.Model:
        """Upload the model to Vertex AI Model Registry."""
        if not self.local_model_path:
            raise ValueError("Model must be saved locally first using save_to_local()")

        # Initialize Vertex AI with project and location
        aiplatform.init(
            project=settings.GCP_PROJECT,
            location=settings.GCP_LOCATION,
        )

        # Use default TensorFlow serving container if none provided
        if not serving_container_image_uri:
            serving_container_image_uri = (
                f"{settings.GCP_ARTIFACT_REGISTRY}/two-tower:latest"
            )

        # Upload model to Vertex AI Registry
        model = upload_model_to_registry(
            model=self.model,
            model_name=model_name,
            model_display_name=model_name,
            description=description,
            serving_container_image_uri=serving_container_image_uri,
        )

        return model

    def deploy_endpoint(
        self,
        model: aiplatform.Model,
        endpoint_id: str,
        machine_type: str = "n1-standard-2",
        min_replica_count: int = 1,
        max_replica_count: int = 1,
    ) -> aiplatform.Endpoint:
        """Deploy the model to a Vertex AI endpoint."""
        # Get pre-created endpoint based on model type
        try:
            # Try to get the existing endpoint
            endpoints = aiplatform.Endpoint.list(filter=f'display_name="{endpoint_id}"')
            if len(endpoints) > 0:
                endpoint = endpoints[0]
                logger.info(f"Found existing endpoint: {endpoint_id}")
            else:
                raise RuntimeError(
                    f"Endpoint {endpoint_id} not found. Please ensure it's created in Terraform."
                )

            # Deploy model to endpoint
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


class QueryModelModule(tf.Module):
    def __init__(self, model: "QueryTower") -> None:
        self.model = model

    @tf.function()
    def compute_embedding(self, instances):
        query_embedding = self.model(instances)

        return {
            "customer_id": instances["customer_id"],
            "month_sin": instances["month_sin"],
            "month_cos": instances["month_cos"],
            "query_emb": query_embedding,
        }


class GCPQueryModel(BaseGCPModel):
    def __init__(self, model: "QueryTower") -> None:
        super().__init__(model)

        self.monitoring = {
            "enable_monitoring": True,
            "sampling_rate": 0.8,
            "monitor_window": "3600s",
            "feature_monitoring_config": {
                "target_field": "prediction",
                "feature_fields": ["customer_id", "age", "month_sin", "month_cos"],
                "objective_config": {
                    "training_dataset": "recsys-dev-gonzo.recsys_dataset.recsys_transactions",
                },
            },
        }

    def save_to_local(self, output_path: str = "query_model") -> str:
        """Save the query tower model in TensorFlow SavedModel format."""
        # Define the input specifications for the instances
        instances_spec = {
            "customer_id": tf.TensorSpec(
                shape=(None,), dtype=tf.string, name="customer_id"
            ),
            "month_sin": tf.TensorSpec(
                shape=(None,), dtype=tf.float64, name="month_sin"
            ),
            "month_cos": tf.TensorSpec(
                shape=(None,), dtype=tf.float64, name="month_cos"
            ),
            "age": tf.TensorSpec(shape=(None,), dtype=tf.float64, name="age"),
        }

        query_module = QueryModelModule(model=self.model)
        inference_signatures = query_module.compute_embedding.get_concrete_function(
            instances_spec
        )

        # Save the model with signatures
        tf.saved_model.save(
            self.model,
            output_path,
            signatures=inference_signatures,
        )

        self.local_model_path = output_path
        return output_path


class GCPCandidateModel(BaseGCPModel):
    def __init__(self, model: "ItemTower"):
        super().__init__(model)

    def save_to_local(self, output_path: str = "candidate_model") -> str:
        """Save the candidate tower model in TensorFlow SavedModel format."""
        tf.saved_model.save(
            self.model,
            output_path,
        )

        self.local_model_path = output_path
        return output_path

    @classmethod
    def load_from_vertex_ai(
        cls,
        model_name: str = "candidate_model",
    ) -> Tuple["ItemTower", dict]:
        """Load the latest version of the candidate model from Vertex AI."""
        # Initialize Vertex AI
        aiplatform.init(
            project=settings.GCP_PROJECT,
            location=settings.GCP_LOCATION,
        )

        # Get the latest model version
        models = aiplatform.Model.list(
            filter=f'display_name="{model_name}"',
            order_by="create_time desc",
        )

        if not models:
            raise RuntimeError(f"No '{model_name}' found in Vertex AI model registry.")

        latest_model = models[0]
        logger.info(f"Loading '{model_name}' version {latest_model.version}")

        # Download the model
        model_path = latest_model.download()
        candidate_model = tf.saved_model.load(model_path)

        # Get model features
        candidate_features = [
            *candidate_model.signatures["serving_default"]
            .structured_input_signature[-1]
            .keys()
        ]

        return candidate_model, candidate_features
