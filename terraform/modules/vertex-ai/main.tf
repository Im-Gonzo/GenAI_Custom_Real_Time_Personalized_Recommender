# Enable required APIs
resource "google_project_service" "vertex_ai" {
  project                    = var.project_id
  service                    = "aiplatform.googleapis.com"
  disable_dependent_services = true
}

resource "google_project_service" "compute" {
  project                    = var.project_id
  service                    = "compute.googleapis.com"
  disable_dependent_services = true
}

# Model Endpoints
resource "google_vertex_ai_endpoint" "query_model_endpoint" {
  name         = "${var.endpoint_id}-query-model"
  display_name = "${var.endpoint_id}-query-model"
  location     = var.region
  project      = var.project_id
  description  = "Endpoint for Query Model"

  depends_on = [google_project_service.vertex_ai]
}

resource "google_vertex_ai_endpoint" "candidate_model_endpoint" {
  name         = "${var.endpoint_id}-candidate-model"
  display_name = "${var.endpoint_id}-candidate-model"
  location     = var.region
  project      = var.project_id
  description  = "Endpoint for Candidate Model"

  depends_on = [google_project_service.vertex_ai]
}

# Create an Artifact Registry repository for model containers
resource "google_artifact_registry_repository" "model_registry" {
  provider = google-beta
  project  = var.project_id
  location = var.region

  repository_id = var.model_registry_repository
  description   = "Repository for recommender system model containers"
  format        = "DOCKER"
}