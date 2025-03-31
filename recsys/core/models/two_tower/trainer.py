"""
Training utilities for the two-tower model.
"""

import tensorflow as tf
from loguru import logger
from typing import Dict

from recsys.config import settings
from .model import TwoTowerModel
from .dataset import TwoTowerDataset


class TwoTowerTrainer:
    def __init__(self, dataset: TwoTowerDataset, model: TwoTowerModel) -> None:
        self._dataset = dataset
        self._model = model

    def train(self, train_ds: tf.data.Dataset, val_ds: tf.data.Dataset) -> Dict:
        """Train the two-tower model."""
        logger.info("Initializing model training...")

        # Initialize query tower normalization
        self._initialize_query_model(train_ds)

        # Configure optimizer
        optimizer = tf.keras.optimizers.AdamW(
            weight_decay=settings.TWO_TOWER_WEIGHT_DECAY,
            learning_rate=settings.TWO_TOWER_LEARNING_RATE,
        )

        # Compile model
        self._model.compile(optimizer=optimizer)
        
        # Define callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=50,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=10,
                min_lr=1e-6
            ),
            tf.keras.callbacks.ModelCheckpoint(
                filepath='checkpoints/best_model',
                monitor='val_loss',
                save_best_only=True,
                save_weights_only=True
            )
        ]

        # Train model
        logger.info(f"Starting training for {settings.TWO_TOWER_NUM_EPOCHS} epochs")
        history = self._model.fit(
            train_ds, 
            validation_data=val_ds, 
            epochs=settings.TWO_TOWER_NUM_EPOCHS,
            callbacks=callbacks,
        )

        logger.info("Training completed")
        return history

    def _initialize_query_model(self, train_ds: tf.data.Dataset) -> None:
        """
        Initialize the query model's normalization layers.

        Args:
            train_ds: Training dataset for normalization statistics
        """
        # Initialize age normalization layer
        self._model.query_model.normalized_age.adapt(train_ds.map(lambda x: x["age"]))

        # Initialize model with sample inputs
        query_df = self._dataset.properties["query_df"]
        query_ds = self._dataset.df_to_ds(query_df).batch(1)
        self._model.query_model(next(iter(query_ds)))
