from dagster import job, op, repository
from database.tursodb import insert_product, get_connection
import os

# Mock Modal client for demonstration purposes
class MockModalClient:
    def create_batch_job(self, name):
        return MockBatchJob()

class MockBatchJob:
    def submit_task(self, task):
        self.task = task

    def wait_for_completion(self):
        pass

    def get_results(self):
        return self.task()

# Initialize the mock client
client = MockModalClient()

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
    # Define the data retrieval function
    def fetch_data():
        conn = get_connection()
        try:
            results = conn.execute("SELECT * FROM products").fetchall()
            return results
        except Exception as e:
            print(f"Error querying products: {e}")
            return []
        finally:
            if hasattr(conn, 'close'):
                conn.close()  # Explicitly close the connection if it has a close method

    # Create a batch job
    batch_job = client.create_batch_job(name='query_products_job')

    # Submit the query task to the batch job
    batch_job.submit_task(fetch_data)

    # Wait for the job to complete and retrieve results
    batch_job.wait_for_completion()
    results = batch_job.get_results()

    # Print the results
    for row in results:
        print(row)

@job
def my_pipeline():
    add_products_to_db()
    query_products_from_db()

@repository
def my_repository():
    return [my_pipeline]