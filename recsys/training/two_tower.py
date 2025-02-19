"""
Two-tower model training functionality.
"""

from recsys.config import settings
from recsys.core.models.two_tower import (
    QueryTower,
    QueryTowerFactory,
    ItemTower,
    ItemTowerFactory,
    TwoTowerModel,
    TwoTowerFactory,
    TwoTowerDataset,
    TwoTowerTrainer,
)
from recsys.utils.split_utils import train_validation_test_split

# Re-export all the components
__all__ = [
    "QueryTower",
    "QueryTowerFactory",
    "ItemTower",
    "ItemTowerFactory",
    "TwoTowerModel",
    "TwoTowerFactory",
    "TwoTowerDataset",
    "TwoTowerTrainer",
]
