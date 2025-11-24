import os
import sys
import logging
import random
import argparse
from typing import List, Dict, Optional

# Load environment variables FIRST
from dotenv import load_dotenv

load_dotenv()

import requests  # API mode
from services.menu_service import get_menu_items, get_stores
from services.order_service import place_order

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

CURRENCY = "£"
PIZZA_OF_DAY_OVERRIDE = os.getenv("PIZZA_OF_THE_DAY")  # e.g., "Pepperoni"
API_BASE_URL: Optional[str] = None  # set from --api or env

# --- API helpers ------------------------------------------------------------


def _use_api() -> bool:
    return bool(API_BASE_URL)


def _api_get(path: str):
    r = requests.get(API_BASE_URL.rstrip("/") + path, timeout=10)
    r.raise_for_status()
    return r.json()


def _api_post(path: str, payload: dict):
    r = requests.post(API_BASE_URL.rstrip("/") + path, json=payload, timeout=15)
    r.raise_for_status()
    return r.json()


def _fetch_menu() -> List[Dict]:
    return _api_get("/menu") if _use_api() else get_menu_items()


def _fetch_stores() -> List[Dict]:
    # Falls back to direct DB call if API /stores is not available
    try:
        return _api_get("/stores") if _use_api() else get_stores()
    except requests.HTTPError:
        return get_stores()


def _submit_order(
    store_id: int, items: List[Dict], payment: str, potd_id: Optional[int]
):
    if _use_api():
        payload = {
            "store_id": store_id,
            "customer_id": None,
            "payment_method": payment,
            "items": items,
        }
        # API already applies PoTD server-side if implemented; keep payload clean
        return _api_post("/orders", payload)
    # Direct service path
    kwargs = {}
    if potd_id:
        kwargs["potd_item_id"] = potd_id
        kwargs["potd_discount_percent"] = 25.0
    try:
        return place_order(
            customer_id=None,
            store_id=store_id,
            items=items,
            payment_method=payment,
            **kwargs,
        )
    except TypeError:
        return place_order(
            customer_id=None, store_id=store_id, items=items, payment_method=payment
        )


# --- Helpers ----------------------------------------------------------------


def _sanitize_menu(items: List[Dict]) -> List[Dict]:
    for it in items:
        it["item_id"] = int(it["item_id"])
        it["box_price"] = float(it.get("box_price") or 0.0)
        it["slice_price"] = float(it.get("slice_price") or 0.0)
        it["category"] = it.get("category") or ""
        it["name"] = it.get("name") or ""
        it["size"] = it.get("size") or "N/A"
    return items


def load_menu_from_db() -> List[Dict]:
    items = _fetch_menu()
    return sorted(_sanitize_menu(items), key=lambda x: x["item_id"])


def _pick_pizza_of_the_day(menu: List[Dict]) -> Optional[Dict]:
    pizzas = [
        m for m in menu if m["category"].lower() == "pizza" and m["box_price"] > 0
    ]
    if not pizzas:
        return None
    if PIZZA_OF_DAY_OVERRIDE:
        for m in pizzas:
            if m["name"].strip().lower() == PIZZA_OF_DAY_OVERRIDE.strip().lower():
                return m
    return random.choice(pizzas)


def print_menu(menu: List[Dict], potd_id: Optional[int]) -> None:
    print("\n---- RushMore Pizza Menu ----")
    for m in menu:
        box = f"{CURRENCY}{m['box_price']:.2f}" if m["box_price"] > 0 else "N/A"
        slc = f"{CURRENCY}{m['slice_price']:.2f}" if m["slice_price"] > 0 else "N/A"
        tag = " [POTD -25% on Box]" if potd_id and m["item_id"] == potd_id else ""
        print(
            f"{m['item_id']:>2} | {m['name']} [{m['size']}]  Box: {box}  Slice: {slc}{tag}"
        )
    print("-----------------------------\n")


