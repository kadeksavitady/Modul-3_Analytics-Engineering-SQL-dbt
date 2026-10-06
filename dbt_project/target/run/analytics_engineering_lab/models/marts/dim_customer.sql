
    

    create  table
      "analytics"."main"."dim_customer__dbt_tmp"
  
    
    as (
      -- models/marts/dim_customer.sql
-- Praktik 12: Dimension customer (Star Schema)
-- Grain: 1 row per customer

SELECT
    customer_id,
    customer_name,
    segment,
    region
FROM "analytics"."main"."stg_customers"
    );
    
  