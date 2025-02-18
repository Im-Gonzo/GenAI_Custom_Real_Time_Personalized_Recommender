"""
Item tower implementation for the two-tower recommendation model.
"""
from typing import List
import tensorflow as tf
from tensorflow.keras.layers import StringLookup


class ItemTowerFactory:
    def __init__(self, item_ids: List[str], garment_groups: List[str], index_groups: List[str]) -> None:
        self._item_ids = item_ids
        self._garment_groups = garment_groups
        self._index_groups = index_groups

    def build(self, embedding_dim: int) -> 'ItemTower':
        return ItemTower(
            item_ids=self._item_ids,
            garment_groups=self._garment_groups,
            index_groups=self._index_groups,
            embedding_dim=embedding_dim,
        )


class ItemTower(tf.keras.Model):
    def __init__(
        self,
        item_ids: List[str],
        garment_groups: List[str],
        index_groups: List[str],
        embedding_dim: int
    ):
        super().__init__()

        self.garment_groups = garment_groups
        self.index_groups = index_groups

        self.item_embedding = tf.keras.Sequential([
            StringLookup(vocabulary=item_ids, mask_token=None),
            tf.keras.layers.Embedding(
                input_dim=len(item_ids) + 1,  # Additional embedding for unknown tokens
                output_dim=embedding_dim,
            ),
        ])

        self.garment_groups_tokenizer = StringLookup(
            vocabulary=garment_groups,
            mask_token=None,
        )

        self.index_groups_tokenizer = StringLookup(
            vocabulary=index_groups,
            mask_token=None,
        )

        self.projection_layers = tf.keras.Sequential([
            tf.keras.layers.Dense(embedding_dim, activation="relu"),
            tf.keras.layers.Dense(embedding_dim),
        ])

    def call(self, inputs):
        garment_group_embedding = tf.one_hot(
            self.garment_groups_tokenizer(inputs["garment_group_name"]),
            len(self.garment_groups),
        )

        index_group_embedding = tf.one_hot(
            self.index_groups_tokenizer(inputs["index_group_name"]),
            len(self.index_groups),
        )

        concatenated_inputs = tf.concat([
            self.item_embedding(inputs["article_id"]),
            garment_group_embedding,
            index_group_embedding,
        ], axis=1)

        return self.projection_layers(concatenated_inputs)
