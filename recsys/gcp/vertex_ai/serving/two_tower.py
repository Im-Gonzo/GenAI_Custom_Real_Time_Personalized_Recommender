"""
Two-tower model serving implementation.
"""

import tensorflow as tf
from loguru import logger
from typing import Tuple, Dict, Any
from google.cloud import aiplatform

from recsys.config import settings
from recsys.gcp.vertex_ai.serving.base import BaseGCPModel
from recsys.gcp.vertex_ai.model_registry import initialize_vertex_ai


class QueryModelModule(tf.Module):
    """Module wrapper for query tower serving."""

    def __init__(self, model: "QueryTower") -> None:
        self.model = model

    @tf.function
    def compute_embedding(
        self, instances: Dict[str, tf.Tensor]
    ) -> Dict[str, tf.Tensor]:
        """
        Compute embeddings for query instances.

        Args:
            instances: Dictionary containing query features

        Returns:
            Dictionary with computed embeddings
        """
        query_embedding = self.model(instances)

        return {
            "customer_id": instances["customer_id"],
            "month_sin": instances["month_sin"],
            "month_cos": instances["month_cos"],
            "query_emb": query_embedding,
        }


class GCPQueryModel(BaseGCPModel):
    """GCP integration for the query tower."""

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
        """
        Save the query tower model in TensorFlow SavedModel format.

        Args:
            output_path: Directory to save the model

        Returns:
            Path where model was saved
        """
        # Define input specifications
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

        # Create serving module and get inference function
        query_module = QueryModelModule(model=self.model)
        inference_signatures = query_module.compute_embedding.get_concrete_function(
            instances_spec
        )

        # Save model with signatures
        tf.saved_model.save(
            self.model,
            output_path,
            signatures=inference_signatures,
        )

        self.local_model_path = output_path
        return output_path


class GCPCandidateModel(BaseGCPModel):
    """GCP integration for the candidate tower."""

    def __init__(self, model: "ItemTower"):
        super().__init__(model)

    def save_to_local(self, output_path: str = "candidate_model") -> str:
        """
        Save the candidate tower model in TensorFlow SavedModel format.

        Args:
            output_path: Directory to save the model

        Returns:
            Path where model was saved
        """
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
        """
        Load the latest version of the candidate model from Vertex AI.

        Args:
            model_name: Name of the model to load

        Returns:
            Tuple of (loaded model, feature names)

        Raises:
            RuntimeError: If model not found
        """
        initialize_vertex_ai()

        # Get latest model version
        models = aiplatform.Model.list(
            filter=f'display_name="{model_name}"',
            order_by="create_time desc",
        )

        if not models:
            raise RuntimeError(f"No '{model_name}' found in Vertex AI model registry.")

        latest_model = models[0]
        logger.info(f"Loading '{model_name}' version {latest_model.version}")

        # Download and load model
        model_path = latest_model.download()
        candidate_model = tf.saved_model.load(model_path)

        # Extract feature names
        candidate_features = [
            *candidate_model.signatures["serving_default"]
            .structured_input_signature[-1]
            .keys()
        ]

        return candidate_model, candidate_features
