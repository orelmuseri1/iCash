CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    price NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS purchases (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    supermarket_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    total_amount NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS purchase_items (
    id SERIAL PRIMARY KEY,
    purchase_id INT REFERENCES purchases(id),
    product_id INT REFERENCES products(id)
);

COPY products(name, price)
FROM '/docker-entrypoint-initdb.d/Products_list.csv'
DELIMITER ','
CSV HEADER;

