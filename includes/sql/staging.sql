CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.superstore_raw (
    "Row ID" TEXT,
    "Order ID" TEXT,
    "Order Date" TEXT,
    "Ship Date" TEXT,
    "Ship Mode" TEXT,
    "Customer ID" TEXT,
    "Customer Name" TEXT,
    "Segment" TEXT,
    "Country" TEXT,
    "City" TEXT,
    "State" TEXT,
    "Postal Code" TEXT,
    "Region" TEXT,
    "Product ID" TEXT,
    "Category" TEXT,
    "Sub-Category" TEXT,
    "Product Name" TEXT,
    "Sales" TEXT,
    "Quantity" TEXT,
    "Discount" TEXT,
    "Profit" TEXT
);