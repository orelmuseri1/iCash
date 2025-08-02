import psycopg2
import csv
import os

# Database connection
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME", "icashdb"),
    user=os.getenv("DB_USER", "icash"),
    password=os.getenv("DB_PASS", "icashpass"),
    host=os.getenv("DB_HOST", "db"),
    port="5432"
)
cur = conn.cursor()

# Clear old data
print("🔄 Clearing products table...")
cur.execute("TRUNCATE TABLE products RESTART IDENTITY CASCADE;")

# CSV path (from mounted volume)
csv_path = "/db/Products_list.csv"
print(f"📂 Loading products from {csv_path}")

with open(csv_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    print(f"Detected columns: {reader.fieldnames}")

    for row in reader:
        name = row['product_name']
        price = float(row['unit_price'])
        cur.execute("INSERT INTO products (name, price) VALUES (%s, %s);", (name, price))
        print(f" → Inserted product: {name} (price: {price})")

# Commit changes
conn.commit()
cur.close()
conn.close()
print("✅ Products table cleared and reloaded successfully.")
