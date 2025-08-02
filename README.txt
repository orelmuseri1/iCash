
http://localhost:5001/ → “Analytics App is running!”

APIs:
http://localhost:5001/unique_customers
http://localhost:5001/loyal_customers
http://localhost:5001/top_products


Docker terminal commands:
 build and remove containers:
     docker compose build --no-cache
     docker compose down -v
 run with detach terminal:
    docker compose up -d
 load data:
    docker compose run --rm data_loader python load_purchases.py
    docker compose run --rm data_loader python load_products.py
 watch DB:
    docker exec -it matala-db-1 psql -U icash -d icashdb
    SELECT COUNT(*) FROM products;
    SELECT COUNT(*) FROM purchases;
    SELECT COUNT(*) FROM purchase_items;

