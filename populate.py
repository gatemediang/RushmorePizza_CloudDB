# populate.py
"""
Populate RushMore PostgreSQL with masked test data.
Usage: fill .env file (or set environment variables), then:
$ python populate.py
"""

import os, random, datetime
import psycopg2
from faker import Faker
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "5434"))
DB_NAME = os.getenv("DB_NAME", "rushmore_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
SSL_MODE = os.getenv("SSL_MODE", "disable")

# Default volumes (override via .env or shell)
NUM_STORES = int(os.getenv("NUM_STORES", "5"))
NUM_MENU = int(os.getenv("NUM_MENU", "24"))
NUM_CUSTOMERS = int(os.getenv("NUM_CUSTOMERS", "1200"))
NUM_ORDERS = int(os.getenv("NUM_ORDERS", "6000"))
RESET_DB = os.getenv("RESET_DB", "0") == "1"

# Control items-per-order (defaults target avg ≈ 3)
ORDER_LINES_MIN = int(os.getenv("ORDER_LINES_MIN", "2"))
ORDER_LINES_MAX = int(os.getenv("ORDER_LINES_MAX", "4"))

fake = Faker()
Faker.seed(42)
random.seed(42)


def safe_varchar(val: str, max_len: int) -> str:
    return (val or "")[:max_len]


def unique_phone():
    """Generate unique phone number in format XXX-XXX-XXXX"""
    return fake.unique.bothify("###-###-####")


def connect():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode=SSL_MODE,
    )


def bulk_insert(cur, sql, rows, page_size=1000):
    if not rows:
        return
    execute_values(cur, sql, rows, page_size=page_size)


# Pizza ingredient data based on project requirements
INGREDIENTS_DATA = [
    # Pizza bases
    ("Pizza Dough", 500.00, "kg"),
    ("Thin Crust Dough", 300.00, "kg"),
    ("Deep Dish Dough", 200.00, "kg"),
    # Cheeses
    ("Mozzarella Cheese", 450.00, "kg"),
    ("Cheddar Cheese", 200.00, "kg"),
    ("Parmesan Cheese", 150.00, "kg"),
    ("Feta Cheese", 100.00, "kg"),
    ("Ricotta Cheese", 120.00, "kg"),
    # Meats
    ("Pepperoni", 300.00, "kg"),
    ("Italian Sausage", 250.00, "kg"),
    ("Bacon", 180.00, "kg"),
    ("Ham", 200.00, "kg"),
    ("Ground Beef", 220.00, "kg"),
    ("Chicken Breast", 200.00, "kg"),
    ("Anchovies", 50.00, "kg"),
    # Vegetables
    ("Mushrooms", 150.00, "kg"),
    ("Bell Peppers", 180.00, "kg"),
    ("Onions", 200.00, "kg"),
    ("Black Olives", 100.00, "kg"),
    ("Green Olives", 100.00, "kg"),
    ("Tomatoes", 250.00, "kg"),
    ("Spinach", 120.00, "kg"),
    ("Jalapeños", 80.00, "kg"),
    ("Pineapple", 150.00, "kg"),
    ("Garlic", 60.00, "kg"),
    # Sauces & Seasonings
    ("Tomato Sauce", 400.00, "liters"),
    ("Marinara Sauce", 300.00, "liters"),
    ("BBQ Sauce", 150.00, "liters"),
    ("Alfredo Sauce", 200.00, "liters"),
    ("Pesto Sauce", 100.00, "liters"),
    ("Olive Oil", 200.00, "liters"),
    ("Oregano", 20.00, "kg"),
    ("Basil", 15.00, "kg"),
    ("Red Pepper Flakes", 10.00, "kg"),
    ("Garlic Powder", 25.00, "kg"),
    # Beverages
    ("Cola", 500.00, "liters"),
    ("Lemon Soda", 400.00, "liters"),
    ("Orange Juice", 300.00, "liters"),
    ("Bottled Water", 800.00, "units"),
    # Sides ingredients
    ("Buffalo Wings", 200.00, "kg"),
    ("Chicken Wings", 250.00, "kg"),
    ("Breadsticks Dough", 150.00, "kg"),
    ("Garlic Butter", 100.00, "kg"),
    ("Caesar Dressing", 80.00, "liters"),
    ("Ranch Dressing", 100.00, "liters"),
]

