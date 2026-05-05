output "raw_bucket_name" {
  value = google_storage_bucket.raw.name
}

output "processed_bucket_name" {
  value = google_storage_bucket.processed.name
}

output "airflow_service_account_email" {
  value = google_service_account.airflow.email
}

output "analyst_service_account_email" {
  value = google_service_account.analyst.email
}

output "bigquery_dataset_id" {
  value = google_bigquery_dataset.analytics.dataset_id
}

output "bigquery_table_id" {
  value = google_bigquery_table.transactions.table_id
}