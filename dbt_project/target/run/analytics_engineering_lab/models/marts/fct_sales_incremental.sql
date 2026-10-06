
        
            delete from "analytics"."main"."fct_sales_incremental"
            where (
                order_id) in (
                select (order_id)
                from "fct_sales_incremental__dbt_tmp20261006151619986722"
            );

        
    

    insert into "analytics"."main"."fct_sales_incremental" ("order_id", "order_date", "customer_id", "product_id", "quantity", "unit_price", "sales_amount")
    (
        select "order_id", "order_date", "customer_id", "product_id", "quantity", "unit_price", "sales_amount"
        from "fct_sales_incremental__dbt_tmp20261006151619986722"
    )
  