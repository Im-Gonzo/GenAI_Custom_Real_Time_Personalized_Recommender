"""
Feature Store configurations.
"""
from typing import Dict, List

# Standard feature groups and their columns
FEATURE_CONFIGS = {
    "transactions": {
        "entity_key": "customer_id",
        "join_keys": ["article_id"],
        "feature_columns": [
            "t_dat",
            "price",
            "month_sin",
            "month_cos"
        ],
    },
    "articles": {
        "entity_key": "article_id",
        "join_keys": [],
        "feature_columns": [
            "garment_group_name",
            "index_group_name",
            "product_type_name",
            "product_group_name",
            "graphical_appearance_name",
            "colour_group_name",
            "perceived_colour_value_name",
            "perceived_colour_master_name",
            "department_name",
            "index_name",
            "section_name"
        ],
    },
    "customers": {
        "entity_key": "customer_id",
        "join_keys": [],
        "feature_columns": [
            "age",
            "club_member_status",
            "age_group",
            "postal_code"
        ],
    },
    "rankings": {
        "entity_key": "customer_id",
        "join_keys": ["article_id"],
        "feature_columns": [
            "prediction",
            "label",
            "rank"
        ],
    }
}


def get_feature_config(
    view_id: str,
    include_join_keys: bool = True
) -> Dict[str, List[str]]:
    """
    Get feature configuration for a view.
    
    Args:
        view_id: ID of the feature view
        include_join_keys: Whether to include join keys in columns
        
    Returns:
        Dict with feature configuration
        
    Raises:
        ValueError: If view_id is unknown
    """
    if view_id not in FEATURE_CONFIGS:
        raise ValueError(f"Unknown feature view: {view_id}")
        
    config = FEATURE_CONFIGS[view_id]
    columns = [config["entity_key"]] + config["feature_columns"]
    
    if include_join_keys:
        columns.extend(config["join_keys"])
        
    return {
        "entity_key": config["entity_key"],
        "join_keys": config["join_keys"],
        "columns": sorted(list(set(columns)))
    }
