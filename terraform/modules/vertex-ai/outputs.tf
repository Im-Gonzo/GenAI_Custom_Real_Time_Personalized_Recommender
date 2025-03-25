# output "query_model_endpoint_id" {
#   description = "ID of the query model endpoint"
#   value       = google_vertex_ai_endpoint.query_model_endpoint.name
# }

# output "candidate_model_endpoint_id" {
#   description = "ID of the candidate model endpoint"
#   value       = google_vertex_ai_endpoint.candidate_model_endpoint.name
# }

output "rankings_model_endpoint_id" {
  description = "ID of the candidate model endpoint"
  value       = google_vertex_ai_endpoint.rankings_model_endpoint.name
}

# output "monitoring_job_id" {
#   description = "ID of the monitoring job, if enabled"
#   value       = var.enable_monitoring ? google_vertex_ai_model_deployment_monitoring_job.monitoring[0].name : null
# }