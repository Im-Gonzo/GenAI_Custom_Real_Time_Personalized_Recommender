# Figure out the GCP version for hopsworks
# import hopworks
# https://github.com/decodingml/personalized-recommender-course/blob/fa0a2dae5ba59ea52b2bd88598b8b2ccf6c194bb/recsys/hopsworks_integration/feature_store.py#L1
# from hsfs import embedding
# https://github.com/decodingml/personalized-recommender-course/blob/fa0a2dae5ba59ea52b2bd88598b8b2ccf6c194bb/recsys/hopsworks_integration/feature_store.py#L3
import pandas as pd
from google.auth.credentials import Credentials
from google.cloud.aiplatform import Featurestore
from loguru import logger

from recsys.config import settings
from recsys.features.transactions import month_cos, month_sin
from recsys.gcp_integrations import constants


def get_feature_store() -> Featurestore:
    """Retreives the selected feature store"""
    try:
        logger.info(
            f"Attempting to retrieve the Featurestore from {settings.GCP_LOCATION}/{settings.GCP_PROJECT}/{settings.VERTEX_FEATURE_STORE_ID}"
        )
        fs = Featurestore(
            featurestore_name=settings.VERTEX_FEATURE_STORE_ID,
            project=settings.GCP_PROJECT,
            location=settings.GCP_LOCATION,
            credentials=settings.GCP_CREDENTIALS,
        )
        return fs
    except ValueError as e:
        logger.error(
            f"Couldn't retrieve the Featurestore from  {settings.GCP_LOCATION}/{settings.GCP_PROJECT}/{settings.VERTEX_FEATURE_STORE_ID}"
        )
        logger.error(e)


########################
#### Feature Groups ####
########################


# CUSTOMER
def create_customers_feature_groups(fs, df: pd.DataFrame, online_enabled: bool = True):
    return


# ARTICLES
def create_articles_feature_group(
    fs,
    df: pd.DataFrame,
    articles_description_embedding_dim: int,
    online_enabled: bool = True,
):
    return


# TRANSACTIONS
def create_transactions_feature_group(
    fs, df: pd.DataFrame, online_enabled: bool = True
):
    return


# INTERACTIONS
def create_interactions_feature_group(
    fs, df: pd.DataFrame, online_enabled: bool = True
):
    return


# RANKING
def create_ranking_feature_group(
    fs, df: pd.DataFrame, parents: list, online_enabled: bool = True
):
    return


# CANDIDATES
def create_candidate_embeddings_feature_group(
    fs, df: pd.DataFrame, online_enabled: bool = True
):
    return


########################
#### Feature Views  ####
########################


def create_retrieval_feature_view(fs):
    return


def create_ranking_feature_view(fs):
    return


def create_candidate_embeddings_feature_view(fs):
    return
