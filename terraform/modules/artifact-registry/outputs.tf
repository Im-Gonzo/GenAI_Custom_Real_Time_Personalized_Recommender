output "artifact_registry_id" {
  description = "ID of the Artifact Registry"
  value       = google_artifact_registry_repository.recsys-artifact-registry-repo.id
}
