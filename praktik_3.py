import duckdb

# 1. LAYER STAGING: Membersihkan dan menstandardisasi data mentah
# Kita membuat VIEW stg_orders dengan mengubah format order_date menjadi DATE
duckdb.sql("""
CREATE OR REPLACE VIEW stg_orders AS
SELECT
    order_id,
    customer_id,
    product_id,
    CAST(order_date AS DATE) AS order_date,
    quantity,
    unit_price
FROM read_csv_auto('data/orders.csv', HEADER=TRUE);
""")

# 2. LAYER INTERMEDIATE: Menambahkan business logic (sales_amount) dari tabel staging
query_intermediate = """
SELECT
    order_id,
    order_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    quantity * unit_price AS sales_amount
FROM stg_orders;
"""

# Eksekusi dan tampilkan hasil layer intermediate
hasil_intermediate = duckdb.query(query_intermediate).df()
print("Hasil Simulasi Praktik 3 - Layer Intermediate (10 baris pertama):")
print(hasil_intermediate.head(10))