# output "two_tower_model_id" {
#   description = "ID of the two tower model"
#   value       = google_vertex_ai_model.two_tower_model.name
# }

# output "ranking_model_id" {
#   description = "ID of the ranking model"
#   value       = google_vertex_ai_model.ranking_model.name
# }

# output "llm_ranking_agent_id" {
#   description = "ID of the Vertex AI Agent for LLM ranking"
#   value       = google_vertex_ai_agent.llm_ranking_agent.name
# }

# output "two_tower_endpoint_id" {
#   description = "ID of the two tower endpoint"
#   value       = google_vertex_ai_endpoint.two_tower_endpoint.name
# }

# output "ranking_endpoint_id" {
#   description = "ID of the ranking endpoint"
#   value       = google_vertex_ai_endpoint.ranking_endpoint.name
# }

output "model_registry_repository" {
  description = "URL of the Artifact Registry repository"
  value       = google_artifact_registry_repository.model_registry.name
}

# output "monitoring_job_id" {
#   description = "ID of the monitoring job, if enabled"
#   value       = var.enable_monitoring ? google_vertex_ai_model_deployment_monitoring_job.monitoring[0].name : null
# }