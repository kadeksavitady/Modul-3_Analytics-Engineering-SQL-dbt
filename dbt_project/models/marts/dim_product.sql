-- models/marts/dim_product.sql
-- Praktik 12: Dimension product (Star Schema)
-- Grain: 1 row per product

SELECT
    product_id,
    product_name,
    category_id,
    category_name,
    department,
    unit_price
FROM {{ ref('stg_products') }}
