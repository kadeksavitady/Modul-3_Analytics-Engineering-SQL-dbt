"""
scripts/percobaan_star_snowflake.py
Praktik 5-6 & Praktik 30: Star vs Snowflake Schema Exercise
"""

import duckdb

DB_PATH = "analytics.duckdb"


def main():
    print("=" * 60)
    print("PRAKTIK 5-6 & 30 — Star vs Snowflake Schema")
    print("=" * 60)

    con = duckdb.connect(DB_PATH)

    # ============================================================
    # STAR SCHEMA
    # ============================================================
    print("\n--- STAR SCHEMA ---")
    print("""
Struktur Star Schema:
                 dim_customer
                      │
dim_date ──────── fct_sales ──────── dim_product
                 (category_name & department di dim_product)

Ciri: category_name dan department LANGSUNG di dim_product
     → tidak perlu join ke tabel lain untuk info category
""")

    # dim_product star schema (sudah berisi category_name & department)
    star_product_cols = con.execute("DESCRIBE dim_product").df()
    print("Kolom dim_product (Star Schema):")
    print(star_product_cols[['column_name', 'column_type']].to_string(index=False))

    # ============================================================
    # SNOWFLAKE SCHEMA
    # ============================================================
    print("\n--- SNOWFLAKE SCHEMA ---")
    print("""
Struktur Snowflake Schema:
dim_customer ──── fct_sales ──── dim_product ──── dim_category ──── dim_department

dim_product di Snowflake hanya menyimpan:
  - product_id
  - product_name
  - category_id (FK ke dim_category)
  - unit_price

dim_category menyimpan:
  - category_id
  - category_name
  - department
""")

    # Cek dim_category
    snowflake_cat = con.execute("SELECT * FROM dim_category ORDER BY category_id").df()
    print("dim_category (Snowflake):")
    print(snowflake_cat.to_string(index=False))

    print("\nPraktik 30 — Jawaban Pertanyaan:")
    print("""
1. Di mana redundansi lebih besar?
   → Star Schema: category_name & department diulang untuk setiap product
     dengan category yang sama.
   → Snowflake Schema: data category hanya tersimpan 1x di dim_category.

2. Mana yang membutuhkan join lebih banyak?
   → Snowflake: query mart harus join ke dim_product LALU ke dim_category.
   → Star: cukup join ke dim_product saja.

3. Mana yang lebih mudah dipahami analyst?
   → Star Schema lebih mudah: semua info product ada di 1 tabel.

4. Kapan normalisasi dimension menjadi relevan?
   → Ketika dimensi sangat besar dan redundansi menjadi masalah storage.
   → Ketika dimension berisi nested hierarchy yang sering berubah.
   → Ketika catalog produk punya ribuan category yang sering diupdate.
   → Pada umumnya, untuk BI/analytics, Star Schema lebih disukai karena
     simplisitas query dan performa yang lebih baik pada tools modern.
""")

    # Bandingkan query Star vs Snowflake
    print("Query Sales per Category — STAR SCHEMA:")
    star_query = con.execute("""
        SELECT p.category_name, SUM(f.sales_amount) AS total_sales
        FROM fct_sales f
        JOIN dim_product p ON f.product_id = p.product_id
        GROUP BY p.category_name
        ORDER BY total_sales DESC
    """).df()
    print(star_query.to_string(index=False))

    print("\nQuery Sales per Category — SNOWFLAKE SCHEMA (butuh 1 join tambahan):")
    snowflake_query = con.execute("""
        SELECT cat.category_name, SUM(f.sales_amount) AS total_sales
        FROM fct_sales f
        JOIN dim_product_snowflake p ON f.product_id = p.product_id
        JOIN dim_category cat ON p.category_id = cat.category_id
        GROUP BY cat.category_name
        ORDER BY total_sales DESC
    """).df()
    print(snowflake_query.to_string(index=False))

    print("\n→ Kedua query menghasilkan hasil yang sama,")
    print("  tetapi Snowflake membutuhkan 1 JOIN tambahan.")

    con.close()
    print("\n✓ Percobaan Star vs Snowflake selesai")


if __name__ == "__main__":
    main()
