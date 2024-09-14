from dagster import job, op, repository
from database.tursodb import insert_product, get_connection
import csv

@op
def add_products_to_db(_):
    products = [
        {"name": "Pixel 9", "price": 100.0},
        {"name": "Pixel 9 Pro", "price": 150.0},
    ]
    for product in products:
        insert_product(product['name'], product['price'])

@op
def query_products_from_db(_):
    conn = get_connection()
    results = conn.execute("SELECT * FROM products").fetchall()
    for row in results:
        print(row)
    return results

@op
def convert_to_csv(_, query_results):
    with open('result.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'name', 'price'])  # Assuming the table has these columns
        for row in query_results:
            writer.writerow(row)
    print("CSV file created successfully.")

@job
def my_pipeline():
    #add_products_to_db()
    query_results = query_products_from_db()
    convert_to_csv(query_results)

@repository
def my_repository():
    return [my_pipeline]