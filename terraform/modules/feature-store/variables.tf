variable "project_id" {
  description = "The ID of the GCP project"
  type        = string
}

variable "region" {
  description = "The region for the feature store"
  type        = string
}

variable "feature_store_id" {
  description = "ID for the feature store"
  type        = string
}

variable "labels" {
  description = "Labels to apply to the feature store"
  type        = map(string)
  default     = {}
}

variable "dataset_id" {
  description = "The ID of the BigQuery Dataset"
  type        = string
}