# Power BI Connection to Azure PostgreSQL

## Prerequisites
- Power BI Desktop installed
- Azure CLI installed and authenticated
- Access to Azure Key Vault: `kv-rushmorepizzakb55ghrh`
- Your local IP added to PostgreSQL firewall rules

## Connection Steps

### 1. Add Your IP to PostgreSQL Firewall

```bash
# Get your public IP
MY_IP=$(curl -s https://api.ipify.org)
echo "Your IP: $MY_IP"

# Add firewall rule
az postgres flexible-server firewall-rule create \
  --resource-group rg-rushmorepizza-prod \
  --name rushmorepizza-pg-kb55ghrh \
  --rule-name "AllowMyIP-$(date +%Y%m%d)" \
  --start-ip-address $MY_IP \
  --end-ip-address $MY_IP
```

### 2. Retrieve Database Password from Key Vault

**🔒 Security Best Practice**: Always retrieve passwords from Azure Key Vault instead of hardcoding them.

```bash
# Retrieve password securely
az keyvault secret show \
  --vault-name kv-rushmorepizzakb55ghrh \
  --name db-password \
  --query value \
  --output tsv
```

**Copy this password** - you'll need it for Power BI connection.

### 3. Get Database Connection Details

```bash
# Get PostgreSQL server FQDN
az postgres flexible-server show \
  --resource-group rg-rushmorepizza-prod \
  --name rushmorepizza-pg-kb55ghrh \
  --query "fullyQualifiedDomainName" \
  --output tsv
```

**Connection Details:**
- **Server**: `rushmorepizza-pg-kb55ghrh.postgres.database.azure.com`
- **Database**: `rushmore_db`
- **Port**: `5432`
- **Username**: `rushmoreadmin`
- **Password**: Retrieved from Key Vault in step 2
- **SSL Mode**: Required

### 4. Connect Power BI Desktop

1. Open **Power BI Desktop**
2. Click **Get Data** → **More** → **Database** → **PostgreSQL database**
3. Enter connection details:
   - **Server**: `rushmorepizza-pg-kb55ghrh.postgres.database.azure.com`
   - **Database**: `rushmore_db`
   - **Data Connectivity mode**: Import (recommended for better performance)

4. Click **Advanced options** to paste custom SQL queries from `analytics.sql`

### 5. Enter Credentials

1. Select **Database** authentication mode
2. **User name**: `rushmoreadmin`
3. **Password**: Paste the password retrieved from Key Vault
4. Click **Connect**

### 6. Load Data

#### Option A: Import Tables (for full data model)
Select these tables:
- `menu_items` - Pizza menu with prices
- `stores` - Store locations
- `customers` - Customer information
- `orders` - Order headers
- `order_items` - Order line items

#### Option B: Use Custom SQL Queries (for analytics)
Paste queries from `analytics.sql`:

**Query 1: Revenue per Store**
```sql
SELECT s.store_id,
       s.city,
       COUNT(o.order_id) AS total_orders,
       ROUND(SUM(o.total_amount), 2) AS total_revenue,
       ROUND(AVG(o.total_amount), 2) AS avg_order_value
FROM orders o
JOIN stores s ON o.store_id = s.store_id
GROUP BY s.store_id, s.city
ORDER BY total_revenue DESC;
```

**Query 2: Top Customers**
```sql
SELECT c.customer_id,
       CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
       c.email,
       COUNT(o.order_id) AS total_orders,
       ROUND(SUM(o.total_amount), 2) AS total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email
ORDER BY total_spent DESC
LIMIT 10;
```

**Query 3: Popular Menu Items**
```sql
SELECT mi.item_id,
       mi.name,
       mi.category,
       COUNT(oi.order_item_id) AS times_ordered,
       SUM(oi.quantity) AS total_quantity,
       ROUND(SUM(oi.quantity * oi.price), 2) AS total_revenue
FROM menu_items mi
JOIN order_items oi ON mi.item_id = oi.item_id
GROUP BY mi.item_id, mi.name, mi.category
ORDER BY times_ordered DESC
LIMIT 10;
```

**Query 4: Average Order Value**
```sql
SELECT ROUND(AVG(total_amount), 2) AS avg_order_value,
       ROUND(MIN(total_amount), 2) AS min_order,
       ROUND(MAX(total_amount), 2) AS max_order,
       COUNT(*) AS total_orders
FROM orders;
```

**Query 5: Busiest Hours**
```sql
SELECT EXTRACT(HOUR FROM order_date) AS hour_of_day,
       COUNT(order_id) AS order_count,
       ROUND(AVG(total_amount), 2) AS avg_order_value
FROM orders
GROUP BY EXTRACT(HOUR FROM order_date)
ORDER BY hour_of_day;
```

