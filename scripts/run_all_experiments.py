"""
scripts/run_all_experiments.py
Menjalankan semua percobaan SQL (Praktik 1-14) menggunakan DuckDB langsung.
Ini menggantikan kebutuhan dbt untuk menyiapkan database dan memverifikasi SQL.
"""

import duckdb
import pandas as pd
from pathlib import Path

DB_PATH = "analytics.duckdb"
# Path ke data relatif terhadap lokasi script ini
SCRIPT_DIR = Path(__file__).parent.parent
DATA_DIR = str(SCRIPT_DIR / "data").replace("\\", "/")



def main():
    print("=" * 70)
    print("PRAKTIKUM ANALYTICS ENGINEERING: SQL & dbt")
    print("Menjalankan semua percobaan SQL via DuckDB")
    print("=" * 70)

    con = duckdb.connect(DB_PATH)

    # ============================================================
    # PRAKTIK 9: Menyiapkan Raw Schema
    # ============================================================
    print("\n" + "=" * 60)
    print("PRAKTIK 9 — Menyiapkan Raw Schema di DuckDB")
    print("=" * 60)

    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    con.execute(f"""
        CREATE OR REPLACE TABLE raw.customers AS
        SELECT * FROM read_csv_auto('{DATA_DIR}/customers.csv', HEADER=TRUE)
    """)
    con.execute(f"""
        CREATE OR REPLACE TABLE raw.products AS
        SELECT * FROM read_csv_auto('{DATA_DIR}/products.csv', HEADER=TRUE)
    """)
    con.execute(f"""
        CREATE OR REPLACE TABLE raw.orders AS
        SELECT * FROM read_csv_auto('{DATA_DIR}/orders.csv', HEADER=TRUE)
    """)
    con.execute(f"""
        CREATE OR REPLACE TABLE raw.payments AS
        SELECT * FROM read_csv_auto('{DATA_DIR}/payments.csv', HEADER=TRUE)
    """)

    result = con.execute("""
        SELECT 'customers' AS tabel, COUNT(*) AS jumlah FROM raw.customers
        UNION ALL SELECT 'products', COUNT(*) FROM raw.products
        UNION ALL SELECT 'orders', COUNT(*) FROM raw.orders
        UNION ALL SELECT 'payments', COUNT(*) FROM raw.payments
    """).df()
    print("\nVerifikasi raw tables:")
    print(result.to_string(index=False))
    print("\n✓ Expected: customers=50, products=30, orders=500, payments=500")

    # ============================================================
    # PRAKTIK 2: SQL Transformasi Dasar
    # ============================================================
    print("\n" + "=" * 60)
    print("PRAKTIK 2 — SQL Transformasi Dasar (Agregasi)")
    print("=" * 60)

    result = con.execute("""
        SELECT
            customer_id,
            SUM(quantity * unit_price) AS total_sales
        FROM raw.orders
        GROUP BY customer_id
        ORDER BY total_sales DESC
        LIMIT 10
    """).df()
    print("\nTop 10 customer by total sales:")
    print(result.to_string(index=False))

    # ============================================================
    # PRAKTIK 3: Layer Staging Views
    # ============================================================
    print("\n" + "=" * 60)
    print("PRAKTIK 3 — Layer Raw → Staging → Intermediate → Marts")
    print("=" * 60)

    # Staging Views
    con.execute("""
        CREATE OR REPLACE VIEW stg_customers AS
        SELECT customer_id, customer_name, segment, region
        FROM raw.customers
    """)
    con.execute("""
        CREATE OR REPLACE VIEW stg_products AS
        SELECT product_id, product_name, category_id, category_name, department, unit_price
        FROM raw.products
    """)
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
        CREATE OR REPLACE VIEW stg_payments AS
        SELECT payment_id, order_id, payment_amount, payment_method, payment_status
        FROM raw.payments
    """)

    print("\n✓ Staging views created: stg_customers, stg_products, stg_orders, stg_payments")

    # Intermediate
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
    print("✓ Intermediate view created: int_sales")

    # ============================================================
    # PRAKTIK 4: Menentukan Grain
    # ============================================================
    print("\n" + "=" * 60)
    print("PRAKTIK 4 — Menentukan Grain Fact Table")
    print("=" * 60)
    print("""
