# Enable required APIs
resource "google_project_service" "vertex_ai" {
  project = var.project_id
  service = "aiplatform.googleapis.com"
  disable_dependent_services = true
}

resource "google_project_service" "compute" {
  project = var.project_id
  service = "compute.googleapis.com"
  disable_dependent_services = true
}

# Enable Gemini API
resource "google_project_service" "gemini" {
  project = var.project_id
  service = "gemini.googleapis.com"
  disable_dependent_services = true
}

# Model Registry - For recommendation models
resource "google_vertex_ai_model" "two_tower_model" {
  project = var.project_id
  location = var.region
  display_name = "two-tower-model"
  description = "Two Tower Model for candidate generation"
  container_spec {
    image_uri = "${var.artifact_registry_repository}/two-tower:latest"
    command = []
    args    = []
  }
}

resource "google_vertex_ai_model" "ranking_model" {
  project = var.project_id
  location = var.region
  display_name = "ranking-model"
  description = "Ranking Model for candidate scoring"
  container_spec {
    image_uri = "${var.artifact_registry_repository}/ranking:latest"
    command = []
    args    = []
  }
}

# Vertex AI Agent for LLM Ranking
resource "google_vertex_ai_agent" "llm_ranking_agent" {
  name         = var.agent_id
  display_name = "LLM Ranking Agent"
  description  = "Gemini-based agent for LLM ranking"
  location     = var.region
  
  agent_config {
    agent_generation_config {
      agent_version = "0.1"
      base_model = "gemini-pro"
      use_system_prompts = true
      allow_custom_prompt = true
      model_parameters = {
        temperature     = 0.2
        top_p          = 0.8
        top_k          = 40
        candidate_count = 1
      }
    }
  }

  depends_on = [google_project_service.gemini]
}

# Model Endpoints
resource "google_vertex_ai_endpoint" "two_tower_endpoint" {
  name        = "${var.endpoint_id}-two-tower"
  display_name = "${var.endpoint_id}-two-tower"
  location    = var.region
  project     = var.project_id
  description = "Endpoint for Two Tower Model"

  network = "projects/${var.project_id}/global/networks/default"
  depends_on = [google_project_service.vertex_ai]
}

resource "google_vertex_ai_endpoint" "ranking_endpoint" {
  name        = "${var.endpoint_id}-ranking"
  display_name = "${var.endpoint_id}-ranking"
  location    = var.region
  project     = var.project_id
  description = "Endpoint for Ranking Model"

  network = "projects/${var.project_id}/global/networks/default"
  depends_on = [google_project_service.vertex_ai]
}

# Model Deployment Monitoring (optional)
resource "google_vertex_ai_model_deployment_monitoring_job" "monitoring" {
  count = var.enable_monitoring ? 1 : 0
  
  display_name = "${var.endpoint_id}-monitoring"
  location     = var.region
  project      = var.project_id

  model_deployment_monitoring_job_config {
    endpoint_id = google_vertex_ai_endpoint.ranking_endpoint.name

    model_deployment_monitoring_objective_configs {
      deployed_model_id = var.model_id
      objective_config {
        training_dataset {
          dataset_id = var.training_dataset_id
        }
        training_prediction_skew_detection_config {
          skew_thresholds {
            value = 0.1
          }
        }
      }
    }

    model_deployment_monitoring_schedule_config {
      monitor_interval = "3600s"
    }
  }
}

# Create an Artifact Registry repository for model containers
resource "google_artifact_registry_repository" "model_registry" {
  provider = google-beta
  project  = var.project_id
  location = var.region
  
  repository_id = var.artifact_registry_id
  description   = "Repository for recommender system model containers"
  format        = "DOCKER"
}