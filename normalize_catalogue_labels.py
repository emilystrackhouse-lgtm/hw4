"""Normalize garment_type and colors labels in data/campus_customs.db's catalogue.

Maps each label variant to one canonical label, so the same garment or color
is always spelled the same way. Details dropped from garment_type (heavyweight,
raglan, men's, crew-neck) are still in each product's description.

Any label not in the canonical lists stops the run without changing anything,
and running it again on normalized data changes nothing.

Usage:
    python normalize_catalogue_labels.py
"""

import json
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "campus_customs.db"

GARMENT_TYPES = {
    "short-sleeve t-shirt",
    "long-sleeve performance shirt",
    "crewneck sweatshirt",
    "mockneck sweatshirt",
    "pullover hoodie",
    "full-zip hoodie",
    "quarter-zip pullover",
    "full-zip fleece jacket",
    "bomber jacket",
}

GARMENT_TYPE_MAP = {
    "short-sleeve T-shirt": "short-sleeve t-shirt",
    "short-sleeve crew-neck t-shirt": "short-sleeve t-shirt",
    "heavyweight short-sleeve t-shirt": "short-sleeve t-shirt",
    "men's long-sleeve performance shirt": "long-sleeve performance shirt",
    "raglan crewneck sweatshirt": "crewneck sweatshirt",
    "hoodie": "pullover hoodie",
    "hooded pullover sweatshirt": "pullover hoodie",
    "full-zip hooded sweatshirt": "full-zip hoodie",
    "quarter-zip pullover sweatshirt": "quarter-zip pullover",
    "fleece jacket": "full-zip fleece jacket",
}

COLORS = {
    "navy", "blue", "light blue",
    "white", "cream",
    "heather gray", "gray", "charcoal gray", "black",
    "red", "dusty coral", "yellow", "gold", "green",
}

COLOR_MAP = {
    "navy blue": "navy",
    "royal blue": "blue",
    "ivory": "cream",
    "light gray": "heather gray",
    "dark heather gray": "charcoal gray",
    "dark heather charcoal": "charcoal gray",
    "heather charcoal gray": "charcoal gray",
}

# "multicolor" isn't a color; replace it with the colors in the product photo.
MULTICOLOR = {
    "school-of-art-1-4-zip": ["white", "blue", "yellow", "red"],
}


def normalize_colors(product_id, colors):
    result = []
    for color in colors:
        color = color.strip().lower()
        replacements = MULTICOLOR[product_id] if color == "multicolor" and product_id in MULTICOLOR else [color]
        for c in replacements:
            c = COLOR_MAP.get(c, c)
            if c not in COLORS:
                raise ValueError(f"{product_id}: unknown color {c!r}")
            if c not in result:
                result.append(c)
    return result


def main():
    con = sqlite3.connect(DB_PATH)
    changed = 0
    try:
        with con:  # one transaction: all changes apply, or none do
            rows = con.execute("SELECT product_id, garment_type, colors FROM catalogue").fetchall()
            for product_id, garment_type, colors_json in rows:
                new_type = GARMENT_TYPE_MAP.get(garment_type, garment_type)
                if new_type not in GARMENT_TYPES:
                    raise ValueError(f"{product_id}: unknown garment_type {garment_type!r}")
                colors = json.loads(colors_json)
                new_colors = normalize_colors(product_id, colors)
                if new_type != garment_type or new_colors != colors:
                    con.execute(
                        "UPDATE catalogue SET garment_type = ?, colors = ? WHERE product_id = ?",
                        (new_type, json.dumps(new_colors), product_id),
                    )
                    changed += 1
    except ValueError as err:
        print(f"Stopped: {err}; nothing changed", file=sys.stderr)
        sys.exit(1)
    finally:
        con.close()
    print(f"{changed} products updated.")


if __name__ == "__main__":
    main()
