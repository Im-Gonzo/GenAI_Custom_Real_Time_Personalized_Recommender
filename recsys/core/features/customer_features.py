"""
Customer feature generation and processing.
"""
import random
from enum import Enum
import polars as pl
from loguru import logger
from typing import Dict, Optional
from recsys.config import CustomerDatasetSize


class DatasetSampler:
    """Handles sampling of customer data for different dataset sizes."""
    
    _SIZES: Dict[str, int] = {
        CustomerDatasetSize.LARGE.value: 50_000,
        CustomerDatasetSize.MEDIUM.value: 5_000,
        CustomerDatasetSize.SMALL.value: 1_000,
    }

    def __init__(self, size: CustomerDatasetSize) -> None:
        """
        Initialize sampler with desired dataset size.
        
        Args:
            size: Enum value indicating desired dataset size
        """
        self._size = size

    @classmethod
    def get_supported_sizes(cls) -> Dict[str, int]:
        """Get dictionary of supported dataset sizes and their counts."""
        return cls._SIZES

    def sample(
        self,
        customers_df: pl.DataFrame,
        transactions_df: pl.DataFrame
    ) -> Dict[str, pl.DataFrame]:
        """
        Sample customers and their transactions.
        
        Args:
            customers_df: DataFrame containing customer data
            transactions_df: DataFrame containing transaction data
            
        Returns:
            Dictionary containing sampled customers and their transactions
        """
        random.seed(27)  # For reproducibility

        n_customers = self._SIZES[self._size.value]
        logger.info(f"Sampling {n_customers} customers")
        
        customers_df = customers_df.sample(n=n_customers)

        logger.info(f"Original transactions count: {transactions_df.height}")
        transactions_df = transactions_df.join(
            customers_df.select("customer_id"),
            on="customer_id"
        )
        logger.info(f"Filtered transactions count: {transactions_df.height}")

        return {
            "customers": customers_df,
            "transactions": transactions_df
        }


def fill_missing_club_status(df: pl.DataFrame) -> pl.DataFrame:
    """
    Fill missing club member status values.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with filled club_member_status
    """
    return df.with_columns(pl.col("club_member_status").fill_null("ABSENT"))


def create_age_group() -> pl.Expr:
    """
    Create age group categories expression.
    
    Returns:
        Polars expression for age group categorization
    """
    return (
        pl.when(pl.col("age").is_between(0, 18))
        .then(pl.lit("0-18"))
        .when(pl.col("age").is_between(19, 25))
        .then(pl.lit("19-25"))
        .when(pl.col("age").is_between(26, 35))
        .then(pl.lit("26-35"))
        .when(pl.col("age").is_between(36, 45))
        .then(pl.lit("36-45"))
        .when(pl.col("age").is_between(46, 55))
        .then(pl.lit("46-55"))
        .when(pl.col("age").is_between(56, 65))
        .then(pl.lit("56-65"))
        .otherwise(pl.lit("66+"))
    ).alias("age_group")


def compute_features_customers(
    df: pl.DataFrame,
    drop_null_age: bool = False,
    additional_columns: Optional[list] = None
) -> pl.DataFrame:
    """
    Compute all customer features from raw data.
    
    Args:
        df: Input DataFrame with raw customer data
        drop_null_age: Whether to drop rows with null age values
        additional_columns: Additional columns to include in output
        
    Returns:
        DataFrame with computed features
    """
    logger.info("Computing customer features...")
    
    # Validate required columns
    required_columns = ["customer_id", "club_member_status", "age", "postal_code"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    # Process features
    df = (
        df.pipe(fill_missing_club_status)
        .with_columns([
            create_age_group(),
            pl.col("age").cast(pl.Float64)
        ])
    )

    # Handle null ages if requested
    if drop_null_age:
        df = df.drop_nulls(subset=["age"])

    # Select output columns
    output_columns = ["customer_id", "club_member_status", "age", "postal_code", "age_group"]
    if additional_columns:
        output_columns.extend(additional_columns)

    logger.info("Customer feature computation complete")
    return df.select(output_columns)
