"""BigQuery utilities for data upload and management"""

from typing import Union, Optional, Dict
import pandas as pd
import polars as pl
from google.cloud import bigquery
from loguru import logger

from recsys.config import settings
from recsys.gcp_integrations.constants import TABLE_CONFIGS
from recsys.gcp_integrations.embeddings import process_embeddings
from recsys.gcp_integrations.schemas import get_table_schema

# BigQuery to Pandas type mapping
BQ_TO_PANDAS_TYPES = {
    "STRING": "string",
    "INTEGER": "int64",
    "FLOAT": "float64",
    "BOOLEAN": "bool",
    "TIMESTAMP": "datetime64[ns]",
}


def get_bigquery_client() -> bigquery.Client:
    """Returns an authenticated BigQuery client"""
    return bigquery.Client(project=settings.GCP_PROJECT)


def convert_types_for_bigquery(df: pd.DataFrame, schema: list) -> pd.DataFrame:
    """Convert DataFrame types to match BigQuery schema."""
    df = df.copy()

    for field in schema:
        if field.field_type != "ARRAY":  # Skip embedding columns
            try:
                if field.field_type in BQ_TO_PANDAS_TYPES:
                    # Convert to string first for safer conversion
                    if field.field_type == "STRING":
                        df[field.name] = df[field.name].astype(str)
                    else:
                        pandas_type = BQ_TO_PANDAS_TYPES[field.field_type]
                        df[field.name] = pd.to_numeric(df[field.name], errors="coerce")
                        df[field.name] = df[field.name].astype(pandas_type)

                logger.debug(f"Converted {field.name} to {field.field_type}")
            except Exception as e:
                logger.error(f"Error converting {field.name}: {str(e)}")
                raise

    return df


def upload_dataframe_to_bigquery(
    df: Union[pd.DataFrame, pl.DataFrame],
    table_name: str,
    write_disposition: str = "WRITE_TRUNCATE",
) -> None:
    """
    Uploads a DataFrame to BigQuery, handling embeddings and primary keys.
    """
    try:
        # Convert Polars to Pandas if needed
        if isinstance(df, pl.DataFrame):
            df = df.to_pandas()

        schema = get_table_schema(table_name)

        df = convert_types_for_bigquery(df, schema)

        # Process embeddings if any
        for embedding_col in TABLE_CONFIGS[table_name]["embedding_columns"]:
            df = process_embeddings(df, embedding_col)

        logger.debug("DataFrame types before upload:")
        for col, dtype in df.dtypes.items():
            logger.debug(f"{col}: {dtype}")

        job_config = bigquery.LoadJobConfig(
            write_disposition=write_disposition, schema=schema
        )

        # Upload data
        client = get_bigquery_client()
        table_id = f"{settings.GCP_PROJECT}.{settings.BIGQUERY_DATASET_ID}.{table_name}"

        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()

        table = client.get_table(table_id)
        logger.info(f"Loaded {table.num_rows} rows to {table_id}")

    except Exception as e:
        logger.error(f"Error uploading to {table_name}: {str(e)}")
        raise


def load_features_to_bigquery(
    customers_df: Optional[Union[pd.DataFrame, pl.DataFrame]] = None,
    articles_df: Optional[Union[pd.DataFrame, pl.DataFrame]] = None,
    interactions_df: Optional[Union[pd.DataFrame, pl.DataFrame]] = None,
    transactions_df: Optional[Union[pd.DataFrame, pl.DataFrame]] = None,
    rankings_df: Optional[Union[pd.DataFrame, pl.DataFrame]] = None,
    write_disposition: str = "WRITE_TRUNCATE",
) -> None:
    """
    Loads feature DataFrames to their respective BigQuery tables.
    """
    try:
        if customers_df is not None:
            upload_dataframe_to_bigquery(
                customers_df, "recsys_customers", write_disposition
            )

        if articles_df is not None:
            upload_dataframe_to_bigquery(
                articles_df, "recsys_articles", write_disposition
            )

        if interactions_df is not None:
            upload_dataframe_to_bigquery(
                interactions_df, "recsys_interactions", write_disposition
            )

        if transactions_df is not None:
            upload_dataframe_to_bigquery(
                transactions_df, "recsys_transactions", write_disposition
            )

        if rankings_df is not None:
            upload_dataframe_to_bigquery(
                rankings_df, "recsys_rankings", write_disposition
            )

        logger.info("Successfully loaded all features")

    except Exception as e:
        logger.error(f"Error in feature loading: {str(e)}")
        raise
