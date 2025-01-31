variable "project_id" {
  description = "The ID of the GCP project"
  type        = string
}

variable "region" {
  description = "The region for the buckets"
  type        = string
}

variable "buckets" {
  description = "Map of storage buckets to create"
  type = map(object({
    name          = string
    location      = string
    storage_class = string
  }))
}