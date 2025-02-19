"""
Query tower implementation for the two-tower recommendation model.
The query tower processes user features to create user embeddings.
"""

from typing import List

import tensorflow as tf
from recsys.config import settings
from tensorflow.keras.layers import Normalization, StringLookup


class QueryTowerFactory:
    """Factory for creating QueryTower instances with configured parameters."""

    def __init__(self, dataset: "TwoTowerDataset") -> None:
        """
        Initialize the factory with user configuration.

        Args:
            user_ids: List of unique user IDs for embedding layer initialization
        """
        self._dataset = dataset

    def build(
        self, embed_dim: int = settings.TWO_TOWER_MODEL_EMBEDDING_SIZE
    ) -> "QueryTower":
        """
        Build a new QueryTower instance.

        Args:
            emb_dim: Dimension of the embedding space

        Returns:
            Configured QueryTower model
        """
        return QueryTower(
            user_ids=self._dataset.properties["user_ids"], emb_dim=embed_dim
        )


class QueryTower(tf.keras.Model):
    """
    Neural network tower that processes user/query features.

    This tower takes user features (user ID, age, temporal features) and
    projects them into a shared embedding space with items.
    """

    def __init__(self, user_ids: List[str], emb_dim: int) -> None:
        """
        Initialize the query tower.

        Args:
            user_ids: List of unique user IDs for embedding layer initialization
            emb_dim: Dimension of the embedding space
        """
        super().__init__()

        # User embedding layer
        self.user_embedding = tf.keras.Sequential(
            [
                StringLookup(vocabulary=user_ids, mask_token=None),
                tf.keras.layers.Embedding(
                    # Add 1 for unknown tokens
                    len(user_ids) + 1,
                    emb_dim,
                ),
            ]
        )

        # Age normalization layer (initialized during training)
        self.normalized_age = Normalization(axis=None)

        # Final feed-forward network
        self.projection_layers = tf.keras.Sequential(
            [
                tf.keras.layers.Dense(emb_dim, activation="relu"),
                tf.keras.layers.Dense(emb_dim),
            ]
        )

    def call(self, inputs: dict) -> tf.Tensor:
        """
        Process input features through the tower.

        Args:
            inputs: Dictionary containing:
                - customer_id: User identifiers
                - age: User ages
                - month_sin: Sinusoidal month encoding
                - month_cos: Cosinusoidal month encoding

        Returns:
            User embeddings tensor
        """
        # Concatenate all input features
        feature_vector = tf.concat(
            [
                self.user_embedding(inputs["customer_id"]),
                tf.reshape(self.normalized_age(inputs["age"]), (-1, 1)),
                tf.reshape(inputs["month_sin"], (-1, 1)),
                tf.reshape(inputs["month_cos"], (-1, 1)),
            ],
            axis=1,
        )

        # Project to final embedding space
        return self.projection_layers(feature_vector)

    def initialize_normalization(self, age_values: tf.data.Dataset) -> None:
        """
        Initialize the age normalization layer with training data statistics.

        Args:
            age_values: Dataset of age values for normalization
        """
        self.normalized_age.adapt(age_values)
