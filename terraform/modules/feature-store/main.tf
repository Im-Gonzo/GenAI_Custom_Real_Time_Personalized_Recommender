resource "google_vertex_ai_feature_online_store" "featurestore" {
  name          = var.feature_store_id
  project       = var.project_id
  region        = var.region
  labels        = var.labels
  force_destroy = false

  optimized {}
}

# Entity Type: Customers
resource "google_vertex_ai_featurestore_entitytype" "customers" {
  name          = "customers"
  featurestore = google_vertex_ai_feature_online_store.featurestore.id
  labels        = var.labels

  monitoring_config {
    snapshot_analysis {
      disabled = false
    }
  }
}

# Entity Type: Articles
resource "google_vertex_ai_featurestore_entitytype" "articles" {
  name          = "articles"
  featurestore = google_vertex_ai_feature_online_store.featurestore.id
  labels        = var.labels

  monitoring_config {
    snapshot_analysis {
      disabled = false
    }
  }
}

# Entity Type: Interactions
resource "google_vertex_ai_featurestore_entitytype" "interactions" {
  name          = "interactions"
  featurestore = google_vertex_ai_feature_online_store.featurestore.id
  labels        = var.labels

  monitoring_config {
    snapshot_analysis {
      disabled = false
    }
  }
}