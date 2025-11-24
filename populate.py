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
NUM_STORES = int(os.getenv("NUM_STORES", "4"))
NUM_MENU = int(os.getenv("NUM_MENU", "24"))
NUM_ING = int(os.getenv("NUM_ING", "45"))
NUM_CUSTOMERS = int(os.getenv("NUM_CUSTOMERS", "1200"))
NUM_ORDERS = int(os.getenv("NUM_ORDERS", "6000"))
RESET_DB = os.getenv("RESET_DB", "0") == "1"

# NEW: control items-per-order (defaults target avg ≈ 3)
ORDER_LINES_MIN = int(os.getenv("ORDER_LINES_MIN", "2"))
ORDER_LINES_MAX = int(os.getenv("ORDER_LINES_MAX", "4"))

fake = Faker()
Faker.seed(42)
random.seed(42)


def safe_varchar(val: str, max_len: int) -> str:
    return (val or "")[:max_len]


def unique_phone():
    # Fixed-length <= 20 (12 chars like 555-123-4567)
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


def chunked(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def main():
    conn = connect()
    cur = conn.cursor()
    try:
        if RESET_DB:
            cur.execute(
                """
                TRUNCATE order_items, orders, menu_item_ingredients,
                         menu_items, ingredients, customers, stores
                RESTART IDENTITY CASCADE;
            """
            )
            conn.commit()

        # 1) Stores
        fake.unique.clear()
        stores = [
            (
                fake.street_address(),
                fake.city(),
                safe_varchar(unique_phone(), 20),
                fake.date_time_this_year(tzinfo=datetime.timezone.utc),
            )
            for _ in range(NUM_STORES)
        ]
        bulk_insert(
            cur,
            "INSERT INTO stores (address, city, phone_number, opened_at) VALUES %s",
            stores,
        )

        # 2) Ingredients (example placeholder)
        fake.unique.clear()
        ingredients = [(f"Ingredient {i}",) for i in range(1, 6)]
        bulk_insert(cur, "INSERT INTO ingredients (name) VALUES %s", ingredients)

        conn.commit()
        print("Database populated.")
    except Exception as e:
        conn.rollback()
        print(f"Populate failed: {e}")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
