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
            early_stopping_rounds=settings.RANKING_EARLY_STOPPING_ROUNDS,
            use_label_encoder=False,
            eval_metric='logloss',
            tree_method='hist'  # This is a fast tree method that handles categorical features well
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
            col for col in x_train.columns
            if x_train[col].dtype in [pl.Categorical, pl.Utf8, pl.String]
        ]

        # Process each categorical column
        for col in cat_features:
            # Create a mapping of unique values to integers
            unique_values = x_train[col].unique().to_list()
            value_to_int = {val: idx for idx, val in enumerate(unique_values)}
            
            # Create the mapping expression for train data
            x_train = x_train.with_columns([
                pl.when(pl.col(col).is_in(list(value_to_int.keys())))
                .then(pl.col(col).replace(value_to_int))
                .otherwise(pl.col(col))
                .alias(col)
            ])
            
            # Create the mapping expression for validation data with default -1 for unseen values
            x_val = x_val.with_columns([
                pl.when(pl.col(col).is_in(list(value_to_int.keys())))
                .then(pl.col(col).replace(value_to_int))
                .otherwise(pl.lit(-1))
                .alias(col)
            ])

        # Convert to numpy arrays for XGBoost
        x_train_np = x_train.to_numpy()
        y_train_np = y_train.to_numpy() if isinstance(y_train, pl.DataFrame) else y_train
        x_val_np = x_val.to_numpy()
        y_val_np = y_val.to_numpy() if isinstance(y_val, pl.DataFrame) else y_val

        return (x_train_np, y_train_np), (x_val_np, y_val_np)

    def fit(self):
        """Train the XGBoost model."""
        x_train, y_train = self._train_dataset
        x_val, y_val = self._eval_dataset

        self._model.fit(
            X=x_train,
            y=y_train,
            eval_set=[(x_val, y_val)],
            verbose=True
        )

        return self._model

    def evaluate(self, log: bool = False):
        """Evaluate the model performance."""
        x_val, y_val = self._eval_dataset
        preds = self._model.predict(x_val)

        precision, recall, fscore, _ = precision_recall_fscore_support(
            y_val, preds, average="binary"
        )

        if log:
            logger.info(classification_report(y_val, preds))

        return {
            "precision": precision,
            "recall": recall,
            "fscore": fscore,
        }

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