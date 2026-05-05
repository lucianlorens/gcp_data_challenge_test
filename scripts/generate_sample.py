import csv
from datetime import datetime

rows = [
    ["t1", "u1", "p1", 10.0, "EUR", datetime.utcnow()],
    ["t2", "u2", "p2", 20.0, "USD", datetime.utcnow()],
]

with open("transactions.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow([
        "transaction_id","user_id","product_id",
        "amount","currency","transaction_ts"
    ])
    writer.writerows(rows)