### 7. Create Relationships (if using tables)

Power BI should auto-detect relationships. Verify:
- `orders.store_id` → `stores.store_id` (Many-to-One)
- `orders.customer_id` → `customers.customer_id` (Many-to-One)
- `order_items.order_id` → `orders.order_id` (Many-to-One)
- `order_items.item_id` → `menu_items.item_id` (Many-to-One)

### 8. Create DAX Measures

```dax
// Financial Metrics
Total Revenue = SUM(orders[total_amount])
Total Orders = COUNTROWS(orders)
Average Order Value = DIVIDE([Total Revenue], [Total Orders], 0)

// Customer Metrics
Total Customers = DISTINCTCOUNT(orders[customer_id])
Orders per Customer = DIVIDE([Total Orders], [Total Customers], 0)

// Product Metrics
Total Items Sold = SUM(order_items[quantity])
Average Items per Order = DIVIDE([Total Items Sold], [Total Orders], 0)

// Store Performance
Top Store Revenue = 
    CALCULATE(
        [Total Revenue],
        TOPN(1, ALL(stores[city]), [Total Revenue], DESC)
    )

// Time Intelligence (if date table exists)
Revenue YTD = TOTALYTD([Total Revenue], 'Date'[Date])
Revenue vs Previous Month = 
    [Total Revenue] - CALCULATE([Total Revenue], DATEADD('Date'[Date], -1, MONTH))
```

### 9. Build Dashboard Visualizations

**Page 1: Executive Summary**
- Card: Total Revenue
- Card: Total Orders
- Card: Average Order Value
- Card: Total Customers
- Line Chart: Revenue Trend over Time
- Bar Chart: Revenue by Store (sorted descending)

**Page 2: Store Performance**
- Map: Store locations with revenue as bubble size
- Table: Store details (City, Orders, Revenue, Avg Order Value)
- Clustered Column Chart: Orders by Store
- Pie Chart: Payment Method Distribution

**Page 3: Customer Insights**
- Table: Top 10 Customers by Revenue
- Scatter Chart: Order Count vs Total Spent
- Histogram: Customer Order Frequency
- Bar Chart: Revenue by Customer Segment

**Page 4: Menu Analytics**
- Bar Chart: Top 10 Menu Items by Quantity
- Tree Map: Revenue by Category
- Matrix: Item Performance (Name, Category, Orders, Revenue)
- Donut Chart: Sales by Pizza Size

**Page 5: Operational Insights**
- Line Chart: Orders by Hour of Day
- Clustered Bar Chart: Peak vs Off-Peak Revenue
- Gauge: Average Order Preparation Time (if available)
- KPI: Order fulfillment rate

### 10. Apply Slicers and Filters

Add slicers for:
- Date Range (order_date)
- Store Location (city)
- Payment Method
- Menu Category
- Customer Type (if segmented)

### 11. Schedule Data Refresh

For automatic updates:
1. Publish report to Power BI Service
2. Configure scheduled refresh
3. Ensure Power BI gateway can access Azure PostgreSQL
4. Set refresh frequency (e.g., daily at 6 AM)

## Troubleshooting

### Connection Timeout
```bash
# Verify firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group rg-rushmorepizza-prod \
  --name rushmorepizza-pg-kb55ghrh \
  --output table

# Your IP might have changed - update the rule
```

### Authentication Failed
```bash
# Verify password in Key Vault
az keyvault secret show \
  --vault-name kv-rushmorepizzakb55ghrh \
  --name db-password \
  --query value \
  --output tsv
```

### SSL Connection Required
- Ensure SSL mode is set to "require" in Power BI connection settings
- Azure PostgreSQL Flexible Server requires SSL by default

## Security Best Practices

✅ **DO:**
- Store passwords in Azure Key Vault
- Use firewall rules to restrict database access
- Use SSL/TLS for database connections
- Rotate passwords regularly
- Use Azure RBAC for Key Vault access

❌ **DON'T:**
- Hardcode passwords in code or documentation
- Share passwords via email or chat
- Allow public access (0.0.0.0/0) to database
- Commit credentials to version control

## Additional Resources

- [Azure PostgreSQL Documentation](https://learn.microsoft.com/en-us/azure/postgresql/)
- [Power BI PostgreSQL Connector](https://learn.microsoft.com/en-us/power-query/connectors/postgresql)
- [Azure Key Vault Best Practices](https://learn.microsoft.com/en-us/azure/key-vault/general/best-practices)