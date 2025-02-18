"""
Interaction feature generation and processing.
"""
import numpy as np
import polars as pl
from typing import Dict, List, Set
from loguru import logger
from tqdm import tqdm


def generate_interaction_data(trans_df: pl.DataFrame) -> pl.DataFrame:
    """
    Generates synthetic interaction data based on transaction history.
    
    Args:
        trans_df: Transaction DataFrame with customer and article information
        
    Returns:
        DataFrame containing generated interaction data
    """
    unique_customers = trans_df["customer_id"].unique()
    all_articles = trans_df["article_id"].unique()
    all_articles_set = set(all_articles)

    interactions = []

    def generate_timestamp(base_ts: int, count: int, min_hours: int, max_hours: int) -> np.ndarray:
        """Generate timestamps within a range of hours before base timestamp."""
        hours = np.random.randint(min_hours, max_hours, size=count)
        return base_ts - (hours * 3_600_000)

    # Interaction generation parameters
    CLICKS_BEFORE_PURCHASE_PROB = 0.9
    MIN_IGNORES = 40
    MAX_IGNORES = 60
    MIN_EXTRA_CLICKS = 5
    MAX_EXTRA_CLICKS = 8
    EXTRA_CLICKS_PROB = 0.95

    chunk_size = 1000
    for chunk_start in tqdm(range(0, len(unique_customers), chunk_size), desc="Processing customers"):
        chunk_end = min(chunk_start + chunk_size, len(unique_customers))
        chunk_customers = unique_customers[chunk_start:chunk_end]

        chunk_transactions = trans_df.filter(pl.col("customer_id").is_in(chunk_customers))

        for customer_id in chunk_customers:
            customer_purchases = chunk_transactions.filter(pl.col("customer_id") == customer_id)

            if len(customer_purchases) == 0:
                continue

            customer_articles: Dict[str, Set[str]] = {
                "purchased": set(),
                "clicked": set(),
                "ignored": set()
            }
            
            last_purchase_timestamp = customer_purchases["t_dat"].max()

            # Generate ignores
            num_ignores = np.random.randint(MIN_IGNORES, MAX_IGNORES)
            available_articles = list(all_articles_set)

            if available_articles and num_ignores > 0:
                ignore_timestamps = generate_timestamp(last_purchase_timestamp, num_ignores, 1, 96)
                selected_ignores = np.random.choice(
                    available_articles,
                    size=min(num_ignores, len(available_articles)),
                    replace=False,
                )

                # Generate multiple sets of ignores
                for ts, art_id in zip(ignore_timestamps, selected_ignores):
                    num_ignore_events = np.random.randint(1, 3)
                    for _ in range(num_ignore_events):
                        ignore_ts = ts - np.random.randint(1, 12) * 3_600_00
                        interactions.append({
                            "t_dat": ignore_ts,
                            "customer_id": customer_id,
                            "article_id": art_id,
                            "interaction_score": 0,
                            "prev_article_id": None,
                        })
                        customer_articles["ignored"].add(art_id)

            # Process actual purchases
            purchase_rows = customer_purchases.iter_rows(named=True)
            for row in purchase_rows:
                purchase_timestamp = row["t_dat"]
                article_id = row["article_id"]

                # Add clicks before purchase
                if np.random.random() < CLICKS_BEFORE_PURCHASE_PROB:
                    num_pre_clicks = np.random.randint(1, 3)
                    for _ in range(num_pre_clicks):
                        click_timestamp = generate_timestamp(purchase_timestamp, 1, 1, 48)[0]
                        interactions.append({
                            "t_dat": click_timestamp,
                            "customer_id": customer_id,
                            "article_id": article_id,
                            "interaction_score": 1,
                            "prev_article_id": None,
                        })
                        customer_articles["clicked"].add(article_id)

                # Add purchase
                interactions.append({
                    "t_dat": purchase_timestamp,
                    "customer_id": customer_id,
                    "article_id": article_id,
                    "interaction_score": 2,
                    "prev_article_id": None,
                })
                customer_articles["purchased"].add(article_id)

            # Generate extra clicks
            if np.random.random() < EXTRA_CLICKS_PROB:
                num_extra_clicks = np.random.randint(MIN_EXTRA_CLICKS, MAX_EXTRA_CLICKS + 1)
                available_for_clicks = list(
                    all_articles_set 
                    - customer_articles["purchased"] 
                    - customer_articles["clicked"] 
                    - customer_articles["ignored"]
                )

                if available_for_clicks and num_extra_clicks > 0:
                    click_timestamp = generate_timestamp(last_purchase_timestamp, num_extra_clicks, 1, 72)
                    selected_clicks = np.random.choice(
                        available_for_clicks,
                        size=min(num_extra_clicks, len(available_for_clicks)),
                        replace=False,
                    )

                    for ts, art_id in zip(click_timestamp, selected_clicks):
                        interactions.append({
                            "t_dat": ts,
                            "customer_id": customer_id,
                            "article_id": article_id,
                            "interaction_score": 1,
                            "prev_article_id": None,
                        })

    if not interactions:
        logger.warning("No interactions generated")
        return pl.DataFrame(schema={
            "t_dat": pl.Int64,
            "customer_id": pl.Utf8,
            "article_id": pl.Utf8,
            "interaction_score": pl.Int64,
            "prev_article_id": pl.Utf8,
        })

    # Create final DataFrame
    interactions_df = pl.DataFrame(interactions)
    sorted_df = interactions_df.sort(["customer_id", "t_dat"])

    # Add previous article information
    final_df = sorted_df.with_columns([
        pl.col("article_id")
        .alias("prev_article_id")
        .shift(1)
        .over("customer_id")
        .fill_null("START")
    ])

    logger.info(f"Generated {len(final_df)} interactions")
    return final_df
