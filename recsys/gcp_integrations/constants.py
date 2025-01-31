from google.cloud.aiplatform import Feature

# Post-Ingestion formatting

customer_feature_descriptions: list[dict] = [
    {"name": "customer_id", "description": "Unique identifier for each customer."},
    {
        "name": "club_member_status",
        "description": "Membership status of the customer in the club.",
    },
    {"name": "age", "description": "Age of the customer."},
    {
        "name": "postal_code",
        "description": "Postal code associated with the customer's address.",
    },
    {"name": "age_group", "description": "Categorized age group of the customer."},
]


transaction_feature_descriptions: list[dict] = [
    {"name": "t_dat", "description": "Timestamp of the data record."},
    {"name": "customer_id", "description": "Unique identifier for each customer."},
    {"name": "article_id", "description": "Identifier for the purchased article."},
    {"name": "price", "description": "Price of the purchased article."},
    {"name": "sales_channel_id", "description": "Identifier for the sales channel."},
    {"name": "year", "description": "Year of the transaction."},
    {"name": "month", "description": "Month of the transaction."},
    {"name": "day", "description": "Day of the transaction."},
    {"name": "day_of_week", "description": "Day of the week of the transaction."},
    {
        "name": "month_sin",
        "description": "Sine of the month used for seasonal patterns.",
    },
    {
        "name": "month_cos",
        "description": "Cosine of the month used for seasonal patterns.",
    },
]

interactions_feature_descriptions: list[dict] = [
    {"name": "t_dat", "description": "Timestamp of the interaction."},
    {"name": "customer_id", "description": "Unique identifier for each customer."},
    {
        "name": "article_id",
        "description": "Identifier for the article that was interacted with.",
    },
    {
        "name": "interaction_score",
        "description": "Type of interaction: 0 = ignore, 1 = click, 2 = purchase.",
    },
    {
        "name": "prev_article_id",
        "description": "Previous article that the customer interacted with, useful for sequential recommendation patterns.",
    },
]

ranking_feature_descriptions: list[dict] = [
    {"name": "customer_id", "description": "Unique identifier for each customer."},
    {"name": "article_id", "description": "Identifier for the purchased article."},
    {"name": "age", "description": "Age of the customer."},
    {"name": "product_type_name", "description": "Name of the product type."},
    {"name": "product_group_name", "description": "Name of the product group."},
    {
        "name": "graphical_appearance_name",
        "description": "Name of the graphical appearance.",
    },
    {"name": "colour_group_name", "description": "Name of the colour group."},
    {
        "name": "perceived_colour_value_name",
        "description": "Name of the perceived colour value.",
    },
    {
        "name": "perceived_colour_master_name",
        "description": "Name of the perceived colour master.",
    },
    {"name": "department_name", "description": "Name of the department."},
    {"name": "index_name", "description": "Name of the index."},
    {"name": "index_group_name", "description": "Name of the index group."},
    {"name": "section_name", "description": "Name of the section."},
    {"name": "garment_group_name", "description": "Name of the garment group."},
    {
        "name": "label",
        "description": "Label indicating whether the article was purchased (1) or not (0).",
    },
]

# Pre-Ingestion format
article_feature_description = [
    Feature(
        feature_name="article_id",
    ),
    Feature(
        feature_name="product_code",
    ),
    Feature(
        feature_name="prod_name",
    ),
    Feature(
        feature_name="product_type_no",
    ),
    Feature(
        feature_name="product_type_name",
    ),
    Feature(
        feature_name="product_group_name",
    ),
    Feature(
        feature_name="graphical_appearance_no",
    ),
    Feature(
        feature_name="graphical_appearance_name",
    ),
    Feature(
        feature_name="colour_group_code",
    ),
    Feature(
        feature_name="colour_group_name",
    ),
    Feature(
        feature_name="perceived_colour_value_id",
    ),
    Feature(
        feature_name="perceived_colour_value_name",
    ),
    Feature(
        feature_name="perceived_colour_master_id",
    ),
    Feature(
        feature_name="perceived_colour_master_name",
    ),
    Feature(
        feature_name="department_no",
    ),
    Feature(
        feature_name="department_name",
    ),
    Feature(
        feature_name="index_code",
    ),
    Feature(
        feature_name="index_name",
    ),
    Feature(
        feature_name="index_group_no",
    ),
    Feature(
        feature_name="index_group_name",
    ),
    Feature(
        feature_name="section_no",
    ),
    Feature(
        feature_name="section_name",
    ),
    Feature(
        feature_name="garment_group_no",
    ),
    Feature(
        feature_name="garment_group_name",
    ),
    Feature(
        feature_name="prod_name_length",
    ),
    Feature(
        feature_name="article_description",
    ),
    Feature(
        feature_name="embeddings",
    ),
    Feature(feature_name="image_url"),
]
