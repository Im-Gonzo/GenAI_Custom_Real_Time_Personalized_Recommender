from enum import Enum
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class CustomerDatasetSize(Enum):
    LARGE = "LARGE"
    MEDIUM = "MEDIUM"
    SMALL = "SMALL"


class RankingModelType(Enum):
    RANKING = "ranking"
    LLM_RANKING = "llmranking"


class Settings(BaseSettings):
    env_path: str = str(Path(__file__).parent.parent / ".env")
    model_config = SettingsConfigDict(env_file=env_path, env_file_encoding="utf-8")

    # GCP Core Configuration
    GCP_PROJECT: str = Field(..., description="GCP Project ID")
    GCP_LOCATION: str = Field(..., description="GCP Region/Location")
    GCP_CREDENTIALS: str = Field(..., description="Path to GCP credentials file")

    # Vertex AI Feature Store
    VERTEX_FEATURE_STORE_ID: str = Field(..., description="Vertex AI Feature Store ID")
    VERTEX_FEATURE_STORE_INSTANCE_ID: str = Field(
        ..., description="Feature Store Instance ID"
    )

    # GCP Resource Names
    GCP_ARTIFACT_REGISTRY: str = Field(..., description="Artifact Registry name")
    GCP_MODEL_REGISTRY: str = Field(..., description="Model Registry name")
    GCP_ENDPOINT_ID: str = Field(..., description="Model endpoint ID")

    # Storage Configuration
    GCS_DATA_BUCKET: str = Field(..., description="GCS bucket for data storage")
    GCS_MODEL_BUCKET: str = Field(..., description="GCS bucket for model storage")
    GCS_ARTIFACT_BUCKET: str = Field(..., description="GCS bucket for artifacts")

    # GCP Agent Configuration
    GEMINI_AGENT_ID: str = Field(..., description="Gemini Agent ID")
    GEMINI_AGENT_API_KEY: SecretStr = Field(..., description="Gemini Agent API Key")

    # BigQuery Configuration
    BIGQUERY_DATASET_ID: str = Field(..., description="The Dataset ID")

    # Feature Engineering
    CUSTOMER_DATA_SIZE: CustomerDatasetSize = Field(
        default=CustomerDatasetSize.SMALL, description="Size of customer dataset to use"
    )
    FEATURES_EMBEDDING_MODEL_ID: str = Field(
        ..., description="Model ID for feature embeddings"
    )

    # Model Training - Two Tower Neural Network
    TWO_TOWER_MODEL_EMBEDDING_SIZE: int = Field(
        default=16, description="Embedding size for two-tower model"
    )
    TWO_TOWER_MODEL_BATCH_SIZE: int = Field(
        default=2048, description="Batch size for training"
    )
    TWO_TOWER_NUM_EPOCHS: int = Field(
        default=10, description="Number of training epochs"
    )
    TWO_TOWER_WEIGHT_DECAY: float = Field(
        default=0.001, description="Weight decay for training"
    )
    TWO_TOWER_LEARNING_RATE: float = Field(
        default=0.01, description="Learning rate for training"
    )
    TWO_TOWER_DATASET_VALIDATION_SPLIT_SIZE: float = Field(
        default=0.1, description="Validation split size"
    )
    TWO_TOWER_DATASET_TEST_SPLIT_SIZE: float = Field(
        default=0.1, description="Test split size"
    )

    # Ranking Model Configuration
    RANKING_DATASET_VALIDATION_SPLIT_SIZE: float = Field(
        default=0.1, description="Validation split size for ranking"
    )
    RANKING_LEARNING_RATE: float = Field(
        default=0.2, description="Learning rate for ranking model"
    )
    RANKING_ITERATIONS: int = Field(
        default=100, description="Number of ranking iterations"
    )
    RANKING_SCALE_POS_WEIGHT: int = Field(
        default=10, description="Positive class weight scaling"
    )
    RANKING_EARLY_STOPPING_ROUNDS: int = Field(
        default=5, description="Early stopping rounds"
    )

    # Model Serving Configuration
    RANKING_MODEL_TYPE: RankingModelType = Field(
        default=RankingModelType.RANKING, description="Type of ranking model to use"
    )

    # Hugging Face
    TOKENIZERS_PARALLELISM: bool = Field(
        ..., description="Enable tokenizers parallelism"
    )


settings = Settings()
