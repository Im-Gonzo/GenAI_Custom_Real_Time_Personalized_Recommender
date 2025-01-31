output "bucket_urls" {
  description = "URLs of the created buckets"
  value = {
    for name, bucket in google_storage_bucket.buckets :
    name => bucket.url
  }
}