-- models/staging/stg_orders.sql
-- Praktik 10-12: staging layer untuk orders
-- Cast order_date ke DATE dari raw.orders

SELECT
    order_id,
    customer_id,
    product_id,
    CAST(order_date AS DATE) AS order_date,
    quantity,
    unit_price
FROM {{ source('raw', 'orders') }}
