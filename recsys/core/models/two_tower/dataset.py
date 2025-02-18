"""
Dataset handling for two-tower model training.
"""
import tensorflow as tf
import polars as pl
from loguru import logger
from typing import Dict, List, Tuple

from recsys.config import settings
from recsys.utils.split_utils import train_validation_test_split


class TwoTowerDataset:
    def __init__(self, training_data: pl.DataFrame, batch_size: int) -> None:
        self._training_data = training_data
        self._batch_size = batch_size
        self._properties = None

    @property
    def query_features(self) -> List[str]:
        return ["customer_id", "age", "month_sin", "month_cos"]

    @property
    def candidate_features(self) -> List[str]:
        return [
            "article_id",
            "garment_group_name",
            "index_group_name",
        ]

    @property
    def properties(self) -> Dict:
        if self._properties is None:
            raise ValueError("Call get_train_val_split() first")
        return self._properties

    def get_items_subset(self) -> tf.data.Dataset:
        """Get dataset containing unique items."""
        item_df = self.properties["train_df"][self.candidate_features]
        item_df = item_df.unique(subset=["article_id"])
        return self.df_to_ds(item_df)

    def get_train_val_split(self) -> Tuple[tf.data.Dataset, tf.data.Dataset]:
        """Create train and validation datasets."""
        logger.info("Creating train/validation split...")

        train_df, val_df, test_df, _, _, _ = train_validation_test_split(
            df=self._training_data,
            validation_size=settings.TWO_TOWER_DATASET_VALIDATION_SPLIT_SIZE,
            test_size=settings.TWO_TOWER_DATASET_TEST_SPLIT_SIZE,
        )

        # Create TensorFlow datasets
        train_ds = (
            self.df_to_ds(train_df)
            .batch(self._batch_size)
            .cache()
            .shuffle(self._batch_size * 10)
        )

        val_ds = self.df_to_ds(val_df).batch(self._batch_size).cache()

        # Store properties for model initialization
        self._properties = {
            "train_df": train_df,
            "val_df": val_df,
            "query_df": train_df[self.query_features],
            "item_df": train_df[self.candidate_features],
            "user_ids": train_df["customer_id"].unique().to_list(),
            "item_ids": train_df["article_id"].unique().to_list(),
            "garment_groups": train_df["garment_group_name"].unique().to_list(),
            "index_groups": train_df["index_group_name"].unique().to_list(),
        }

        return train_ds, val_ds

    def df_to_ds(self, df: pl.DataFrame) -> tf.data.Dataset:
        """Convert Polars DataFrame to TensorFlow Dataset."""
        # Get columns that are available in the DataFrame
        cols = set(self.query_features + self.candidate_features)
        available_cols = [col for col in cols if col in df.columns]

        # Create tensor slices
        return tf.data.Dataset.from_tensor_slices(
            {col: df[col] for col in available_cols}
        )
