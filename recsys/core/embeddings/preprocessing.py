"""
Preprocessing utilities for embeddings generation.
"""

import pandas as pd
from typing import List


def preprocess_candidates(
    train_df: pd.DataFrame, candidate_features: List[str]
) -> pd.DataFrame:
    """
    Preprocess candidate features for embedding generation.

    Args:
        train_df: DataFrame containing candidate data
        candidate_features: List of feature columns to use

    Returns:
        Preprocessed DataFrame with unique candidates
    """
    # Select candidate features from the training DF
    item_df = train_df[candidate_features]

    # Drop duplicate rows based on the 'article_id' to get unique candidates
    item_df.drop_duplicates(subset="article_id", inplace=True)

    return item_df
