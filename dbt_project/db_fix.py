import duckdb

# Terhubung langsung ke file database yang dicari oleh dbt (satu tingkat di atas folder saat ini)
con = duckdb.connect('../analytics.duckdb')

# Membuat schema raw dan memasukkan datanya dari folder data/
query = """
CREATE SCHEMA IF NOT EXISTS raw;
CREATE OR REPLACE TABLE raw.customers AS SELECT * FROM read_csv_auto('../data/customers.csv', HEADER=TRUE);
CREATE OR REPLACE TABLE raw.products AS SELECT * FROM read_csv_auto('../data/products.csv', HEADER=TRUE);
CREATE OR REPLACE TABLE raw.orders AS SELECT * FROM read_csv_auto('../data/orders.csv', HEADER=TRUE);
CREATE OR REPLACE TABLE raw.payments AS SELECT * FROM read_csv_auto('../data/payments.csv', HEADER=TRUE);
"""

con.execute(query)
con.close()
print("Skema 'raw' berhasil disuntikkan ke ../analytics.duckdb!")