"""
Configuration for ranking container.
Centralizes all configuration values and environment variables.
"""

import os
import logging

# Environment and debug settings
ENV = os.getenv("ENV", "development")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
LOG_LEVEL_INT = LOG_LEVEL_MAP.get(LOG_LEVEL, logging.INFO)

# Server settings
PORT = int(os.getenv("AIP_HTTP_PORT", "8080"))
HOST = os.getenv("HOST", "0.0.0.0")
WORKERS = int(os.getenv("WORKERS", "1"))

# Vertex AI Feature Store
FEATURE_STORE_ID = os.getenv("FEATURE_STORE_ID", "recsys_feature_store_dev")
PROJECT_ID = os.getenv("PROJECT_ID", "recsys-dev-gonzo-2")
LOCATION = os.getenv("LOCATION", "us-central1")
DATASET_ID = os.getenv("DATASET_ID", "recsys_dataset")

# Model Registry
MODEL_ID = os.getenv("MODEL_ID", "9164593244745498624")
MODEL_VERSION = os.getenv("MODEL_VERSION", "default")

# Recommendation settings
TOP_K_CANDIDATES = int(os.getenv("TOP_K_CANDIDATES", "100"))
MAX_RECOMMENDATIONS = int(os.getenv("MAX_RECOMMENDATIONS", "10"))

# BigQuery settings
MAX_QUERY_RETRIES = int(os.getenv("MAX_QUERY_RETRIES", "3"))
QUERY_TIMEOUT_SECONDS = int(os.getenv("QUERY_TIMEOUT_SECONDS", "30"))

# Table names
ARTICLES_TABLE = f"{PROJECT_ID}.{DATASET_ID}.recsys_articles"
CUSTOMERS_TABLE = f"{PROJECT_ID}.{DATASET_ID}.recsys_customers"
TRANSACTIONS_TABLE = f"{PROJECT_ID}.{DATASET_ID}.recsys_transactions"
CANDIDATES_TABLE = f"{PROJECT_ID}.{DATASET_ID}.recsys_candidates"
RANKINGS_TABLE = f"{PROJECT_ID}.{DATASET_ID}.recsys_rankings"

# Ranking model
RANKING_MODEL_FEATURES = {
    "index_name": 0.11068467,
    "section_name": 0.09530671,
    "colour_group_name_right": 0.08258159,
    "garment_group_name": 0.08252611,
    "age": 0.08237267,
    "index_group_name": 0.0788623,
    "department_name": 0.07626842,
    "perceived_colour_master_name": 0.073050514,
    "product_group_name": 0.06565918,
    "product_type_name": 0.06417185,
    "graphical_appearance_name": 0.06368775,
    "perceived_colour_value_name": 0.063513115,
    "colour_group_name": 0.061315097,
    "month_sin": 0.0,
    "month_cos": 0.0,
}

# Feature importance for explanation (sorted)
FEATURE_IMPORTANCE = dict(
    sorted(RANKING_MODEL_FEATURES.items(), key=lambda item: item[1], reverse=True)
)
