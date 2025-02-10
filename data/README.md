# Data Directory

This directory contains the data used for the GenAI Custom Real-Time Personalized Recommender system.

## Kaggle Dataset

### Dataset Requirements
1. Download the H&M Personalized Fashion Recommendations dataset from Kaggle:
   - Dataset URL: [H&M Personalized Fashion Recommendations](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/data)
   - You will need a Kaggle account to download the dataset

### Files Required
Place the following files in this directory:
- `articles.csv`: Contains article information (clothing items)
- `customers.csv`: Contains customer data
- `transactions_train.csv`: Contains the transaction history

### Data Processing Steps
1. Download the dataset from Kaggle
2. Extract the ZIP file
3. Place the CSV files in this directory
4. Ensure file permissions are correctly set
5. The data pipeline will automatically process these files according to the defined schemas in the feature store

### Data Structure
- articles.csv: Article metadata including product type, color, and category
- customers.csv: Customer information including age and location
- transactions_train.csv: Historical transaction data with customer-article interactions

## Data Loading Configuration

In the notebooks directory, we use a constant `ONLINE` to determine the data source:
- When `ONLINE = True`: Data is loaded from the Google Cloud Storage (GCS) bucket
- When `ONLINE = False`: Data is loaded locally from this directory (`data/`)

This configuration allows for flexible development and testing:
- Local development: Set `ONLINE = False` to work with local data files
- Production/Cloud: Set `ONLINE = True` to work with GCS bucket data

## Note
- The raw data files are not included in the repository due to size constraints
- Make sure to keep the data directory in your `.gitignore` file
- Handle the data according to Kaggle's terms of use and competition rules