import duckdb

# Database akan dibuat persis di sebelah file profiles.yml
con = duckdb.connect('analytics.duckdb')

con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
con.execute("CREATE OR REPLACE TABLE raw.customers AS SELECT * FROM read_csv_auto('../data/customers.csv', HEADER=TRUE);")
con.execute("CREATE OR REPLACE TABLE raw.products AS SELECT * FROM read_csv_auto('../data/products.csv', HEADER=TRUE);")
con.execute("CREATE OR REPLACE TABLE raw.orders AS SELECT * FROM read_csv_auto('../data/orders.csv', HEADER=TRUE);")
con.execute("CREATE OR REPLACE TABLE raw.payments AS SELECT * FROM read_csv_auto('../data/payments.csv', HEADER=TRUE);")

print("SUKSES! Data orders:", con.execute("SELECT COUNT(*) FROM raw.orders").fetchone()[0], "baris.")
con.close()