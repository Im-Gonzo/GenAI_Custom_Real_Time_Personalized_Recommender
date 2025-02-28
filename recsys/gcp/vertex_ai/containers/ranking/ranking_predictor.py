"""
XGBoost predictor for ranking model in Vertex AI.
Loads model from Google Cloud Model Registry and generates predictions.
"""

import os
import time
import xgboost as xgb
import numpy as np
import tempfile
from typing import Dict, List, Any, Optional, Union
from google.cloud import storage
from google.cloud import aiplatform
from google.cloud.exceptions import NotFound
from config import PROJECT_ID, LOCATION, MODEL_ID, MODEL_VERSION
from logger import logger


class RankingPredictor:
    """
    Loads and runs an XGBoost model for ranking predictions.

    This class handles:
    1. Loading the model from Vertex AI Model Registry
    2. Preparing features for prediction
    3. Running predictions with XGBoost
    """

    def __init__(self):
        """
        Initialize XGBoost model from Model Registry.

        Loads the model from Vertex AI Model Registry and prepares it for predictions.
        """
        logger.info(f"🤖 Initializing RankingPredictor")
        self.model = None

        try:
            # Format model ID
            self._model_id = (
                f"projects/{PROJECT_ID}/locations/{LOCATION}/models/{MODEL_ID}"
            )

            # Load model metadata from Vertex AI
            model = aiplatform.Model(model_name=self._model_id, version=MODEL_VERSION)
            logger.model(f"Loading model: {MODEL_ID} (version: {MODEL_VERSION})")

            # Get model URI
            model_uri = model.uri
            logger.info(f"📦 Model artifact location: {model_uri}")

            # Download and load the model
            self._load_model_from_gcs(model_uri)

            # Log model info
            logger.model(f"Model feature count: {self.model.num_features()}")
            logger.success("XGBoost model loaded successfully")

        except NotFound as e:
            logger.error(f"❌ Model not found: {str(e)}", exc_info=True)
            raise ValueError(f"Model {MODEL_ID} not found in registry")

        except Exception as e:
            logger.error(
                f"❌ Error initializing predictor: {type(e).__name__}: {str(e)}",
                exc_info=True,
            )
            raise

    def _load_model_from_gcs(self, model_uri: str) -> None:
        """
        Download and load model from GCS.

        Args:
            model_uri: GCS URI of the model

        Raises:
            IOError: If model download fails
        """
        try:
            # Start timing model load
            logger.timer_start("model_load")

            # Parse GCS path
            gcs_path = model_uri.replace("gs://", "")
            bucket_name = gcs_path.split("/")[0]
            prefix = "/".join(gcs_path.split("/")[1:])

            # Create temp directory and file path
            temp_dir = tempfile.mkdtemp()
            local_model_path = os.path.join(temp_dir, "model.bst")

            # Download from GCS
            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket_name)
            model_blob_path = os.path.join(prefix, "model.bst")
            blob = bucket.blob(model_blob_path)

            logger.info(f"📥 Downloading model: {model_blob_path}")
            blob.download_to_filename(local_model_path)

            # Load model
            self.model = xgb.Booster()
            self.model.load_model(local_model_path)

            # Log completion time
            logger.timer_end("model_load")

        except Exception as e:
            logger.error(
                f"❌ Error loading model: {type(e).__name__}: {str(e)}", exc_info=True
            )
            raise

        finally:
            # Cleanup temp files
            try:
                if os.path.exists(local_model_path):
                    os.remove(local_model_path)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as e:
                logger.warning(f"⚠️ Error cleaning up temp files: {str(e)}")

    def predict(self, inputs: List[Dict[str, Any]]) -> Dict[str, List]:
        """
        Generate ranking predictions using XGBoost.

        Args:
            inputs: List of dictionaries containing ranking_features and article_ids

        Returns:
            Dictionary with scores and article_ids

        Raises:
            ValueError: If model is not loaded or inputs are invalid
        """
        # Start timing prediction
        logger.timer_start("prediction")

        try:
            # Check if model is loaded
            if self.model is None:
                raise ValueError("Model not loaded")

            # Check inputs
            if not inputs or len(inputs) == 0:
                logger.warning("⚠️ Empty inputs for prediction")
                return {"scores": [], "article_ids": []}

            # Extract ranking features and article IDs from the inputs
            features_df = inputs[0].pop("ranking_features")
            article_ids = inputs[0].pop("article_ids")

            # Log prediction info
            logger.model(f"Making predictions for {len(features_df)} candidates")

            # Process categorical features
            if len(features_df) > 0:
                # Identify categorical columns
                categorical_cols = [
                    col
                    for col in features_df.columns
                    if features_df[col].dtype == "object"
                ]

                # Convert categorical columns to numeric
                for col in categorical_cols:
                    logger.data(f"Encoding categorical feature: {col}")
                    # Create mapping of unique values to integers
                    unique_values = features_df[col].unique()
                    value_map = {val: idx for idx, val in enumerate(unique_values)}

                    # Apply the mapping
                    features_df[col] = features_df[col].map(value_map)

                # Convert to numpy array
                features_np = features_df.to_numpy()

                # Convert to DMatrix for XGBoost
                dmatrix = xgb.DMatrix(np.array(features_np, dtype=np.float32))

                # Get prediction scores
                scores = self.model.predict(dmatrix).tolist()

                # Log prediction completion
                logger.timer_end("prediction")

                return {
                    "scores": scores,
                    "article_ids": article_ids,
                }
            else:
                # No features to predict
                logger.warning("⚠️ No features to predict")
                return {
                    "scores": [],
                    "article_ids": article_ids,
                }

        except ValueError as e:
            # Handle validation errors
            logger.error(f"❌ Validation error: {str(e)}", exc_info=True)
            return {
                "scores": [],
                "article_ids": article_ids if "article_ids" in locals() else [],
            }

        except Exception as e:
            # Handle all other errors
            logger.error(
                f"❌ Prediction error: {type(e).__name__}: {str(e)}", exc_info=True
            )
            return {
                "scores": [],
                "article_ids": article_ids if "article_ids" in locals() else [],
            }
