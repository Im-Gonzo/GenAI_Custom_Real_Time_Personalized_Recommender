# GenAI Real-Time Personalized Recommender

A real-time recommender system using GCP Vertex AI, Feature Store, and Gemini for personalized recommendations.

## Project Structure 📁

```
.
├── recsys/               # Main recommender system code
├── terraform/            # Infrastructure as Code
├── notebooks/           # Jupyter notebooks for experiments
├── pyproject.toml      # Poetry dependencies
└── poetry.lock         # Poetry lock file
```

## Dataset 📊

This project uses the H&M Personalized Fashion Recommendations dataset:

1. **Access the Dataset**
   - Visit [H&M Kaggle Competition](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/data)
   - Create a Kaggle account if you don't have one
   - Download the dataset files

2. **Upload to GCS**
   - After infrastructure deployment, manually upload the dataset files to:
     ```
     gs://gonzo-recsys-data/h-and-m/
     ```
   - Required files:
     - articles.csv
     - customers.csv
     - transactions_train.csv
     - images/ (folder with article images)

## Prerequisites 📋

- Python 3.11+
- Poetry
- Terraform 1.0+
- Google Cloud SDK
- Make
- Kaggle account (for dataset access)

## Quick Start 🚀

```bash
# Install tools and set up environment
make setup

# Configure infrastructure
make deploy-all

# Upload dataset to GCS
gsutil -m cp -r /path/to/downloaded/data/* gs://gonzo-recsys-data/h-and-m/
```

