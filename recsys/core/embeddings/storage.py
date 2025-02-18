"""
Utilities for processing and storing embeddings.
"""
import numpy as np
import pandas as pd
import tensorflow as tf
from typing import List
from loguru import logger


def process_for_storage(df: pd.DataFrame, embedding_column: str) -> pd.DataFrame:
    """
    Process embeddings into storage-compatible format (e.g., for BigQuery).
    
    Args:
        df: DataFrame containing embeddings
        embedding_column: Name of the embedding column
        
    Returns:
        DataFrame with processed embeddings as float lists
    """
    if embedding_column in df.columns:
        # Handle different embedding formats
        if isinstance(df[embedding_column].iloc[0], (np.ndarray, tf.Tensor)):
            df[embedding_column] = df[embedding_column].apply(lambda x: x.tolist())

        # Ensure all values are float lists
        df[embedding_column] = df[embedding_column].apply(
            lambda x: [float(v) for v in x]
        )

        logger.info(f"Processed embeddings in {embedding_column}")
    return df


def validate_embeddings(df: pd.DataFrame, embedding_column: str, expected_dim: int) -> bool:
    """
    Validate embedding dimensions and formats.
    
    Args:
        df: DataFrame containing embeddings
        embedding_column: Name of the embedding column
        expected_dim: Expected embedding dimension
        
    Returns:
        bool indicating whether validation passed
    """
    if embedding_column not in df.columns:
        logger.error(f"Embedding column {embedding_column} not found")
        return False
        
    # Check dimensions
    dims = df[embedding_column].apply(len).unique()
    if len(dims) != 1 or dims[0] != expected_dim:
        logger.error(f"Invalid embedding dimensions. Expected {expected_dim}, got {dims}")
        return False
        
    return True
