"""
Model serving implementations for Vertex AI.
"""
from .base import BaseGCPModel
from .two_tower import (
    GCPQueryModel,
    GCPCandidateModel,
    QueryModelModule
)
from .ranking import GCPRankingModel

__all__ = [
    'BaseGCPModel',
    'GCPQueryModel',
    'GCPCandidateModel',
    'QueryModelModule',
    'GCPRankingModel'
]
