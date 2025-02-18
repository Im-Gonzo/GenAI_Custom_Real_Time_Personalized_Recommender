from loguru import logger
from typing import Optional, Dict, Any
from google.cloud import aiplatform
import os

from recsys.config import settings
from recsys.gcp_integrations.two_tower_serving import BaseGCPModel


class GCPRankingModel(BaseGCPModel):
    """Class for handling ranking model integration with GCP."""
    
    def __init__(self, model: 'XGBClassifier') -> None:
        super().__init__(model)
        
        self.monitoring = {
            "enable_monitoring": True,
            "sampling_rate": 0.8,
            "monitor_window": "3600s",
            "feature_monitoring_config": {
                "target_field": "prediction",
                "feature_fields": [
                    "customer_id", "article_id", "age", "month_sin", "month_cos",
                    "product_type_name", "product_group_name", "graphical_appearance_name",
                    "colour_group_name", "perceived_colour_value_name",
                    "perceived_colour_master_name", "department_name", "index_name",
                    "index_group_name", "section_name", "garment_group_name"
                ],
                "objective_config": {
                    "training_dataset": "recsys-dev-gonzo.recsys_dataset.recsys_rankings",
                }
            }
        }

    def save_to_local(self, output_path: str = "ranking_model") -> str:
        """Save the ranking model in XGBoost format.
        
        This method is required by BaseGCPModel but the actual saving
        is handled by upload_model_to_registry.
        """
        return output_path

    def upload_to_vertex_ai(
        self,
        model_name: str,
        description: str,
        serving_container_image_uri: Optional[str] = None,
    ) -> aiplatform.Model:
        """Upload the model to Vertex AI Model Registry."""
        # Initialize Vertex AI with project and location
        aiplatform.init(
            project=settings.GCP_PROJECT,
            location=settings.GCP_LOCATION,
        )

        # Use XGBoost pre-built container if none provided
        if not serving_container_image_uri:
            serving_container_image_uri = "us-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-1:latest"

        # Upload model to Vertex AI Registry using the shared registry function
        from recsys.gcp_integrations.model_registry import upload_model_to_registry
        model = upload_model_to_registry(
            model=self.model,
            model_name=model_name,
            model_display_name=model_name,
            description=description,
            serving_container_image_uri=serving_container_image_uri,
        )
        
        return model

    @classmethod
    def load_from_vertex_ai(
        cls,
        model_name: str = "ranking_model",
    ) -> 'XGBClassifier':
        """Load the latest version of the ranking model from Vertex AI."""
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
        model_file = os.path.join(model_path, "model.bst")
        
        # Load model using XGBoost's native format
        from xgboost import XGBClassifier
        ranking_model = XGBClassifier()
        ranking_model.load_model(model_file)
        
        return ranking_model

    def predict(self, instances: Dict[str, Any]) -> Dict[str, float]:
        """Make predictions using the ranking model.
        
        Args:
            instances: Dictionary containing feature values for prediction
            
        Returns:
            Dictionary containing prediction probabilities
        """
        try:
            predictions = self.model.predict_proba(instances)[:, 1]
            return {"predictions": predictions.tolist()}
        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            raise