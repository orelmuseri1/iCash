import psycopg2
import csv

conn = psycopg2.connect(
    dbname='icashdb',
    user='icash',
    password='icashpass',
    host='localhost',  # אם מתוך קונטיינר - 'db'
    port='5432'
)

cur = conn.cursor()

with open('../db/Products_list.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row['name']
        price = float(row['price'])
        cur.execute("INSERT INTO products (name, price) VALUES (%s, %s);", (name, price))

conn.commit()
cur.close()
conn.close()
print("✅ Products loaded.")
