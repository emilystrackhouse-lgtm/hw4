"""Fix known data problems in data/campus_customs.db's catalogue table.

Each fix names the value it expects to replace. A fix that is already applied
is skipped, and any other unexpected value stops the run without changing
anything, so the script is safe to run more than once.

Product IDs and image filenames are left unchanged: inventory rows, image
files, and saved chat history all refer to products by ID.

Usage:
    python fix_catalogue_data.py
"""

import json
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "campus_customs.db"

STUB_DESCRIPTION = (
    "Campus Customs product photo ({}). Vision blocked; filename-based stub."
)

# (product_id, column, expected current value, new value)
FIXES = [
    # 1. Three rows where the vision step failed; filled in from the photos.
    ("benjamin-franklin-t-shirt", "garment_type", "t-shirt", "short-sleeve t-shirt"),
    (
        "benjamin-franklin-t-shirt",
        "description",
        STUB_DESCRIPTION.format("benjamin franklin t shirt"),
        "Heather gray short-sleeve T-shirt featuring a large centered Benjamin "
        "Franklin College shield crest in red, blue, and white with fleur-de-lis, "
        "and BENJAMIN FRANKLIN COLLEGE text beneath in black.",
    ),
    ("benjamin-franklin-t-shirt", "colors", [], ["heather gray", "red", "blue", "white", "black"]),
    (
        "benjamin-franklin-t-shirt",
        "search_tags",
        ["benjamin", "franklin", "t", "shirt"],
        ["Yale", "Benjamin Franklin", "Benjamin Franklin College", "residential college",
         "crest shirt", "logo t-shirt", "gray t-shirt", "short sleeve", "fleur-de-lis",
         "Yale merch"],
    ),
    ("berkeley-sweater-fleece-jacket", "garment_type", "jacket", "full-zip fleece jacket"),
    (
        "berkeley-sweater-fleece-jacket",
        "description",
        STUB_DESCRIPTION.format("berkeley sweater fleece jacket"),
        "Light heather gray full-zip sweater fleece jacket with a stand collar, "
        "charcoal gray zipper and pocket trim, zippered hand pockets, and a small "
        "red Berkeley College shield crest with BERKELEY text on the left chest.",
    ),
    ("berkeley-sweater-fleece-jacket", "colors", [], ["heather gray", "charcoal gray", "red", "white"]),
    (
        "berkeley-sweater-fleece-jacket",
        "search_tags",
        ["berkeley", "sweater", "fleece", "jacket"],
        ["Yale", "Berkeley", "Berkeley College", "residential college", "fleece jacket",
         "sweater fleece", "full zip", "gray jacket", "college crest", "left chest logo"],
    ),
    ("timothy-dwight-college-crewneck", "garment_type", "crewneck", "crewneck sweatshirt"),
    (
        "timothy-dwight-college-crewneck",
        "description",
        STUB_DESCRIPTION.format("timothy dwight college crewneck"),
        "Heather gray long-sleeve crewneck sweatshirt with ribbed collar, cuffs, and "
        "waistband, featuring a small red-and-white Timothy Dwight College shield "
        "crest with TIMOTHY DWIGHT text on the left chest.",
    ),
    ("timothy-dwight-college-crewneck", "colors", [], ["heather gray", "red", "white", "black"]),
    (
        "timothy-dwight-college-crewneck",
        "search_tags",
        ["timothy", "dwight", "college", "crewneck"],
        ["Yale", "Timothy Dwight", "Timothy Dwight College", "TD", "residential college",
         "crewneck", "sweatshirt", "gray sweatshirt", "crest", "left chest logo"],
    ),
    # 2. Named "crewneck" but the photo, description, type, and price are a quarter-zip.
    (
        "school-of-architecture-crewneck",
        "name",
        "School Of Architecture Crewneck",
        "School Of Architecture 1 4 Zip",
    ),
    # 3. Named and tagged "tennis" but the photo says YALE SQUASH.
    ("squash-left-chest-tennis", "name", "Squash Left Chest Tennis", "Squash Left Chest Crewneck"),
    (
        "squash-left-chest-tennis",
        "search_tags",
        ["Yale", "Yale Squash", "squash", "tennis", "navy sweatshirt", "crewneck",
         "long sleeve", "left chest graphic", "college merch", "Campus Customs"],
        ["Yale", "Yale Squash", "squash", "navy sweatshirt", "crewneck",
         "long sleeve", "left chest graphic", "college merch", "Campus Customs"],
    ),
    # 4. Same pullover hoodie as the other Yale Sports Hoodies ($68), but typed
    #    "hooded sweatshirt" and priced at $45.
    ("yale-sports-hoodie-tennis", "garment_type", "hooded sweatshirt", "pullover hoodie"),
    ("yale-sports-hoodie-tennis", "price", 45.0, 68.0),
]

JSON_COLUMNS = {"colors", "search_tags"}


def decode(column, value):
    return json.loads(value) if column in JSON_COLUMNS else value


def encode(column, value):
    return json.dumps(value) if column in JSON_COLUMNS else value


def main():
    con = sqlite3.connect(DB_PATH)
    applied, skipped = 0, 0
    try:
        with con:  # one transaction: all fixes apply, or none do
            for product_id, column, expected, new in FIXES:
                row = con.execute(
                    f"SELECT {column} FROM catalogue WHERE product_id = ?", (product_id,)
                ).fetchone()
                if row is None:
                    raise ValueError(f"{product_id}: product not found")
                current = decode(column, row[0])
                if current == new:
                    skipped += 1
                    continue
                if current != expected:
                    raise ValueError(
                        f"{product_id}.{column}: unexpected value {current!r}; nothing changed"
                    )
                con.execute(
                    f"UPDATE catalogue SET {column} = ? WHERE product_id = ?",
                    (encode(column, new), product_id),
                )
                applied += 1
                print(f"fixed {product_id}.{column}")
    except ValueError as err:
        print(f"Stopped: {err}", file=sys.stderr)
        sys.exit(1)
    finally:
        con.close()
    print(f"{applied} fixes applied, {skipped} already in place.")


if __name__ == "__main__":
    main()