Grain fct_sales: 1 row per order line

Kolom utama:
  - order_id    (natural key / PK)
  - order_date  (FK ke dim_date)
  - customer_id (FK ke dim_customer)
  - product_id  (FK ke dim_product)
  - quantity    (measure)
  - unit_price  (measure/degenerate)
  - sales_amount = quantity * unit_price (derived measure)
""")

    # Ilustrasi grain: berapa order line per order_id?
    grain_check = con.execute("""
        SELECT COUNT(DISTINCT order_id) AS unique_orders,
               COUNT(*) AS total_rows
        FROM stg_orders
    """).df()
    print("Grain check:")
    print(grain_check.to_string(index=False))
    print("→ unique_orders == total_rows berarti grain sudah 1 row per order line ✓")

    # ============================================================
    # PRAKTIK 5: Star Schema - Membuat Dimensions
    # ============================================================
    print("\n" + "=" * 60)
    print("PRAKTIK 5 — Star Schema: Membuat Dimensions")
    print("=" * 60)

    con.execute("""
        CREATE OR REPLACE TABLE dim_customer AS
        SELECT customer_id, customer_name, segment, region
        FROM stg_customers
    """)
    con.execute("""
        CREATE OR REPLACE TABLE dim_product AS
        SELECT product_id, product_name, category_id, category_name, department, unit_price
        FROM stg_products
    """)
    con.execute("""
        CREATE OR REPLACE TABLE dim_date AS
        SELECT DISTINCT
            order_date AS full_date,
            EXTRACT(year FROM order_date)    AS year,
            EXTRACT(month FROM order_date)   AS month,
            EXTRACT(quarter FROM order_date) AS quarter
        FROM stg_orders
    """)

    dim_counts = con.execute("""
        SELECT 'dim_customer' AS model, COUNT(*) AS rows FROM dim_customer
        UNION ALL SELECT 'dim_product', COUNT(*) FROM dim_product
        UNION ALL SELECT 'dim_date', COUNT(*) FROM dim_date
    """).df()
    print("\nDimension table row counts:")
    print(dim_counts.to_string(index=False))

    # ============================================================
    # PRAKTIK 6: Snowflake Schema
    # ============================================================
    print("\n" + "=" * 60)
    print("PRAKTIK 6 — Snowflake Schema")
    print("=" * 60)

    con.execute("""
        CREATE OR REPLACE TABLE dim_category AS
        SELECT DISTINCT category_id, category_name, department
        FROM stg_products
    """)
    con.execute("""
        CREATE OR REPLACE TABLE dim_product_snowflake AS
        SELECT product_id, product_name, category_id, unit_price
        FROM stg_products
    """)

    snowflake_count = con.execute("SELECT COUNT(*) AS rows FROM dim_category").df()
    print("\ndim_category (Snowflake):")
    print(snowflake_count.to_string(index=False))

    categories = con.execute("SELECT * FROM dim_category ORDER BY category_id").df()
    print("\nKategori unik:")
    print(categories.to_string(index=False))

    print("\nPerbandingan Star vs Snowflake:")
    print("""
