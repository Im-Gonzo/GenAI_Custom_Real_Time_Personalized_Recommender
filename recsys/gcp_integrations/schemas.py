import json
from pathlib import Path
from typing import List

from google.cloud import bigquery
from loguru import logger

from recsys.gcp_integrations.constants import TABLE_CONFIGS


def get_schema_path(schema_file: str) -> Path:
    """Returns path to schema file in terraform directory"""
    return (
        Path(__file__).parents[2]
        / "terraform"
        / "modules"
        / "feature-store"
        / "schemas"
        / schema_file
    )


def get_table_schema(table_name: str) -> List[bigquery.SchemaField]:
    """Gets schema from Terraform-defined JSON files"""
    if table_name not in TABLE_CONFIGS:
        raise ValueError(f"Unknown table: {table_name}")

    schema_path = get_schema_path(TABLE_CONFIGS[table_name]["schema_file"])

    try:
        with open(schema_path) as f:
            schema_json = json.load(f)
            schema_fields = []
            for field in schema_json:
                # Special handling for embedding fields
                if field["name"] in TABLE_CONFIGS[table_name]["embedding_columns"]:
                    schema_fields.append(
                        bigquery.SchemaField(
                            name=field["name"],
                            field_type="ARRAY",  # Embeddings are arrays
                            mode=field["mode"],
                            description=field.get("description"),
                            field_type_params={"item_type": "FLOAT64"},
                        )
                    )
                else:
                    # Regular fields
                    schema_fields.append(
                        bigquery.SchemaField(
                            name=field["name"],
                            field_type=field["type"],
                            mode=field["mode"],
                            description=field.get("description"),
                        )
                    )
            return schema_fields
    except Exception as e:
        logger.error(f"Error loading schema for {table_name}: {str(e)}")
        raise
