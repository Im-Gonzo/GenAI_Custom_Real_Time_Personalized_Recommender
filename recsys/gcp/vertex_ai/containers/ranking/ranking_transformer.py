"""
Transformer for ranking model in Vertex AI.
Handles preprocessing of inputs and postprocessing of outputs.
"""

import time
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from google.cloud import aiplatform, bigquery
from google.cloud.exceptions import GoogleCloudError, NotFound
from vertexai.resources.preview.feature_store import FeatureOnlineStore, FeatureView
from config import (
    FEATURE_STORE_ID,
    PROJECT_ID,
    LOCATION,
    RANKING_MODEL_FEATURES,
    TOP_K_CANDIDATES,
    TRANSACTIONS_TABLE,
    ARTICLES_TABLE,
    RANKINGS_TABLE,
    CANDIDATES_TABLE
)
from logger import logger


# Initialize GCP clients
aiplatform.init(project=PROJECT_ID, location=LOCATION)
client = bigquery.Client(project=PROJECT_ID)


class RankingTransformer:
    """
    Handles preprocessing and postprocessing for the ranking model.

    This transformer prepares data for the ranking model by:
    1. Finding similar items using embedding similarity
    2. Filtering out already purchased items
    3. Retrieving article features
    4. Combining with customer features
    5. Preparing the features in the format needed by the model

    After prediction, it formats the results into a ranked list.
    """

    def __init__(self):
        """Initialize feature store connections and views."""
        logger.info("🔄 Initializing RankingTransformer")

        try:
            # Initialize feature store
            self.feature_store = FeatureOnlineStore(name=FEATURE_STORE_ID)
            logger.info(f"📦 Connected to feature store: {FEATURE_STORE_ID}")

            # Initialize feature views
            self.articles_view = FeatureView(
                name="articles",
                feature_online_store_id=self.feature_store.name,
                location=LOCATION,
            )
            self.customers_view = FeatureView(
                name="customers",
                feature_online_store_id=self.feature_store.name,
                location=LOCATION,
            )
            self.transactions_view = FeatureView(
                name="transactions",
                feature_online_store_id=self.feature_store.name,
                location=LOCATION,
            )
            self.candidates_view = FeatureView(
                name="candidates",
                feature_online_store_id=self.feature_store.name,
                location=LOCATION,
            )

            # Get feature names for the model
            self.ranking_model_feature_names = list(RANKING_MODEL_FEATURES.keys())

            logger.success("RankingTransformer initialized successfully")

        except Exception as e:
            logger.error(
                f"❌ Failed to initialize RankingTransformer: {str(e)}", exc_info=True
            )
            raise

    def _execute_query(
        self, query: str, query_name: str = "query"
    ) -> bigquery.table.RowIterator:
        """
        Execute a BigQuery query safely.

        Args:
            query: The SQL query to execute
            query_name: Name of the query for logging

        Returns:
            Result of the query

        Raises:
            GoogleCloudError: If query execution fails
        """
        try:
            # Log the query (truncated for readability)
            truncated_query = query[:300] + "..." if len(query) > 300 else query
            logger.query(f"Executing {query_name}: {truncated_query}")

            # Time the query execution
            start_time = time.time()

            # Execute the query
            query_job = client.query(query)
            results = query_job.result()

            # Log query completion time
            duration = time.time() - start_time
            row_count = (
                results.total_rows if hasattr(results, "total_rows") else "unknown"
            )
            logger.info(
                f"🔍 {query_name} completed in {duration:.3f}s, rows: {row_count}"
            )

            return results

        except GoogleCloudError as e:
            logger.error(
                f"❌ BigQuery error executing {query_name}: {str(e)}", exc_info=True
            )
            raise
        except Exception as e:
            logger.error(
                f"❌ Unexpected error executing {query_name}: {str(e)}", exc_info=True
            )
            raise

    def _get_already_bought_items(self, customer_id: str) -> List[str]:
        """
        Get list of items already bought by customer.

        Args:
            customer_id: ID of the customer

        Returns:
            List of article IDs already purchased
        """
        logger.info(
            f"🛒 Getting already purchased items for customer: {customer_id[:8]}..."
        )

        try:
            # Use parameterized query to prevent SQL injection
            query = f"""
                SELECT
                    article_id
                FROM
                    {TRANSACTIONS_TABLE}
                WHERE
                    customer_id = @customer_id
            """

            # Set query parameters
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("customer_id", "STRING", customer_id)
                ]
            )

            # Execute query
            query_job = client.query(query, job_config=job_config)
            results = query_job.result()

            # Extract article IDs
            article_ids = [str(row.article_id) for row in results]

            if article_ids:
                logger.info(f"🛍️ Found {len(article_ids)} previously purchased articles")
                return article_ids

            logger.warning(f"⚠️ No transactions found for customer: {customer_id[:8]}")
            return []

        except Exception as e:
            logger.error(
                f"❌ Error reading transactions: {type(e).__name__}: {str(e)}",
                exc_info=True,
            )
            # Return empty list rather than failing
            return []

    def _find_similar_items(
        self, query_embedding: List[float], k: int = TOP_K_CANDIDATES
    ) -> List[str]:
        """
        Find similar items based on embedding similarity.

        Args:
            query_embedding: Vector embedding for similarity search
            k: Number of similar items to return

        Returns:
            List of article IDs similar to the query
        """
        logger.info(f"🔍 Finding top {k} similar items")

        try:
            # Convert query embedding to string safely
            query_vector_str = str(query_embedding)

            query = f"""
                SELECT
                    article_id,
                    ARRAY_LENGTH(embeddings) as emb_size,
                    ML.DISTANCE(embeddings, {query_vector_str}) as similarity
                FROM
                    {CANDIDATES_TABLE}
                ORDER BY
                    similarity 
                DESC
                LIMIT {k}
            """

            # Execute query
            results = self._execute_query(query, "similarity_search")

            # Extract article IDs
            article_ids = [str(row.article_id) for row in results]

            logger.info(f"✨ Found {len(article_ids)} similar items")
            return article_ids

        except Exception as e:
            logger.error(
                f"❌ Error in similarity search: {type(e).__name__}: {str(e)}",
                exc_info=True,
            )
            return []

    def _get_articles_data(self, articles: List[str]) -> pd.DataFrame:
        """
        Get features for a list of articles.

        Args:
            articles: List of article IDs

        Returns:
            DataFrame with article features
        """
        if not articles:
            logger.warning("⚠️ Empty article list for feature retrieval")
            return pd.DataFrame()

        logger.info(f"📊 Getting features for {len(articles)} articles")

        try:
            # Format article list for SQL IN clause
            articles_formatted = ", ".join([f"'{article}'" for article in articles])

            query = f"""
                SELECT
                    *
                FROM
                    {ARTICLES_TABLE}
                WHERE
                    article_id IN ({articles_formatted})
            """

            # Execute query
            results = self._execute_query(query, "articles_data")

            # Convert to DataFrame
            df = results.to_dataframe()

            logger.info(f"📊 Retrieved features for {len(df)} articles")
            return df

        except Exception as e:
            logger.error(
                f"❌ Error retrieving article features: {type(e).__name__}: {str(e)}",
                exc_info=True,
            )
            return pd.DataFrame()

    def _get_rankings_data(self, customer_id: str) -> pd.DataFrame:
        """
        Get previous rankings data for a customer.

        Args:
            customer_id: ID of the customer

        Returns:
            DataFrame with ranking data
        """
        logger.info(f"🏆 Getting previous rankings for customer: {customer_id[:8]}")

        try:
            # Use parameterized query to prevent SQL injection
            query = f"""
                SELECT
                    *
                FROM
                    {RANKINGS_TABLE}
                WHERE
                    customer_id = @customer_id
            """

            # Set query parameters
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("customer_id", "STRING", customer_id)
                ]
            )

            # Execute query
            query_job = client.query(query, job_config=job_config)
            results = query_job.result()

            # Convert to DataFrame
            df = results.to_dataframe()

            logger.info(f"🏆 Retrieved {len(df)} previous rankings")
            return df

        except Exception as e:
            logger.error(
                f"❌ Error retrieving rankings: {type(e).__name__}: {str(e)}",
                exc_info=True,
            )
            return pd.DataFrame()

    def preprocess(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess inputs for ranking prediction.

        Args:
            inputs: Dictionary with input data

        Returns:
            Dictionary with processed inputs ready for model prediction
        """
        logger.timer_start("preprocess")

        try:
            # Extract the input instance
            instance = inputs["instances"][0]
            customer_id = instance["customer_id"]
            query_embedding = instance["query_emb"]

            logger.info(f"🔄 Preprocessing for customer: {customer_id[:8]}")

            # 1. Find similar items using vector search
            neighbor_ids = self._find_similar_items(query_embedding)

            if not neighbor_ids:
                logger.warning("⚠️ No candidate items found via embedding similarity")
                return {
                    "inputs": [{"ranking_features": pd.DataFrame(), "article_ids": []}]
                }

            # 2. Get items already bought by the customer
            logger.timer_start("get_bought_items")
            already_bought_items_ids = self._get_already_bought_items(customer_id)
            logger.timer_end("get_bought_items")

            # 3. Filter out already bought items
            article_entities = [
                str(item_id)
                for item_id in neighbor_ids
                if str(item_id) not in already_bought_items_ids
            ]

            if not article_entities:
                logger.warning(
                    "⚠️ No new items to recommend after filtering out purchased items"
                )
                return {
                    "inputs": [{"ranking_features": pd.DataFrame(), "article_ids": []}]
                }

            # 4. Get article features
            logger.timer_start("get_article_features")
            articles_data = self._get_articles_data(article_entities)
            logger.timer_end("get_article_features")

            # 5. Get customer features
            logger.timer_start("get_customer_features")
            self.customers_view.sync()
            customer_result = self.customers_view.read(key=[customer_id])
            customer_features = customer_result.to_dict()["features"]
            logger.timer_end("get_customer_features")

            # 6. Create feature DataFrame
            ranking_model_inputs = articles_data.copy()

            # 7. Add customer and temporal features
            logger.data("Adding customer and temporal features")
            ranking_model_inputs["age"] = customer_features[1]["value"].get(
                "double_value", 0
            )
            ranking_model_inputs["month_sin"] = instance["month_sin"]
            ranking_model_inputs["month_cos"] = instance["month_cos"]

            # 8. Handle special case for colour_group_name_right
            if (
                "colour_group_name_right" in self.ranking_model_feature_names
                and "colour_group_name_right" not in ranking_model_inputs.columns
            ):
                if "colour_group_name" in ranking_model_inputs.columns:
                    logger.info(
                        "🎨 Copying colour_group_name to colour_group_name_right"
                    )
                    ranking_model_inputs["colour_group_name_right"] = (
                        ranking_model_inputs["colour_group_name"]
                    )

            # 9. Add missing features with zeros
            for feature in self.ranking_model_feature_names:
                if feature not in ranking_model_inputs.columns:
                    logger.warning(f"⚠️ Adding missing feature {feature} with zeros")
                    ranking_model_inputs[feature] = 0

            # 10. Select only the features needed by the model
            try:
                ranking_model_inputs = ranking_model_inputs[
                    self.ranking_model_feature_names
                ]
            except KeyError as e:
                # Log detailed information about missing features
                missing_features = set(self.ranking_model_feature_names) - set(
                    ranking_model_inputs.columns
                )
                logger.error(f"❌ Missing features: {missing_features}")
                logger.error(
                    f"❌ Available features: {ranking_model_inputs.columns.tolist()}"
                )
                raise ValueError(f"Missing required features: {missing_features}")

            logger.success(
                f"Preprocessing complete with {len(ranking_model_inputs)} candidates"
            )
            logger.timer_end("preprocess")

            return {
                "inputs": [
                    {
                        "ranking_features": ranking_model_inputs,
                        "article_ids": article_entities,
                    }
                ]
            }

        except Exception as e:
            logger.error(
                f"❌ Error in preprocessing: {type(e).__name__}: {str(e)}",
                exc_info=True,
            )
            # Re-raise with more context
            raise ValueError(f"Preprocessing failed: {type(e).__name__}: {str(e)}")

    def postprocess(self, outputs: Dict[str, Any]) -> Dict[str, List]:
        """
        Process model outputs into ranked list of recommendations.

        Args:
            outputs: Dictionary with model prediction outputs

        Returns:
            Dictionary with ranking results
        """
        logger.timer_start("postprocess")

        try:
            # Validate outputs
            if not outputs.get("scores") or not outputs.get("article_ids"):
                logger.warning("⚠️ Empty prediction results")
                return {"ranking": []}

            # Get scores and article IDs
            scores = outputs["scores"]
            article_ids = outputs["article_ids"]

            # Create ranking pairs
            ranking = list(zip(scores, article_ids))

            # Sort by score (descending)
            ranking.sort(reverse=True)

            # Take only the top 10 predictions
            top_10_ranking = ranking[:10]
            logger.info(f"📊 Returning top {len(top_10_ranking)} recommendations")

            # Log top scores for monitoring
            if top_10_ranking:
                top_score = top_10_ranking[0][0]
                bottom_score = top_10_ranking[-1][0]
                logger.info(f"📈 Score range: {bottom_score:.4f} to {top_score:.4f}")

            logger.timer_end("postprocess")

            return {
                "ranking": top_10_ranking,
            }

        except Exception as e:
            logger.error(
                f"❌ Error in postprocessing: {type(e).__name__}: {str(e)}",
                exc_info=True,
            )
            # Return empty ranking rather than failing
            return {"ranking": []}
