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

variable "artifact_registry_id" {
  description = "ID for the Artifact Registry repository"
  type        = string
  default     = "recsys-models"
}

variable "artifact_registry_repository" {
  description = "Full path to the Artifact Registry repository"
  type        = string
}

variable "agent_id" {
  description = "ID for the Vertex AI Agent (Gemini)"
  type        = string
  default     = "llm-ranking-agent"
}

variable "enable_monitoring" {
  description = "Whether to enable model monitoring"
  type        = bool
  default     = false
}

variable "model_id" {
  description = "ID of the model to monitor"
  type        = string
  default     = ""
}

variable "training_dataset_id" {
  description = "ID of the training dataset for monitoring"
  type        = string
  default     = ""
}