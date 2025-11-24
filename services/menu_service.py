from psycopg2.extras import RealDictCursor
from .db import connect


def get_menu_items():
    with connect() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT item_id, name, category, size, box_price, slice_price
            FROM menu_items
            ORDER BY item_id ASC
        """
        )
        rows = cur.fetchall()
    return [
        {
            "item_id": int(r["item_id"]),
            "name": r["name"],
            "category": r["category"],
            "size": r["size"],
            "box_price": float(r["box_price"] or 0),
            "slice_price": float(r["slice_price"] or 0),
        }
        for r in rows
    ]


def get_stores():
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT store_id, city FROM stores ORDER BY store_id;")
        return [{"store_id": r[0], "city": r[1]} for r in cur.fetchall()]
