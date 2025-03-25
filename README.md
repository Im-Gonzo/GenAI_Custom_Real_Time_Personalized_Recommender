# GenAI Custom Real-Time Personalized Recommender

A real-time recommender system using GCP Vertex AI, Feature Store, and Gemini for personalized recommendations. This system leverages two-tower architecture, feature engineering, and generative AI to provide highly relevant and customized product suggestions.

## Project Overview 🚀

This project implements a modern recommendation system with:
- Two-Tower architecture (query and item models)
- Real-time feature computation
- Vertex AI Feature Store integration
- Gemini integration for content enhancement
- Infrastructure as Code (Terraform)
- CI/CD pipelines

## Project Structure 📁

```
.
├── recsys/                 # Main recommender system code
│   ├── core/               # Core recommender components
│   ├── data/               # Data processing modules
│   ├── features/           # Feature engineering
│   └── gcp/                # GCP integration utilities
├── terraform/              # Infrastructure as Code
│   ├── modules/            # Terraform modules
│   └── ...                 # Terraform configuration files
├── notebooks/              # Jupyter notebooks for model development
│   ├── 1_feature_computing.ipynb            # Feature computation
│   ├── 2_tp_training_retrieval_model.ipynb  # Two-tower retrieval 
│   ├── 3_tp_training_ranking_model.ipynb    # Ranking model training
│   ├── 4_ip_computing_item_embeddings.ipynb # Item embedding 
│   ├── 5_ip_creating_deployments.ipynb      # Production deployment
├── data/                   # Data directory (not in repository)
│   └── images/             # Product images (30GB, excluded from git)
├── src/                    # Additional source code
├── .env.example            # Example environment variables
├── LOCAL_SETUP.md          # Detailed local setup instructions
├── Makefile                # Build and automation tasks
├── poetry.lock             # Poetry lock file
└── pyproject.toml          # Poetry dependencies
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
     gs://my-gcs-bucket/h-and-m/
     ```
   - Required files:
     - articles.csv
     - customers.csv
     - transactions_train.csv
     - images/ (folder with article images)

## Prerequisites 📋

- Python 3.11+
- Poetry (Python package manager)
- Terraform 1.0+
- Google Cloud SDK
- Kaggle account (for dataset access)

## Quick Start 🚀

```bash
# Install tools and set up environment
make setup

# Configure infrastructure
make deploy-all

# Upload dataset to GCS
gsutil -m cp -r /path/to/downloaded/data/* gs://my-gcs-bucket/h-and-m/
```

## Development Workflow 🔧

1. **Environment Setup**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd GenAI_Custom_Real_Time_Personalized_Recommender
   
   # Install dependencies
   make dev-setup
   ```

2. **Infrastructure Management**
   ```bash
   # Initialize Terraform
   make tf-init
   
   # Plan changes
   make tf-plan
   
   # Apply changes
   make tf-apply
   
   # Destroy resources (when needed)
   make tf-destroy
   ```

3. **Code Quality**
   ```bash
   # Format code
   make format
   
   # Run linters
   make lint
   
   ```

## Recommender System Pipeline 🔄

1. **Feature Engineering**
   - Extract user behavior patterns
   - Process item metadata
   - Create feature vectors

2. **Model Training**
   - Two-tower architecture for retrieval
   - Ranking model for personalized recommendations
   - Item embedding computation

3. **Deployment**
   - Feature Store population
   - Model deployment to Vertex AI
   - API endpoint configuration

## Troubleshooting 🛠️

If you encounter issues:

1. **Authentication Problems**
   ```bash
   make auth-fix
   ```

2. **Environment Issues**
   ```bash
   make fix-env
   ```

3. **Clean and Reinitialize**
   ```bash
   make tf-clean
   ```

## Available Make Commands 📝

| Command | Description |
|---------|-------------|
| `make setup` | Complete setup process |
| `make deploy-all` | Deploy all resources |
| `make format` | Format code |
| `make lint` | Run linters |
| `make tf-init` | Initialize Terraform |
| `make tf-plan` | Plan Terraform changes |
| `make tf-apply` | Apply Terraform changes |
| `make tf-destroy` | Destroy Terraform resources |
| `make clean` | Clean up local files |
| `make fix-env` | Fix environment issues |
| `make dev-setup` | Setup development environment |

For more detailed setup instructions, see [LOCAL_SETUP.md](LOCAL_SETUP.md).
