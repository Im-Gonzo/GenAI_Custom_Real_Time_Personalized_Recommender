"""
Core embeddings functionality for recommendation system.
"""
from .preprocessing import preprocess_candidates
from .computation import compute_embeddings
from .storage import process_for_storage, validate_embeddings

__all__ = [
    'preprocess_candidates',
    'compute_embeddings',
    'process_for_storage',
    'validate_embeddings',
]
