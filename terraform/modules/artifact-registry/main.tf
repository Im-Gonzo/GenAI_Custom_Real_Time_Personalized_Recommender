# Enable required APIs
resource "google_project_service" "artifact_registry" {
  project                    = var.project_id
  service                    = "artifactregistry.googleapis.com"
  disable_dependent_services = true
}

resource "google_artifact_registry_repository" "recsys-artifact-registry-repo" {
  project       = var.project_id
  location      = var.region
  repository_id = var.artifact_registry_repository
  description   = "Artifact Registry Docker Repository for Recsys Project"
  format        = "DOCKER"

  depends_on = [google_project_service.artifact_registry]
}

# data "google_artifact_registry_docker_image" "recsys-ranking-image" {
#   location      = google_artifact_registry_repository.recsys-artifact-registry-repo.location
#   repository_id = google_artifact_registry_repository.recsys-artifact-registry-repo.repository_id
#   image_name    = var.artifact_registry_ranking_image
# }