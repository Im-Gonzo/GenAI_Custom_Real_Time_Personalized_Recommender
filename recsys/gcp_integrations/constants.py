from google.cloud.aiplatform import Feature


# Feature Store Constants
FEATURE_ONLINE_STORE_ID = "recsys_feature_store_dev"

# BigQuery Constants
BQ_DATASET_ID = "recsys_dataset"
BQ_CUSTOMERS_TABLE = "recsys_customers"
BQ_ARTICLES_TABLE = "recsys_articles"
BQ_INTERACTIONS_TABLE = "recsys_interactions"

# Feature View Constants
CUSTOMERS_FEATURE_VIEW = "customers"
ARTICLES_FEATURE_VIEW = "articles"
INTERACTIONS_FEATURE_VIEW = "interactions"

# Entity Type Definitions
customer_features = [
    Feature(
        feature_name="customer_id",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=CUSTOMERS_FEATURE_VIEW,
    ),
    Feature(
        feature_name="club_member_status",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=CUSTOMERS_FEATURE_VIEW,
    ),
    Feature(
        feature_name="age",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=CUSTOMERS_FEATURE_VIEW,
    ),
    Feature(
        feature_name="postal_code",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=CUSTOMERS_FEATURE_VIEW,
    ),
    Feature(
        feature_name="age_group",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=CUSTOMERS_FEATURE_VIEW,
    ),
]

article_features = [
    Feature(
        feature_name="article_id",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=ARTICLES_FEATURE_VIEW,
    ),
    Feature(
        feature_name="prod_name",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=ARTICLES_FEATURE_VIEW,
    ),
    Feature(
        feature_name="prod_name_length",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=ARTICLES_FEATURE_VIEW,
    ),
    Feature(
        feature_name="product_type_name",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=ARTICLES_FEATURE_VIEW,
    ),
    Feature(
        feature_name="product_group_name",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=ARTICLES_FEATURE_VIEW,
    ),
    Feature(
        feature_name="graphical_appearance_name",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=ARTICLES_FEATURE_VIEW,
    ),
    Feature(
        feature_name="perceived_colour_value_name",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=ARTICLES_FEATURE_VIEW,
    ),
    Feature(
        feature_name="perceived_colour_master_name",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=ARTICLES_FEATURE_VIEW,
    ),
    Feature(
        feature_name="colour_group_code",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=ARTICLES_FEATURE_VIEW,
    ),
    Feature(
        feature_name="index_group_name",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=ARTICLES_FEATURE_VIEW,
    ),
    Feature(
        feature_name="section_name",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=ARTICLES_FEATURE_VIEW,
    ),
    Feature(
        feature_name="garment_group_name",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=ARTICLES_FEATURE_VIEW,
    ),
    Feature(
        feature_name="article_id",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=ARTICLES_FEATURE_VIEW,
    ),
    Feature(
        feature_name="image_url",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=ARTICLES_FEATURE_VIEW,
    ),
]

interaction_features = [
    Feature(
        feature_name="t_dat",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=INTERACTIONS_FEATURE_VIEW,
    ),
    Feature(
        feature_name="customer_id",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=INTERACTIONS_FEATURE_VIEW,
    ),
    Feature(
        feature_name="article_id",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=INTERACTIONS_FEATURE_VIEW,
    ),
    Feature(
        feature_name="interaction_score",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=INTERACTIONS_FEATURE_VIEW,
    ),
    Feature(
        feature_name="prev_article_id",
        featurestore_id=FEATURE_ONLINE_STORE_ID,
        entity_type_id=INTERACTIONS_FEATURE_VIEW,
    ),
]

# Feature View Sources
# customer_view_source = FeatureViewSource(
#     bigquery_source=f"bq://{BQ_DATASET_ID}.{BQ_CUSTOMERS_TABLE}",
#     entity_id_columns=["customer_id"],
# )

# article_view_source = FeatureViewSource(
#     bigquery_source=f"bq://{BQ_DATASET_ID}.{BQ_ARTICLES_TABLE}",
#     entity_id_columns=["article_id"],
# )

# interaction_view_source = FeatureViewSource(
#     bigquery_source=f"bq://{BQ_DATASET_ID}.{BQ_INTERACTIONS_TABLE}",
#     entity_id_columns=["customer_id", "article_id"],
# )

# Sync Configurations
SYNC_CONFIG = {
    "cron": "0 0 * * *"  # Daily at midnight
}