def _choose_store_id() -> int:
    stores = _fetch_stores()
    if not stores:
        raise RuntimeError("No stores available.")
    print("Available stores:")
    for s in stores:
        print(f"{s['store_id']}: {s.get('city','Store')}")
    while True:
        s_in = input("Select store_id: ").strip()
        if s_in.isdigit() and any(s["store_id"] == int(s_in) for s in stores):
            return int(s_in)
        print("Invalid store_id, try again.")


# --- Single-order flow ------------------------------------------------------


def order_single_item_flow(menu: List[Dict], potd_id: Optional[int]) -> None:
    id_map = {m["item_id"]: m for m in menu}

    # 1) Pick item by id
    while True:
        raw = input("Enter item_id (or 'q' to quit): ").strip().lower()
        if raw == "q":
            print("Goodbye!")
            sys.exit(0)
        if raw.isdigit() and int(raw) in id_map:
            item_id = int(raw)
            break
        print("Invalid item_id, try again.")
    item = id_map[item_id]

    # 2) Ask Box/Slice based on availability
    has_box = item["box_price"] > 0
    has_slice = item["slice_price"] > 0
    if not (has_box or has_slice):
        print("This item is not available to order.")
        return

    if has_box and has_slice:
        order_type = input("Box or Slice? ").strip().title()
        while order_type not in ("Box", "Slice"):
            order_type = input("Enter 'Box' or 'Slice': ").strip().title()
    elif has_box:
        print("Only Box available for this item.")
        order_type = "Box"
    else:
        print("Only Slice available for this item.")
        order_type = "Slice"

    # 3) Quantity
    while True:
        qraw = input("Quantity: ").strip()
        if qraw.isdigit() and int(qraw) > 0:
            quantity = int(qraw)
            break
        print("Enter a positive integer.")

    # 4) Store ID
    store_id = _choose_store_id()

    payment_method = "cash"
    # 5) Compute expected total (client-side) and place order
    unit_price = item["box_price"] if order_type == "Box" else item["slice_price"]
    if potd_id and item["item_id"] == potd_id and order_type == "Box":
        unit_price *= 0.75  # 25% off POTD box
        print("Pizza of the Day selected — 25% discount applies.")
    expected_total = unit_price * quantity
    print(f"Expected total: {CURRENCY}{expected_total:.2f}")
    cart = [
        {"item_id": item["item_id"], "order_type": order_type, "quantity": quantity}
    ]
    try:
        res = _submit_order(
            store_id=store_id, items=cart, payment=payment_method, potd_id=potd_id
        )
        print(
            f"Order placed! ID: {res['order_id']}  Total: {CURRENCY}{res['total_amount']:.2f}  Lines: {res['lines']}"
        )
    except Exception as e:
        logging.exception("Order failed: %s", e)
        print(f"Order failed: {e}")


# --- CLI entry --------------------------------------------------------------


def main_system():
    print("🍕 Welcome to RushMore Pizzeria 🍕")
    try:
        menu = load_menu_from_db()
    except Exception as e:
        logging.exception("Failed to load menu: %s", e)
        print("Failed to load menu from database. Check env vars and DB connection.")
        return

    potd = _pick_pizza_of_the_day(menu)
    potd_id = potd["item_id"] if potd else None
    if potd:
        print(f"🌟 Pizza of the Day: {potd['name']} - 25% off on Box orders! 🌟")

    print_menu(menu, potd_id)

    while True:
        order_single_item_flow(menu, potd_id)
        again = input("Place another order? [y/N]: ").strip().lower()
        if again not in ("y", "yes"):
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RushMore Pizza CLI")
    parser.add_argument(
        "--api",
        help="Base URL for FastAPI (e.g. http://127.0.0.1:8000)",
        default=os.getenv("API_BASE_URL"),
    )
    args = parser.parse_args()
    API_BASE_URL = args.api
    try:
        main_system()
    except KeyboardInterrupt:
        sys.exit(0)
