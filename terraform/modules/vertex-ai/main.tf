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

resource "google_vertex_ai_endpoint" "rankings_model_endpoint" {
  name         = "${var.endpoint_id}-rankings-model"
  display_name = "${var.endpoint_id}-rankings-model"
  location     = var.region
  project      = var.project_id
  description  = "Endpoint for Ranking Model"

  depends_on = [google_project_service.vertex_ai]
}