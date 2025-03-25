# Local Environment Setup Guide

## Prerequisites Installation

1. **Install Terraform**
   ```bash
   # For macOS using Homebrew
   brew tap hashicorp/tap
   brew install hashicorp/tap/terraform

   # Verify installation
   terraform --version
   ```

2. **Install Google Cloud SDK**
   ```bash
   # For macOS using Homebrew
   brew install --cask google-cloud-sdk

   # Verify installation
   gcloud --version
   ```

## GCP Project Setup

1. **Create New Project** (if not exists)
   ```bash
   # Create new project
   gcloud projects create recsys-dev --name="Recommender System Dev"

   # Set as default project
   gcloud config set project recsys-dev
   ```

2. **Enable Required APIs**
   ```bash
   # Enable APIs
   gcloud services enable cloudresourcemanager.googleapis.com
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable artifactregistry.googleapis.com
   gcloud services enable gemini.googleapis.com
   gcloud services enable iam.googleapis.com
   ```

3. **Create Service Account**
   ```bash
   # Create service account
   gcloud iam service-accounts create terraform-sa \
     --description="Service Account for Terraform" \
     --display-name="Terraform Service Account"

   # Grant necessary roles
   gcloud projects add-iam-policy-binding recsys-dev \
     --member="serviceAccount:terraform-sa@recsys-dev.iam.gserviceaccount.com" \
     --role="roles/owner"

   # Create and download key
   gcloud iam service-accounts keys create terraform-sa-key.json \
     --iam-account=terraform-sa@recsys-dev.iam.gserviceaccount.com
   ```

## Local Configuration

1. **Create Environment Variables**
   ```bash
   # Create .env file
   cat > .env << EOL
   # GCP Configuration
   export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/terraform-sa-key.json"
   export TF_VAR_project_id="recsys-dev"
   export TF_VAR_region="us-central1"
   export TF_VAR_zone="us-central1-a"

   # Feature Store Configuration
   export TF_VAR_feature_store_id="recsys-feature-store"
   export TF_VAR_feature_store_instance_id="recsys-feature-store-instance"

   # Model Configuration
   export TF_VAR_endpoint_id="recsys"
   export TF_VAR_agent_id="llm-ranking-agent"

   # Storage Configuration
   export TF_VAR_artifact_registry_id="recsys-models"
   export TF_VAR_gcs_data_bucket="recsys-data-dev"
   export TF_VAR_gcs_model_bucket="recsys-models-dev"
   export TF_VAR_gcs_artifact_bucket="recsys-artifacts-dev"
   EOL
   ```

2. **Setup Terraform Backend**
   ```bash
   # Create backend.tf
   cat > terraform/backend.tf << EOL
   terraform {
     backend "local" {
       path = "terraform.tfstate"
     }
   }
   EOL
   ```

## Usage Instructions

1. **Initial Setup**
   ```bash
   # Source environment variables
   source .env

   # Initialize Terraform
   make init
   ```

2. **Create Infrastructure**
   ```bash
   # Format and validate
   make format
   make validate

   # Plan changes
   make plan

   # Apply changes
   make apply
   ```

3. **Clean Up**
   ```bash
   # Destroy resources
   make destroy

   # Clean local files
   make clean
   ```

## Structure Check
```bash
tree -L 2
.
├── .env
├── LOCAL_SETUP.md
├── Makefile
├── README.md
├── terraform
│   ├── backend.tf
│   ├── main.tf
│   ├── modules/
│   ├── outputs.tf
│   ├── terraform.tfvars
│   └── variables.tf
└── terraform-sa-key.json
```

## Validation Steps

1. **Check GCP Connection**
   ```bash
   # Verify authentication
   gcloud auth list
   
   # Verify project
   gcloud config list project
   ```

2. **Verify Terraform Setup**
   ```bash
   # Check Terraform configuration
   terraform -chdir=terraform init -backend=false
   ```

3. **Validate GCP Permissions**
   ```bash
   # List available services
   gcloud services list --available
   
   # Check service account permissions
   gcloud projects get-iam-policy recsys-dev \
     --flatten="bindings[].members" \
     --format='table(bindings.role)' \
     --filter="bindings.members:terraform-sa"
   ```

## Common Issues

1. **API Not Enabled**
   ```bash
   # Enable missing API
   gcloud services enable [API_NAME].googleapis.com
   ```

2. **Permission Issues**
   - Verify service account roles
   - Check key file path
   - Ensure environment variables are set

3. **Resource Name Conflicts**
   - Ensure globally unique names for:
     - GCS buckets
     - Feature store instances
     - Endpoints