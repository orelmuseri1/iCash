from flask import Flask, request, jsonify, render_template
import psycopg2
import os
from datetime import datetime
import uuid

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "icashdb"),
        user=os.getenv("DB_USER", "icash"),
        password=os.getenv("DB_PASS", "icashpass"),
        host=os.getenv("DB_HOST", "db"),
        port="5432"
    )

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM products;")
    products = [row[0] for row in cur.fetchall()]
    supermarkets = ["SMKT001", "SMKT002", "SMKT003"]
    conn.close()
    return render_template("index.html", products=products, supermarkets=supermarkets)

@app.route("/purchase", methods=["POST"])
def create_purchase():
    if request.is_json:
        data = request.get_json()
    else:
        return jsonify({"error": "Request must be JSON"}), 400

    supermarket_id = data.get("supermarket_id")
    user_id = data.get("user_id")
    items = data.get("items", [])

    # Validation
    if not supermarket_id or not items:
        return jsonify({"error": "supermarket_id and at least one item required"}), 400

    # Validate UUID
    if user_id and not is_valid_uuid(user_id):
        return jsonify({"error": "Invalid user_id, must be a valid UUID format"}), 400
    if not user_id:
        user_id = str(uuid.uuid4())

    # Remove duplicates (only one unit of each item)
    items = list(set(items))

    conn = get_db_connection()
    cur = conn.cursor()

    # Get product prices
    cur.execute("SELECT name, price FROM products;")
    price_map = {name.lower(): price for name, price in cur.fetchall()}

    total_amount = 0
    for item in items:
        if item.lower() not in price_map:
            conn.close()
            return jsonify({"error": f"Product '{item}' not found"}), 400
        total_amount += float(price_map[item.lower()])

    # Convert list to comma-separated string
    items_list = ",".join(items)

    # Insert purchase
    cur.execute("""
        INSERT INTO purchases (user_id, supermarket_id, timestamp, items_list, total_amount)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """, (user_id, supermarket_id, datetime.now(), items_list, total_amount))
    purchase_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "purchase_id": purchase_id,
        "user_id": user_id,
        "total_amount": total_amount,
        "items_list": items_list
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