┌──────────────┬─────────────────────┬────────────────────────────┐
│ Aspek        │ Star                │ Snowflake                  │
├──────────────┼─────────────────────┼────────────────────────────┤
│ Dimension    │ Denormalisasi       │ Lebih ternormalisasi       │
│ Struktur     │ Sederhana           │ Lebih kompleks             │
│ Query        │ Sederhana           │ Butuh join tambahan        │
│ Redundansi   │ Lebih besar         │ Lebih kecil                │
│ Pemahaman   │ Mudah               │ Relatif lebih kompleks     │
└──────────────┴─────────────────────┴────────────────────────────┘
    """)

    # ============================================================
    # PRAKTIK 7: Implementasi Dimensional Model — Fact
    # ============================================================
    print("\n" + "=" * 60)
    print("PRAKTIK 7 — Implementasi Dimensional Model dengan SQL")
    print("=" * 60)

    con.execute("""
        CREATE OR REPLACE TABLE fct_sales AS
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

    fct_summary = con.execute("""
        SELECT
            COUNT(*) AS rows,
            SUM(quantity) AS total_quantity,
            ROUND(SUM(sales_amount), 2) AS total_sales_amount
        FROM fct_sales
    """).df()
    print("\nFact table summary:")
    print(fct_summary.to_string(index=False))
    print("\n✓ Expected: rows=500, quantity=1549, sales_amount=219137.50")

    # ============================================================
    # PRAKTIK 14: Membuat Sales Mart
    # ============================================================
    print("\n" + "=" * 60)
    print("PRAKTIK 14 — Sales Mart")
    print("=" * 60)

    con.execute("""
        CREATE OR REPLACE TABLE sales_mart AS
        SELECT
            d.year,
            d.month,
            c.segment,
            c.region,
            p.category_name AS category,
            ROUND(SUM(f.sales_amount), 2) AS total_sales,
            SUM(f.quantity)     AS total_quantity
        FROM fct_sales f
        JOIN dim_customer c ON f.customer_id = c.customer_id
        JOIN dim_product p  ON f.product_id = p.product_id
        JOIN dim_date d      ON f.order_date = d.full_date
        GROUP BY d.year, d.month, c.segment, c.region, p.category_name
    """)

    mart_sample = con.execute("""
        SELECT * FROM sales_mart
        ORDER BY year, month, total_sales DESC
        LIMIT 15
    """).df()
    print("\nSales Mart (top 15 rows):")
    print(mart_sample.to_string(index=False))

    mart_total = con.execute("SELECT COUNT(*) AS rows FROM sales_mart").df()
    print(f"\nTotal mart rows: {mart_total['rows'][0]}")

    # ============================================================
    # PRAKTIK 20-23: Automated Testing (Manual SQL)
    # ============================================================
    print("\n" + "=" * 60)
    print("PRAKTIK 20-23 — Automated Testing (SQL Equivalents)")
    print("=" * 60)

    tests = {}

    # TEST 1: unique customer_id
    dups_cust = con.execute("""
        SELECT COUNT(*) AS n FROM (
            SELECT customer_id, COUNT(*) c FROM dim_customer
            GROUP BY customer_id HAVING c > 1
        )
    """).fetchone()[0]
    tests["dim_customer.customer_id UNIQUE"] = "PASS" if dups_cust == 0 else "FAIL"

    # TEST 2: not_null customer_id
    null_cust = con.execute("SELECT COUNT(*) FROM dim_customer WHERE customer_id IS NULL").fetchone()[0]
    tests["dim_customer.customer_id NOT_NULL"] = "PASS" if null_cust == 0 else "FAIL"

    # TEST 3: unique product_id
    dups_prod = con.execute("""
        SELECT COUNT(*) AS n FROM (
            SELECT product_id, COUNT(*) c FROM dim_product
            GROUP BY product_id HAVING c > 1
        )
    """).fetchone()[0]
    tests["dim_product.product_id UNIQUE"] = "PASS" if dups_prod == 0 else "FAIL"

    # TEST 4: unique order_id pada fct_sales
    dups_fact = con.execute("""
        SELECT COUNT(*) AS n FROM (
            SELECT order_id, COUNT(*) c FROM fct_sales
            GROUP BY order_id HAVING c > 1
        )
    """).fetchone()[0]
    tests["fct_sales.order_id UNIQUE"] = "PASS" if dups_fact == 0 else "FAIL"

    # TEST 5: not_null order_id
    null_order = con.execute("SELECT COUNT(*) FROM fct_sales WHERE order_id IS NULL").fetchone()[0]
    tests["fct_sales.order_id NOT_NULL"] = "PASS" if null_order == 0 else "FAIL"

    # TEST 6: relationships customer_id
    orphan_cust = con.execute("""
        SELECT COUNT(*) FROM fct_sales f
        LEFT JOIN dim_customer c ON f.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
    """).fetchone()[0]
    tests["fct_sales.customer_id RELATIONSHIPS"] = "PASS" if orphan_cust == 0 else "FAIL"

    # TEST 7: relationships product_id
    orphan_prod = con.execute("""
        SELECT COUNT(*) FROM fct_sales f
        LEFT JOIN dim_product p ON f.product_id = p.product_id
        WHERE p.product_id IS NULL
    """).fetchone()[0]
    tests["fct_sales.product_id RELATIONSHIPS"] = "PASS" if orphan_prod == 0 else "FAIL"

    # TEST 8: sales_amount positif
    neg_sales = con.execute("SELECT COUNT(*) FROM fct_sales WHERE sales_amount <= 0").fetchone()[0]
    tests["fct_sales.sales_amount POSITIVE"] = "PASS" if neg_sales == 0 else "FAIL"

    # TEST 9: mart tidak kosong
    mart_rows = con.execute("SELECT COUNT(*) FROM sales_mart").fetchone()[0]
    tests["sales_mart NON_EMPTY"] = "PASS" if mart_rows > 0 else "FAIL"

    print("\nHasil Test:")
    all_pass = True
    for test_name, result in tests.items():
        status = "✓" if result == "PASS" else "✗"
        print(f"  {status} {test_name}: {result}")
        if result == "FAIL":
            all_pass = False

    print(f"\n{'✓ ALL TESTS PASSED' if all_pass else '✗ SOME TESTS FAILED'}")

    # ============================================================
    # PRAKTIK 29: Data Quality Failure Lab
    # ============================================================
    print("\n" + "=" * 60)
    print("PRAKTIK 29 — Data Quality Failure Lab")
    print("=" * 60)

    print("\n35.1 Simulasi duplicate customer_id:")
    con.execute("""
        CREATE OR REPLACE TABLE dim_customer_broken AS
        SELECT * FROM dim_customer
        UNION ALL
        SELECT customer_id, customer_name, segment, region
        FROM dim_customer LIMIT 1
    """)
    dup_check = con.execute("""
        SELECT COUNT(*) AS n FROM (
            SELECT customer_id, COUNT(*) c FROM dim_customer_broken
            GROUP BY customer_id HAVING c > 1
        )
    """).fetchone()[0]
    print(f"  Duplicate customer_ids found: {dup_check}")
    print(f"  Test unique → {'FAIL ✗ (expected)' if dup_check > 0 else 'PASS'}")

    print("\n35.2 Simulasi NULL customer_id:")
    con.execute("""
        CREATE OR REPLACE TABLE dim_customer_null AS
        SELECT * FROM dim_customer
        UNION ALL
        SELECT NULL, 'Ghost Customer', 'Unknown', 'Unknown'
    """)
    null_check = con.execute("SELECT COUNT(*) FROM dim_customer_null WHERE customer_id IS NULL").fetchone()[0]
    print(f"  NULL customer_ids found: {null_check}")
    print(f"  Test not_null → {'FAIL ✗ (expected)' if null_check > 0 else 'PASS'}")

    print("\n35.3 Simulasi foreign key invalid (customer_id = C999):")
    con.execute("""
        CREATE OR REPLACE TABLE fct_sales_broken AS
        SELECT * FROM fct_sales
        UNION ALL
        SELECT 'O99999', CURRENT_DATE, 'C999', 'P001', 1, 100.0, 100.0
    """)
    orphan_check = con.execute("""
        SELECT COUNT(*) FROM fct_sales_broken f
        LEFT JOIN dim_customer c ON f.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
    """).fetchone()[0]
    print(f"  Orphan customer_ids found: {orphan_check}")
    print(f"  Test relationships → {'FAIL ✗ (expected)' if orphan_check > 0 else 'PASS'}")

    print("\n→ Tujuan pembelajaran: test adalah quality gate, bukan formalitas!")

    con.close()
    print("\n" + "=" * 70)
    print("✓ Semua percobaan SQL selesai dieksekusi")
    print("=" * 70)


if __name__ == "__main__":
    main()
