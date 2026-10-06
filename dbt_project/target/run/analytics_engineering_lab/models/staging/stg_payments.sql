
  
  create view "analytics"."main"."stg_payments__dbt_tmp" as (
    -- models/staging/stg_payments.sql
-- Praktik 10-12: staging layer untuk payments

SELECT
    payment_id,
    order_id,
    payment_amount,
    payment_method,
    payment_status
FROM "analytics"."raw"."payments"
  );
