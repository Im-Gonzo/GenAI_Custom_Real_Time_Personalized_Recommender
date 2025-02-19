"""
Data management utilities for recommendation system.

This package provides data handling functionality including:
- Data sources access
- Preprocessing and feature engineering
- Data validation and quality assurance
"""

from . import sources
from . import preprocessing
from . import validation

__all__ = ["sources", "preprocessing", "validation"]
