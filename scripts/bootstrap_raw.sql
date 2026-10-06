-- scripts/bootstrap_raw.sql
-- Praktik 9: Menyiapkan Raw Schema di DuckDB
-- Dijalankan untuk memuat CSV ke DuckDB sebagai tabel raw

CREATE SCHEMA IF NOT EXISTS raw;

CREATE OR REPLACE TABLE raw.customers AS
SELECT * FROM read_csv_auto('../data/customers.csv', HEADER=TRUE);

CREATE OR REPLACE TABLE raw.products AS
SELECT * FROM read_csv_auto('../data/products.csv', HEADER=TRUE);

CREATE OR REPLACE TABLE raw.orders AS
SELECT * FROM read_csv_auto('../data/orders.csv', HEADER=TRUE);

CREATE OR REPLACE TABLE raw.payments AS
SELECT * FROM read_csv_auto('../data/payments.csv', HEADER=TRUE);

-- Verifikasi jumlah baris
SELECT 'customers' AS tabel, COUNT(*) AS jumlah FROM raw.customers
UNION ALL
SELECT 'products', COUNT(*) FROM raw.products
UNION ALL
SELECT 'orders', COUNT(*) FROM raw.orders
UNION ALL
SELECT 'payments', COUNT(*) FROM raw.payments;
