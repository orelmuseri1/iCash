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
    # Get request data (JSON preferred)
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict(flat=False)
        data["items"] = data.get("items", [])
        if isinstance(data["items"], str):
            data["items"] = [data["items"]]

    supermarket_id = data.get("supermarket_id")
    user_id = data.get("user_id")
    items = data.get("items", [])

    # Validation
    if not supermarket_id or not items:
        return jsonify({"error": "supermarket_id and items are required"}), 400

    # Check UUID validity
    if user_id and not is_valid_uuid(user_id):
        return jsonify({"error": "Invalid user_id, must be a valid UUID format"}), 400
    if not user_id:
        user_id = str(uuid.uuid4())

    # Connect to DB
    conn = get_db_connection()
    cur = conn.cursor()

    # Load products mapping
    cur.execute("SELECT id, name, price FROM products;")
    product_map = {name.lower(): {"id": pid, "price": price} for pid, name, price in cur.fetchall()}

    # Calculate total & prepare items
    total_amount = 0
    item_ids = []
    for item in items:
        item_lower = item.lower()
        if item_lower not in product_map:
            conn.close()
            return jsonify({"error": f"Product '{item}' not found"}), 400
        total_amount += float(product_map[item_lower]["price"])
        item_ids.append(product_map[item_lower]["id"])

    # Insert purchase
    cur.execute("""
        INSERT INTO purchases (user_id, supermarket_id, timestamp, total_amount)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """, (user_id, supermarket_id, datetime.now(), total_amount))
    purchase_id = cur.fetchone()[0]

    # Insert purchase items
    for product_id in item_ids:
        cur.execute("INSERT INTO purchase_items (purchase_id, product_id) VALUES (%s, %s);",
                    (purchase_id, product_id))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "purchase_id": purchase_id,
        "user_id": user_id,
        "total_amount": total_amount,
        "items": items
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
