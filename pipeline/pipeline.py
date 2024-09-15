import csv
from typing import List, Dict, Any
from database.tursodb import get_connection, insert_product
from dagster import op, job, repository

@op
def add_products_to_db() -> None:
    products: List[Dict[str, Any]] = [
        {"name": "Pixel 9", "price": 100.0},
        {"name": "Pixel 9 Pro", "price": 150.0},
    ]
    for product in products:
        insert_product(product['name'], product['price'])

@op
def query_products_from_db() -> List[Dict[str, Any]]:
    conn = get_connection()
    results = conn.execute("SELECT * FROM products").fetchall()
    column_names = ['id', 'name', 'price']
    dict_results = [dict(zip(column_names, row)) for row in results]
    for row in dict_results:
        print(row)
    return dict_results

@op
def convert_to_csv(query_results: List[Dict[str, Any]]) -> None:
    with open('result.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'name', 'price'])  # Assuming the table has these columns
        for row in query_results:
            writer.writerow([row['id'], row['name'], row['price']])
    print("CSV file created successfully.")

@job
def my_pipeline() -> None:
    add_products_to_db()
    query_results = query_products_from_db()
    convert_to_csv(query_results)

@repository
def my_repository() -> List[Any]:
    return [my_pipeline]