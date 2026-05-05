CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.transactions (
  transaction_id STRING,
  user_id STRING,
  product_id STRING,
  amount FLOAT64,
  currency STRING,
  transaction_ts TIMESTAMP,
  processed_at TIMESTAMP
)
PARTITION BY DATE(transaction_ts)
CLUSTER BY user_id;