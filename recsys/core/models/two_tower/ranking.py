import numpy as np
import polars as pl
from loguru import logger
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, precision_recall_fscore_support

from recsys.config import settings


class RankingModelFactory:
    @classmethod
    def build(cls) -> XGBClassifier:
        return XGBClassifier(
            learning_rate=settings.RANKING_LEARNING_RATE,
            n_estimators=settings.RANKING_ITERATIONS,
            max_depth=10,
            scale_pos_weight=settings.RANKING_SCALE_POS_WEIGHT,
            min_child_weight=5,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.5,
            reg_lambda=2.0,
            early_stopping_rounds=settings.RANKING_EARLY_STOPPING_ROUNDS,
            use_label_encoder=False,
            eval_metric=["logloss", "auc", "aucpr", "error"],
            tree_method="hist",  # This is a fast tree method that handles categorical features well
        )


class RankingModelTrainer:
    def __init__(self, model, train_dataset, eval_dataset):
        self._model = model
        self._x_train, self._y_train = train_dataset
        self._x_val, self._y_val = eval_dataset

        # Convert and store the preprocessed datasets
        self._train_dataset, self._eval_dataset = self._initialize_dataset(
            train_dataset, eval_dataset
        )

    def get_model(self):
        return self._model

    def _initialize_dataset(self, train_dataset, eval_dataset):
        """Initialize datasets for XGBoost training and evaluation.

        Args:
            train_dataset: Tuple of (X_train, y_train)
            eval_dataset: Tuple of (X_val, y_val)

        Returns:
            Tuple of (train_data, eval_data) as numpy arrays
        """
        x_train, y_train = train_dataset
        x_val, y_val = eval_dataset

        # Get categorical features
        cat_features = [
            col
            for col in x_train.columns
            if x_train[col].dtype in [pl.Categorical, pl.Utf8, pl.String]
        ]

        logger.info(
            f"Detected {len(cat_features)} categorical features: {cat_features}"
        )

        # Process each categorical column
        for col in cat_features:
            value_counts = x_train[col].value_counts()

            # Create a mapping based on frequency (higher frequency = lower integer)
            # This helps the model prioritize common categories
            sorted_values = value_counts.sort("count", descending=True)

            sorted_values_list = sorted_values[col].to_list()

            value_to_int = {val: idx for idx, val in enumerate(sorted_values_list)}

            # Create the mapping expression for train data
            x_train = x_train.with_columns(
                [
                    pl.when(pl.col(col).is_in(list(value_to_int.keys())))
                    .then(pl.col(col).replace(value_to_int))
                    .otherwise(pl.lit(-1))
                    .alias(col)
                ]
            )

            # Create the mapping expression for validation data
            x_val = x_val.with_columns(
                [
                    pl.when(pl.col(col).is_in(list(value_to_int.keys())))
                    .then(pl.col(col).replace(value_to_int))
                    .otherwise(pl.lit(-1))
                    .alias(col)
                ]
            )

        # Convert to numpy arrays for XGBoost
        x_train_np = x_train.to_numpy()
        y_train_np = (
            y_train.to_numpy() if isinstance(y_train, pl.DataFrame) else y_train
        )
        x_val_np = x_val.to_numpy()
        y_val_np = y_val.to_numpy() if isinstance(y_val, pl.DataFrame) else y_val

        return (x_train_np, y_train_np), (x_val_np, y_val_np)

    def fit(self):
        """Train the XGBoost model with improved settings for class imbalance."""
        x_train, y_train = self._train_dataset
        x_val, y_val = self._eval_dataset

        # Calculate positive class weight for unbalanced data
        # Alternative to scale_pos_weight, can be used together for better control
        pos_count = int(np.sum(y_train == 1))
        neg_count = int(np.sum(y_train == 0))

        # Log class distribution
        logger.info(
            f"Training data: {pos_count} positive samples, {neg_count} negative samples"
        )
        logger.info(f"Class ratio (neg/pos): {neg_count / pos_count:.2f}")

        # Train with sample weights and evaluation metrics
        self._model.fit(
            X=x_train,
            y=y_train,
            eval_set=[(x_val, y_val)],
            verbose=True,
        )

        return self._model

    def evaluate(self, log: bool = False, threshold=0.5):
        """Evaluate the model performance with adjustable threshold."""
        x_val, y_val = self._eval_dataset

        # Get probability predictions
        proba_preds = self._model.predict_proba(x_val)[:, 1]

        # Apply threshold to get binary predictions
        preds = (proba_preds >= threshold).astype(int)

        precision, recall, fscore, _ = precision_recall_fscore_support(
            y_val, preds, average="binary"
        )

        if log:
            logger.info(f"Evaluation with threshold {threshold}:")
            logger.info(classification_report(y_val, preds))

        return {
            "precision": precision,
            "recall": recall,
            "fscore": fscore,
            "threshold": threshold,
        }

    def find_optimal_threshold(self, step=0.05):
        """Find threshold that maximizes F1 score."""
        x_val, y_val = self._eval_dataset
        proba_preds = self._model.predict_proba(x_val)[:, 1]

        best_fscore = 0
        best_threshold = 0.5
        best_metrics = None

        # Try different thresholds
        thresholds = [i * step for i in range(1, int(1 / step))]

        logger.info(f"Finding optimal threshold from {len(thresholds)} values...")

        for threshold in thresholds:
            preds = (proba_preds >= threshold).astype(int)
            precision, recall, fscore, _ = precision_recall_fscore_support(
                y_val, preds, average="binary"
            )

            # Log each threshold's performance
            logger.info(
                f"Threshold {threshold:.2f}: Precision {precision:.3f}, Recall {recall:.3f}, F1 {fscore:.3f}"
            )

            if fscore > best_fscore:
                best_fscore = fscore
                best_threshold = threshold
                best_metrics = {
                    "precision": precision,
                    "recall": recall,
                    "fscore": fscore,
                }

        logger.info(
            f"Optimal threshold: {best_threshold:.2f} with F1: {best_fscore:.3f}"
        )
        return best_threshold, best_metrics

    def get_feature_importance(self) -> dict:
        """Get feature importance scores."""
        feat_to_score = {
            feature: score
            for feature, score in zip(
                self._x_train.columns,
                self._model.feature_importances_,
            )
        }

        feat_to_score = dict(
            sorted(feat_to_score.items(), key=lambda item: item[1], reverse=True)
        )

        return feat_to_score
