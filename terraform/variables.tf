variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-west1"
}

variable "raw_bucket_name" {
  description = "Raw bucket name"
  type        = string
  default     = "lm-nebulapay-raw"
}

variable "processed_bucket_name" {
  description = "Processed bucket name"
  type        = string
  default     = "lm-nebulapay-processed"
}

variable "dataset_id" {
  description = "BigQuery dataset ID"
  type        = string
  default     = "analytics"
}

variable "table_id" {
  description = "BigQuery table ID"
  type        = string
  default     = "transactions"
}