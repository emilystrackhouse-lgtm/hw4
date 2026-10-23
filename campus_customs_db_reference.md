# Campus Customs Database — Reference

A field-by-field guide to `data/campus_customs.db` (SQLite), based on a profile of every table. The catalogue was then cleaned in two steps (see "Data-quality problems" below):

1. `fix_catalogue_data.py` fixed four known product problems.
2. `normalize_catalogue_labels.py` gave each garment type and color one standard label.

The figures in this guide reflect the cleaned database. The untouched original is still in `~/Downloads/data 2/`.

## At a glance

| Table | Rows | What it holds |
|---|---|---|
| `catalogue` | 102 | One row per product: name, type, description, colors, search tags, image, price |
| `inventory` | 612 | Stock for every product in 6 sizes (102 × 6) |
| `users` | 3 | Shopper accounts for the Campus Customs chat app |
| `chat_messages` | 22 | Past conversations between shoppers and the app's AI assistant |
| `sessions` | varies | Logged-in sessions, added in Problem 4 (see below) |

How the tables connect:

- `inventory.product_id` → `catalogue.product_id` (many sizes per product)
- `chat_messages.user_id` → `users.id` (many messages per user)
- Every link is complete: no orphan rows, and every product has inventory.
- There is **no orders, cart, or sales table**, so the database can't tell you what sold.
- Foreign keys are declared but not enforced (`PRAGMA foreign_keys = 0`). The integrity check passes.

---

## `catalogue` — the product list

| Field | Type | Meaning | Notes |
|---|---|---|---|
| `product_id` | TEXT, primary key | URL-style slug, such as `yale-dad-hoodie` | Matches the image filename exactly |
| `name` | TEXT | Display name | Made mechanically from the slug in title case, so it has quirks: "1 4 Zip" means ¼-zip, "Ua Mens Tech L S 2 0", and a typo, "Creqneck" |
| `garment_type` | TEXT | Kind of garment | **9 standard labels** (22 inconsistent ones before cleanup; see below) |
| `description` | TEXT | One-sentence visual description | 93–215 characters, written by an AI vision model from the photo (the 3 former stubs were written from the photos during the fixes) |
| `colors` | TEXT (JSON array) | Colors **visible in the product photo** | 14 standard lowercase labels. Not the colorways you can buy. See the caution below |
| `search_tags` | TEXT (JSON array) | Keywords for search | 7–12 per product, 265 distinct tags |
| `image_file_path` | TEXT | Relative path, always `products/<product_id>.jpg` | All 102 images exist. They are square JPGs, 600–900 px, 3.7 MB total |
| `price` | REAL | Retail price in USD | Only 7 price points, set by garment type. One exception: the Under Armour Gameday hood is a pullover hoodie at $45 |

### Price tiers

| Price | Products | Garment family |
|---|---|---|
| $32 | 25 | T-shirts |
| $45 | 4 | Performance long-sleeves, mockneck, Under Armour Gameday hood |
| $58 | 28 | Crewneck sweatshirts |
| $68 | 24 | Pullover hoodies |
| $72 | 11 | Quarter-zips |
| $88 | 2 | Full-zip hoodies (Brooks Brothers, Champion) |
| $98 | 8 | Fleece jackets and the bomber jacket |

Range: $32–$98, average $58.71.

### `garment_type` labels

There are 9 standard labels. The table shows which old labels were merged into each.

| Label | Products | Price | Merged from |
|---|---|---|---|
| `crewneck sweatshirt` | 28 | $58 | `crewneck`, `raglan crewneck sweatshirt` |
| `short-sleeve t-shirt` | 25 | $32 | `short-sleeve T-shirt`, `t-shirt`, `short-sleeve crew-neck t-shirt`, `heavyweight short-sleeve t-shirt` |
| `pullover hoodie` | 25 | $68 (UA Gameday $45) | `hoodie`, `hooded sweatshirt`, `hooded pullover sweatshirt` |
| `quarter-zip pullover` | 11 | $72 | `quarter-zip pullover sweatshirt` |
| `full-zip fleece jacket` | 7 | $98 | `fleece jacket`, `jacket` |
| `long-sleeve performance shirt` | 2 | $45 | `men's long-sleeve performance shirt` |
| `full-zip hoodie` | 2 | $88 | `full-zip hooded sweatshirt` |
| `mockneck sweatshirt` | 1 | $45 | — |
| `bomber jacket` | 1 | $98 | — |

Details dropped from the type, such as "heavyweight", "raglan", "men's", and "crew-neck", are still in each product's description.

### Product groups (from names and IDs)

