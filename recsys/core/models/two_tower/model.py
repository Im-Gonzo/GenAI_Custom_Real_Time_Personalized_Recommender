"""
Main two-tower model implementation combining query and item towers.
"""
import tensorflow as tf
import tensorflow_recommenders as tfrs
from .query_tower import QueryTower
from .item_tower import ItemTower


class TwoTowerFactory:
    def __init__(self, item_dataset: tf.data.Dataset) -> None:
        self._item_dataset = item_dataset

    def build(
        self,
        query_model: QueryTower,
        item_model: ItemTower,
        batch_size: int,
    ) -> 'TwoTowerModel':
        return TwoTowerModel(
            query_model=query_model,
            item_model=item_model,
            item_dataset=self._item_dataset,
            batch_size=batch_size,
        )


class TwoTowerModel(tf.keras.Model):
    def __init__(
        self,
        query_model: QueryTower,
        item_model: ItemTower,
        item_dataset: tf.data.Dataset,
        batch_size: int,
    ) -> None:
        super().__init__()
        
        self.query_model = query_model
        self.item_model = item_model
        
        self.task = tfrs.tasks.Retrieval(
            metrics=tfrs.metrics.FactorizedTopK(
                candidates=item_dataset.batch(batch_size).map(self.item_model)
            )
        )

    def train_step(self, batch) -> tf.Tensor:
        with tf.GradientTape() as tape:
            # Get embeddings for users and items
            user_embeddings = self.query_model(batch)
            item_embeddings = self.item_model(batch)
            
            # Compute retrieval loss
            loss = self.task(
                user_embeddings,
                item_embeddings,
                compute_metrics=False,
            )

            # Add regularization losses
            regularization_loss = sum(self.losses)
            total_loss = loss + regularization_loss

        # Apply gradients
        gradients = tape.gradient(total_loss, self.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))

        return {
            "loss": loss,
            "regularization_loss": regularization_loss,
            "total_loss": total_loss,
        }

    def test_step(self, batch) -> tf.Tensor:
        # Get embeddings
        user_embeddings = self.query_model(batch)
        item_embeddings = self.item_model(batch)

        # Compute loss
        loss = self.task(
            user_embeddings,
            item_embeddings,
            compute_metrics=False,
        )

        # Add regularization
        regularization_loss = sum(self.losses)
        total_loss = loss + regularization_loss

        # Gather metrics
        metrics = {metric.name: metric.result() for metric in self.metrics}
        metrics.update({
            "loss": loss,
            "regularization_loss": regularization_loss,
            "total_loss": total_loss,
        })

        return metrics

    def compute_user_embeddings(self, user_features):
        """Compute embeddings for user features."""
        return self.query_model(user_features)

    def compute_item_embeddings(self, item_features):
        """Compute embeddings for item features."""
        return self.item_model(item_features)
