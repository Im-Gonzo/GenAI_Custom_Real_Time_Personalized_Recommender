resource "google_storage_bucket" "buckets" {
  for_each = var.buckets

  name          = each.value.name
  location      = each.value.location
  storage_class = each.value.storage_class
  project       = var.project_id

  uniform_bucket_level_access = true
  force_destroy               = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
}