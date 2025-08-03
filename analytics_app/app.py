from flask import Flask, jsonify, render_template
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
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    # Unique customers
    cur.execute("SELECT COUNT(DISTINCT user_id) FROM purchases;")
    unique_customers = cur.fetchone()[0]

    # Loyal customers (3+ purchases)
    cur.execute("""
        SELECT user_id
        FROM purchases
        GROUP BY user_id
        HAVING COUNT(*) >= 3;
    """)
    loyal_customers = [row[0] for row in cur.fetchall()]

    # Top products (parse items_list)
    cur.execute("SELECT items_list FROM purchases;")
    rows = cur.fetchall()
    conn.close()

    counter = Counter()
    for (items_str,) in rows:
        if not items_str:
            continue
        items = items_str.split(",")
        for item in items:
            counter[item] += 1  # כל פריט נספר פעם אחת

    sorted_items = counter.most_common()
    if len(sorted_items) <= 3:
        threshold = sorted_items[-1][1] if sorted_items else 0
    else:
        threshold = sorted_items[2][1]
    top_products = {prod: count for prod, count in counter.items() if count >= threshold}

    return render_template("index.html",
                           unique_customers=unique_customers,
                           loyal_customers=loyal_customers,
                           top_products=top_products)

@app.route("/unique_customers", methods=["GET"])
def unique_customers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(DISTINCT user_id) FROM purchases;")
    count = cur.fetchone()[0]
    conn.close()
    return jsonify({"unique_customers": count})

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
    customers = [row[0] for row in cur.fetchall()]
    conn.close()
    return jsonify({"loyal_customers": customers})

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
            counter[item] += 1

    sorted_items = counter.most_common()
    if len(sorted_items) <= 3:
        threshold = sorted_items[-1][1] if sorted_items else 0
    else:
        threshold = sorted_items[2][1]
    top_products = {prod: count for prod, count in counter.items() if count >= threshold}

    return jsonify({"top_products": top_products})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
