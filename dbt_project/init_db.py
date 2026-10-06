import duckdb
import os

# Menunjuk ke database satu tingkat di atas dbt_project
db_path = '../analytics.duckdb'
print(f"Membuat/mengupdate database di: {os.path.abspath(db_path)}")

con = duckdb.connect(db_path)

# Membuat skema dan menarik data dari folder ../data/
con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
con.execute("CREATE OR REPLACE TABLE raw.customers AS SELECT * FROM read_csv_auto('../data/customers.csv', HEADER=TRUE);")
con.execute("CREATE OR REPLACE TABLE raw.products AS SELECT * FROM read_csv_auto('../data/products.csv', HEADER=TRUE);")
con.execute("CREATE OR REPLACE TABLE raw.orders AS SELECT * FROM read_csv_auto('../data/orders.csv', HEADER=TRUE);")
con.execute("CREATE OR REPLACE TABLE raw.payments AS SELECT * FROM read_csv_auto('../data/payments.csv', HEADER=TRUE);")

print("Verifikasi jumlah baris raw.orders:")
print(con.execute("SELECT COUNT(*) FROM raw.orders").fetchone()[0], "baris")
con.close()