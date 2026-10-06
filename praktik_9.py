import duckdb

# 1. PENTING: Membuat dan terhubung ke file database fisik 'analytics.duckdb'
con = duckdb.connect('analytics.duckdb')

# 2. Mengeksekusi SQL untuk membuat schema dan memuat data CSV
query = """
CREATE SCHEMA IF NOT EXISTS raw;

CREATE OR REPLACE TABLE raw.customers AS
SELECT * FROM read_csv_auto('data/customers.csv', HEADER=TRUE);

CREATE OR REPLACE TABLE raw.products AS
SELECT * FROM read_csv_auto('data/products.csv', HEADER=TRUE);

CREATE OR REPLACE TABLE raw.orders AS
SELECT * FROM read_csv_auto('data/orders.csv', HEADER=TRUE);

CREATE OR REPLACE TABLE raw.payments AS
SELECT * FROM read_csv_auto('data/payments.csv', HEADER=TRUE);
"""

con.execute(query)

# 3. Verifikasi jumlah baris data (Sesuai modul)
print("--- Verifikasi Data Raw ---")
print("Customers:", con.execute("SELECT COUNT(*) FROM raw.customers").fetchone()[0])
print("Products:", con.execute("SELECT COUNT(*) FROM raw.products").fetchone()[0])
print("Orders:", con.execute("SELECT COUNT(*) FROM raw.orders").fetchone()[0])
print("Payments:", con.execute("SELECT COUNT(*) FROM raw.payments").fetchone()[0])

con.close()
print("Skema 'raw' berhasil dimuat ke analytics.duckdb!")