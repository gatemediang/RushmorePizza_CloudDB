-- 1. Total sales revenue per store
SELECT s.store_id,
       s.city,
       COUNT(o.order_id) AS order_count,
       ROUND(SUM(o.total_amount),2) AS total_revenue,
       ROUND(AVG(o.total_amount),2) AS avg_order_value_store
FROM orders o
JOIN stores s ON o.store_id = s.store_id
GROUP BY s.store_id, s.city
ORDER BY total_revenue DESC;

-- 2. Top 10 most valuable customers (by total spending)
SELECT c.customer_id,
       c.first_name,
       c.last_name,
       COUNT(o.order_id) AS orders_placed,
       ROUND(SUM(o.total_amount),2) AS total_spent,
       ROUND(AVG(o.total_amount),2) AS avg_order_value_customer
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_spent DESC
LIMIT 10;

-- 3. Most popular menu item (by quantity sold across all stores)
SELECT m.item_id,
       m.name,
       SUM(oi.quantity) AS total_quantity_sold
FROM order_items oi
JOIN menu_items m ON oi.item_id = m.item_id
GROUP BY m.item_id, m.name
ORDER BY total_quantity_sold DESC
LIMIT 1;

-- (Optional list of top 10 items)
-- SELECT m.name, SUM(oi.quantity) qty FROM order_items oi JOIN menu_items m ON oi.item_id=m.item_id
-- GROUP BY m.name ORDER BY qty DESC LIMIT 10;

-- 4. Average order value (all orders)
SELECT ROUND(AVG(total_amount),2) AS avg_order_value
FROM orders;

-- 5. Busiest hours of the day (by order count)
SELECT EXTRACT(HOUR FROM order_date) AS hour_of_day,
       COUNT(*) AS orders_count
FROM orders
GROUP BY hour_of_day
ORDER BY orders_count DESC;



-- 6. Busiest hour per store
WITH hourly AS (
  SELECT 
    store_id, 
    EXTRACT(HOUR FROM order_date) AS hr, 
    COUNT(*) AS cnt
  FROM orders
  GROUP BY store_id, hr
),
ranked AS (
  SELECT 
    h.store_id, 
    s.city, 
    h.hr AS hour_of_day, 
    h.cnt AS orders_count,
    RANK() OVER (PARTITION BY h.store_id ORDER BY h.cnt DESC) AS rnk
  FROM hourly h 
  JOIN stores s ON h.store_id = s.store_id
)
SELECT 
  store_id, 
  city, 
  hour_of_day, 
  orders_count
FROM ranked
WHERE rnk = 1
ORDER BY orders_count DESC;