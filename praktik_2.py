import duckdb

# Kita menggunakan DuckDB untuk langsung menjalankan query SQL ke file orders.csv
# read_csv_auto menggantikan tabel 'raw_orders' pada modul
query = """
SELECT
    customer_id,
    SUM(quantity * unit_price) AS total_sales
FROM read_csv_auto('data/orders.csv', HEADER=TRUE)
GROUP BY customer_id
ORDER BY total_sales DESC;
"""

# Mengeksekusi query dan menampilkan hasilnya dalam bentuk DataFrame
hasil_query = duckdb.query(query).df()
print("Hasil Praktik 2 - Total Sales per Customer:")
print(hasil_query)