-- models/marts/fct_sales_incremental.sql
-- Praktik 16-17: Incremental model untuk fact sales
-- unique_key: order_id
-- Watermark: MAX(order_date) pada target table



SELECT
    order_id,
    order_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    sales_amount
FROM "analytics"."main"."int_sales"



WHERE order_date >= (
    SELECT
        COALESCE(
            MAX(order_date),
            CAST('1900-01-01' AS DATE)
        )
    FROM "analytics"."main"."fct_sales_incremental"
)

