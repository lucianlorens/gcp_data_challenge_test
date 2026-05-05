# gcp_data_challenge_test
# LumenMart – NebulaPay Data Pipeline (GCP)

Secure, automated data pipeline that ingests daily transaction files from GCS, validates and transforms them via Airflow (Cloud Composer), and loads clean data into BigQuery with strict least-privilege IAM controls.
Designed for reproducibility using Terraform and production-ready operational practices.
Focus: data quality, security, and idempotent processing.

---

### Prerequisites

* Google Cloud Project with billing enabled
* Terraform ≥ 1.5
* Python ≥ 3.9
* Google Cloud SDK (`gcloud`)
* Access to enable APIs:

  * Cloud Composer
  * BigQuery
  * Cloud Storage
  * IAM
* (Optional) Docker for local Airflow testing (TBD)

---

**Flow Overview:**

1. NebulaPay drops CSV file into:

   ```
   gs://lm-nebulapay-raw/transactions/date=YYYY-MM-DD/transactions.csv
   ```

2. Airflow DAG:

   * Waits for file (sensor)
   * Validates schema & business rules
   * Transforms data (currency → EUR, adds metadata)
   * Loads into BigQuery
   * Quarantines invalid data

3. Output:

   * Clean data → processed bucket
   * Invalid data → raw/invalid/
   * `_SUCCESS` marker ensures idempotency

---

## Getting Started

:construction: [work_in_progress] :construction:

1. Clone repository:

   ```
   git clone <repo_url>
   cd lumenmart-gcp-pipeline
   ```

2. Initialize Terraform:

   ```
   terraform init
   ```

3. Plan infrastructure:

   ```
   terraform plan
   ```

4. Apply infrastructure:

   ```
   terraform apply
   ```

5. Upload DAG to Composer (if not automated):

   ```
   gcloud composer environments storage dags import \
     --environment <env-name> \
     --location <region> \
     --source dags/lm_nebulapay_transactions_daily.py
   ```

6. Upload sample file:

   ```
   gsutil cp transactions.csv \
   gs://lm-nebulapay-raw/transactions/date=YYYY-MM-DD/
   ```

---

### Installing

* Terraform: https://developer.hashicorp.com/terraform/downloads
* Google Cloud SDK: https://cloud.google.com/sdk/docs/install
* Python: https://www.python.org/downloads/

---

### Running the tests

Basic validation can be done by:

1. Uploading valid and invalid CSV files
2. Triggering DAG manually
3. Observing:

   * DAG success/failure states
   * BigQuery table updates
   * GCS folder outputs

---

### Break down into end to end tests

:construction: [work_in_progress] :construction:

**Test Case 1 — Valid File**

* Input: correct schema + values
* Expected:

  * Data loaded into BigQuery
  * `_SUCCESS` file created
  * Clean file in processed bucket

**Test Case 2 — Invalid File**

* Input: negative amount or missing fields
* Expected:

  * File moved to `invalid/`
  * DAG fails or stops
  * No BigQuery load

---

### And coding style tests

* Python formatted with `black`
* Linting via `flake8`
* Terraform validated using:

  ```
  terraform validate
  ```

---

### Deployment

CI/CD can be implemented using GitHub Actions or Cloud Build:

Pipeline stages:

1. `terraform fmt + validate`
2. `terraform plan`
3. Manual approval
4. `terraform apply`
5. DAG deployment to Composer

---

## Built With

* Terraform – Infrastructure provisioning
* Google Cloud Composer – Workflow orchestration
* BigQuery – Analytics storage
* Cloud Storage – Data lake
* Apache Airflow – DAG execution

---

## IAM Design (Least Privilege)

### Service Accounts

**lm-airflow-runner**

* Storage:

  * Read raw bucket
  * Write processed bucket
* BigQuery:

  * Run load jobs
  * Append to dataset

**lm-analyst-viewer**

* Read-only access to BigQuery dataset
* No GCS access

### Design Principles

* No project-wide roles
* Bucket-level permissions for storage
* Dataset-level permissions for BigQuery
* Strict separation of responsibilities

---

## Incident Drill (Operational Readiness)

### 1. Prevent Duplicate Loads

* Use `_SUCCESS` markers to track processed partitions
* Implement deduplication using `transaction_id`
* Optionally use staging tables + `MERGE` into final table

---

### 2. Reprocess a Single Day

Steps:

1. Delete affected partition:

   ```sql
   DELETE FROM analytics.transactions
   WHERE DATE(transaction_ts) = 'YYYY-MM-DD';
   ```
2. Remove `_SUCCESS` marker
3. Re-run DAG for that execution date

---

### 3. Schema Evolution

* Add new fields as nullable
* Use BigQuery schema update options (`ALLOW_FIELD_ADDITION`)
* Introduce versioned tables for breaking changes
* Maintain upstream data contracts

---

## Contributing

The structure for commits messages are:

{{Emoji}} {{feat/ , fix/ or debug/}} {{issue identifier}} {{"commit message"}}

* The pattern for commits are used with Gitmoji by Carlos Cuesta:
  https://gitmoji.dev/

---

### Versioning

Semantic Versioning (SemVer) recommended:

* MAJOR – breaking changes
* MINOR – new features
* PATCH – fixes

---

### Branches

* Production: **main**
* Development: **dev**

---

### Commit Pattern:

Using https://gitmoji.dev/ emoji pattern to easily identify commit intent

---

## Authors

* **Lucian Lorens** - *Initial work* - [lucianlorens](https://github.com/lucianlorens)

---

## License

MIT License

