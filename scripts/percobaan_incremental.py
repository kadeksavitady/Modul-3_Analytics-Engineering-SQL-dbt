"""
scripts/percobaan_incremental.py
Praktik 15-18: Incremental model, watermark, simulasi data baru
"""

import duckdb
from pathlib import Path

# Use absolute paths
SCRIPT_DIR = Path(__file__).parent.parent
DB_PATH = str(SCRIPT_DIR / "analytics.duckdb")
DATA_DIR = str(SCRIPT_DIR / "data").replace("\\", "/")


def main():
    print("=" * 60)
    print("PRAKTIK 15-18 — Incremental Model & Watermark")
    print("=" * 60)

    con = duckdb.connect(DB_PATH)

    # Buat tabel incremental pertama kali (full load = first run)
    print("\n--- FIRST RUN: Full Load ---")
    print("is_incremental() = FALSE → proses semua data")

    con.execute("""
        CREATE OR REPLACE TABLE fct_sales_incremental AS
        SELECT
            order_id,
            order_date,
            customer_id,
            product_id,
            quantity,
            unit_price,
            ROUND(quantity * unit_price, 2) AS sales_amount
        FROM int_sales
    """)

    count_before = con.execute("SELECT COUNT(*) FROM fct_sales_incremental").fetchone()[0]
    max_date_before = con.execute("SELECT MAX(order_date) FROM fct_sales_incremental").fetchone()[0]
    print(f"\nSetelah first run:")
    print(f"  Total rows       : {count_before}")
    print(f"  Max order_date   : {max_date_before}")
    print(f"  Expected: 500 rows")

    # Simulasi: tambah data baru dari orders_incremental.csv
    print("\n--- SIMULASI DATA BARU: orders_incremental.csv ---")
    print("Menambahkan 50 transaksi baru ke raw.orders...")

    con.execute(f"""
        INSERT INTO raw.orders
        SELECT * FROM read_csv_auto('{DATA_DIR}/orders_incremental.csv', HEADER=TRUE)
    """)

    count_raw = con.execute("SELECT COUNT(*) FROM raw.orders").fetchone()[0]
    print(f"  raw.orders sekarang: {count_raw} rows (expected: 550)")

    # Refresh staging + intermediate views agar mencerminkan data baru
    con.execute("""
        CREATE OR REPLACE VIEW stg_orders AS
        SELECT
            order_id,
            customer_id,
            product_id,
            CAST(order_date AS DATE) AS order_date,
            quantity,
            unit_price
        FROM raw.orders
    """)
    con.execute("""
        CREATE OR REPLACE VIEW int_sales AS
        SELECT
            order_id,
            order_date,
            customer_id,
            product_id,
            quantity,
            unit_price,
            quantity * unit_price AS sales_amount
        FROM stg_orders
    """)

    # SECOND RUN: Incremental (watermark = MAX(order_date) dari tabel target)
    print("\n--- SECOND RUN: Incremental ---")
    watermark = con.execute("SELECT MAX(order_date) FROM fct_sales_incremental").fetchone()[0]
    print(f"  Watermark (MAX order_date di target): {watermark}")
    print(f"  Hanya memproses order_date >= {watermark}")

    new_rows = con.execute(f"""
        SELECT COUNT(*) FROM int_sales
        WHERE order_date >= DATE '{watermark}'
    """).fetchone()[0]
    print(f"  Rows baru yang akan diproses: {new_rows}")

    # Simulasi incremental merge (upsert) — DuckDB: DELETE existing + INSERT new
    # Ini meniru strategi merge yang dilakukan dbt dengan unique_key
    con.execute(f"""
        DELETE FROM fct_sales_incremental
        WHERE order_id IN (
            SELECT order_id FROM int_sales
            WHERE order_date >= DATE '{watermark}'
        )
    """)
    con.execute(f"""
        INSERT INTO fct_sales_incremental
        SELECT
            order_id,
            order_date,
            customer_id,
            product_id,
            quantity,
            unit_price,
            ROUND(quantity * unit_price, 2) AS sales_amount
        FROM int_sales
        WHERE order_date >= DATE '{watermark}'
    """)

    count_after = con.execute("SELECT COUNT(*) FROM fct_sales_incremental").fetchone()[0]
    max_date_after = con.execute("SELECT MAX(order_date) FROM fct_sales_incremental").fetchone()[0]
    print(f"\nSetelah second run (incremental):")
    print(f"  Total rows       : {count_after}")
    print(f"  Max order_date   : {max_date_after}")
    print(f"  Expected: 550 rows")

    # ============================================================
    # PRAKTIK 18: Memahami Unique Key
    # ============================================================
    print("\n" + "=" * 60)
    print("PRAKTIK 18 — Memahami Unique Key")
    print("=" * 60)
    print("""
Pertanyaan:
1. Mengapa order_id harus unik?
   → order_id adalah natural key dari 1 order line. Duplikasi akan
     menyebabkan double counting pada agregasi sales_amount.

2. Apa yang terjadi jika source mengirim record yang sama?
   → Dengan unique_key='order_id', dbt akan melakukan UPSERT:
     jika order_id sudah ada → UPDATE, jika belum → INSERT.
     Ini mencegah duplikasi pada tabel target.

3. Bagaimana jika order dapat berubah (update)?
   → Harus menggunakan merge strategy dengan unique_key.
     Pastikan kolom updated_at tersedia sebagai filter tambahan.
""")

    # ============================================================
    # PRAKTIK 19: Late-Arriving Data
    # ============================================================
    print("=" * 60)
    print("PRAKTIK 19 — Late-Arriving Data")
    print("=" * 60)
    print(f"""
Skenario:
  Watermark saat ini: {max_date_after}
  Transaksi late-arriving: order_date = (3 hari sebelum watermark)

Masalah dengan strategi WHERE order_date > MAX(order_date):
  → Record dengan order_date < watermark TIDAK akan diproses
  → Data hilang/ter-skip

Solusi production:
  1. Lookback window: WHERE order_date >= MAX(order_date) - INTERVAL 3 DAY
  2. Ingestion timestamp: filter berdasarkan kapan data masuk, bukan order_date
  3. CDC (Change Data Capture): menangkap perubahan di sumber
  4. Merge berdasarkan unique_key tanpa watermark
  5. Reprocessing period tertentu secara periodik
""")

    con.close()
    print("✓ Percobaan incremental selesai")


if __name__ == "__main__":
    main()
