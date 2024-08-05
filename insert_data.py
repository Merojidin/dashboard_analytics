import pandas as pd
from get_data import get_data_xlsx
from connector import set_connection

customer = get_data_xlsx('olist_order_customers_dataset')
orders = get_data_xlsx('olist_orders_dataset')
products = get_data_xlsx('olist_products_dataset')
sellers = get_data_xlsx('olist_sellers_dataset')
order_items = get_data_xlsx('olist_order_items_dataset')
reviews = get_data_xlsx('olist_order_reviews_dataset')

payments = get_data_xlsx('olist_order_payments_dataset')

# Преобразование customer_id в строковый тип данных
customer['customer_id'] = customer['customer_id'].astype(str)

with set_connection() as ps:
    customer.to_sql(
        name='customer',
        schema='course_prj',
        con=ps,
        index=False,
        if_exists='append'
    )
    orders.to_sql(
        name='orders',
        schema='course_prj',
        con=ps,
        index=False,
        if_exists='append'
    )
    products.to_sql(
        name='products',
        schema='course_prj',
        con=ps,
        index=False,
        if_exists='append'
    )
    sellers.to_sql(
        name='sellers',
        schema='course_prj',
        con=ps,
        index=False,
        if_exists='append'
    )
    order_items.to_sql(
        name='order_items',
        schema='course_prj',
        con=ps,
        index=False,
        if_exists='append'
    )
    reviews.to_sql(
        name='reviews',
        schema='course_prj',
        con=ps,
        index=False,
        if_exists='append'
    )
    
    payments.to_sql(
        name='payments',
        schema='course_prj',
        con=ps,
        index=False,
        if_exists='append'
    )

