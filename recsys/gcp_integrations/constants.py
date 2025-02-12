# Table configurations with schema and primary key information
TABLE_CONFIGS = {
    "recsys_customers": {
        "schema_file": "customers_schema.json",
        "embedding_columns": [],  # No embeddings
    },
    "recsys_articles": {
        "schema_file": "articles_schema.json",
        "embedding_columns": ["embeddings"],  # Article embeddings
    },
    "recsys_interactions": {
        "schema_file": "interactions_schema.json",
        "embedding_columns": [],  # No embeddings
    },
    "recsys_transactions": {
        "schema_file": "transactions_schema.json",
        "embedding_columns": [],  # No embeddings
    },
    "recsys_rankings": {
        "schema_file": "rankings_schema.json",
        "embedding_columns": [],  # No embeddings
    },
    "recsys_candidates": {},
}
