variable "project_id" {
  description = "The ID of the GCP project"
  type        = string
  default     = "recsys-dev-gonzo-2"
}

variable "region" {
  description = "The region for GCP resources"
  type        = string
  default     = "us-central1"
}

variable "feature_store_id" {
  description = "ID for the Vertex AI Feature Store"
  type        = string
  default     = "recsys_feature_store_dev"
}

variable "dataset_id" {
  description = "The ID of the BigQuery Dataset"
  type        = string
  default     = "recsys_dataset"
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
      name          = "gonzo-recsys-data"
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

variable "model_registry_repository" {
  description = "The ID of the Model Registry"
  type        = string
  default     = "recsys-model-registry"
}