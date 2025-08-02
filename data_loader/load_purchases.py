import psycopg2
import csv
import os

# Connect to DB
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME", "icashdb"),
    user=os.getenv("DB_USER", "icash"),
    password=os.getenv("DB_PASS", "icashpass"),
    host=os.getenv("DB_HOST", "db"),
    port="5432"
)
cur = conn.cursor()

# Clear old data
print("🔄 Clearing purchases and purchase_items tables...")
cur.execute("TRUNCATE TABLE purchase_items RESTART IDENTITY CASCADE;")
cur.execute("TRUNCATE TABLE purchases RESTART IDENTITY CASCADE;")

# Load product mapping {product_name -> id}
cur.execute("SELECT id, name FROM products;")
product_map = {name.lower(): pid for pid, name in cur.fetchall()}
print(f"Product map: {product_map}")

csv_path = "/db/purchases.csv"
print(f"📂 Loading purchases from {csv_path}")

with open(csv_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    print(f"Detected CSV columns: {reader.fieldnames}")

    for row in reader:
        supermarket_id = row['supermarket_id']  # keep as text
        timestamp = row['timestamp']
        user_id = row['user_id']
        items_str = row['items_list']
        total_amount = float(row['total_amount'])

        # Convert items from "eggs,milk" → product IDs
        items = []
        for item_name in items_str.split(','):
            item_name = item_name.strip().lower()
            if item_name in product_map:
                items.append(product_map[item_name])
            else:
                print(f"⚠️ Unknown product name '{item_name}', skipping it.")

        # Insert purchase
        cur.execute("""
            INSERT INTO purchases (user_id, supermarket_id, timestamp, total_amount)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (user_id, supermarket_id, timestamp, total_amount))
        purchase_id = cur.fetchone()[0]

        # Insert items
        for product_id in items:
            cur.execute("""
                INSERT INTO purchase_items (purchase_id, product_id)
                VALUES (%s, %s);
            """, (purchase_id, product_id))

        print(f" → Inserted purchase for user {user_id} at {supermarket_id} with {len(items)} items")

conn.commit()
cur.close()
conn.close()
print("✅ Purchases and purchase_items tables cleared and reloaded successfully.")
