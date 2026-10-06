import duckdb

# Membuat koneksi DuckDB
con = duckdb.connect()

# 1. Membuat layer Staging (Membaca langsung dari CSV sesuai Praktik 7.1, 7.2, 7.3)
con.execute("""
CREATE OR REPLACE VIEW stg_customers AS
SELECT customer_id, customer_name, segment, region FROM read_csv_auto('data/customers.csv', HEADER=TRUE);

CREATE OR REPLACE VIEW stg_products AS
SELECT product_id, product_name, category_id, category_name, department, unit_price FROM read_csv_auto('data/products.csv', HEADER=TRUE);

CREATE OR REPLACE VIEW stg_orders AS
SELECT order_id, customer_id, product_id, DATE(order_date) AS order_date, quantity, unit_price FROM read_csv_auto('data/orders.csv', HEADER=TRUE);
""")

# 2. Membuat tabel Fact dan Dimensi waktu (dim_date) untuk kebutuhan join
con.execute("""
CREATE OR REPLACE VIEW fct_sales AS
SELECT order_id, order_date, customer_id, product_id, quantity, unit_price, ROUND(quantity * unit_price, 2) AS sales_amount
FROM stg_orders;

CREATE OR REPLACE VIEW dim_date AS
SELECT DISTINCT order_date AS full_date, EXTRACT(year FROM order_date) AS year, EXTRACT(month FROM order_date) AS month, EXTRACT(quarter FROM order_date) AS quarter
FROM stg_orders;
""")

# 3. Membuat Analytical Mart (Sesuai Praktik 7.5)
query_mart = """
SELECT
    d.year,
    d.month,
    c.segment,
    c.region,
    p.category_name AS category,
    SUM(f.sales_amount) AS total_sales,
    SUM(f.quantity) AS total_quantity
FROM fct_sales f
JOIN stg_customers c ON f.customer_id = c.customer_id
JOIN stg_products p ON f.product_id = p.product_id
JOIN dim_date d ON f.order_date = d.full_date
GROUP BY d.year, d.month, c.segment, c.region, p.category_name;
"""

# Eksekusi dan tampilkan hasil
print("Hasil Analytical Mart (Layer Akhir Bisnis):")
hasil_mart = con.query(query_mart).df()
print(hasil_mart.head(10)) # Menampilkan 10 baris pertama hasil rekap penjualan