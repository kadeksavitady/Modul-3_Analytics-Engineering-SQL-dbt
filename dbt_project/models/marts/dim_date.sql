-- models/marts/dim_date.sql
-- Praktik 12: Dimension date
-- Grain: 1 row per distinct order_date

SELECT DISTINCT
    order_date AS full_date,
    EXTRACT(year FROM order_date)    AS year,
    EXTRACT(month FROM order_date)   AS month,
    EXTRACT(quarter FROM order_date) AS quarter
FROM {{ ref('stg_orders') }}
