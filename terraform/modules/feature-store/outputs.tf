output "feature_store_id" {
  description = "ID of the created feature store"
  value       = google_vertex_ai_feature_online_store.featurestore.name
}

output "customer_entitytype_id" {
  description = "ID of the customers entity type"
  value       = google_vertex_ai_feature_online_store_featureview.customers.name
}

output "articles_entitytype_id" {
  description = "ID of the articles entity type"
  value       = google_vertex_ai_feature_online_store_featureview.articles.name
}

output "interactions_entitytype_id" {
  description = "ID of the interactions entity type"
  value       = google_vertex_ai_feature_online_store_featureview.interactions.name
}