locals {
  customers_schema    = file("${path.module}/schemas/customers_schema.json")
  articles_schema     = file("${path.module}/schemas/articles_schema.json")
  interactions_schema = file("${path.module}/schemas/interactions_schema.json")
  transactions_schema = file("${path.module}/schemas/transactions_schema.json")
  rankings_schema     = file("${path.module}/schemas/rankings_schema.json")
  candidates_schema   = file("${path.module}/schemas/candidates_schema.json")
}

resource "google_project_service" "vertex_ai" {
  project                    = var.project_id
  service                    = "aiplatform.googleapis.com"
  disable_dependent_services = true
}

###############
## BigQuery ##
##############

resource "google_bigquery_dataset" "featurestore_dataset" {
  project     = var.project_id
  dataset_id  = var.dataset_id
  description = "The BigQuery dataset that stores the features of RecSys FeatureStore"
  location    = var.region
}

resource "google_bigquery_table" "recsys_featurestore_customers" {
  project             = var.project_id
  deletion_protection = false
  dataset_id          = google_bigquery_dataset.featurestore_dataset.dataset_id
  table_id            = "recsys_customers"
  schema              = local.customers_schema
  clustering          = ["customer_id"]

  depends_on = [google_bigquery_dataset.featurestore_dataset]
}

resource "google_bigquery_table" "recsys_featurestore_articles" {
  project             = var.project_id
  deletion_protection = false
  dataset_id          = google_bigquery_dataset.featurestore_dataset.dataset_id
  table_id            = "recsys_articles"
  schema              = local.articles_schema
  clustering          = ["article_id"]

  depends_on = [google_bigquery_dataset.featurestore_dataset]
}

resource "google_bigquery_table" "recsys_featurestore_interactions" {
  project             = var.project_id
  deletion_protection = false
  dataset_id          = google_bigquery_dataset.featurestore_dataset.dataset_id
  table_id            = "recsys_interactions"
  schema              = local.interactions_schema
  clustering          = ["customer_id", "article_id"]

  depends_on = [google_bigquery_dataset.featurestore_dataset]
}

resource "google_bigquery_table" "recsys_featurestore_transactions" {
  project             = var.project_id
  deletion_protection = false
  dataset_id          = google_bigquery_dataset.featurestore_dataset.dataset_id
  table_id            = "recsys_transactions"
  schema              = local.transactions_schema
  clustering          = ["customer_id"]

  depends_on = [google_bigquery_dataset.featurestore_dataset]
}

resource "google_bigquery_table" "recsys_featurestore_rankings" {
  project             = var.project_id
  deletion_protection = false
  dataset_id          = google_bigquery_dataset.featurestore_dataset.dataset_id
  table_id            = "recsys_rankings"
  schema              = local.rankings_schema
  clustering          = ["customer_id", "article_id"]

  depends_on = [google_bigquery_dataset.featurestore_dataset]
}

resource "google_bigquery_table" "recsys_featurestore_candidates" {
  project             = var.project_id
  deletion_protection = false
  dataset_id          = google_bigquery_dataset.featurestore_dataset.dataset_id
  table_id            = "recsys_candidates"
  schema              = local.candidates_schema

  depends_on = [google_bigquery_dataset.featurestore_dataset]
}

##########################
## Feature Online Store ##
##########################

resource "google_vertex_ai_feature_online_store" "featurestore" {
  name          = var.feature_store_id
  project       = var.project_id
  region        = var.region
  labels        = var.labels
  force_destroy = false

  bigtable {
    auto_scaling {
      min_node_count         = 1
      max_node_count         = 2
      cpu_utilization_target = 50
    }
  }

  depends_on = [ google_project_service.vertex_ai ]
}


resource "google_vertex_ai_feature_online_store_featureview" "customers" {
  name                 = "customers"
  project              = var.project_id
  region               = var.region
  feature_online_store = google_vertex_ai_feature_online_store.featurestore.name
  labels               = var.labels

  sync_config {
    cron = "0 0 * * *"
  }

  big_query_source {
    uri               = "bq://${var.project_id}.${google_bigquery_dataset.featurestore_dataset.dataset_id}.${google_bigquery_table.recsys_featurestore_customers.table_id}"
    entity_id_columns = ["customer_id"]
  }
}


resource "google_vertex_ai_feature_online_store_featureview" "articles" {
  name                 = "articles"
  project              = var.project_id
  region               = var.region
  feature_online_store = google_vertex_ai_feature_online_store.featurestore.name
  labels               = var.labels

  sync_config {
    cron = "0 0 * * *"
  }

  big_query_source {
    uri               = "bq://${var.project_id}.${google_bigquery_dataset.featurestore_dataset.dataset_id}.${google_bigquery_table.recsys_featurestore_articles.table_id}"
    entity_id_columns = ["article_id"]
  }

}


resource "google_vertex_ai_feature_online_store_featureview" "interactions" {
  name                 = "interactions"
  project              = var.project_id
  region               = var.region
  feature_online_store = google_vertex_ai_feature_online_store.featurestore.name
  labels               = var.labels

  sync_config {
    cron = "0 0 * * *"
  }

  big_query_source {
    uri               = "bq://${var.project_id}.${google_bigquery_dataset.featurestore_dataset.dataset_id}.${google_bigquery_table.recsys_featurestore_interactions.table_id}"
    entity_id_columns = ["customer_id", "article_id"]
  }
}

resource "google_vertex_ai_feature_online_store_featureview" "transactions" {
  name                 = "transactions"
  project              = var.project_id
  region               = var.region
  feature_online_store = google_vertex_ai_feature_online_store.featurestore.name
  labels               = var.labels

  sync_config {
    cron = "0 0 * * *"
  }

  big_query_source {
    uri               = "bq://${var.project_id}.${google_bigquery_dataset.featurestore_dataset.dataset_id}.${google_bigquery_table.recsys_featurestore_transactions.table_id}"
    entity_id_columns = ["customer_id"]
  }
}

resource "google_vertex_ai_feature_online_store_featureview" "rankings" {
  name                 = "rankings"
  project              = var.project_id
  region               = var.region
  feature_online_store = google_vertex_ai_feature_online_store.featurestore.name
  labels               = var.labels

  sync_config {
    cron = "0 0 * * *"
  }

  big_query_source {
    uri               = "bq://${var.project_id}.${google_bigquery_dataset.featurestore_dataset.dataset_id}.${google_bigquery_table.recsys_featurestore_rankings.table_id}"
    entity_id_columns = ["customer_id", "article_id"]
  }
}

resource "google_vertex_ai_feature_online_store_featureview" "candidates" {
  name                 = "candidates"
  project              = var.project_id
  region               = var.region
  feature_online_store = google_vertex_ai_feature_online_store.featurestore.name
  labels               = var.labels

  sync_config {
    cron = "0 0 * * *"
  }

  big_query_source {
    uri               = "bq://${var.project_id}.${google_bigquery_dataset.featurestore_dataset.dataset_id}.${google_bigquery_table.recsys_featurestore_candidates.table_id}"
    entity_id_columns = ["article_id"]
  }
}