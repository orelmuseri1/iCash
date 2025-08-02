CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    price NUMERIC NOT NULL
);

CREATE TABLE purchases (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    supermarket_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    items_list TEXT NOT NULL,
    total_amount NUMERIC NOT NULL
);

COPY products(name, price)
FROM '/docker-entrypoint-initdb.d/Products_list.csv'
DELIMITER ','
CSV HEADER;

