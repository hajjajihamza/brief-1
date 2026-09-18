from sqlalchemy import text
from config.database import engine

def load(df):
    df.apply(insert_row, axis=1)

def insert_row(row):
    customer_query = text("""
        INSERT INTO core.customer (
            customer_id,
            customer_name,
            segment,
            country,
            city,
            state,
            region
        )
        VALUES (
            :customer_id,
            :customer_name,
            :segment,
            :country,
            :city,
            :state,
            :region
        )
        ON CONFLICT (customer_id) DO NOTHING;
    """)

    product_query = text("""
        INSERT INTO core.product (
            product_id,
            category,
            subcategory,
            product_name
        )
        VALUES (
            :product_id,
            :category,
            :subcategory,
            :product_name
        )
        ON CONFLICT (product_id) DO NOTHING;
    """)

    order_query = text("""
        INSERT INTO core.orders (
            row_id,
            order_id,
            customer_id,
            product_id,
            order_date,
            ship_date,
            ship_mode,
            ship_duration,
            sales,
            quantity,
            discount,
            price
        )
        VALUES (
            :row_id,
            :order_id,
            :customer_id,
            :product_id,
            :order_date,
            :ship_date,
            :ship_mode,
            :ship_duration,
            :sales,
            :quantity,
            :discount,
            :price
        );
    """)

    with engine.begin() as connection:
        connection.execute(customer_query, {
            "customer_id": row["customer_id"],
            "customer_name": row["customer_name"],
            "segment": row["segment"],
            "country": row["country"],
            "city": row["city"],
            "state": row["state"],
            "region": row["region"],
        })

        connection.execute(product_query, {
            "product_id": row["product_id"],
            "category": row["category"],
            "subcategory": row["sub-category"],
            "product_name": row["product_name"],
        })

        connection.execute(order_query, {
            "row_id": row["row_id"],
            "order_id": row["order_id"],
            "customer_id": row["customer_id"],
            "product_id": row["product_id"],
            "order_date": row["order_date"],
            "ship_date": row["ship_date"],
            "ship_mode": row["ship_mode"],
            "ship_duration": row["ship_duration"],
            "sales": row["sales"],
            "quantity": row["quantity"],
            "discount": row["discount"],
            'price': row['price']
        })