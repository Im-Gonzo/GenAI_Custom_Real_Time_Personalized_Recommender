variable "project_id" {
  description = "The ID of the GCP project"
  type        = string
}

variable "region" {
  description = "The region for Vertex AI resources"
  type        = string
}

variable "artifact_registry_repository" {
  description = "Full path to the Artifact Registry repository"
  type        = string
}

variable "artifact_registry_ranking_image" {
  description = "The Artifact Image URI"
  type        = string
}