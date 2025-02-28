"""
Core functionality for computing embeddings.
"""

import polars as pl
import pandas as pd
import tensorflow as tf
from typing import Any


def compute_embeddings(df: pl.DataFrame, model: Any) -> pl.DataFrame:
    """
    Compute embeddings for items using the provided model.

    Args:
        df: DataFrame containing item features
        model: TensorFlow model for computing embeddings

    Returns:
        DataFrame with article IDs and their corresponding embeddings
    """
    pandas_df = df.to_pandas()

    ds = tf.data.Dataset.from_tensor_slices(
        {col: pandas_df[col] for col in pandas_df.columns}
    )

    candidate_embeddings = ds.batch(2048).map(lambda x: (x["article_id"], model(x)))

    all_article_ids = tf.concat([batch[0] for batch in candidate_embeddings], axis=0)
    all_embeddings = tf.concat([batch[1] for batch in candidate_embeddings], axis=0)

    all_article_ids = all_article_ids.numpy().astype(int).tolist()
    all_embeddings = all_embeddings.numpy().tolist()

    embeddings_df = pl.DataFrame(
        {
            "article_id": all_article_ids,
            "embeddings": all_embeddings,
        }
    )

    return embeddings_df
