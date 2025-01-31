resource "google_service_account" "feature_store_sa" {
  account_id   = var.feature_store_service_account
  display_name = "Feature Store Service Account"
  project      = var.project_id
}

resource "google_project_iam_member" "feature_store_roles" {
  for_each = toset([
    "roles/aiplatform.user",
    "roles/aiplatform.featureStoreAdmin",
    "roles/storage.objectViewer"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.feature_store_sa.email}"
}

# Allow service account to be impersonated by CI/CD
resource "google_service_account_iam_binding" "workload_identity_user" {
  service_account_id = google_service_account.feature_store_sa.name
  role               = "roles/iam.workloadIdentityUser"
  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[default/github-actions]",
  ]
}