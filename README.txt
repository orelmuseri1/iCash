
Requirements
- Docker – for containerized deployment
- Docker Compose – for orchestrating multiple containers
- Python 3.11 – base programming language
- Flask – web framework for building APIs and simple UI
- psycopg2 – PostgreSQL database driver for Python
- Jinja2 – templating engine (used for HTML pages)
- PostgreSQL 15 – relational database


docker compose build --no-cache
docker compose up -d

If needed :
     docker compose down -v
load data (The loader scripts must run after DB is up):
   docker compose run --rm data_loader python load_products.py
   docker compose run --rm data_loader python load_purchases.py
watch DB:
   docker exec -it matala-db-1 psql -U icash -d icashdb
   SELECT COUNT(*) FROM products;
   SELECT COUNT(*) FROM purchases;

Purchase UI:
http://localhost:5000/

Analytics Dashboard:
http://localhost:5001/

Analytics APIs:
http://localhost:5001/unique_customers
http://localhost:5001/loyal_customers
http://localhost:5001/top_products

notes:
1) All purchases are stored in one table (purchases) with a single items_list column.
2) User IDs must be valid UUIDs. If none provided, one is generated automatically.
3) This is a demo system, not for production use.

Feature Ideas for Future Development:
Authentication & Authorization: Add login for managers and staff, with role-based permissions.
Modern UI Framework: Rebuild the frontend using React for a more dynamic experience.
Advanced Reports: Daily/weekly/monthly sales reports with product breakdowns.
Caching Layer: Use Redis to cache frequent analytics queries.


