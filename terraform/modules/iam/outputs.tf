output "feature_store_sa_email" {
  description = "Email of the Feature Store service account"
  value       = google_service_account.feature_store_sa.email
}

output "feature_store_sa_name" {
  description = "Name of the Feature Store service account"
  value       = google_service_account.feature_store_sa.name
}