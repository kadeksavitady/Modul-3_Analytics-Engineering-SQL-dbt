-- models/marts/fct_sales_incremental.sql
-- Praktik 16-17: Incremental model untuk fact sales
-- unique_key: order_id
-- Watermark: MAX(order_date) pada target table

{{ config(
    materialized='incremental',
    unique_key='order_id'
) }}

SELECT
    order_id,
    order_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    sales_amount
FROM {{ ref('int_sales') }}

{% if is_incremental() %}

WHERE order_date >= (
    SELECT
        COALESCE(
            MAX(order_date),
            CAST('1900-01-01' AS DATE)
        )
    FROM {{ this }}
)

{% endif %}
