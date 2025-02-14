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
resource "google_vertex_ai_endpoint" "two_tower_endpoint" {
  name         = "${var.endpoint_id}-two-tower"
  display_name = "${var.endpoint_id}-two-tower"
  location     = var.region
  project      = var.project_id
  description  = "Endpoint for Two Tower Model"

  # network    = "projects/${data.google_project.project.number}/global/networks/default"
  depends_on = [google_project_service.vertex_ai]
}

resource "google_vertex_ai_endpoint" "ranking_endpoint" {
  name         = "${var.endpoint_id}-ranking"
  display_name = "${var.endpoint_id}-ranking"
  location     = var.region
  project      = var.project_id
  description  = "Endpoint for Ranking Model"

  # network    = "projects/${data.google_project.project.number}/global/networks/default"
  depends_on = [google_project_service.vertex_ai]
}

# # Model Deployment Monitoring
# resource "google_vertex_ai_model_deployment_monitoring_job" "two_tower_monitoring" {
#   count = var.enable_monitoring ? 1 : 0

#   display_name = "${var.endpoint_id}-two-tower-monitoring"
#   location     = var.region
#   project      = var.project_id

#   model_deployment_monitoring_job_config {
#     endpoint_id = google_vertex_ai_endpoint.two_tower_endpoint.name

#     model_deployment_monitoring_objective_configs {
#       deployed_model_id = var.two_tower_model_id
#       objective_config {
#         training_dataset {
#           dataset_id = var.two_tower_training_dataset_id
#         }
#         training_prediction_skew_detection_config {
#           skew_thresholds {
#             value = 0.1
#           }
#         }
#       }
#     }

#     model_deployment_monitoring_schedule_config {
#       monitor_interval = "3600s"
#     }
#   }
# }

# resource "google_vertex_ai_model_deployment_monitoring_job" "ranking_monitoring" {
#   count = var.enable_monitoring ? 1 : 0

#   display_name = "${var.endpoint_id}-ranking-monitoring"
#   location     = var.region
#   project      = var.project_id

#   model_deployment_monitoring_job_config {
#     endpoint_id = google_vertex_ai_endpoint.ranking_endpoint.name

#     model_deployment_monitoring_objective_configs {
#       deployed_model_id = var.ranking_model_id
#       objective_config {
#         training_dataset {
#           dataset_id = var.ranking_training_dataset_id
#         }
#         training_prediction_skew_detection_config {
#           skew_thresholds {
#             value = 0.1
#           }
#         }
#       }
#     }

#     model_deployment_monitoring_schedule_config {
#       monitor_interval = "3600s"
#     }
#   }
# }

# Create an Artifact Registry repository for model containers
resource "google_artifact_registry_repository" "model_registry" {
  provider = google-beta
  project  = var.project_id
  location = var.region

  repository_id = var.model_registry_repository
  description   = "Repository for recommender system model containers"
  format        = "DOCKER"
}