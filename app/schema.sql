-- Remove the PostGIS extension since it's no longer needed
-- CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');
CREATE TYPE payment_method AS ENUM ('credit_card', 'paypal', 'bank_transfer');
CREATE TYPE payment_status AS ENUM ('pending', 'completed', 'failed', 'refunded');

-- Core Entities
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP
);

CREATE TABLE addresses (
    address_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    street_address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT false
);

-- Product Catalog
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_category_id INT REFERENCES categories(category_id) ON DELETE SET NULL,
    lft INT NOT NULL,
    rgt INT NOT NULL,
    depth INT NOT NULL
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category_id INT NOT NULL REFERENCES categories(category_id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE product_variations (
    variation_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    sku VARCHAR(50) UNIQUE NOT NULL,
    attributes JSONB NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    image_urls TEXT[],
    available_from DATE NOT NULL,
    available_to DATE
);

-- Inventory Management
CREATE TABLE warehouses (
    warehouse_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    address TEXT NOT NULL
);

CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,
    variation_id INT NOT NULL REFERENCES product_variations(variation_id) ON DELETE CASCADE,
    warehouse_id INT NOT NULL REFERENCES warehouses(warehouse_id),
    quantity INT NOT NULL CHECK (quantity >= 0),
    low_stock_threshold INT NOT NULL DEFAULT 10
);

-- Order Management
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id),
    shipping_address_id INT NOT NULL REFERENCES addresses(address_id),
    order_date TIMESTAMP NOT NULL DEFAULT NOW(),
    status order_status NOT NULL DEFAULT 'pending',
    total_amount NUMERIC(12,2) NOT NULL
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    variation_id INT NOT NULL REFERENCES product_variations(variation_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    price_at_purchase NUMERIC(10,2) NOT NULL
);

CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(order_id),
    amount NUMERIC(10,2) NOT NULL,
    method payment_method NOT NULL,
    status payment_status NOT NULL DEFAULT 'pending',
    transaction_id VARCHAR(255),
    payment_date TIMESTAMP
);

-- User Generated Content
CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id),
    product_id INT NOT NULL REFERENCES products(product_id),
    rating SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- Relationships
CREATE TABLE product_tags (
    product_id INT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    tag VARCHAR(50) NOT NULL,
    PRIMARY KEY (product_id, tag)
);

CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact_email VARCHAR(100),
    contact_phone VARCHAR(20)
);

CREATE TABLE product_suppliers (
    product_id INT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    supplier_id INT NOT NULL REFERENCES suppliers(supplier_id),
    cost_price NUMERIC(10,2) NOT NULL,
    lead_time_days INT NOT NULL,
    PRIMARY KEY (product_id, supplier_id)
);

-- Promotions
CREATE TABLE discounts (
    discount_id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    discount_type VARCHAR(20) NOT NULL CHECK (discount_type IN ('percentage', 'fixed')),
    amount NUMERIC(10,2) NOT NULL,
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP NOT NULL,
    max_uses INT,
    use_count INT NOT NULL DEFAULT 0
);

CREATE TABLE product_discounts (
    product_id INT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    discount_id INT NOT NULL REFERENCES discounts(discount_id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, discount_id)
);

-- Triggers
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_modtime
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_products_modtime
BEFORE UPDATE ON products
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_reviews_modtime
BEFORE UPDATE ON reviews
FOR EACH ROW EXECUTE FUNCTION update_modified_column();