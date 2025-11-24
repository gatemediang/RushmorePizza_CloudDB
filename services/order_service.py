import datetime
from psycopg2.extras import execute_values
from .db import connect


def _price_map(cur):
    cur.execute("SELECT item_id, box_price, slice_price FROM menu_items;")
    return {r[0]: {"box": float(r[1]), "slice": float(r[2])} for r in cur.fetchall()}


def place_order(
    customer_id,
    store_id,
    items,
    payment_method="cash",
    ordered_at=None,
    potd_item_id=None,
    potd_discount_percent=25.0,
):
    """
    items: list of {item_id:int, order_type:'Box'|'Slice', quantity:int}
    returns: {order_id, total_amount: float, lines: int}
    """
    if not items:
        raise ValueError("items cannot be empty")
    ordered_at = ordered_at or datetime.datetime.now(datetime.timezone.utc)

    with connect() as conn, conn.cursor() as cur:
        # Validate store and customer (customer_id may be None)
        cur.execute("SELECT 1 FROM stores WHERE store_id=%s", (store_id,))
        if cur.fetchone() is None:
            raise ValueError(f"store_id {store_id} not found")
        if customer_id is not None:
            cur.execute("SELECT 1 FROM customers WHERE customer_id=%s", (customer_id,))
            if cur.fetchone() is None:
                raise ValueError(f"customer_id {customer_id} not found")

        prices = _price_map(cur)

        cur.execute(
            "INSERT INTO orders (customer_id, store_id, order_timestamp, total_amount, payment_method, status) "
            "VALUES (%s,%s,%s,%s,%s,%s) RETURNING order_id",
            (customer_id, store_id, ordered_at, 0.00, payment_method, "completed"),
        )
        order_id = cur.fetchone()[0]

        rows, total = [], 0.0
        for it in items:
            iid = int(it["item_id"])
            otype = str(it["order_type"])
            qty = int(it["quantity"])
            if otype not in ("Box", "Slice"):
                raise ValueError("order_type must be 'Box' or 'Slice'")
            unit_price = prices[iid]["box"] if otype == "Box" else prices[iid]["slice"]
            # Prevent zero-priced lines (e.g., Box for slice-only items)
            if unit_price <= 0:
                raise ValueError(f"{otype} not available for item_id {iid}")

            # Apply POTD 25% off for Box orders of the selected item
            disc_pct = 0.0
            disc_amt = 0.0
            if otype == "Box" and potd_item_id is not None and iid == int(potd_item_id):
                disc_pct = float(potd_discount_percent)
                disc_amt = round(unit_price * qty * (disc_pct / 100.0), 2)

            line_total = round(unit_price * qty - disc_amt, 2)
            rows.append(
                (
                    order_id,
                    iid,
                    otype,
                    qty,
                    unit_price,
                    disc_pct,
                    disc_amt,
                    line_total,
                    "Pizza of the Day" if disc_pct > 0 else None,
                )
            )
            total += line_total

        execute_values(
            cur,
            "INSERT INTO order_items (order_id,item_id,order_type,quantity,unit_price,discount_percent,discount_amount,line_total,discount_reason) VALUES %s",
            rows,
        )
        cur.execute(
            "UPDATE orders SET total_amount=%s WHERE order_id=%s",
            (round(total, 2), order_id),
        )
        conn.commit()  # ensure persistence
        return {
            "order_id": order_id,
            "total_amount": round(total, 2),
            "lines": len(rows),
        }