# Menu items with realistic pricing
MENU_ITEMS = [
    # Pizzas - Large
    ("Margherita Pizza", "Pizza", "Large", 12.99, 2.50),
    ("Pepperoni Pizza", "Pizza", "Large", 14.99, 3.00),
    ("Vegetarian Supreme", "Pizza", "Large", 13.99, 2.75),
    ("Meat Lovers", "Pizza", "Large", 16.99, 3.50),
    ("Hawaiian Pizza", "Pizza", "Large", 14.99, 3.00),
    ("BBQ Chicken Pizza", "Pizza", "Large", 15.99, 3.25),
    ("Four Cheese Pizza", "Pizza", "Large", 15.99, 3.25),
    ("Buffalo Chicken Pizza", "Pizza", "Large", 16.99, 3.50),
    # Pizzas - Medium
    ("Margherita Pizza", "Pizza", "Medium", 10.99, 2.00),
    ("Pepperoni Pizza", "Pizza", "Medium", 12.99, 2.50),
    ("Vegetarian Supreme", "Pizza", "Medium", 11.99, 2.25),
    ("Meat Lovers", "Pizza", "Medium", 14.99, 3.00),
    # Sides
    ("Garlic Breadsticks", "Sides", None, 5.99, 0.00),
    ("Buffalo Wings (10pcs)", "Sides", None, 9.99, 0.00),
    ("Chicken Wings (10pcs)", "Sides", None, 8.99, 0.00),
    ("Caesar Salad", "Sides", None, 6.99, 0.00),
    ("Garden Salad", "Sides", None, 5.99, 0.00),
    # Beverages
    ("Coca-Cola", "Beverage", "2L", 3.99, 0.00),
    ("Sprite", "Beverage", "2L", 3.99, 0.00),
    ("Orange Juice", "Beverage", "1L", 4.99, 0.00),
    ("Bottled Water", "Beverage", "500ml", 1.99, 0.00),
    # Desserts
    ("Chocolate Brownie", "Dessert", None, 4.99, 0.00),
    ("Cinnamon Sticks", "Dessert", None, 5.99, 0.00),
    ("Cheesecake Slice", "Dessert", None, 5.99, 0.00),
]


