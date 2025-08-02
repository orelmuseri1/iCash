from flask import Flask, jsonify
import os
import psycopg2

app = Flask(__name__)

DB_NAME = os.getenv("DB_NAME", "icashdb")
DB_USER = os.getenv("DB_USER", "icash")
DB_PASS = os.getenv("DB_PASS", "icashpass")
DB_HOST = os.getenv("DB_HOST", "db")  # 'db' is the service name from docker-compose

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST
    )

@app.route('/')
def home():
    return "Analytics App is running!"

@app.route('/unique_customers')
def unique_customers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(DISTINCT user_id) FROM purchases;")
    count = cur.fetchone()[0]
    conn.close()
    return jsonify({'unique_customers': count})

@app.route('/loyal_customers')
def loyal_customers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, COUNT(*) AS purchases
        FROM purchases
        GROUP BY user_id
        HAVING COUNT(*) >= 3;
    """)
    rows = cur.fetchall()
    conn.close()
    return jsonify({'loyal_customers': [dict(user_id=r[0], purchases=r[1]) for r in rows]})

@app.route('/top_products')
def top_products():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.name, COUNT(*) as sold
        FROM purchase_items pi
        JOIN products p ON pi.product_id = p.id
        GROUP BY p.name
        ORDER BY sold DESC
        LIMIT 3;
    """)
    rows = cur.fetchall()
    conn.close()
    return jsonify({'top_products': [dict(name=r[0], sold=r[1]) for r in rows]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
