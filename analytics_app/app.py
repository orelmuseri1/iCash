from flask import Flask, jsonify
import psycopg2
import os
from collections import Counter

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "icashdb"),
        user=os.getenv("DB_USER", "icash"),
        password=os.getenv("DB_PASS", "icashpass"),
        host=os.getenv("DB_HOST", "db"),
        port="5432"
    )

@app.route("/")
def home():
    return "Analytics App is running!"

@app.route("/unique_customers", methods=["GET"])
def unique_customers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(DISTINCT user_id) FROM purchases;")
    unique_count = cur.fetchone()[0]
    conn.close()
    return jsonify({"unique_customers": unique_count})

@app.route("/loyal_customers", methods=["GET"])
def loyal_customers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id
        FROM purchases
        GROUP BY user_id
        HAVING COUNT(*) >= 3;
    """)
    loyal_customers = [row[0] for row in cur.fetchall()]
    conn.close()
    return jsonify({"loyal_customers": loyal_customers})

@app.route("/top_products", methods=["GET"])
def top_products():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT items_list FROM purchases;")
    rows = cur.fetchall()
    conn.close()

    counter = Counter()
    for (items_str,) in rows:
        if not items_str:
            continue
        items = items_str.split(",")
        for item in items:
            if "x" in item:
                name, qty = item.split("x")
                try:
                    qty = int(qty)
                except ValueError:
                    qty = 1
                counter[name] += qty
            else:
                counter[item] += 1

    if not counter:
        return jsonify({"top_products": {}})

    # Get the top 3 counts (כולל מוצרים באותו דירוג)
    sorted_items = counter.most_common()
    if len(sorted_items) <= 3:
        threshold = sorted_items[-1][1]
    else:
        threshold = sorted_items[2][1]

    top_products_counts = {prod: count for prod, count in counter.items() if count >= threshold}

    return jsonify({"top_products": top_products_counts})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
