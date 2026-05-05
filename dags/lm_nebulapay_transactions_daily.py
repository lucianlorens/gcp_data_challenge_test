from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.utils.dates import days_ago
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime
import csv
import os
from google.cloud import storage

RAW_BUCKET = "lm-nebulapay-raw"
PROCESSED_BUCKET = "lm-nebulapay-processed"

def get_path(execution_date):
    date_str = execution_date.strftime("%Y-%m-%d")
    return f"transactions/date={date_str}/transactions.csv"

def validate_file(**context):
    execution_date = context["execution_date"]
    path = get_path(execution_date)

    client = storage.Client()
    bucket = client.bucket(RAW_BUCKET)
    blob = bucket.blob(path)

    content = blob.download_as_text().splitlines()
    reader = csv.DictReader(content)

    valid_rows = []
    invalid = False

    for row in reader:
        if (
            not row["transaction_id"]
            or float(row["amount"]) < 0
            or not row["currency"]
        ):
            invalid = True
            break
        valid_rows.append(row)

    return "transform" if not invalid else "quarantine"


def quarantine_file(**context):
    execution_date = context["execution_date"]
    date_str = execution_date.strftime("%Y-%m-%d")

    client = storage.Client()
    source_bucket = client.bucket(RAW_BUCKET)

    src_path = get_path(execution_date)
    dest_path = f"invalid/date={date_str}/transactions.csv"

    blob = source_bucket.blob(src_path)
    source_bucket.copy_blob(blob, source_bucket, dest_path)
    blob.delete()


def transform_file(**context):
    execution_date = context["execution_date"]
    date_str = execution_date.strftime("%Y-%m-%d")

    rates = {"EUR": 1.0, "USD": 0.92, "GBP": 1.17}

    client = storage.Client()
    raw_bucket = client.bucket(RAW_BUCKET)
    processed_bucket = client.bucket(PROCESSED_BUCKET)

    blob = raw_bucket.blob(get_path(execution_date))
    content = blob.download_as_text().splitlines()

    reader = csv.DictReader(content)
    output_rows = []

    for row in reader:
        amount = float(row["amount"]) * rates[row["currency"]]
        row["amount"] = amount
        row["currency"] = "EUR"
        row["processed_at"] = datetime.utcnow().isoformat()
        output_rows.append(row)

    output_path = f"clean/date={date_str}/transactions_clean.csv"
    out_blob = processed_bucket.blob(output_path)

    keys = output_rows[0].keys()
    lines = [",".join(keys)]
    for r in output_rows:
        lines.append(",".join(str(r[k]) for k in keys))

    out_blob.upload_from_string("\n".join(lines))


def mark_success(**context):
    execution_date = context["execution_date"]
    date_str = execution_date.strftime("%Y-%m-%d")

    client = storage.Client()
    bucket = client.bucket(PROCESSED_BUCKET)

    blob = bucket.blob(f"done/date={date_str}/_SUCCESS")
    blob.upload_from_string("done")


with DAG(
    "lm_nebulapay_transactions_daily",
    start_date=days_ago(1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    wait_for_file = GCSObjectExistenceSensor(
        task_id="wait_for_file",
        bucket=RAW_BUCKET,
        object="{{ 'transactions/date=' + ds + '/transactions.csv' }}",
    )

    validate = BranchPythonOperator(
        task_id="validate",
        python_callable=validate_file,
        provide_context=True,
    )

    quarantine = PythonOperator(
        task_id="quarantine",
        python_callable=quarantine_file,
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=transform_file,
    )

    load_to_bq = GCSToBigQueryOperator(
        task_id="load_to_bq",
        bucket=PROCESSED_BUCKET,
        source_objects=["clean/date={{ ds }}/transactions_clean.csv"],
        destination_project_dataset_table="analytics.transactions",
        write_disposition="WRITE_APPEND",
        source_format="CSV",
        skip_leading_rows=1,
        autodetect=False,
    )

    success = PythonOperator(
        task_id="mark_success",
        python_callable=mark_success,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    wait_for_file >> validate
    validate >> quarantine
    validate >> transform >> load_to_bq >> success