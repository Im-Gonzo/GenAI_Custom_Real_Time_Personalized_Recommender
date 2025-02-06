import numpy as np
import pandas as pd
import tensorflow as tf
from loguru import logger


def process_embeddings(df: pd.DataFrame, embedding_column: str) -> pd.DataFrame:
    """
    Process embeddings into BigQuery-compatible format

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