- **Residential colleges: 19 products, 11 colleges.** Benjamin Franklin, Berkeley, Branford, Davenport, Grace Hopper, Jonathan Edwards, Morse, Pierson, Saybrook, Timothy Dwight, and Trumbull. Ezra Stiles, Pauli Murray, and Silliman have no products.
- **Graduate and professional schools: 13 products.** Architecture (2), Art (2), Divinity, Engineering, Forestry ("The Forest School"), Law, Management (SOM crest tee), Medicine, Music, Nursing, and Public Health.
- **Family: 12 products.** Mom (2), Dad (3), Grandma, Grandpa (2), Aunt, Uncle, Brother, and Cousin. Useful for the "parent" customer profile.
- **Sports: about 33 products, 17 sports.** Hockey, field hockey, baseball, diving, soccer, tennis, football, squash, track & field, volleyball, golf, crew, fencing, lacrosse, sailing, basketball, and swimming. Most are "Left Chest", "Yale Sports", or "Tri Blend Sports" lines.
- **Brand partners: 15 products.** Champion (4), District (5, vintage bulldog and shield designs), Brooks Brothers (2), Hype and Vice (2), and Under Armour (2).
- **Spirit and game day.** 2025 Yale vs Harvard, Boola Boola, Yale Bowl, Big Yale, Arched Yale, and Block Y designs.

### Colors

- **14 standard labels** (22 before cleanup).
  - Blues: `navy` (80), `blue` (12), `light blue` (3)
  - Whites: `white` (56), `cream` (4)
  - Grays and black: `heather gray` (45), `charcoal gray` (8), `gray` (3), `black` (11)
  - Others: `red` (13), `yellow` (9), `gold` (4), `green` (4), `dusty coral` (1)
- **Merged variants:**
  - `navy blue` → `navy`. Keeping "navy" separate from "blue" means a search for "blue" won't return every navy item.
  - `royal blue` → `blue`
  - `ivory` → `cream`
  - `light gray` → `heather gray`
  - `dark heather gray`, `dark heather charcoal`, and `heather charcoal gray` → `charcoal gray`
- **`multicolor` replaced:** on the School of Art quarter-zip, it now lists the crest's actual colors from the photo (blue, yellow, red).
- **Kept separate on purpose:** `gold` and `yellow` are different color names, and plain `gray` is used for accents such as lettering.
- **Caution:** `colors` lists every color in the *photo*, including the logo. "Navy, white" usually means a navy garment with white lettering, **not** "available in navy or white." Each product has only one colorway. The app's assistant got this wrong in past chats (see `chat_messages`).
- No product is pink. None is labeled women's, kids', or youth.

### Data-quality problems

**Fixed** by `fix_catalogue_data.py` (17 field changes in 6 products, run on 2026-10-17). Each fix was checked against the product photo.

1. **3 stub rows where the vision step failed.** `benjamin-franklin-t-shirt`, `berkeley-sweater-fleece-jacket`, and `timothy-dwight-college-crewneck` had the description "Vision blocked; filename-based stub", empty `colors`, and tags split from the filename.
   - **Fix:** wrote a description, colors, and search tags for each from its photo, matching the style of similar products. Also normalized their garment types to `short-sleeve t-shirt`, `full-zip fleece jacket`, and `crewneck sweatshirt`.
2. **`school-of-architecture-crewneck` is really a quarter-zip.**
   - **Fix:** renamed it "School Of Architecture 1 4 Zip", matching the other quarter-zips. Its type ($72, quarter-zip) was already correct.
3. **`squash-left-chest-tennis` is a squash crewneck.**
   - **Fix:** renamed it "Squash Left Chest Crewneck" and removed the wrong "tennis" search tag.
4. **`yale-sports-hoodie-tennis` was underpriced.** It's the same pullover hoodie as the other "Yale Sports Hoodie" items.
   - **Fix:** changed its type from `hooded sweatshirt` to `pullover hoodie` and its price from $45 to $68.

**Not changed on purpose:**

- **Product IDs and image filenames still use the old slugs** (`school-of-architecture-crewneck`, `squash-left-chest-tennis`). Inventory rows, image files, and saved chats all refer to products by ID, so renaming them would break those links.
- **Chat history was left as it happened.** Messages 18 and 20 still hold the old Berkeley stub in their `products_json` snapshots.

**Normalized** by `normalize_catalogue_labels.py` (77 products, run on 2026-10-17):

5. **Inconsistent garment-type and color labels.** These were cut from 22 to 9 garment types and from 22 to 14 colors, as described above. Only `garment_type` and `colors` changed. Each script refuses to run if it finds a label it doesn't recognize, and running either script again changes nothing.

**Still open (not fixed):**

6. **"Campus Customs" appears as a search tag on only 15 products,** so don't use that tag to tell whether something is a Campus Customs product.
7. **No product mentions "Handsome Dan".** Ten products mention a bulldog.
8. **Color words inside `search_tags` and `description` were not changed.** For example, 6 products still have "navy blue" in their search tags. Tags are free-text keywords, so this is harmless for search.

---

## `inventory` — stock by size

