-- models/marts/sales_mart.sql
-- Praktik 14 + Mini Project: Analytical mart
-- Aggregasi sales per bulan, customer segment, region, dan product category

SELECT
    d.year,
    d.month,
    c.segment,
    c.region,
    p.category_name AS category,
    SUM(f.sales_amount) AS total_sales,
    SUM(f.quantity)     AS total_quantity
FROM {{ ref('fct_sales') }} f
JOIN {{ ref('dim_customer') }} c
    ON f.customer_id = c.customer_id
JOIN {{ ref('dim_product') }} p
    ON f.product_id = p.product_id
JOIN {{ ref('dim_date') }} d
    ON f.order_date = d.full_date
GROUP BY
    d.year,
    d.month,
    c.segment,
    c.region,
    p.category_name
