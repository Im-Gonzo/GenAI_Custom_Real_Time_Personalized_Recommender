resource "google_vertex_ai_featurestore" "featurestore" {
  name        = var.feature_store_id
  project    = var.project_id
  region      = var.region
  labels      = var.labels
  
  online_serving_config {
    scaling {
      min_node_count = 1
      max_node_count = 2
    }
  }
}

# Entity Type: Customers
resource "google_vertex_ai_featurestore_entitytype" "customers" {
  name            = "customers"
  featurestore    = google_vertex_ai_featurestore.featurestore.id
  labels          = var.labels

  monitoring_config {
    snapshot_analysis {
      disabled = false
    }
  }
}

# Entity Type: Articles
resource "google_vertex_ai_featurestore_entitytype" "articles" {
  name            = "articles"
  featurestore = google_vertex_ai_featurestore.featurestore.id
  labels          = var.labels

  monitoring_config {
    snapshot_analysis {
      disabled = false
    }
  }
}

# Entity Type: Interactions
resource "google_vertex_ai_featurestore_entitytype" "interactions" {
  name            = "interactions"
  featurestore = google_vertex_ai_featurestore.featurestore.id
  labels          = var.labels

  monitoring_config {
    snapshot_analysis {
      disabled = false
    }
  }
}