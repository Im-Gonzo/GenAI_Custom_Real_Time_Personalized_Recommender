"""
Preprocessing utilities for embeddings generation.
"""

import polars as pl
from typing import List


def preprocess_candidates(
    train_df: pl.DataFrame,
    candidate_features: List
) -> pl.DataFrame:
    """
    Preprocess candidate features for embedding generation.

    Args:
        train_df: DataFrame containing candidate data
        candidate_features: List of feature columns to use

    Returns:
        Preprocessed DataFrame with unique candidates
    """
    # # Select candidate features from the training DF
    item_df = train_df.select(candidate_features)
    
    # Drop duplicate rows based on the 'article_id' to get unique candidates
    item_df = item_df.unique(subset=["article_id"], keep="first")

    return item_df
