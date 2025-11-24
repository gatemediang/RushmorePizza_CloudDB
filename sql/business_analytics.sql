-- 1. Total sales revenue per store
SELECT 
    s.store_id,
    s.city,
    s.state,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(o.total_amount) as total_revenue,
    AVG(o.total_amount) as avg_order_value
FROM stores s
LEFT JOIN orders o ON s.store_id = o.store_id
GROUP BY s.store_id, s.city, s.state
ORDER BY total_revenue DESC;

-- 2. Top 10 most valuable customers (by total spending)
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(o.total_amount) as total_spent,
    AVG(o.total_amount) as avg_order_value,
    MAX(o.order_date) as last_order_date
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email
ORDER BY total_spent DESC
LIMIT 10;

-- 3. Most popular menu item (by quantity sold) across all stores
SELECT 
    m.item_id,
    m.name,
    m.category,
    m.size,
    SUM(ol.quantity) as total_quantity_sold,
    COUNT(DISTINCT ol.order_id) as times_ordered,
    SUM(ol.line_total) as total_revenue
FROM menu_items m
JOIN order_lines ol ON m.item_id = ol.item_id
GROUP BY m.item_id, m.name, m.category, m.size
ORDER BY total_quantity_sold DESC
LIMIT 1;

-- 4. Average order value
SELECT 
    AVG(total_amount) as average_order_value,
    MIN(total_amount) as min_order_value,
    MAX(total_amount) as max_order_value,
    STDDEV(total_amount) as stddev_order_value
FROM orders;

-- 5. Busiest hours of the day for orders
SELECT 
    EXTRACT(HOUR FROM order_date) as hour_of_day,
    COUNT(order_id) as total_orders,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value
FROM orders
GROUP BY EXTRACT(HOUR FROM order_date)
ORDER BY total_orders DESC;

-- Additional Analytics Queries

-- 6. Revenue by payment method
SELECT 
    payment_method,
    COUNT(order_id) as total_orders,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value,
    ROUND(100.0 * COUNT(order_id) / SUM(COUNT(order_id)) OVER (), 2) as percentage_of_orders
FROM orders
GROUP BY payment_method
ORDER BY total_revenue DESC;

-- 7. Best selling items by category
SELECT 
    m.category,
    m.name,
    SUM(ol.quantity) as total_sold,
    SUM(ol.line_total) as revenue,
    RANK() OVER (PARTITION BY m.category ORDER BY SUM(ol.quantity) DESC) as rank_in_category
FROM menu_items m
JOIN order_lines ol ON m.item_id = ol.item_id
GROUP BY m.category, m.name, m.item_id
ORDER BY m.category, total_sold DESC;

-- 8. Customer retention analysis
SELECT 
    CASE 
        WHEN order_count = 1 THEN 'One-time'
        WHEN order_count BETWEEN 2 AND 5 THEN 'Occasional'
        WHEN order_count > 5 THEN 'Loyal'
    END as customer_segment,
    COUNT(customer_id) as customer_count,
    SUM(total_spent) as segment_revenue,
    AVG(total_spent) as avg_customer_value
FROM (
    SELECT 
        customer_id,
        COUNT(order_id) as order_count,
        SUM(total_amount) as total_spent
    FROM orders
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
) customer_stats
GROUP BY customer_segment
ORDER BY segment_revenue DESC;