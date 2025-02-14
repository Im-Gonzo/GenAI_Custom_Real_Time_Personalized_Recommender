variable "project_id" {
  description = "The ID of the GCP project"
  type        = string
}

variable "region" {
  description = "The region for Vertex AI resources"
  type        = string
}

variable "endpoint_id" {
  description = "Base ID for model endpoints"
  type        = string
  default     = "recsys"
}

variable "model_registry_repository" {
  description = "Full path to the Model Registry repository"
  type        = string
}

variable "enable_monitoring" {
  description = "Whether to enable model monitoring"
  type        = bool
  default     = false
}

variable "two_tower_model_id" {
  description = "ID of the two tower model to monitor"
  type        = string
  default     = ""
}

variable "two_tower_training_dataset_id" {
  description = "ID of the two tower training dataset for monitoring"
  type        = string
  default     = ""
}

variable "ranking_model_id" {
  description = "ID of the ranking model to monitor"
  type        = string
  default     = ""
}

variable "ranking_training_dataset_id" {
  description = "ID of the ranking training dataset for monitoring"
  type        = string
  default     = ""
}