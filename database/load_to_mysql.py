import pandas as pd
import mysql.connector
import config

CSV_FILE = "data/processed/daily_state_prices.csv"
SCHEMA_FILE = "database/schema.sql"

conn = mysql.connector.connect(
    host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD
)
cursor = conn.cursor()

# create database and table from schema.sql
with open(SCHEMA_FILE) as f:
    for statement in f.read().split(";"):
        if statement.strip():
            cursor.execute(statement)

df = pd.read_csv(CSV_FILE)
rows = [
    (r.state, r.commodity, r.arrival_date,
     float(r.modal_price), float(r.min_price), float(r.max_price), int(r.num_records))
    for r in df.itertuples()
]

sql = """
INSERT INTO daily_prices
    (state, commodity, price_date, modal_price, min_price, max_price, num_records)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    modal_price = VALUES(modal_price),
    min_price = VALUES(min_price),
    max_price = VALUES(max_price),
    num_records = VALUES(num_records)
"""

BATCH = 2000
for i in range(0, len(rows), BATCH):
    cursor.executemany(sql, rows[i:i + BATCH])
    conn.commit()
    print("Inserted", min(i + BATCH, len(rows)), "of", len(rows))

cursor.execute("SELECT COUNT(*), MIN(price_date), MAX(price_date) FROM daily_prices")
print("\nIn database (rows, first date, last date):", cursor.fetchone())

cursor.execute("""
    SELECT state, commodity, price_date, modal_price
    FROM daily_prices WHERE state = 'Kerala' AND commodity = 'Tomato'
    ORDER BY price_date DESC LIMIT 3
""")
print("\nLatest Kerala tomato rows:")
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()