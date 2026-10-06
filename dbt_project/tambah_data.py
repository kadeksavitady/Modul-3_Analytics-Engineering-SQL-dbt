import duckdb

con = duckdb.connect('analytics.duckdb')

# Memasukkan 50 transaksi dummy baru dengan tanggal masa depan (1 Desember 2026)
con.execute("""
    INSERT INTO raw.orders
    SELECT 
        'O_NEW_' || i AS order_id, 
        'C001' AS customer_id, 
        'P001' AS product_id, 
        CAST('2026-12-01' AS DATE) AS order_date, 
        2 AS quantity, 
        150 AS unit_price
    FROM range(1, 51) AS t(i);
""")

total = con.execute("SELECT COUNT(*) FROM raw.orders").fetchone()[0]
print(f"SUKSES! 50 Order baru berhasil ditambahkan. Total data raw.orders sekarang: {total}")
con.close()