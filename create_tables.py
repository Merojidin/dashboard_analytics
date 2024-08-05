from connector import set_connection
from sqlalchemy import text

tbl_creation_query = """
    set search_path = course_prj;

    create table if not exists customer (
        customer_id varchar primary key,
        customer_unique_id varchar(50) not null,
        customer_zip_code_prefix int not null,
        customer_city text,
        customer_state text
    );

    create table if not exists orders (
        order_id varchar primary key,
        customer_id varchar references customer(customer_id),
        order_status varchar(50),
        order_purchase_timestamp timestamp,
        order_approved_at timestamp,
        order_delivered_carrier_date timestamp,
        order_delivered_customer_date timestamp, 
        order_estimated_delivery_date timestamp
    );

    create table if not exists products (
        product_id varchar primary key,
        product_category_name varchar(255),
        product_name_lenght float,
        product_description_lenght float,
        product_photos_qty float,
        product_weight_g float,
        product_length_cm float,
        product_height_cm float,
        product_width_cm float
    );

    create table if not exists sellers (
        seller_id varchar primary key, 
        seller_zip_code_prefix int not null,
        seller_city varchar(255) not null,
        seller_state char(2) not null
    );

    create table if not exists order_items (
        order_id varchar references orders(order_id),
        order_item_id int not null, 
        product_id varchar references products(product_id),
        seller_id varchar references sellers(seller_id),
        shipping_limit_date timestamp not null, 
        price decimal(10,2) not null,
        freight_value decimal (10,2)
    );

    create table if not exists reviews (
        order_id varchar references orders(order_id),
        review_id varchar not null,
        review_score int, 
        review_comment_title text, 
        review_comment_message text,
        review_creation_date timestamp,
        review_answer_timestamp timestamp
    );

   

    create table if not exists payments (
        order_id varchar references orders(order_id),
        payment_sequential int,
        payment_type varchar(50),
        payment_installments int,
        payment_value float
        
    );
    """

with set_connection() as ps:
    ps.execute(text(tbl_creation_query))
    ps.commit()



