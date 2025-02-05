terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.18.1"
    }
  }

  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Feature Store Module
module "feature_store" {
  source = "./modules/feature-store"

  project_id       = var.project_id
  region           = var.region
  feature_store_id = var.feature_store_id
  dataset_id       = var.dataset_id
}

# Vertex AI Module
# module "vertex_ai" {
#   source = "./modules/vertex-ai"

#   project_id = var.project_id
#   region     = var.region
# }

# Storage Module
module "storage" {
  source = "./modules/storage"

  project_id = var.project_id
  region     = var.region
  buckets    = var.storage_buckets
}

# IAM Module
module "iam" {
  source = "./modules/iam"

  project_id                    = var.project_id
  feature_store_service_account = var.feature_store_service_account
}