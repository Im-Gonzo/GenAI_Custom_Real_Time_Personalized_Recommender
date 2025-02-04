locals {
  customers_schema    = file("${path.module}/schemas/customers_schema.json")
  articles_schema    = file("${path.module}/schemas/articles_schema.json")
  interactions_schema = file("${path.module}/schemas/interactions_schema.json")
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
  dataset_id         = google_bigquery_dataset.featurestore_dataset.dataset_id
  table_id           = "recsys_customers"
  schema             = local.customers_schema

  depends_on = [google_bigquery_dataset.featurestore_dataset]
}

resource "google_bigquery_table" "recsys_featurestore_articles" {
  project             = var.project_id
  deletion_protection = false
  dataset_id         = google_bigquery_dataset.featurestore_dataset.dataset_id
  table_id           = "recsys_articles"
  schema             = local.articles_schema

  depends_on = [google_bigquery_dataset.featurestore_dataset]
}

resource "google_bigquery_table" "recsys_featurestore_interactions" {
  project             = var.project_id
  deletion_protection = false
  dataset_id         = google_bigquery_dataset.featurestore_dataset.dataset_id
  table_id           = "recsys_interactions"
  schema             = local.interactions_schema

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

  optimized {}
}


resource "google_vertex_ai_feature_online_store_featureview" "customers" {
  name                  = "customers"
  project               = var.project_id
  region                = var.region
  feature_online_store  = google_vertex_ai_feature_online_store.featurestore.name
  labels                = var.labels

  sync_config {
    cron = "0 0 * * *"
  }

  big_query_source {
    uri = "bq://${var.project_id}.${google_bigquery_dataset.featurestore_dataset.dataset_id}.${google_bigquery_table.recsys_featurestore_customers.table_id}"
    entity_id_columns = ["customer_id"]
  }
}


resource "google_vertex_ai_feature_online_store_featureview" "articles" {
  name                  = "articles"
  project               = var.project_id
  region                = var.region
  feature_online_store  = google_vertex_ai_feature_online_store.featurestore.name
  labels                = var.labels

  sync_config {
    cron = "0 0 * * *"
  }

  big_query_source {
    uri = "bq://${var.project_id}.${google_bigquery_dataset.featurestore_dataset.dataset_id}.${google_bigquery_table.recsys_featurestore_articles.table_id}"
    entity_id_columns = ["article_id"]
  }

}


resource "google_vertex_ai_feature_online_store_featureview" "interactions" {
  name                  = "interactions"
  project               = var.project_id
  region                = var.region
  feature_online_store  = google_vertex_ai_feature_online_store.featurestore.name
  labels                = var.labels

  sync_config {
    cron = "0 0 * * *"
  }

  big_query_source {
    uri = "bq://${var.project_id}.${google_bigquery_dataset.featurestore_dataset.dataset_id}.${google_bigquery_table.recsys_featurestore_interactions.table_id}"
    entity_id_columns = ["customer_id", "article_id"]
  }
}