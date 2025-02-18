"""
Ranking model serving implementation.
"""
import os
from typing import Dict, Any
from loguru import logger
from google.cloud import aiplatform
from xgboost import XGBClassifier

from recsys.config import settings
from recsys.gcp.vertex_ai.serving.base import BaseGCPModel
from recsys.gcp.vertex_ai.model_registry import initialize_vertex_ai


class GCPRankingModel(BaseGCPModel):
    """GCP integration for the ranking model."""
    
    def __init__(self, model: XGBClassifier) -> None:
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
        """
        Save the ranking model in XGBoost format.
        
        Args:
            output_path: Directory to save the model
            
        Returns:
            Path where model was saved
        """
        self.local_model_path = output_path
        return output_path

    def predict(self, instances: Dict[str, Any]) -> Dict[str, float]:
        """
        Make predictions using the ranking model.
        
        Args:
            instances: Dictionary containing feature values
            
        Returns:
            Dictionary containing prediction probabilities
        """
        try:
            predictions = self.model.predict_proba(instances)[:, 1]
            return {"predictions": predictions.tolist()}
        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            raise

    @classmethod
    def load_from_vertex_ai(
        cls,
        model_name: str = "ranking_model",
    ) -> XGBClassifier:
        """
        Load the latest version of the ranking model from Vertex AI.
        
        Args:
            model_name: Name of the model to load
            
        Returns:
            Loaded XGBoost model
            
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
        model_file = os.path.join(model_path, "model.bst")
        
        ranking_model = XGBClassifier()
        ranking_model.load_model(model_file)
        
        return ranking_model
