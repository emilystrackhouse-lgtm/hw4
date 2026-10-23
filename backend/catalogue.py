"""Reads products and stock from the database.

Shared by the product pages (main.py) and the chatbot's tools (tools.py), so the
website and the assistant always see the same names, prices, and stock.
"""

from __future__ import annotations

import json
import re
import sqlite3

from db import query
from models import InventoryItem, Product, ProductDetail, StyleName

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]

# The style groups shoppers browse by, matching the website's filter chips.
STYLES: dict[StyleName, list[str]] = {
    "T-Shirts": ["short-sleeve t-shirt"],
    "Long Sleeves": ["long-sleeve performance shirt", "mockneck sweatshirt"],
    "Crewnecks": ["crewneck sweatshirt"],
    "Hoodies": ["pullover hoodie", "full-zip hoodie"],
    "Quarter-Zips": ["quarter-zip pullover"],
    "Fleece & Outerwear": ["full-zip fleece jacket", "bomber jacket"],
}

# Catalogue names were generated from URL slugs ("Morse 1 4 Zip"); these
# rules turn them into storefront names ("Morse ¼-Zip") without changing the data.
NAME_FIXES: list[tuple[str, str]] = [
    (r"\b1 4 Zip\b", "¼-Zip"),
    (r"\bT Shirt\b", "T-Shirt"),
    (r"\bTri Blend\b", "Tri-Blend"),
    (r"\bCreqneck\b", "Crewneck"),
    (r"^Ua\b", "UA"),
    (r"\bMens\b", "Men's"),
    (r"\bL S 2 0\b", "L/S 2.0"),
    (r"\bVs\b", "vs."),
    (r"\bOf\b", "of"),
    (r"\bAnd\b", "and"),
    (r" 1$", ""),
]

PRODUCT_QUERY = """
    SELECT c.*, COALESCE(SUM(i.quantity), 0) AS total_stock
    FROM catalogue c
    LEFT JOIN inventory i USING (product_id)
"""


def display_name(name: str) -> str:
    for pattern, replacement in NAME_FIXES:
        name = re.sub(pattern, replacement, name)
    return name


def _to_product(row: sqlite3.Row, sizes: list[str] | None = None) -> Product:
    return Product(
        product_id=row["product_id"],
        name=display_name(row["name"]),
        garment_type=row["garment_type"],
        description=row["description"],
        colors=json.loads(row["colors"]),
        price=row["price"],
        # The database stores "products/<file>.jpg"; images are served under /media.
        image_url=f"/media/{row['image_file_path']}",
        total_stock=row["total_stock"],
        sizes_in_stock=sizes or [],
    )


def list_products() -> list[Product]:
    rows = query(f"{PRODUCT_QUERY} GROUP BY c.product_id ORDER BY c.name")
    sizes = sizes_in_stock_by_product()
    return [_to_product(row, sizes.get(row["product_id"], [])) for row in rows]


def get_product(product_id: str) -> ProductDetail | None:
    rows = query(f"{PRODUCT_QUERY} WHERE c.product_id = ? GROUP BY c.product_id", (product_id,))
    if not rows:
        return None
    stock = {r["size"]: r["quantity"] for r in query("SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,))}
    sizes = [s for s in SIZE_ORDER if s in stock] + sorted(s for s in stock if s not in SIZE_ORDER)
    in_stock = [size for size in sizes if stock[size] > 0]
    return ProductDetail(
        **_to_product(rows[0], in_stock).model_dump(),
        search_tags=json.loads(rows[0]["search_tags"]),
        inventory=[InventoryItem(size=size, quantity=stock[size]) for size in sizes],
    )


def search_tags_by_product() -> dict[str, list[str]]:
    return {row["product_id"]: json.loads(row["search_tags"]) for row in query("SELECT product_id, search_tags FROM catalogue")}


def sizes_in_stock_by_product() -> dict[str, list[str]]:
    sizes: dict[str, list[str]] = {}
    for row in query("SELECT product_id, size FROM inventory WHERE quantity > 0"):
        sizes.setdefault(row["product_id"], []).append(row["size"])
    return {pid: sorted(found, key=lambda s: SIZE_ORDER.index(s) if s in SIZE_ORDER else 99) for pid, found in sizes.items()}
