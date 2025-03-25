variable "project_id" {
  description = "The ID of the GCP project"
  type        = string
  default     = "recsys-dev-gonzo-1" # PROJECT_ID
}

variable "region" {
  description = "The region for GCP resources"
  type        = string
  default     = "us-central1" # REGION
}

variable "feature_store_id" {
  description = "ID for the Vertex AI Feature Store"
  type        = string
  default     = "recsys_dev_feature_store" # VERTEX_FEATURE_STORE_ID
}

variable "dataset_id" {
  description = "The ID of the BigQuery Dataset"
  type        = string
  default     = "recsys_dev_retail_dataset" # BIGQUERY_DATASET_ID
}

variable "storage_buckets" {
  description = "Map of storage buckets to create"
  type = map(object({
    name          = string
    location      = string
    storage_class = string
  }))
  default = {
    data = {
      name          = "recsys-dev-data" # GCS_DATA_BUCKET
      location      = "US"
      storage_class = "STANDARD"
    }
    models = {
      name          = "gonzo-recsys-models"
      location      = "US"
      storage_class = "STANDARD"
    }
    artifacts = {
      name          = "gonzo-recsys-artifacts"
      location      = "US"
      storage_class = "STANDARD"
    }
  }
}

variable "feature_store_service_account" {
  description = "Service account for Feature Store operations"
  type        = string
  default     = "feature-store-sa"
}

#####################
# Artifact Registry #
#####################

variable "artifact_registry_repository" {
  description = "The ID of the Artifact Registry"
  type        = string
  default     = "recsys-dev-artifact-registry" # GCP_ARTIFACT_REGISTRY
}

variable "artifact_registry_ranking_image" {
  description = "The Artifact Image URI"
  type        = string
  default     = "recsys-ranking-predictor:latest"
}