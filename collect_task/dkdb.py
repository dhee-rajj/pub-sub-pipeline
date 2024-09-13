import duckdb
import os
from database.tursodb import insert_product

def load_and_process_data():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the absolute path to the CSV file
    csv_file_path = os.path.join(script_dir, 'products.csv')

    # Load CSV data into a DuckDB table and create a DuckDB database
    conn = duckdb.connect()
    conn.execute("INSTALL sqlite")
    conn.execute("LOAD sqlite")
    conn.execute(f"CREATE TABLE my_table AS SELECT * FROM read_csv_auto('{csv_file_path}')")

    # Fetch data from DuckDB table
    result = conn.execute("SELECT * FROM my_table").fetchall()

    # Insert data into TursoDB using the insert_product function
    for row in result:
        insert_product(row[0], row[1])

if __name__ == "__main__":
    load_and_process_data()