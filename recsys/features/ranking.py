import polars as pl


def validate_dataframes(
    trans_df: pl.DataFrame, articles_df: pl.DataFrame, customers_df: pl.DataFrame
):
    required_trans_cols = ["article_id", "customer_id"]
    required_customer_cols = ["customer_id", "age"]
    required_article_cols = ["article_id"]

    if not all(col in trans_df.columns for col in required_trans_cols):
        raise ValueError(
            f"Transaction dataframe missing required columns: {required_trans_cols}"
        )
    if not all(col in customers_df.columns for col in required_customer_cols):
        raise ValueError(
            f"Customers dataframe missing required columns: {required_customer_cols}"
        )
    if not all(col in articles_df.columns for col in required_article_cols):
        raise ValueError(
            f"Articles dataframe missing required columns: {required_article_cols}"
        )


def compute_rankings_dataset(
    trans_df: pl.DataFrame,
    articles_df: pl.DataFrame,
    customers_df: pl.DataFrame,
) -> pl.DataFrame:
    validate_dataframes(trans_df, articles_df, customers_df)

    trans_df = trans_df.with_columns(pl.col("article_id").cast(pl.Utf8))
    articles_df = articles_df.with_columns(pl.col("article_id").cast(pl.Utf8))

    # Get unique transactions
    query_features = ["customer_id", "article_id"]
    df = trans_df.select(query_features).unique()

    # Join with customers data
    df = df.join(
        customers_df.select(["customer_id", "age"]), on="customer_id", how="left"
    )

    # Get positive pairs of existing transactions
    positive_pairs = df.clone()

    # Calculate number of negative pairs to generate
    n_neg = len(positive_pairs) * 10

    # Sampling negative pairs
    article_ids = (
        df.select("article_id")
        .unique()
        .sample(n=n_neg, with_replacement=True, seed=2)
        .get_column("article_id")
    )

    customer_ids = (
        df.select("customer_id")
        .sample(n=n_neg, with_replacement=True, seed=3)
        .get_column("customer_id")
    )

    other_features = df.select(["age"]).sample(n=n_neg, with_replacement=True, seed=4)

    # Construct negative DataFrame
    negative_pairs = pl.DataFrame(
        {
            "article_id": article_ids,
            "customer_id": customer_ids,
            "age": other_features.get_column("age"),
        }
    )

    # Labeling
    positive_pairs = positive_pairs.with_columns(pl.lit(1).alias("label"))
    negative_pairs = negative_pairs.with_columns(pl.lit(0).alias("label"))

    # Concatenate dfs
    ranking_df = pl.concat(
        [positive_pairs, negative_pairs.select(positive_pairs.columns)]
    )

    item_features = [
        "article_id",
        "product_type_name",
        "product_group_name",
        "graphical_appearance_name",
        "perceived_colour_value_name",
        "perceived_colour_master_name",
        "department_name",
        "index_name",
        "index_group_name",
        "section_name",
        "garment_group_name",
    ]

    item_df = articles_df.unique(subset=["article_id"]).select(item_features)
    ranking_df = ranking_df.join(item_df, on="article_id", how="left")

    return ranking_df
