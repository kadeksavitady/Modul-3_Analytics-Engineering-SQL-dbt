-- models/staging/stg_products.sql
-- Praktik 10-12: staging layer untuk products
-- Melakukan rename dan cast dasar dari raw.products

SELECT
    product_id,
    product_name,
    category_id,
    category_name,
    department,
    unit_price
FROM "analytics"."raw"."products"