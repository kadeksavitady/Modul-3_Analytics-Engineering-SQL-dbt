import duckdb

# Terhubung ke database yang fix dibaca oleh dbt
con = duckdb.connect('analytics.duckdb')

try:
    # 1. Duplikat Customer ID (Pasti bikin unique test FAIL)
    con.execute("INSERT INTO raw.customers VALUES ('C001', 'Budi Duplikat', 'Retail', 'East')")
    
    # 2. Customer ID bernilai NULL (Pasti bikin not_null test FAIL)
    con.execute("INSERT INTO raw.customers VALUES (NULL, 'Anonim', 'Retail', 'West')")
    
    # 3. Order dari Customer siluman yang tidak ada di tabel dimensi (Pasti bikin relationships test FAIL)
    con.execute("INSERT INTO raw.orders VALUES ('O999', 'C999', 'P001', '2026-08-01', 1, 500)")
    
    print("Data kotor berhasil ditanamkan ke dalam analytics.duckdb!")
except Exception as e:
    print("Error saat memasukkan data:", e)

con.close()