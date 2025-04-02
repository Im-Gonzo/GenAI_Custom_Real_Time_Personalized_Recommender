import polars as pl
from typing import List


def preprocess_candidates(
    train_df: pl.DataFrame,
    features: List
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
    item_df = train_df.select(features)
    
    # Drop duplicate rows based on the 'article_id' to get unique candidates
    item_df = item_df.unique(subset=["article_id"], keep="first")
    
    # Preprocess categorial into numerical
    categorical_cols = [
        col for col in item_df.columns
        if col != 'article_id' and item_df[col].dtype == pl.Utf8
    ]

    for col in categorical_cols:
        categories = item_df[col].unique()
        category_map = {val: idx for idx, val in enumerate(categories.to_list())}

        item_df = item_df.with_columns(
            pl.lit([category_map].get(val, -1) for val in item_df[col]).alias(col)
        )

    return item_df
