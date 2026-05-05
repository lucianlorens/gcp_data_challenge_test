# IAM Design

## SA: lm-airflow-runner

### GCS
- roles/storage.objectViewer (raw bucket)
  → Required to read incoming files

- roles/storage.objectCreator (processed bucket)
  → Required to write transformed + success files

### BigQuery
- roles/bigquery.jobUser
  → Required to run load jobs

- roles/bigquery.dataEditor (dataset-level)
  → Required to append data

---

## SA: lm-analyst-viewer

### BigQuery
- roles/bigquery.dataViewer (dataset-level)
  → Read-only access for analytics

### No GCS access
→ Prevents access to raw/processed data

---

## Design Principles

- No project-level roles used
- Access scoped to:
  - specific buckets
  - specific dataset
- Prevents lateral movement and data exposure