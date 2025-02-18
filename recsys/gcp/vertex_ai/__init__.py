"""
Vertex AI integration utilities.
"""
from .model_registry import (
    initialize_vertex_ai,
    upload_model_to_registry,
    deploy_model_to_endpoint,
    list_models,
    get_model
)
from .serving import (
    BaseGCPModel,
    GCPQueryModel,
    GCPCandidateModel,
    GCPRankingModel
)

__all__ = [
    # Model Registry
    'initialize_vertex_ai',
    'upload_model_to_registry',
    'deploy_model_to_endpoint',
    'list_models',
    'get_model',
    
    # Serving
    'BaseGCPModel',
    'GCPQueryModel',
    'GCPCandidateModel',
    'GCPRankingModel'
]
