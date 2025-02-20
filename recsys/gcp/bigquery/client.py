"""
BigQuery client and data management utilities.
"""

from typing import Union, Optional, Dict, List
import pandas as pd
import polars as pl
from google.cloud import bigquery
from google.cloud import aiplatform
from loguru import logger

from recsys.config import settings
from recsys.gcp.common.constants import TABLE_CONFIGS
from recsys.gcp.bigquery.schemas import get_table_schema
from recsys.core.features.transaction_features import month_cos, month_sin
from recsys.core.embeddings import process_for_storage

from vertexai.resources.preview.feature_store import FeatureView


# BigQuery to Pandas type mapping
BQ_TO_PANDAS_TYPES = {
    "STRING": "string",
    "INTEGER": "int64",
    "FLOAT": "float64",
    "BOOLEAN": "bool",
    "TIMESTAMP": "datetime64[ns]",
}


def get_client() -> bigquery.Client:
    """Get an authenticated BigQuery client."""
    return bigquery.Client(project=settings.GCP_PROJECT)


def convert_types(df: pd.DataFrame, schema: List[bigquery.SchemaField]) -> pd.DataFrame:
    """
    Convert DataFrame types to match BigQuery schema.

    Args:
        df: Input DataFrame
        schema: BigQuery schema fields

    Returns:
        DataFrame with converted types
    """
    df = df.copy()

    for field in schema:
        if field.field_type != "ARRAY":  # Skip embedding columns
            try:
                if field.field_type in BQ_TO_PANDAS_TYPES:
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


def upload_dataframe(
    df: Union[pd.DataFrame, pl.DataFrame],
    table_name: str,
    write_disposition: str = "WRITE_TRUNCATE",
) -> None:
    """
    Upload a DataFrame to BigQuery.

    Args:
        df: DataFrame to upload
        table_name: Target table name
        write_disposition: BigQuery write disposition
    """
    try:
        # Convert Polars to Pandas if needed
        if isinstance(df, pl.DataFrame):
            df = df.to_pandas()

        schema = get_table_schema(table_name)
        df = convert_types(df, schema)

        # Process embeddings if any
        for embedding_col in TABLE_CONFIGS[table_name]["embedding_columns"]:
            df = process_for_storage(df, embedding_col)

        logger.debug("DataFrame types before upload:")
        for col, dtype in df.dtypes.items():
            logger.debug(f"{col}: {dtype}")

        job_config = bigquery.LoadJobConfig(
            write_disposition=write_disposition, schema=schema
        )

        # Upload data
        client = get_client()
        table_id = f"{settings.GCP_PROJECT}.{settings.BIGQUERY_DATASET_ID}.{table_name}"

        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()

        table = client.get_table(table_id)
        logger.info(f"Loaded {table.num_rows} rows to {table_id}")

    except Exception as e:
        logger.error(f"Error uploading to {table_name}: {str(e)}")
        raise


def load_features(
    customers_df: Optional[Union[pd.DataFrame, pl.DataFrame]] = None,
    articles_df: Optional[Union[pd.DataFrame, pl.DataFrame]] = None,
    interactions_df: Optional[Union[pd.DataFrame, pl.DataFrame]] = None,
    transactions_df: Optional[Union[pd.DataFrame, pl.DataFrame]] = None,
    rankings_df: Optional[Union[pd.DataFrame, pl.DataFrame]] = None,
    candidates_df: Optional[Union[pd.DataFrame, pl.DataFrame]] = None,
    write_disposition: str = "WRITE_TRUNCATE",
) -> None:
    """
    Load feature DataFrames to their respective BigQuery tables.

    Args:
        customers_df: Customer features DataFrame
        articles_df: Article features DataFrame
        interactions_df: Interaction features DataFrame
        transactions_df: Transaction features DataFrame
        rankings_df: Ranking features DataFrame
        write_disposition: BigQuery write disposition
    """
    try:
        if customers_df is not None:
            upload_dataframe(customers_df, "recsys_customers", write_disposition)

        if articles_df is not None:
            upload_dataframe(articles_df, "recsys_articles", write_disposition)

        if interactions_df is not None:
            upload_dataframe(interactions_df, "recsys_interactions", write_disposition)

        if transactions_df is not None:
            month = pl.from_epoch(transactions_df["t_dat"]).dt.month()
            transactions_df = transactions_df.with_columns(
                [
                    month_sin(month).alias("month_sin"),
                    month_cos(month).alias("month_cos"),
                ]
            )
            upload_dataframe(transactions_df, "recsys_transactions", write_disposition)

        if rankings_df is not None:
            upload_dataframe(rankings_df, "recsys_rankings", write_disposition)

        if candidates_df is not None:
            upload_dataframe(candidates_df, "recsys_candidates", write_disposition)

        logger.info("Successfully loaded all features")

    except Exception as e:
        logger.error(f"Error in feature loading: {str(e)}")
        raise


def fetch_feature_view_data(
    feature_view: FeatureView,
    select_columns: Optional[List[str]] = None,
    except_columns: Optional[List[str]] = None,
) -> pl.DataFrame:
    """
    Fetch data from a feature view by querying its BigQuery source.

    Args:
        feature_view: Feature view to query
        select_columns: Columns to select
        except_columns: Columns to exclude

    Returns:
        DataFrame containing feature view data
    """
    logger.info(f"Fetching data from feature view: {feature_view.name}")

    client = get_client()
    table_ref = feature_view.gca_resource.big_query_source.uri.replace("bq://", "")

    if select_columns:
        columns_str = ", ".join(select_columns)
        query = f"SELECT {columns_str} FROM `{table_ref}`"
    elif except_columns:
        query = f"SELECT * EXCEPT({', '.join(except_columns)}) FROM `{table_ref}`"
    else:
        query = f"SELECT * FROM `{table_ref}`"

    logger.info(f"Executing query: {query}")
    query_result = client.query(query)
    df = pl.from_pandas(query_result.to_dataframe())
    logger.info(f"DataFrame shape: {df.shape}")

    return df
