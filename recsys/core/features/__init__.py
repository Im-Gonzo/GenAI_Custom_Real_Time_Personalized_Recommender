"""
Feature computation and management for the recommendation system.
"""
from .article_features import (
    compute_features as compute_article_features,
    generate_text_embeddings as generate_article_embeddings
)
from .customer_features import (
    compute_features as compute_customer_features,
    CustomerDatasetSize,
    CustomerSampler
)
from .interaction_features import (
    generate_interaction_data
)
from .transaction_features import (
    compute_features as compute_transaction_features,
    month_sin,
    month_cos,
    calculate_month_sin_cos
)
from .ranking_features import (
    compute_rankings_dataset,
    fetch_feature_view_data
)

__all__ = [
    # Article features
    'compute_article_features',
    'generate_article_embeddings',
    
    # Customer features
    'compute_customer_features',
    'CustomerDatasetSize',
    'CustomerSampler',
    
    # Interaction features
    'generate_interaction_data',
    
    # Transaction features
    'compute_transaction_features',
    'month_sin',
    'month_cos',
    'calculate_month_sin_cos',
    
    # Ranking features
    'compute_rankings_dataset',
    'fetch_feature_view_data'
]
