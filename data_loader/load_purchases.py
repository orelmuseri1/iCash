import psycopg2
import csv
import ast

conn = psycopg2.connect(
    dbname='icashdb',
    user='icash',
    password='icashpass',
    host='localhost',  # אם מתוך קונטיינר - 'db'
    port='5432'
)

cur = conn.cursor()

with open('../db/purchases.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        try:
            user_id = row['user_id']
            supermarket_id = int(row['supermarket_id'])
            timestamp = row['timestamp']
            total_amount = float(row['total_amount'])
            items = ast.literal_eval(row['items'])

            cur.execute("""
                INSERT INTO purchases (user_id, supermarket_id, timestamp, total_amount)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, (user_id, supermarket_id, timestamp, total_amount))

            purchase_id = cur.fetchone()[0]

            for product_id in items:
                cur.execute("""
                    INSERT INTO purchase_items (purchase_id, product_id)
                    VALUES (%s, %s);
                """, (purchase_id, product_id))

        except Exception as e:
            print(f"Error in row: {row}")
            print(e)

conn.commit()
cur.close()
conn.close()
print("✅ Purchases loaded.")
