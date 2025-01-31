output "feature_store_id" {
  description = "ID of the created Feature Store"
  value       = module.feature_store.feature_store_id
}

output "storage_bucket_urls" {
  description = "URLs of the created storage buckets"
  value       = module.storage.bucket_urls
}

output "feature_store_sa_email" {
  description = "Email of the Feature Store service account"
  value       = module.iam.feature_store_sa_email
}