"""
Ranking model serving implementation.
"""

import joblib
import pandas as pd
from typing import Dict
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

    def save_to_local(self, output_path: str = "ranking_model") -> None:
        """
        Save the ranking model in XGBoost format.

        Args:
            output_path: Directory to save the model

        Returns:
            Path where model was saved
        """
        logger.info(f'Saving model into: {output_path}')
        joblib.dump(self.model, output_path)
        logger.info(f'Model successfully saved')
        self.local_model_path = output_path

    @classmethod
    def deploy(cls, model):
        return
