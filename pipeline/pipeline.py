from dagster import job, op, repository
from database.tursodb import insert_product, get_connection

@op
def add_products_to_db(_):
    products = [
        {"name": "Product 1", "price": 10.0},
        {"name": "Product 2", "price": 20.0},
    ]
    for product in products:
        insert_product(product['name'], product['price'])

@op
def query_products_from_db(_):
    conn = get_connection()
    results = conn.execute("SELECT * FROM products").fetchall()
    return [dict(row) for row in results]

@job
def my_pipeline():
    add_products_to_db()
    query_products_from_db()

@repository
def my_repository():
    return [my_pipeline]