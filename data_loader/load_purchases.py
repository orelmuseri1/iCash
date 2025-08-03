import csv
import psycopg2
import os
from datetime import datetime

DB_NAME = os.getenv("DB_NAME", "icashdb")
DB_USER = os.getenv("DB_USER", "icash")
DB_PASS = os.getenv("DB_PASS", "icashpass")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = "5432"

CSV_PATH = "/db/purchases.csv"

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )

print("🔄 Connecting to database...")
conn = get_db_connection()
cur = conn.cursor()

print("🔄 Clearing purchases table...")
cur.execute("TRUNCATE TABLE purchases RESTART IDENTITY CASCADE;")
conn.commit()

print(f"📂 Loading purchases from {CSV_PATH}")
with open(CSV_PATH, newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    detected_cols = reader.fieldnames
    print(f"Detected CSV columns: {detected_cols}")

    count = 0
    for row in reader:
        supermarket_id = row.get("supermarket_id") or row.get("\ufeffsupermarket_id")
        timestamp = datetime.fromisoformat(row["timestamp"])
        user_id = row["user_id"]
        items_list = row["items_list"]
        total_amount = float(row["total_amount"])

        cur.execute("""
            INSERT INTO purchases (user_id, supermarket_id, timestamp, items_list, total_amount)
            VALUES (%s, %s, %s, %s, %s);
        """, (user_id, supermarket_id, timestamp, items_list, total_amount))
        count += 1

conn.commit()
cur.close()
conn.close()
print(f"✅ Loaded {count} purchases into the database.")