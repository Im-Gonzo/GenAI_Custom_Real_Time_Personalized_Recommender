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

# Create a zero-byte object to represent the h-and-m folder
resource "google_storage_bucket_object" "h_and_m_folder" {
  name       = "h-and-m/"
  content    = " " # Empty content for folder
  bucket     = google_storage_bucket.buckets["gonzo-recsys-data"].name
  depends_on = [google_storage_bucket.buckets]
}