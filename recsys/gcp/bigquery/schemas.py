"""
BigQuery table schema definitions and utilities.
"""

import json
from pathlib import Path
from typing import List
from google.cloud import bigquery
from loguru import logger

from recsys.gcp.common.constants import TABLE_CONFIGS


def get_schema_path(schema_file: str) -> Path:
    """
    Get path to schema file in terraform directory.

    Args:
        schema_file: Name of the schema file

    Returns:
        Path to schema file
    """
    return (
        Path(__file__).parents[3]  # Adjusted for new directory structure
        / "terraform"
        / "modules"
        / "feature-store"
        / "schemas"
        / schema_file
    )


def get_table_schema(table_name: str) -> List[bigquery.SchemaField]:
    """
    Get schema from Terraform-defined JSON files.

    Args:
        table_name: Name of the table to get schema for

    Returns:
        List of BigQuery SchemaField objects

    Raises:
        ValueError: If table_name is unknown
    """
    if table_name not in TABLE_CONFIGS:
        raise ValueError(f"Unknown table: {table_name}")

    schema_path = get_schema_path(TABLE_CONFIGS[table_name]["schema_file"])
    try:
        with open(schema_path) as f:
            schema_json = json.load(f)
            schema_fields = []
            for field in schema_json:
                # Handle embedding fields
                if field["name"] in TABLE_CONFIGS[table_name]["embedding_columns"]:
                    schema_fields.append(
                        bigquery.SchemaField(
                            name=field["name"],
                            field_type="FLOAT64",
                            mode=field["mode"],
                            description=field.get("description"),
                        )
                    )
                else:
                    # Handle regular fields
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
