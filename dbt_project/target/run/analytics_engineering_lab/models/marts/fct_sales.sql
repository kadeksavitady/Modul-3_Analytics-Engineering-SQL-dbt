
    

    create  table
      "analytics"."main"."fct_sales__dbt_tmp"
  
    
    as (
      -- models/marts/fct_sales.sql
-- Praktik 13: Fact table sales
-- Grain: 1 row per order line

SELECT
    order_id,
    order_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    sales_amount
FROM "analytics"."main"."int_sales"
    );
    
  