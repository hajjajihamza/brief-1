CREATE SCHEMA IF NOT EXISTS core;

CREATE TABLE IF NOT EXISTS core.customer (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_name CHAR(100) NOT NULL,
    segment VARCHAR(50),
    country VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    region VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS core.product (
    product_id VARCHAR(20) PRIMARY KEY,
    category VARCHAR(50),
    subcategory VARCHAR(100),
    product_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS core.orders (
    row_id INTEGER PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL UNIQUE,

    customer_id VARCHAR(20) NOT NULL,
    product_id VARCHAR(20) NOT NULL,

    order_date DATE,
    ship_date DATE,
    ship_mode VARCHAR(50),
    ship_duration INTEGER,

    sales NUMERIC(12, 2),
    quantity INTEGER,
    discount NUMERIC(5, 4),
    price NUMERIC(12, 4),

    FOREIGN KEY (customer_id)
    REFERENCES core.customer(customer_id),

    FOREIGN KEY (product_id)
    REFERENCES core.product(product_id)
);