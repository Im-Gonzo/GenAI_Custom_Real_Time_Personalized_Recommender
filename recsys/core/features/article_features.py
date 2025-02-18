"""
Article feature generation and processing.
"""
import sys
import contextlib
import polars as pl
from loguru import logger
from tqdm.auto import tqdm
from typing import Optional
from sentence_transformers import SentenceTransformer

from recsys.config import settings


def get_article_id(df: pl.DataFrame) -> pl.Series:
    """
    Extracts and returns the article_id column as a string.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Article ID series cast to string type
    """
    return df["article_id"].cast(pl.Utf8)


def create_prod_name_length(df: pl.DataFrame) -> pl.Series:
    """
    Creates a new column representing the length of 'prod_name'.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Series containing product name lengths
    """
    return df["prod_name"].str.len_chars()


def create_article_description(row) -> str:
    """
    Creates a comprehensive string description of an article.
    
    Args:
        row: DataFrame row containing article attributes
        
    Returns:
        Formatted article description string
    """
    description: str = f"{row['prod_name']} - {row['product_type_name']} in {row['product_group_name']}"
    description += f"\n Appearance: {row['graphical_appearance_name']}"
    description += f"\n Color: {row['perceived_colour_value_name']} {row['perceived_colour_master_name']} {row['colour_group_code']}"
    description += f"\n Category: {row['index_group_name']} {row['section_name']} {row['garment_group_name']}"

    if row["detail_desc"]:
        description += f"\n Details: {row['detail_desc']}"

    return description


def get_image_url(article_id: str, online: bool, path: Optional[str] = None) -> str:
    """
    Generates the URL/path for an article's image.
    
    Args:
        article_id: Article identifier
        online: Whether to use online or local path
        path: Base path for local images
        
    Returns:
        Complete image URL/path
    """
    if online:
        url = f"gs://{settings.GCS_DATA_BUCKET}/h-and-m/images/0"
    else:
        url = f"{path}/data/images/0"

    article_id_str = str(article_id)
    folder = article_id_str[:2]
    image_name = article_id_str

    return f"{url}{folder}/0{image_name}.jpg"


def compute_features_articles(df: pl.DataFrame, online: bool, path: Optional[str] = None) -> pl.DataFrame:
    """
    Computes all article features from raw data.
    
    Args:
        df: Input DataFrame with raw article data
        online: Whether to use online resources
        path: Base path for local resources
        
    Returns:
        DataFrame with computed features
    """
    logger.info("Computing article features...")
    
    df = df.with_columns(
        [
            get_article_id(df).alias("article_id"),
            create_prod_name_length(df).alias("prod_name_length"),
            pl.struct(df.columns)
            .map_elements(create_article_description)
            .alias("article_description"),
        ]
    )

    # Add image url
    df = df.with_columns(
        image_url=pl.col("article_id").map_elements(
            lambda x: get_image_url(article_id=x, online=online, path=path)
        )
    )
    
    # Drop null values and unnecessary columns
    df = df.select([col for col in df.columns if not df[col].is_null().any()])
    columns_to_drop = ["detail_desc", "detail_desc_length"]
    columns_to_keep = [col for col in df.columns if col not in columns_to_drop]

    logger.info("Article feature computation complete")
    return df.select(columns_to_keep)


def generate_embeddings_for_dataframe(
    df: pl.DataFrame,
    text_column: str,
    model: SentenceTransformer,
    batch_size: int = 32
) -> pl.DataFrame:
    """
    Generates embeddings for text data using a SentenceTransformer model.
    
    Args:
        df: Input DataFrame
        text_column: Column containing text to embed
        model: SentenceTransformer model
        batch_size: Batch size for embedding generation
        
    Returns:
        DataFrame with added embeddings column
    """
    @contextlib.contextmanager
    def suppress_stdout():
        new_stdout = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = new_stdout

        try:
            yield new_stdout
        finally:
            sys.stdout = old_stdout

    total_rows = len(df)
    pbar = tqdm(total=total_rows, desc="Generating embeddings...")

    texts = df[text_column].to_list()

    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        with suppress_stdout():
            batch_embeddings = model.encode(
                batch_texts, device=model.device, show_progress_bar=False
            )
        all_embeddings.extend(batch_embeddings.tolist())
        pbar.update(len(batch_texts))

    df_with_embeddings = df.with_columns(embeddings=pl.Series(all_embeddings))

    pbar.close()

    return df_with_embeddings
