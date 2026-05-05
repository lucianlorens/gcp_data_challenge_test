resource "google_storage_bucket" "raw" {
  name     = "lm-nebulapay-raw"
  location = "EU"

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
}

resource "google_storage_bucket" "processed" {
  name     = "lm-nebulapay-processed"
  location = "EU"

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
}

resource "google_service_account" "airflow" {
  account_id   = "lm-airflow-runner"
  display_name = "Airflow Runner"
}

resource "google_service_account" "analyst" {
  account_id   = "lm-analyst-viewer"
  display_name = "Analyst Viewer"
}

resource "google_bigquery_dataset" "analytics" {
  dataset_id = "analytics"
  location   = "EU"
}

resource "google_bigquery_table" "transactions" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "transactions"

  schema = file("${path.module}/../bigquery/schema.json")

  time_partitioning {
    type  = "DAY"
    field = "transaction_ts"
  }

  clustering = ["user_id"]
}