-- RushMore PoC schema (PostgreSQL 16/17)

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS stores (
  store_id SERIAL PRIMARY KEY,
  address VARCHAR(255) NOT NULL,
  city VARCHAR(100) NOT NULL,
  phone_number VARCHAR(20) UNIQUE NOT NULL,
  opened_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customers (
  customer_id SERIAL PRIMARY KEY,
  first_name VARCHAR(100) NOT NULL,
  last_name  VARCHAR(100) NOT NULL,
  email VARCHAR(255) UNIQUE,
  phone_number VARCHAR(20) UNIQUE,
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ingredients (
  ingredient_id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL,
  stock_quantity NUMERIC(10,2) NOT NULL DEFAULT 0,
  unit VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS menu_items (
  item_id SERIAL PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  category VARCHAR(50) NOT NULL,
  size VARCHAR(20),
  box_price NUMERIC(8,2) NOT NULL DEFAULT 0.00,
  slice_price NUMERIC(8,2) NOT NULL DEFAULT 0.00,
  CONSTRAINT uq_menu UNIQUE (name, size)
);

CREATE TABLE IF NOT EXISTS menu_item_ingredients (
  menu_item_id INTEGER NOT NULL REFERENCES menu_items(item_id) ON DELETE CASCADE,
  ingredient_id INTEGER NOT NULL REFERENCES ingredients(ingredient_id) ON DELETE RESTRICT,
  quantity_required NUMERIC(10,4) NOT NULL,
  unit VARCHAR(20) NOT NULL,
  PRIMARY KEY (menu_item_id, ingredient_id)
);

CREATE TABLE IF NOT EXISTS orders (
  order_id SERIAL PRIMARY KEY,
  customer_id INTEGER REFERENCES customers(customer_id) ON DELETE SET NULL,
  store_id INTEGER REFERENCES stores(store_id) ON DELETE RESTRICT,
  order_timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  total_amount NUMERIC(10,2) NOT NULL DEFAULT 0.00,
  payment_method VARCHAR(30) NOT NULL DEFAULT 'cash',
  status VARCHAR(30) NOT NULL DEFAULT 'completed'
);

CREATE TABLE IF NOT EXISTS order_items (
  order_item_id SERIAL PRIMARY KEY,
  order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
  item_id INTEGER NOT NULL REFERENCES menu_items(item_id) ON DELETE RESTRICT,
  order_type VARCHAR(10) NOT NULL CHECK (order_type IN ('Box','Slice')),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  unit_price NUMERIC(8,2) NOT NULL,
  discount_percent NUMERIC(5,2) NOT NULL DEFAULT 0,
  discount_amount NUMERIC(8,2) NOT NULL DEFAULT 0,
  line_total NUMERIC(10,2) NOT NULL,
  discount_reason VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS idx_orders_store_ts ON orders(store_id, order_timestamp);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_order_items_item_id ON order_items(item_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_menu_items_category ON menu_items(category);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_ingredients_name ON ingredients(name);
