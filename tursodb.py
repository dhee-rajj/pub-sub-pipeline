import libsql_experimental as libsql
import os

url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

conn = libsql.connect("products", sync_url=url, auth_token=auth_token)
conn.sync()
