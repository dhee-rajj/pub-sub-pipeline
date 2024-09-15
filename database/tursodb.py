import os
import libsql_experimental as libsql
import logging
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_connection() -> libsql.Connection:
    url: Optional[str] = os.getenv("TURSO_DATABASE_URL")
    auth_token: Optional[str] = os.getenv("TURSO_AUTH_TOKEN")
    conn: libsql.Connection = libsql.connect("products.db", sync_url=url, auth_token=auth_token)
    conn.sync()
    return conn

def insert_product(name: str, price: float) -> None:
    conn = get_connection()
    conn.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
    conn.commit()

# Initialize the database connection and create the table if it doesn't exist
if __name__ == "__main__":
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL
        );
    """)
    conn.commit()