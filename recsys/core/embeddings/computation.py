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
    

    article_ids = df['article_id']
    df = df.select(pl.exclude('article_id'))

    embeddings = model.predict_proba(df)

    embeddings_df = pl.DataFrame(
        {
            "article_id": article_ids,
            "embeddings": embeddings,
        }
    )

    return embeddings_df
