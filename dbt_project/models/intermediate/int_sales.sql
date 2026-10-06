-- models/intermediate/int_sales.sql
-- Praktik 11: menggunakan ref() untuk merujuk stg_orders
-- Menghitung sales_amount = quantity * unit_price sebagai business logic

SELECT
    order_id,
    order_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    quantity * unit_price AS sales_amount
FROM {{ ref('stg_orders') }}
