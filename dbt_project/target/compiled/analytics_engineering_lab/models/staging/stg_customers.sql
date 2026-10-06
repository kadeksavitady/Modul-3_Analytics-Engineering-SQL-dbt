-- models/staging/stg_customers.sql
-- Praktik 10-12: staging layer untuk customers
-- Melakukan rename dan cast dasar dari raw.customers

SELECT
    customer_id,
    customer_name,
    segment,
    region
FROM "analytics"."raw"."customers"