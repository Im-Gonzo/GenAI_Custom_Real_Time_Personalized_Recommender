from typing import Optional, List

import pandas as pd
from google.cloud import bigquery
from google.cloud.aiplatform import Featurestore, EntityType, Feature


from loguru import logger

from recsys.config import settings
from recsys.gcp_integrations import constants


def get_feature_store() -> Featurestore:
    """Retrieves the selected feature store"""
    try:
        logger.info(
            f"Attempting to retrieve the Featurestore from {settings.GCP_LOCATION}/{settings.GCP_PROJECT}/{settings.VERTEX_FEATURE_STORE_ID}"
        )
        fs = Featurestore(
            featurestore_name=settings.VERTEX_FEATURE_STORE_ID,
            project=settings.GCP_PROJECT,
            location=settings.GCP_LOCATION,
        )
        return fs
    except ValueError as e:
        logger.error(
            f"Couldn't retrieve the Featurestore from {settings.GCP_LOCATION}/{settings.GCP_PROJECT}/{settings.VERTEX_FEATURE_STORE_ID}"
        )
        logger.error(e)
        raise


def get_bigquery_client() -> bigquery.Client:
    """Returns an authenticated BigQuery client"""
    return bigquery.Client(project=settings.GCP_PROJECT)


def create_feature_group(
    fs: Featurestore,
    df: pd.DataFrame,
    table_name: str,
    feature_view_id: str,
    features: List[Feature],
    view_source: dict,
    online_enabled: bool = True,
):
    """Generic function to create or update a feature group and its corresponding view

    Args:
        fs: Featurestore instance
        df: DataFrame containing the feature data
        table_name: Name of the BigQuery table
        feature_view_id: ID for the feature view
        features: List of Feature objects defining the schema
        view_source: Source configuration for the feature view
        online_enabled: Whether to enable online serving

    Returns:
        FeatureView if online_enabled is True, None otherwise
    """
    try:
        # Upload data to BigQuery
        client = get_bigquery_client()
        table_id = f"{settings.GCP_PROJECT}.{constants.BQ_DATASET_ID}.{table_name}"

        # Upload DataFrame to BigQuery
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE", schema=features
        )

        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()  # Wait for the job to complete

        logger.info(f"Loaded {len(df)} rows to {table_id}")

        if online_enabled:
            # Create Feature View for online serving
            view = FeatureView.create(
                feature_view_id=feature_view_id,
                project=settings.GCP_PROJECT,
                region=settings.GCP_LOCATION,
                feature_store=settings.VERTEX_FEATURE_STORE_ID,
                source=view_source,
                sync_config=constants.SYNC_CONFIG,
            )
            logger.info(f"Created feature view: {view.feature_view_id}")
            return view

    except Exception as e:
        logger.error(f"Error creating feature group {table_name}: {str(e)}")
        raise


def create_customers_feature_group(
    fs: Featurestore, df: pd.DataFrame, online_enabled: bool = True
) -> Optional[FeatureView]:
    """Creates or updates the customers feature group"""
    return create_feature_group(
        fs=fs,
        df=df,
        table_name=constants.BQ_CUSTOMERS_TABLE,
        feature_view_id=constants.CUSTOMERS_FEATURE_VIEW,
        features=constants.customer_features,
        view_source=constants.customer_view_source,
        online_enabled=online_enabled,
    )


def create_articles_feature_group(
    fs: Featurestore,
    df: pd.DataFrame,
    articles_description_embedding_dim: int,
    online_enabled: bool = True,
) -> Optional[FeatureView]:
    """Creates or updates the articles feature group"""
    return create_feature_group(
        fs=fs,
        df=df,
        table_name=constants.BQ_ARTICLES_TABLE,
        feature_view_id=constants.ARTICLES_FEATURE_VIEW,
        features=constants.article_features,
        view_source=constants.article_view_source,
        online_enabled=online_enabled,
    )


def create_interactions_feature_group(
    fs: Featurestore, df: pd.DataFrame, online_enabled: bool = True
):
    """Creates or updates the interactions feature group"""
    return create_feature_group(
        fs=fs,
        df=df,
        table_name=constants.BQ_INTERACTIONS_TABLE,
        feature_view_id=constants.INTERACTIONS_FEATURE_VIEW,
        features=constants.interaction_features,
        view_source=constants.interaction_view_source,
        online_enabled=online_enabled,
    )


########################
#### Feature Views  ####
########################


def create_retrieval_feature_view(fs: Featurestore):
    """Creates a feature view for retrieval model training"""
    try:
        # Create the SQL query to join the tables
        query = f"""
        SELECT 
            t.customer_id,
            t.article_id,
            t.t_dat,
            c.club_member_status,
            c.age,
            c.age_group,
            a.prod_name,
            a.product_type_name,
            a.garment_group_name
        FROM 
            `{settings.GCP_PROJECT}.{constants.BQ_DATASET_ID}.{constants.BQ_INTERACTIONS_TABLE}` t
        JOIN 
            `{settings.GCP_PROJECT}.{constants.BQ_DATASET_ID}.{constants.BQ_CUSTOMERS_TABLE}` c
        ON 
            t.customer_id = c.customer_id
        JOIN 
            `{settings.GCP_PROJECT}.{constants.BQ_DATASET_ID}.{constants.BQ_ARTICLES_TABLE}` a
        ON 
            t.article_id = a.article_id
        """

        # Create view in BigQuery
        client = get_bigquery_client()
        view_id = f"{settings.GCP_PROJECT}.{constants.BQ_DATASET_ID}.retrieval_view"
        view = bigquery.Table(view_id)
        view.view_query = query

        client.create_table(view, exists_ok=True)
        logger.info(f"Created BigQuery view: {view_id}")

        return view

    except Exception as e:
        logger.error(f"Error creating retrieval feature view: {str(e)}")
        raise


def create_ranking_feature_view(fs: Featurestore):
    """Creates a feature view for the ranking model"""
    try:
        # Create the SQL query to join the tables
        query = f"""
        SELECT 
            t.customer_id,
            t.article_id,
            t.interaction_score as label,
            c.age,
            c.club_member_status,
            a.product_type_name,
            a.product_group_name,
            a.graphical_appearance_name,
            a.perceived_colour_value_name,
            a.perceived_colour_master_name,
            a.section_name,
            a.garment_group_name
        FROM 
            `{settings.GCP_PROJECT}.{constants.BQ_DATASET_ID}.{constants.BQ_INTERACTIONS_TABLE}` t
        JOIN 
            `{settings.GCP_PROJECT}.{constants.BQ_DATASET_ID}.{constants.BQ_CUSTOMERS_TABLE}` c
        ON 
            t.customer_id = c.customer_id
        JOIN 
            `{settings.GCP_PROJECT}.{constants.BQ_DATASET_ID}.{constants.BQ_ARTICLES_TABLE}` a
        ON 
            t.article_id = a.article_id
        """

        # Create view in BigQuery
        client = get_bigquery_client()
        view_id = f"{settings.GCP_PROJECT}.{constants.BQ_DATASET_ID}.ranking_view"
        view = bigquery.Table(view_id)
        view.view_query = query

        client.create_table(view, exists_ok=True)
        logger.info(f"Created BigQuery view: {view_id}")

        return view

    except Exception as e:
        logger.error(f"Error creating ranking feature view: {str(e)}")
        raise
