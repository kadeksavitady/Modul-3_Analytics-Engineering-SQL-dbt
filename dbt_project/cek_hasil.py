import duckdb

# Terhubung ke database finalmu
con = duckdb.connect('analytics.duckdb')

print("=== PREVIEW DATA SALES MART ===")
# Menarik 10 baris pertama dan menampilkannya dalam format tabel
con.sql("SELECT * FROM sales_mart LIMIT 10").show()

con.close()