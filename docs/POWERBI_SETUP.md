# Power BI Connection to Azure PostgreSQL

## Prerequisites
- Power BI Desktop installed
- Access to Azure PostgreSQL server
- Database credentials from Azure Key Vault

## Connection Steps

### 1. Get Database Connection Details
```bash
az postgres flexible-server show \
  --resource-group rg-rushmorepizza-prod \
  --name <your-postgres-server-name> \
  --query "{fqdn:fullyQualifiedDomainName}" -o tsv
```

### 2. Open Power BI Desktop
1. Click **Get Data** → **Database** → **PostgreSQL database**
2. Enter connection details:
   - **Server**: `<server-name>.postgres.database.azure.com`
   - **Database**: `rushmore_db`
   - **Data Connectivity mode**: Import

### 3. Enter Credentials
1. Select **Database** authentication
2. **User name**: `rushmoreadmin`
3. **Password**: (from Azure Key Vault secret)

### 4. Load Tables
Select the following tables:
- `menu_items`
- `stores`
- `customers`
- `orders`
- `order_lines`

### 5. Create Relationships
Power BI should auto-detect relationships, but verify:
- `orders.store_id` → `stores.store_id`
- `orders.customer_id` → `customers.customer_id`
- `order_lines.order_id` → `orders.order_id`
- `order_lines.item_id` → `menu_items.item_id`

### 6. Create Measures

```dax
Total Revenue = SUM(orders[total_amount])
Total Orders = COUNTROWS(orders)
Average Order Value = DIVIDE([Total Revenue], [Total Orders])
Total Customers = DISTINCTCOUNT(orders[customer_id])
```

### 7. Build Dashboards
Create visualizations for:
- Revenue by Store (Map/Bar Chart)
- Top Customers (Table)
- Popular Menu Items (Bar Chart)
- Busiest Hours (Line Chart)
- Payment Method Distribution (Pie Chart)