def main():
    conn = connect()
    cur = conn.cursor()

    try:
        if RESET_DB:
            print("Resetting database...")
            cur.execute(
                """
                TRUNCATE order_items, orders, menu_item_ingredients,
                         menu_items, ingredients, customers, stores
                RESTART IDENTITY CASCADE;
                """
            )
            conn.commit()
            print("✓ Database reset complete")

        # 1) Stores
        print(f"Populating {NUM_STORES} stores...")
        fake.unique.clear()
        stores = [
            (
                safe_varchar(fake.street_address(), 255),
                safe_varchar(fake.city(), 100),
                unique_phone(),
                fake.date_time_this_year(tzinfo=datetime.timezone.utc),
            )
            for _ in range(NUM_STORES)
        ]
        bulk_insert(
            cur,
            "INSERT INTO stores (address, city, phone_number, opened_at) VALUES %s",
            stores,
        )
        print(f"✓ {NUM_STORES} stores inserted")

        # 2) Ingredients
        print(f"Populating {len(INGREDIENTS_DATA)} ingredients...")
        bulk_insert(
            cur,
            "INSERT INTO ingredients (name, stock_quantity, unit) VALUES %s",
            INGREDIENTS_DATA,
        )
        print(f"✓ {len(INGREDIENTS_DATA)} ingredients inserted")

        # 3) Menu Items
        print(f"Populating {len(MENU_ITEMS)} menu items...")
        bulk_insert(
            cur,
            "INSERT INTO menu_items (name, category, size, box_price, slice_price) VALUES %s",
            MENU_ITEMS,
        )
        print(f"✓ {len(MENU_ITEMS)} menu items inserted")

        # 4) Menu Item Ingredients (simplified mapping)
        print("Creating menu item-ingredient relationships...")
        # Get ingredient and menu item IDs
        cur.execute(
            "SELECT ingredient_id FROM ingredients WHERE name IN ('Pizza Dough', 'Mozzarella Cheese', 'Tomato Sauce')"
        )
        base_ingredients = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT item_id FROM menu_items WHERE category = 'Pizza'")
        pizza_items = [row[0] for row in cur.fetchall()]

        # Link pizzas to base ingredients
        menu_item_ingredients = []
        for item_id in pizza_items:
            for ing_id in base_ingredients:
                menu_item_ingredients.append(
                    (item_id, ing_id, round(random.uniform(0.2, 0.5), 4), "kg")
                )

        if menu_item_ingredients:
            bulk_insert(
                cur,
                "INSERT INTO menu_item_ingredients (menu_item_id, ingredient_id, quantity_required, unit) VALUES %s",
                menu_item_ingredients,
            )
            print(f"✓ {len(menu_item_ingredients)} ingredient relationships created")

        # 5) Customers
        print(f"Populating {NUM_CUSTOMERS} customers...")
        fake.unique.clear()
        customers = []
        for _ in range(NUM_CUSTOMERS):
            first_name = safe_varchar(fake.first_name(), 100)
            last_name = safe_varchar(fake.last_name(), 100)
            email = safe_varchar(fake.unique.email(), 255)
            phone = unique_phone()
            created = fake.date_time_this_year(tzinfo=datetime.timezone.utc)
            customers.append((first_name, last_name, email, phone, created))

        bulk_insert(
            cur,
            "INSERT INTO customers (first_name, last_name, email, phone_number, created_at) VALUES %s",
            customers,
        )
        print(f"✓ {NUM_CUSTOMERS} customers inserted")

        # 6) Orders and Order Items
        print(f"Populating {NUM_ORDERS} orders...")
        cur.execute("SELECT item_id, box_price, slice_price, category FROM menu_items")
        menu_data = cur.fetchall()

        orders = []
        order_items = []

        for order_num in range(1, NUM_ORDERS + 1):
            customer_id = random.randint(1, NUM_CUSTOMERS)
            store_id = random.randint(1, NUM_STORES)
            order_time = fake.date_time_this_year(tzinfo=datetime.timezone.utc)
            payment = random.choice(["cash", "card", "online"])
            status = random.choice(["completed", "completed", "completed", "pending"])

            # Generate order lines
            num_lines = random.randint(ORDER_LINES_MIN, ORDER_LINES_MAX)
            line_items = random.sample(menu_data, min(num_lines, len(menu_data)))

            order_total = 0.0
            for item_id, box_price, slice_price, category in line_items:
                # Determine order type
                if category == "Pizza":
                    order_type = random.choice(["Box", "Slice", "Slice"])
                    unit_price = float(
                        box_price if order_type == "Box" else slice_price
                    )
                    qty = 1 if order_type == "Box" else random.randint(2, 4)
                else:
                    order_type = "Box"
                    unit_price = float(box_price)
                    qty = random.randint(1, 3)

                # Apply occasional discounts
                discount_pct = 0.0
                discount_reason = None
                if random.random() < 0.1:  # 10% chance of discount
                    discount_pct = random.choice([5.0, 10.0, 15.0])
                    discount_reason = random.choice(
                        ["Student", "Senior", "Loyalty", "Promotion"]
                    )

                discount_amt = round(unit_price * qty * discount_pct / 100, 2)
                line_total = round((unit_price * qty) - discount_amt, 2)
                order_total += line_total

                order_items.append(
                    (
                        order_num,
                        item_id,
                        order_type,
                        qty,
                        unit_price,
                        discount_pct,
                        discount_amt,
                        line_total,
                        discount_reason,
                    )
                )

            orders.append(
                (
                    customer_id,
                    store_id,
                    order_time,
                    round(order_total, 2),
                    payment,
                    status,
                )
            )

        # Insert orders
        bulk_insert(
            cur,
            "INSERT INTO orders (customer_id, store_id, order_timestamp, total_amount, payment_method, status) VALUES %s",
            orders,
        )
        print(f"✓ {NUM_ORDERS} orders inserted")

        # Insert order items
        bulk_insert(
            cur,
            """INSERT INTO order_items (order_id, item_id, order_type, quantity, unit_price, 
               discount_percent, discount_amount, line_total, discount_reason) VALUES %s""",
            order_items,
        )
        print(f"✓ {len(order_items)} order items inserted")

        conn.commit()
        print("\n" + "=" * 50)
        print("✓ Database populated successfully!")
        print("=" * 50)
        print(f"Stores: {NUM_STORES}")
        print(f"Ingredients: {len(INGREDIENTS_DATA)}")
        print(f"Menu Items: {len(MENU_ITEMS)}")
        print(f"Customers: {NUM_CUSTOMERS}")
        print(f"Orders: {NUM_ORDERS}")
        print(f"Order Items: {len(order_items)}")
        print("=" * 50)

    except Exception as e:
        conn.rollback()
        print(f"✗ Populate failed: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
