"""
Feature Store integration utilities.
"""
from .client import (
    initialize_feature_store,
    get_client,
    get_feature_views
)
from .datasets import (
    create_training_dataset,
    create_ranking_dataset
)
from .config import (
    FEATURE_CONFIGS,
    get_feature_config
)

__all__ = [
    # Client
    'initialize_feature_store',
    'get_client',
    'get_feature_views',
    
    # Datasets
    'create_training_dataset',
    'create_ranking_dataset',
    
    # Config
    'FEATURE_CONFIGS',
    'get_feature_config'
]
