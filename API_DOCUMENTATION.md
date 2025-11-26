# RushMore Pizza API Documentation

## Base URLs

- **Production:** `http://rushmorepizza-aci-kb55ghrh.uksouth.azurecontainer.io:8000`
- **Local Development:** `http://localhost:8000`

---

## General Information

- All endpoints return JSON responses.
- No authentication required for current endpoints.
- Standard HTTP status codes are used (`200`, `201`, `400`, `404`, `500`).

---

## Health Check

### `GET /health`

**Description:**  
Check if the API is running.

**Response:**
```json
{ "status": "ok" }
```

---

## Menu Endpoints

### `GET /menu`

**Description:**  
Retrieve all menu items.

**Response Example:**
```json
[
  {
    "item_id": 1,
    "name": "Margherita",
    "category": "Pizza",
    "size": "Medium",
    "box_price": 12.99,
    "slice_price": 2.50
  }
]
```

---

## Store Endpoints

### `GET /stores`

**Description:**  
Retrieve all store locations.

**Response Example:**
```json
[
  {
    "store_id": 1,
    "address": "123 Main St",
    "city": "London",
    "phone_number": "020-1234-5678",
    "opened_at": "2024-01-01T00:00:00Z"
  }
]
```

---

## Customer Endpoints

### `GET /customers`

**Description:**  
Retrieve all customers.

**Response Example:**
```json
[
  {
    "customer_id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": "07123-456789",
    "created_at": "2024-01-01T10:00:00Z"
  }
]
```

---

## Order Endpoints

### `GET /orders`

**Description:**  
Retrieve all orders.  
Supports optional query parameters: `store_id`, `customer_id`.

**Query Example:**
```
GET /orders?store_id=1
GET /orders?customer_id=5
```

**Response Example:**
```json
[
  {
    "order_id": 101,
    "customer_id": 1,
    "store_id": 1,
    "order_timestamp": "2025-11-26T12:00:00Z",
    "total_amount": 25.50,
    "payment_method": "card",
    "status": "completed"
  }
]
```

---

### `POST /orders`

**Description:**  
Create a new order.

**Request Body:**
```json
{
  "store_id": 1,
  "customer_id": 1,
  "items": [
    {
      "item_id": 5,
      "order_type": "Box",
      "quantity": 2
    }
  ],
  "payment_method": "card"
}
```

**Response Example:**
```json
{
  "order_id": 102,
  "total_amount": 23.99,
  "lines": 1
}
```

**Error Response Example:**
```json
{
  "detail": "Invalid store_id"
}
```

---

## Analytics Endpoints

### `GET /analytics/revenue-by-store`

**Description:**  
Get total revenue per store.

**Response Example:**
```json
[
  {
    "store_id": 1,
    "city": "London",
    "order_count": 120,
    "total_revenue": 2500.00,
    "avg_order_value_store": 20.83
  }
]
```

---

### `GET /analytics/top-customers`

**Description:**  
Get top 10 customers by spending.

**Response Example:**
```json
[
  {
    "customer_id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "orders_placed": 15,
    "total_spent": 350.00,
    "avg_order_value_customer": 23.33
  }
]
```

---

### `GET /analytics/popular-items`

**Description:**  
Get most popular menu items.

**Response Example:**
```json
[
  {
    "item_id": 5,
    "name": "Pepperoni",
    "total_quantity_sold": 200
  }
]
```

---

### `GET /analytics/busiest-hours`

**Description:**  
Get order volume by hour of day.

**Response Example:**
```json
[
  {
    "hour_of_day": 18,
    "orders_count": 35
  }
]
```

---

### `GET /analytics/average-order-value`

**Description:**  
Get average order value.

**Response Example:**
```json
{
  "avg_order_value": 21.50
}
```

---

## Error Handling

- All errors return a JSON object with a `detail` field.
- Example:
  ```json
  { "detail": "Resource not found" }
  ```

---

## Interactive Documentation

- **Swagger UI:**  
  [http://rushmorepizza-aci-kb55ghrh.uksouth.azurecontainer.io:8000/docs](http://rushmorepizza-aci-kb55ghrh.uksouth.azurecontainer.io:8000/docs)
- **ReDoc:**  
  [http://rushmorepizza-aci-kb55ghrh.uksouth.azurecontainer.io:8000/redoc](http://rushmorepizza-aci-kb55ghrh.uksouth.azurecontainer.io:8000/redoc)

---

## Example Usage

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://rushmorepizza-aci-kb55ghrh.uksouth.azurecontainer.io:8000/menu"
Invoke-RestMethod -Uri "http://rushmorepizza-aci-kb55ghrh.uksouth.azurecontainer.io:8000/stores"
```

**Python:**
```python
import requests
BASE_URL = "http://rushmorepizza-aci-kb55ghrh.uksouth.azurecontainer.io:8000"
menu = requests.get(f"{BASE_URL}/menu").json()
stores = requests.get(f"{BASE_URL}/stores").json()
```

**cURL:**
```bash
curl http://rushmorepizza-aci-kb55ghrh.uksouth.azurecontainer.io:8000/menu
curl http://rushmorepizza-aci-kb55ghrh.uksouth.azurecontainer.io:8000/stores
```

---

## Version

- **API Version:** 1.0.0
- **Last Updated:** November 26, 2025

---

## Contact

- Maintainer: Tunji Ologun
- Email: tunjiologun@gmail.com
- GitHub: [https://github.com/yourusername/RushmorePizza_CloudDB](https://github.com/yourusername/RushmorePizza_CloudDB)

---

**For more details, see the [README.md](./README.md)**