| Field | Type | Meaning |
|---|---|---|
| `id` | INTEGER, primary key, autoincrement | Row ID, 1–612 |
| `product_id` | TEXT | Links to `catalogue` |
| `size` | TEXT | One of `XS`, `S`, `M`, `L`, `XL`, `XXL` |
| `quantity` | INTEGER | Units on hand |

- `(product_id, size)` is unique. Every product has exactly 6 rows, one for each size.
- **Quantities are synthetic.** Only 8 values appear: 0, 2, 5, 8, 12, 15, 20, 25. There are no negatives.
- **5,920 units in total**, worth **$345,709 at retail** ($344,168 before the tennis-hoodie price fix). Products average 58 units, ranging from 9 to 116.
- **145 size rows (24%) are out of stock**, and another 115 rows have only 2 or 5 units.
- **No product is completely sold out.** 25 products have every size in stock. 21 products are out of stock in 3 or more sizes.
- Lowest stock: `football-left-chest-t-shirt` (9 units), `tri-blend-sports-hockey-t-shirt` (13), `t-felt-y-heavyweight` (14).
- Highest stock: `tri-blend-sports-football-t-shirt` (116), `2025-yale-vs-harvard-t-shirt` (112), `branford-1-4-zip` (95).
- Units by size are fairly even, from XL (914) to XXL (1,076).
- Stock is a fixed snapshot. The past chats quote the same numbers that are in the table now.

---

## `users` — shopper accounts

| Field | Type | Meaning | Notes |
|---|---|---|---|
| `id` | INTEGER, primary key, autoincrement | User ID | 1–3 |
| `name` | TEXT | Full display name | |
| `email` | TEXT, unique | Login email | |
| `password_hash` | TEXT | Hashed password | Format `pbkdf2_sha256$<salt>$<64-hex hash>`: PBKDF2-HMAC-SHA256 with 120,000 iterations, the salt used as text. Seeded accounts and new signups use the same recipe (see `backend/README.md`). No plain-text passwords are stored |
| `created_at` | TEXT | Sign-up time, `YYYY-MM-DD HH:MM:SS` (UTC, SQLite `datetime('now')`) | All on 2026-09-19 |
| `first_name` | TEXT, nullable | First name | Added to the table later, after `created_at` |
| `last_name` | TEXT, nullable | Last name | Added to the table later |

The three accounts:

| id | Name | Email domain | Created | Chats |
|---|---|---|---|---|
| 1 | Test User | campuscustoms.yale.edu | 2026-09-19 11:34 | 3 exchanges |
| 2 | Ada Lovelace | yale.edu (email has a numeric suffix, so it looks like a test sign-up) | 2026-09-19 11:56 | none |
| 3 | Tauhid Zaman | yale.edu | 2026-09-19 11:57 | 8 exchanges |

No user has a profile field such as role, school, or "parent" vs. "student", so a customer profile has to come from somewhere else.

New accounts from the site's Create account page (Problem 4) are added here. Their emails are stored in lowercase, and `name` is filled in as "First Last".

---

## `sessions` — who is logged in (added in Problem 4)

| Field | Type | Meaning |
|---|---|---|
| `token_hash` | TEXT, primary key | SHA-256 hash of the random session token in the shopper's HttpOnly cookie. The token itself is never stored |
| `user_id` | INTEGER | Links to `users` (rows are deleted along with their user) |
| `created_at` | TEXT | When the shopper logged in (UTC) |
| `expires_at` | TEXT | Seven days after login. Expired rows are ignored and cleaned up at the next login |

The API creates this table on startup if it's missing. Logging out deletes the row.

---

## `chat_messages` — assistant conversation history

| Field | Type | Meaning |
|---|---|---|
| `id` | INTEGER, primary key, autoincrement | Message ID, 1–22 |
| `user_id` | INTEGER | Links to `users` |
| `role` | TEXT | `user` or `assistant` |
| `content` | TEXT | The message text. Assistant replies use Markdown |
| `products_json` | TEXT (JSON), nullable | On assistant messages: the products shown in the app's product panel. Always NULL on user messages |
| `created_at` | TEXT | Timestamp. Each question and its answer share the same second |

Each object in `products_json` is a snapshot of a catalogue row plus:

- `image_url` — a web path, such as `/media/products/<id>.jpg`
- `inventory` — a list of `{size, quantity}`
- `total_stock` — total units

What the chat history shows about the existing app:

- **Results are capped at 8 products.** "What hoodies do you have?" returned 8, even though there are about 25 hoodies.
- **Search is keyword-based.** "Handsome Dan" found nothing, even though bulldog products exist. "gym shorts" found nothing, because the store has no shorts.
- **The assistant treated `colors` as available colorways.** It said the Basic Hoodie "comes in navy blue or white."
- **It answered "cheapest fleece" with a $72 quarter-zip,** which isn't a fleece.
- **It greets users by first name,** using `users.first_name`.
