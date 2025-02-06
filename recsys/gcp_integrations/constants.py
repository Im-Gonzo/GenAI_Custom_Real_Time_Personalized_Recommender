# Table configurations with schema and primary key information
TABLE_CONFIGS = {
    "recsys_customers": {
        "schema_file": "customers_schema.json",
        "primary_key": ["customer_id"],
        "embedding_columns": [],  # No embeddings
    },
    "recsys_articles": {
        "schema_file": "articles_schema.json",
        "primary_key": ["article_id"],
        "embedding_columns": ["embeddings"],  # Article embeddings
    },
    "recsys_interactions": {
        "schema_file": "interactions_schema.json",
        "primary_key": ["customer_id", "article_id"],
        "embedding_columns": [],  # No embeddings
    },
}
