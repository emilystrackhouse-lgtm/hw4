# Homework 4 — AI Prompt Log

This file is the running record of AI-assisted work completed during the Homework 4 session. It is updated as we work. Each problem has its own section, and every section includes:

- **Problem number and title**
- **Original prompt** — at least one prompt typed in this session for the problem
- **Follow-up prompt** — a prompt describing what was added beyond the original prompt
- **Work completed** — files created or changed, key decisions, and outcomes

## Problem 1 — Vibe Coder Prompts

### Original prompt

> create a new folder within AI foundations for managers called Homework 4. create AI_prompts.md and keep it updated as i work so it can keep a log of what i've typed

### Follow-up prompt — Problem number and title for every section

> perfect, yes exactly good memory - the problem numbers & titles - continue with that same cadence for this homework. the initial request for the prompts to be tracked and this problem/title request is "Problem 1: Vibe Coder Prompts"

**What this added beyond the original prompt:** a required structure for every section of this log, carried over from Homework 3. Each problem gets its own section with its number and title, the original prompt, and a follow-up prompt. It also named this first section "Problem 1: Vibe Coder Prompts."

### Work completed

- Created the `Homework 4` folder inside `Homework`, alongside `Homework 1`, `Homework 2`, and `Homework 3`.
- Created this prompt log (`AI_prompts.md`), then organized it into problem sections that follow the Homework 3 format.

## Problem 2 — Analyze the Database

### Original prompt — Locate the Campus Customs database

> great thank you. do you have access to data/campus_customs.db or know where to find that?

### Work completed

- Searched the Desktop, Downloads, and Documents folders. The only copy is at `~/Downloads/data 2/campus_customs.db`. It is not in the course folder or in Homework 3's `data` folder yet.
- `~/Downloads/data 2/` also has a `products/` folder with 102 product images.
- Read the database's structure without changing it. It has four tables:
  - `catalogue` (102 products): product ID, name, garment type, description, colors, search tags, image file path, and price.
  - `inventory` (612 rows): stock quantity for each product and size.
  - `users` (3 rows): account records, including names, emails, and password hashes.
  - `chat_messages` (22 rows): chat history linked to users, including any products recommended.

### Follow-up prompt — Copy the data into Homework 4

> Yes, copy ~/Downloads/data 2 into Homework 4 as data/ (leave the original in Downloads).

**What this added beyond the original prompt:** brought the database and product images into the homework folder so the assignment can use them directly.

### Work completed

- Copied `~/Downloads/data 2/` to `Homework 4/data/`. The original in Downloads was left unchanged.
- Checked that the copy matches the original exactly: `campus_customs.db` plus 102 images in `data/products/`.
- The database's integrity check passed, and all 102 catalogue image paths (stored as `products/<file>.jpg`) point to files in `data/products/`.

### Follow-up prompt — Learn the database in depth

> ensure you have a deep understandign of the info and fields within data/campus_customs.db. know as much as possible, especially catalogue, inventory, and users

**What this added beyond the original prompt:** moved from finding the database to understanding every table and field, with the most attention on `catalogue`, `inventory`, and `users`.

### Work completed

- Profiled all four tables without changing anything: field types, allowed values, row counts, distributions, and how the tables link.
- Wrote `campus_customs_db_reference.md`, a field-by-field guide to the database.
- Key findings:
  - **Prices:** 7 price tiers ($32–$98), set by garment type.
  - **Garment types:** 22 inconsistent labels that collapse into 7 garment families.
  - **Colors:** the `colors` field lists colors visible in the photo, not colorways you can buy.
  - **Stock:** 5,920 units worth $344,168 at retail. 24% of size rows are out of stock, but no product is fully sold out.
  - **Users:** 3 accounts with PBKDF2-SHA256 password hashes and no customer-profile fields.
  - **Chat history:** shows the app's assistant caps results at 8 products and misreads `colors`.
- Found data-quality problems:
  - 3 products where image analysis failed and the description is a placeholder. I looked at their photos and described them in the reference.
  - `school-of-architecture-crewneck` is really a quarter-zip.
  - `squash-left-chest-tennis` is a squash crewneck.
  - `yale-sports-hoodie-tennis` may be underpriced.

### Follow-up prompt — Fix the data problems

> please fix those data problems

**What this added beyond the original prompt:** moved from documenting the database's problems to correcting them in the Homework 4 copy.

### Work completed

- Wrote `fix_catalogue_data.py`, which applies 17 field changes to 6 catalogue products in one transaction.
  - Each fix checks for the old value before changing anything, so running the script twice is safe.
  - Ran it once to apply the fixes, then a second time to confirm every fix was already in place.
- **Placeholder rows:** filled in the description, colors, and search tags for the Benjamin Franklin tee, Berkeley fleece, and Timothy Dwight crewneck from their photos, and normalized their garment types.
- **Architecture:** renamed `school-of-architecture-crewneck` to "School Of Architecture 1 4 Zip" (it's a quarter-zip).
- **Squash:** renamed `squash-left-chest-tennis` to "Squash Left Chest Crewneck" and removed its wrong "tennis" tag.
- **Tennis hoodie:** `yale-sports-hoodie-tennis` is now a "pullover hoodie" at $68 (was $45), matching the other Yale Sports Hoodies. I checked its photo first. Stock value at retail rose from $344,168 to $345,709.
- **Left alone on purpose:** product IDs and image filenames, because inventory, image files, and chat history refer to products by ID. Past chat messages were also left as they happened.
- **Verified:** the database integrity check passes, no placeholder rows remain, and inventory, users, and chat_messages match the original exactly. The untouched original is still in `~/Downloads/data 2/`.
- Updated `campus_customs_db_reference.md` to reflect the fixes and list the problems that are still open.

### Follow-up prompt — Normalize garment type and color labels

> Yes, also normalize the garment_type and color labels (e.g. T-shirt vs t-shirt, navy vs navy blue).

**What this added beyond the original prompt:** went beyond fixing individual products to making labels consistent across the whole catalogue, so the same garment or color is always spelled the same way.

### Work completed

- Wrote `normalize_catalogue_labels.py`, which maps every label variant to one standard label in a single transaction. It refuses to run if it finds a label it doesn't recognize, and running it again changes nothing.
- **Garment types: 18 labels → 9.**
  - Standard labels: `short-sleeve t-shirt`, `crewneck sweatshirt`, `pullover hoodie`, `quarter-zip pullover`, `full-zip hoodie`, `full-zip fleece jacket`, `long-sleeve performance shirt`, `mockneck sweatshirt`, `bomber jacket`
  - Before merging the 5 items labeled just `hoodie` into `pullover hoodie`, I checked that each one is a pullover.
  - Details like "heavyweight" and "raglan" are still in the descriptions.
- **Colors: 22 labels → 14.**
  - `navy blue` → `navy`, which also keeps a search for "blue" from returning every navy item
  - Three dark grays → `charcoal gray`
  - `light gray` → `heather gray`
  - `ivory` → `cream`
  - `royal blue` → `blue`
- **`multicolor`:** replaced on the School of Art quarter-zip with the crest's actual colors from the photo.
- **Kept separate on purpose:** `gold` and `yellow`, and plain `gray` for accents.
- **Verified:**
  - 77 products changed, and only in `garment_type` and `colors`.
  - The integrity check passes.
  - Inventory, users, and chat_messages still match the original.
  - Re-running either script changes nothing.
- Updated `campus_customs_db_reference.md` with the new standard labels and what each one replaced.
- **Open:** the Under Armour Gameday hood is a pullover hoodie at $45, while the other hoodies are $68. It's a brand item, so I didn't change its price.

### Organization prompt and follow-up — Name Problem 2 and start the harness

> ok great. and thanks for the reminder - since the database prompt, its been "Problem 2: Analyze the database". continuing in that problem, start the file output/harness.md. write down each table and its fields and one shrot line on why each field matters for the shop or the chatbot

**What this added beyond the original prompt:**

- Named this section "Problem 2: Analyze the Database". Every prompt since the database question belongs to it.
- Asked for the first harness output: a plain explanation of what each field is for.

### Work completed

- Retitled this section of the log "Problem 2 — Analyze the Database".
- Created `output/harness.md` with a short overview of the database and how the tables link.
- Listed all four tables (`catalogue`, `inventory`, `users`, `chat_messages`) and every field, each with one line on why it matters to the shop or the chatbot.
- Flagged where the chatbot must be careful:
  - `colors` lists colors in the photo, not color choices a shopper can buy.
  - The chatbot should never recommend a size with 0 in stock.
  - The chatbot must never read or reveal `password_hash`.

## Problem 3 — Build the Campus Customs Website

### Original prompt — Scaffold the front end with a nav bar

> Ok now moving on to Problem 3: Build the Campus Customs website. scaffold a React + Vite + TypeScript front end for Campus Customs. Put a nav bar at the top that links to the main page:
>
> * Home
> * Products
> * About Us
> * Log in
> * Create account
>
>
> make sure it's all in Campus Customs-style branding, wording, typography etc. Ensure that it fits the vibe, but make it original (don't copy text from the site exactly).

### Work completed

- **Studied the real brand:** looked at campuscustoms.com for its look and voice.
  - Colors: deep navy `#0c233f` and steel blue `#7ba0c5`.
  - Type: condensed Archivo Narrow.
  - Logo: an "Est. 1975" mark.
  - Voice: warm and family-focused. The shop has been across from Yale since 1975, is now run by the founder's sons, and does printing and embroidery next door.
  - All site wording is original; none was copied from the real site.
- **Branding choice:** used Campus Customs colors instead of the workspace's default black-and-pink style, because this prompt asked for Campus Customs branding. This is noted in the README.
- **Scaffold:** created `Homework 4/frontend/` with Vite (React + TypeScript) and added `react-router` for page links.
  - Kept `node_modules` out of iCloud sync, as `AGENTS.md` requires.
  - The dev server runs on port 5177 (`npm run dev`), since 5173–5176 are used by the lecture apps. It's also added to `.claude/launch.json` as `hw4-frontend`.
- **Nav bar:** sits at the top of every page and links to Home, Products, About Us, Log in, and Create account.
  - Shows which page you're on.
  - Collapses into a Menu button on phones.
  - The Escape key closes the menu.
- **Branding elements:**
  - An original italic two-tone "Campus Customs" wordmark with an "Est. 1975" rule
  - A circular "New Haven, Connecticut · Est. 1975" seal
  - A navy banner reading "Family-run and right across from Yale since 1975"
  - A matching footer
- **Pages:**
  - **Home:** hero ("Dressed in Yale Blue since 1975"), store facts, collection cards, a story teaser, and a sign-up call to action
  - **Products:** shop by style, with real counts and starting prices from the database, and shop by collection
  - **About Us:** the family story, the print and embroidery services, and how the shop does business
  - **Log in** and **Create account:** forms with field checks and clear error messages. They say plainly that accounts aren't connected yet.
  - A **404 page** for unknown links
- **Store facts:** product counts, prices, and collection details are kept in `src/data/shop.ts` and taken from `data/campus_customs.db`.
- **Verified:**
  - Type check, production build, and lint all pass.
  - Every nav link goes to the right page and title.
  - The forms show errors and move focus to the first problem.
  - No console errors.
  - No sideways scrolling on a phone (390px) or desktop (1280px).
  - After reviewing screenshots, fixed two things: card grids that left a single card alone on a row, and the phone banner wrapping onto two lines.

### Follow-up prompt — Product images, product pages, chat panel, and an API

> still problem 3 - on the products page - show product images from teh catalogue (use the image paths in teh databse) with base product info (name, price, short description, and color).
>
> make each product open a single-item page (large image on one side, full product text on the other - description, price, sizes/stock when you have them). clicking a card on products should take the shopper there.
>
> add a chat interface in the bottom right of the site (a floating chat panel).
>
> you will need a small API soon to read the database - please start a simple FastAPI app in backend/main.py just to serve products and images for now. we will grow it later.

**What this added beyond the original prompt:** connected the site to the real catalogue with a backend, added a page for each product, and added the first piece of the shop's chat assistant.

### Work completed

- **Backend (`backend/main.py`):** a small FastAPI app on port 8002 that opens the database read-only. It's also added to `.claude/launch.json` as `hw4-backend`.
  - `GET /api/products` lists all 102 products.
  - `GET /api/products/{product_id}` returns one product with stock for each size, or a 404 if the product doesn't exist.
  - `/media/products/...` serves photos, using `image_file_path` from the database.
  - A small `display_name()` step turns the slug-style catalogue names into storefront names, for example "Morse 1 4 Zip" → "Morse ¼-Zip" and "Yale Vs Harvard T Shirt" → "Yale vs. Harvard T-Shirt". The data itself isn't changed.
  - Kept `.venv` out of iCloud sync, and added `requirements.txt`, `.gitignore`, and a README.
- **Product photos:** 76 of the 102 photos had solid black backgrounds, left over from transparent images, which looked like black squares on the site.
  - Wrote `prepare_product_images.py`. It whitens only the black connected to the image edges, so black logos and lettering stay. It also cleans up the leftover dark outline around each garment.
  - The script saves copies to `data/products_web/`, and the API serves those. The originals are untouched.
  - My first version spilled into the darkest navy hoodie, so I lowered the tolerance and checked all 102 photos on a contact sheet.
- **Products page:**
  - A grid of product cards, each with a photo, name, price, two-line description, and color swatches with the main color named.
  - Style filter chips (All, T-Shirts, Long Sleeves, Crewnecks, Hoodies, Quarter-Zips, Fleece & Outerwear) with live counts. The filter is saved in the URL, so the footer links to Hoodies, Crewnecks, and T-shirts work too.
  - Loading placeholders, plus an error message with a **Try again** button if the API is down.
  - Each card opens its product page.
- **Product page (`/products/:productId`):**
  - A large photo on one side.
  - On the other side: a breadcrumb, garment type, name, price, and full description.
  - Sizes and stock: a box for each size marked In stock, Only N left, or Sold out, plus a one-line summary.
  - The colors in the design. This is labeled carefully, because these aren't color choices a shopper can buy.
  - Tags, an **Ask about this item** button that opens the chat with a question filled in, and a link to more items in the same style.
  - A friendly "We can't find that item" page for unknown products.
- **Floating chat panel:** an **Ask us** button in the bottom right of every page.
  - It opens a branded panel with a greeting, suggested questions, a message box, and a send button.
  - The conversation stays put as you move between pages.
  - Escape closes the panel and returns focus to the button.
  - It isn't connected to an AI yet, so every reply says so plainly and points to the Products page.
- **Verified:**
  - Lint, type check, and build pass.
  - The API returns all 102 products, sends 404 for unknown products, and blocks path tricks on images.
  - All 102 card images load, and the filters show the right counts.
  - Clicking a card opens the right product page.
  - The chat opens, sends messages, closes with Escape, and gets its question pre-filled from a product page.
  - With the API stopped, the error and Try again work.
  - No sideways scrolling on a phone (390px) or desktop (1280px).
- Updated `frontend/README.md` and added `backend/README.md`.

## Problem 4 — Create Account and Login

### Original prompt — Build a create account and login flow

> Problem 4: Create account and login
>
> build a typical create account/login flow
>
> * create account with the following fields: first name, last name, email, pw and confirm pw
> * login: email & pw
>
>
> new accts go into a "users" table. make sure to store passwords securely so hackers of any kind cannot access them

### Work completed

- **Password storage (`backend/passwords.py`):** passwords are never stored. Each one is mixed with a secret pepper using HMAC-SHA256, then hashed with Argon2id, the OWASP-recommended password hash.
  - Argon2id uses 64 MiB of memory and 3 passes per guess, plus a random 16-byte salt for every password.
  - The pepper lives only in `backend/.env`. I generated it locally without printing it, and `.env` is git-ignored with a `.env.example` alongside. A copied database is useless without the pepper.
  - The API refuses to start if the pepper is missing.
- **Accounts API (`backend/auth.py`):**
  - `POST /api/auth/signup` adds the new user to the existing `users` table (first name, last name, lowercased email, `name`, and the hash), then logs them in.
  - `POST /api/auth/login`, `POST /api/auth/logout`, and `GET /api/auth/me`.
- **Other protections:**
  - **Sessions:** a random token in an HttpOnly, SameSite cookie that page scripts can't read. Only a SHA-256 hash of the token is stored, in a new `sessions` table. Sessions expire after 7 days, and logging out deletes them.
  - **Same answer for wrong password and unknown email:** both get one generic message, and a dummy hash check keeps both taking the same time.
  - **Rate limits:** 5 failed logins per email, or 20 per IP, within 15 minutes. Signups are also rate-limited.
  - **Password rules:** at least 8 characters. Very common passwords, and passwords equal to the email, are refused.
  - **Duplicate emails:** caught no matter the capitalization.
  - **SQL injection:** every query uses parameters.
  - **No leaks:** passwords are kept out of logs, and the API never returns a hash.
  - **Upgrades:** weaker hashes are re-hashed automatically when someone logs in.
- **Tests (`backend/tests/`):** 10 automated tests against a throwaway copy of the database cover hashing, salts, the pepper, cookies, login and logout, enumeration, duplicates, field checks, rate limiting, and injection attempts. All 10 pass.
- **Front end:**
  - Create account and Log in now really work: loading states ("Creating your account…"), server messages under the right field, a form-level alert for login errors, and a Show/Hide password button.
  - A new **My account** page shows name, email, and member-since date, with Log out. It sends logged-out visitors to Log in.
  - Once you're logged in, the nav shows "Hi, {first name}" and Log out, the footer links to My account, and the chat greets you by name.
- **Verified in the browser:**
  - Signing up lands on the welcome page, and page scripts can't see the session cookie.
  - Logging out returns you to Home, and `/account` then sends you to Log in.
  - A wrong password shows the generic message and clears the password box. The right password logs you in.
  - Duplicate emails, any capitalization, are caught. "password123" is refused.
  - No console errors on a fresh visit.
  - The database now holds `$argon2id$…` hashes with no plain-text password anywhere.
  - Test accounts made during checking (`qa-…@example.com`) were deleted afterward, leaving the 3 original users.
- **Fixes found while testing:**
  - Logging out from the account page went to Log in instead of Home. It now leaves the page before ending the session.
  - The "who am I" check now returns "no user" instead of an error, so logged-out pages don't log console errors.
- **Open item:** the 3 original accounts use an older `pbkdf2_sha256$salt$hash` format that doesn't record its round count, so they can't be checked and can't log in. Logins for them fail safely.
- Updated `backend/README.md` (endpoints, a threat-by-threat security table, setup, and tests), `frontend/README.md`, and `campus_customs_db_reference.md` (the new password format and the `sessions` table).

### Follow-up prompt — New passwords for the 3 original accounts

> Give the 3 original accounts new passwords in the secure format so they can log in, and tell me how I set or see them.

**What this added beyond the original prompt:** brought the three older accounts (Test User, Ada Lovelace, and Tauhid Zaman) onto the secure password format, and asked for a way to manage passwords afterward.

### Work completed

- Wrote `backend/set_password.py`, an admin tool that sets a password the secure way (peppered Argon2id) and logs that account out everywhere.
  - Type a new password, hidden as you type: `.venv/bin/python set_password.py EMAIL`.
  - Or add `--generate` for a strong random password (20 characters with no look-alike characters) that's shown once.
  - `--old-accounts` handles every account still on the old format.
  - It applies the same password rules as signup. I moved those rules into `passwords.py` so both use one copy.
- Added 2 automated tests, for 12 in total, all passing: an old account can log in after a reset, and weak passwords and unknown emails are refused.
- Ran the tool end to end on a throwaway copy of the database first (generated passwords hidden from the output). Then ran `set_password.py --old-accounts --generate` in the user's Terminal panel, so the 3 new passwords appeared only there, never in the chat or any file.
- Confirmed in the database that all 3 accounts are now stored as `$argon2id$v=19$m=65536,t=3,p=4$…`.
- **How to "see" a password:** you can't. Only a one-way hash is stored, so nobody can look a password up, not even with the database and the pepper. Generated passwords are shown once when they're created. After that, the only option is to set a new one.
- Updated `backend/README.md` (a new "Setting or resetting a password" section) and `campus_customs_db_reference.md`.

### Follow-up prompt — Use the seed hash recipe and document auth in the harness

> use the test user in the seed database
>
> * email: test@campuscustoms.yale.edu
> * pw: password
> * hash function: PBKDF2-HMAC-SHA256, 120,000 iterations (storred as pbkdf2_sha256$salt$hash)
>
>
> how login checks a pw:
>
> * you never un-hash the stored value. you re-hash what the user typed and compare
> * read the salt out of the stored string (middle piece) - do not make a new one at login
> * hash the typed pw with that same salt, then compare to the stored hash. use a constant-time compare
> * signup and login must be the same hash settings (same function, same salt handling, same iteration count). if they differ, even the right pw will not match
> * surest check: log in as the seeded test user, and that a brand-new acct you create also works
>
>
> update  output/harness.md with how auth works (what you store for a user and how passwords are protected)

**What this added beyond the original prompt:** the exact password recipe used by the seed data, the exact way login must check a password, a required end-to-end check, and documenting auth in the harness.

### Work completed

- **Confirmed the recipe first:** checked against the untouched seed database in Downloads. PBKDF2-HMAC-SHA256 of the test user's password, with the stored salt (as text) and 120,000 iterations, reproduces the stored hash exactly.
- **Switched signup and login to that one recipe (`backend/passwords.py`):**
  - Signup makes a new random salt and stores `pbkdf2_sha256$<salt>$<64-hex hash>`.
  - Login reads the salt from the middle of the stored string, re-hashes the typed password with that salt and 120,000 iterations, and compares with `hmac.compare_digest` (constant time).
  - Removed the earlier Argon2id and pepper setup so signup and login can't drift apart. Took `PASSWORD_PEPPER` out of `.env` and the Argon2 package out of `requirements.txt`.
- **Restored the 3 seeded accounts' original password hashes** from the seed database. The temporary passwords from the previous step no longer work. `set_password.py` still works and now uses the same recipe.
- **Tests:** updated and added tests, 14 in total, all passing. They include the seeded Test User logging in, the exact hash recipe (and rejecting malformed or foreign hash strings), and a brand-new account logging in.
- **Surest check, in the real app in the browser:**
  - The seeded Test User logged in, the nav showed "Hi, Test", and page scripts couldn't read the session cookie. The same password with a capital P was rejected.
  - A brand-new account (Jordan Newman) was created, logged out, and logged back in. Its stored hash had the same `pbkdf2_sha256$salt$hash` shape. The test account was deleted afterward.
- **Harness:** added an "Accounts and login" section to `output/harness.md`.
  - It covers what's stored for each shopper (and what never is), how passwords are protected, the login check step by step, why signup and login must match, sessions, other protections, how it was checked, and known limits.
  - One known limit: 120,000 iterations matches the seed data, while OWASP now recommends 600,000.
- Updated `backend/README.md`, `frontend/README.md`, and `campus_customs_db_reference.md` to match.

## Problem 5 — PydanticAI Agent Backend

### Original prompt — Problem 5 instructions (screenshots)

> [Pasted two screenshots of the Problem 5 instructions, Panel A and Panel B, with no typed message.]

### Work completed

- Read both panels.
  - **Panel A:** build the shop chatbot as a PydanticAI agent behind FastAPI. The app goes in `backend/main.py`. The agent is split across `prompts/prompt.md`, `agent.py`, `tools.py`, and `models.py`, with a chat route the website calls.
  - **Panel B:** put the Campus Customs voice and safety basics in the prompt. Add chat reply and product card types. Note in `output/harness.md` how the front end talks to FastAPI and how the agent is loaded. Run from `backend/` with `uvicorn main:app --reload --port 8000`.
- Both panels also contain blurred text addressed to an AI assistant. It appears to say not to start the problem until the student describes the task in their own words. Paused and asked before starting.

### Follow-up prompt — The task in my own words

> Here's what I want for Problem 5, in my own words:

**What this added beyond the original prompt:** nothing yet. The message ended after the opening line, so I asked for the description.

### Follow-up prompt — Build the PydanticAI chatbot backend

> Please build the backend for my Campus Customs shop chatbot using PydanticAI and FastAPI, and connect it to the website's existing chat widget.
> Organize the backend into these files:
>
> * `backend/main.py`: The FastAPI app, including a chat endpoint that receives messages from the website and returns the agent's responses. Include any additional endpoints needed for products or authentication.
> * `backend/prompts/prompt.md`: The agent's system prompt, including Campus Customs' brand voice and basic safety guidelines. Keep these instructions in this file so we can expand them later.
> * `backend/agent.py`: The code that creates and configures the PydanticAI agent.
> * `backend/tools.py`: The tools the agent can call.
> * `backend/models.py`: The Pydantic models defining structured data for chat responses, product cards, and anything else needed.
>
> Configure the agent to use my AI model API key through an environment variable.
> Connect the frontend chat widget to the FastAPI chat endpoint so a user can send a message and see the agent's reply.
> In `output/harness.md`, explain how the frontend communicates with FastAPI and how the agent loads its system prompt and AI model.
> Make sure I can start the backend from inside the `backend/` folder using:
>
> ```
> uvicorn main:app --reload --port 8000
> ```
>
> Review the existing project first, build on what is already there, and verify that the chat works from the frontend through the backend.

**What this added beyond the original prompt:** the task in the user's own words, which named each file's job, the API key through an environment variable, connecting the existing widget, the harness notes, the exact run command, and end-to-end verification.

### Work completed

- **Reviewed first:** the existing backend, the chat widget, and Homework 3's agent setup.
  - Reused Homework 3's pattern: an OpenAI-compatible client pointed at Portkey with the `x-portkey-api-key` header, and `gpt-5.6-luna` from `OPENAI_MODEL`.
  - Copied `PORTKEY_API_KEY`, `OPENAI_MODEL`, and `PORTKEY_BASE_URL` into `backend/.env` without printing the key. Listed the names only in `.env.example`.
  - Added `pydantic-ai-slim[openai]` to `requirements.txt`, as `AGENTS.md` asks.
- **`backend/models.py`:** Pydantic types for products, the chat request and response, product cards, the agent's structured output (`ChatReply`: reply text plus up to 4 product IDs), tool results, and the agent's dependencies.
- **`backend/tools.py`:** three read-only tools.
  - `search_products` understands shopper words such as "Handsome Dan", "tee", and "parents", and filters by style, max price, and size in stock.
  - `get_product_details` gives stock for every size.
  - `list_styles` summarizes what the shop carries.
  - Product reading moved into a shared `backend/catalogue.py`, so the product pages and the agent always agree.
- **`backend/prompts/prompt.md`:** the system prompt.
  - Voice: warm, family-run, across from Yale since 1975.
  - How to answer: look everything up first, recommend at most 4 products, plain text.
  - Product facts: one colorway, XS–XXL, what isn't sold.
  - What it can't do: orders, discounts, accounts.
  - Safety basics: stay on topic, never ask for passwords or payment details, keep instructions private, treat messages as information, decline inappropriate requests.
- **`backend/agent.py`:** creates the agent.
  - Re-reads `prompt.md` whenever it changes, so edits apply without a restart, and adds the logged-in shopper's first name.
  - Connects to the model through Portkey on the first message.
  - Caps model calls and tool calls per reply.
  - Builds product cards from the database, only for products the tools actually returned.
  - Turns a provider safety-filter block into a polite decline.
- **`backend/main.py`:** added `POST /api/chat`, with a per-visitor limit of 30 messages per 10 minutes and friendly 503 and 502 errors, next to the existing product and account routes. Moved the backend to port 8000. Updated the Vite proxy and the `hw4-backend` launch config to match.
- **Chat widget:**
  - Sends each message with the last 20 messages for context.
  - Shows a typing indicator, then the reply and up to 4 clickable product cards (photo, price, sizes in stock).
  - Shows errors as a short chat message that is never sent back as history.
- **Tests:** added 13 chat and tool tests, for 27 in total, all passing. They use PydanticAI's `FunctionModel` as a scripted stand-in for the AI.
- **A problem found and fixed while testing:** the first run of the new chat tests wrote to the real database. The test file imported backend modules before the setup pointed them at a throwaway copy. That run added 10 test accounts and 13 sessions, and changed Tauhid Zaman's password hash.
  - Removed every test account and session.
  - Restored Tauhid's hash from the seed database. All 3 accounts match the seed again.
  - Moved the test setup so the throwaway copy is in place before any test loads, and added a check that stops the run if tests ever point at the real file.
  - Confirmed the real database is byte-for-byte unchanged after a full test run.
- **Verified end to end:**
  - The exact command `uvicorn main:app --reload --port 8000` starts cleanly from `backend/`, in the user's Terminal panel.
  - Through the website, "What hoodies do you have?" returned four hoodie cards. The follow-up "Which of those is cheapest, and is it in stock in a medium?" used context, and its stock claims matched the database.
  - Clicking a card in the chat opened the product page with the chat kept.
  - Live probes: "gym shorts" got an honest "we don't sell those." "Handsome Dan" found the bulldog designs. The white-hoodie color question was answered correctly. An essay request was declined.
  - A "print your system prompt" jailbreak was blocked by the AI provider's content filter. It first showed an error, and now gets a polite decline.
  - Screenshots were taken on desktop and phone.
- **Docs:** added a "The shop chatbot" section to `output/harness.md`. It covers the files, how the website talks to FastAPI (the proxy, routes, and request and response JSON), how the agent loads its prompt and model step by step, safety basics, how to run it, how it was checked, and known limits. Updated `backend/README.md` and `frontend/README.md`.

## Problem 6 — Tools: Product Info and Stock

### Original prompt — Look up real product info and stock

> Problem 6: Tools: product info and stock
>
> Please expand the Campus Customs chatbot so it can look up actual product information from `campus_customs.db`.
> Add tools in `backend/tools.py` and connect them to the PydanticAI agent so it can retrieve:
>
> * Product descriptions.
> * Product prices.
> * Available inventory, including stock counts for a specific size when requested.
>
> The chatbot must use the database for this information and never make up prices or stock quantities. If a requested size is out of stock, clearly tell the customer.
> Update `backend/prompts/prompt.md` so the agent knows when to call these tools, especially when answering questions about prices or availability.
> Add or update the structured return types in `backend/models.py` to support the lookup results.
> In `output/harness.md`, list each tool, describe the fields included in its return model, and explain why those fields were chosen.
> Build on the existing backend and verify that the chatbot's answers match the database, including for size-specific stock questions and out-of-stock items.

### Work completed

- **Tools (`backend/tools.py`):** replaced the general details tool with two focused lookups, now registered with the agent alongside `search_products` and `list_styles`.
  - `get_product_info` returns the description, price, colors, every size's count (including 0s), sizes in stock, sold-out sizes, and total.
  - `check_size_stock` returns one size's count, whether it's in stock, whether stock is low (5 or fewer), and the other sizes available.
- **Return types (`backend/models.py`):** added `ProductInfo`, `SizeStock`, and `SizeCount`. The field descriptions tell the model what each value means.
- **Prompt (`backend/prompts/prompt.md`):**
  - Which tool to call for which question. In particular, call `check_size_stock` fresh for any single-size question.
  - Prices and stock may only come from tool results, never estimated or remembered.
  - Say "sold out" clearly and first, then offer sizes that are in stock.
  - Mention low stock.
- **Tests:** 30 in total, all passing. The new tests compare the tools with direct database queries: price, every size's count, the sold-out list, and the total. They cover a sold-out size (Football Left Chest T-Shirt, M = 0), a low-stock size (L = 2), and a well-stocked size, and confirm the agent has all four tools and that a "sold out" answer reaches the website. The real database stayed unchanged.
- **Live checks with the real AI, all matching the database:**
  - Football tee in medium: sold out, available in S, L, and XXL, $32.
  - Saybrook fleece: $98, sold out in XXL.
  - Yale Dad Crewneck in large: 0, sold out.
  - Pierson Crewneck: correct description, $58, sold out in L and XL.
  - Through the website's chat panel, the Yale Dad Crewneck in medium: sold out, with in-stock sizes listed and shown on the card.
- **Harness:** added "The chatbot's tools" to `output/harness.md`. It covers each tool, when it's used, every field in its return model and why it was chosen, and a table comparing live answers with the database. Updated the chatbot section and `backend/README.md` to match.

## Problem 7 — Chat Search That Updates the Page

### Original prompt — Chat-driven product search

> Problem 7: Chat search that updates the page
>
> Please add a chat-driven product search feature to the Campus Customs website.
>
> When a customer asks about a product category, such as "What hoodies do you have?", the agent should search the catalog and the website should automatically display matching products as cards. Each card should include the product's image, name, price, and a short description.
>
> Have the backend return the matching products as structured data through the API, and have the frontend use that data to update the products displayed on the page.
>
> Keep the product detail functionality from Problem 3 working for every card, including cards loaded through chat search. Clicking a card should open its individual product page with a larger image and full product information.
>
> Update backend/prompts/prompt.md so the agent knows when to search the catalog and return product matches. Update output/harness.md to explain how search results move from the agent through the API to the website.
>
> Build on the existing project and verify that a customer can ask for a product category, see matching cards appear, and click one to view its full details.

### Work completed

- **Backend:**
  - `search_products` now keeps every ranked match (up to 48) for the page and returns a `ProductSearch`: the true total plus the best 8 for the AI to read.
  - The agent's `ChatReply` gained `show_search_on_page` and `page_title`.
  - `agent.py` builds `SearchResults` (a title plus full `Product` data) from the database for those matches.
  - `/api/chat` now returns `{reply, products, search}`.
- **Prompt:** a "Browsing a category puts results on the page" rule. It says when to search and set the flag, to give the true total, and to leave the page alone for single-product, size, or price questions.
- **Front end:**
  - Chat search results go into shared chat state, and the site goes to `/products`.
  - The Products page replaces its grid with every match under a "From the shop assistant" banner, using the same cards (photo, name, price, short description, colors).
  - Every card opens the Problem 3 product page.
  - Results survive Back. "Show all products" or a style button clears them.
- **Fixed during testing:** the first live reply said "I found 8 hoodies" while the page showed 27, because the AI saw only the top 8. The tool now reports `total_matches`, and the reply says "27 hoodies in all".
- **Tests:** 33 in total, all passing. They cover all 27 hoodies returned with complete card data and working product pages, search only when asked, empty searches leaving the page alone, and the true total.
- **Verified live in the browser:**
  - Asking for hoodies from the About page jumped to Products with 27 hoodie cards.
  - "Saybrook College gear" showed the 3 Saybrook items.
  - A single-size question answered correctly (25 left in large) without changing the page.
  - Clicking a search card opened the full product page.
  - Back kept the results, and "Show all products" restored all 102.
- **Docs:** added "Chat search that updates the page" to `output/harness.md` (a step-by-step diagram from the agent through the API to the page, key choices, new types, the prompt rule, and checks). Updated both READMEs.

## Problem 8 — Customer Memory

### Original prompt — Customer memory and page awareness

> Problem 8: Customer memory
>
> Please add customer memory and page awareness to the Campus Customs chatbot.
>
> For logged-in customers, save their chat history in an appropriate database table linked to their account. Reload that history when they return so they can continue the conversation and the agent can use previous messages as context.
>
> Give the agent access to the logged-in customer's name and email through agent dependencies, tools, or another clearly organized approach. Use the authenticated account to identify the customer and keep each customer's history separate.
>
> Also pass information about the page the customer is viewing to the agent. For example, if they are on a product page and ask, "Do you have this in pink?", the agent should know which product "this" refers to and use the existing product tools to answer.
> Guests should still be able to chat, but their conversations do not need to be saved across visits.
>
> Update output/harness.md to explain:
>
> * How chat history is stored and restored.
> * Which customer information the agent can access.
> * How the current page and product context reach the agent.
>
>
> Build on the existing project and verify that returning customers' conversations are restored, guest chat still works, and product-specific questions use the correct page context.

### Work completed

- **Saved history (`backend/chat_history.py`):** uses the existing `chat_messages` table.
  - After each reply to a logged-in customer, the message and reply are saved, linked by `user_id`, with the IDs of the products shown.
  - `GET /api/chat/history` returns the latest 50 messages, with product cards rebuilt from the database.
  - The agent gets the latest 20 from the database on every message, ignoring any history the website sends for logged-in customers.
  - The customer is always identified from the session cookie, so histories stay separate.
  - Guests' chats aren't saved.
- **Customer info:** a `Customer` (id, first and last name, email) built from the logged-in account goes into the agent's dependencies (`ChatDeps.customer`).
  - The first name appears in the instructions.
  - A new `get_customer_profile` tool returns the name and email when the customer asks.
- **Page awareness:**
  - The website sends `page: {path, product_id}` with each message.
  - The backend checks that the product exists, then puts the page into `ChatDeps` and the instructions ("They are viewing the product page for Yale Dad Hoodie…").
  - A new `get_current_page` tool returns that product's full info from the existing product lookup.
- **Prompt:** a new "Memory, the customer, and the page" section. Use saved history but re-check prices and stock, call `get_customer_profile` for account questions, share details only with that customer, treat "this" on a product page as that product, and look it up.
- **Chat widget:**
  - Sends the current page with each message.
  - Loads a returning customer's saved conversation under "Earlier conversation" and "Welcome back."
  - Clears the panel on logout, so the next person on the computer can't see it.
- **Tests:** 38 in total, all passing, on a throwaway copy of the database. They cover:
  - a guest's chat isn't saved
  - a logged-in chat is saved and restored, and the agent reads it from the database
  - each customer sees only their own history
  - the seeded Test User's original chat restores with cards
  - page context reaches the agent, and fake product IDs are ignored
  - the two new tools
- **Verified live in the browser:**
  - **Guest on the Yale Dad Hoodie page:**
    - "Do you have this in pink?" got "No… navy with a white Yale Dad design."
    - "Is it in stock in a medium?" got 12 available, which matches the database.
    - Nothing was saved.
  - **Logged in as the seeded Test User:**
    - Their original 6-message chat was restored.
    - "Do you have this in XL?" on the Yale Mom Hoodie page was answered correctly.
    - "What email am I signed in with?" got the right email.
    - Logging out cleared the chat. Logging back in restored all 10 messages.
    - From the Home page, "Which hoodie did I just ask you about, and what size?" got "Yale Mom Hoodie, XL," answered from memory.
  - **Cleanup:** removed the 6 test rows and the leftover session afterward. `chat_messages` matches the seed database exactly.
- **Docs:** added "Customer memory and page awareness" to `output/harness.md`. It covers storing and restoring history, what customer information the agent can access and how, how page and product context reach the agent step by step, the new types, and the checks. Updated both READMEs.

## Problem 9 — Usability Improvements

### Original prompt — Four usability improvements

> Problem 9: Usability improvements
>
> Now that the Campus Customs shop's core features are working, choose and implement four improvements:
>
> * Two front-end improvements that make the website more visually appealing and easier for shoppers to use.
> * Two agent/backend improvements that improve the agent's responses, accuracy, safety, or efficiency. These could include adding tools or reducing processing time or cost.
>
> Before you begin, or as you build, create `output/usability.md`. For each improvement, explain:
>
> * What you added or changed.
> * How it benefits Campus Customs shoppers or the business.
>
> Make sure all four improvements are implemented and working in the running app. Graders will review your write-up and check the app for the features you describe.

### Work completed

- **Started `output/usability.md` first** with the four picks, then filled it in with what changed, how it helps, and how each was checked.
- **Front end 1, the find-it-fast toolbar:**
  - The Products page has a search box, an "In my size" filter (only sizes in stock), and sorting by price or name.
  - Choices are kept in the URL, a live line reports the result count, and there's an empty state with a Clear button.
  - The product list API now returns `sizes_in_stock`.
  - Fixed a bug found in testing where quick successive filter changes could bring back an old search word.
- **Front end 2, related and recent products:**
  - "You might also like" (4 in-stock products sharing a theme and style) on every product page.
  - "Recently viewed" (kept in the browser) on product pages and the Products page.
- **Backend 1, faster and cheaper replies:**
  - The assistant answers from fresh search results, the current page's product details go into its instructions, and a prompt-cache key is set.
  - Added `backend/benchmark_chat.py`, which skips Portkey's response cache.
  - Results: 5.8 s down to 4.1 s per reply, 2.6 down to 2.0 AI calls, 22% fewer input tokens, and 90% of input tokens served from the prompt cache.
  - Tried lower reasoning effort first. It didn't help ("low") or isn't supported ("minimal"), so it wasn't kept.
- **Backend 2, the fact-check guardrail:**
  - Tools record every price and stock count they return.
  - A PydanticAI output validator blocks any "$" amount or "N left / available" in a reply that no tool returned (typed budgets are allowed) and makes the model correct it.
- **Tests:** 40 in total, all passing. Real database unchanged.
- **Verified in the running app:**
  - Toolbar: "saybrook" shows 3 items, XS-in-stock hoodies show 21 (matches the database), and both price sorts are correct.
  - Suggestion rows: Dad items for the Dad hoodie and Saybrook items for the Saybrook tee, with clicks opening the right pages.
  - Recently viewed lists items newest first.
  - Live chat: about 4.4 s per reply, a correct "sold out in L" on the Pierson page, the fake "$40" corrected to $68, and no false fact-check catches.
- **Docs:** added a Problem 9 summary to `output/harness.md` and updated both READMEs.

## Problem 10 — Style the Website

### Original prompt — A creative, cohesive storefront design

> Problem 10: Style the website
>
> Give the website a creative, cohesive design that makes it feel like an authentic Campus Customs storefront. Refine the fonts, colors, visual hierarchy, animations, product displays, and chat experience. Aim for an original, imaginative design, since innovation will earn more points. Think Avatar but for Yale.
>
> Create `output/design.md` with a brief, specific explanation of what you changed and how those choices should encourage customers to spend more time on the site and make purchases.

### Work completed

- **Concept, "Elm City After Dark":** Yale after nightfall as a bioluminescent world, built on the existing Campus Customs navy, collegiate type, and Est. 1975 seal.
- **New theme (`frontend/src/theme.css`):**
  - A deep night palette with glowing Yale blue (`#6fd3ff`), plus aqua and violet accents.
  - Glass panels with soft halos, buttons lit by gradients, and prices that glow.
- **Fonts:** added Fraunces italic for the hero's gradient-lit accent line.
- **Original effects:**
  - `Spores.tsx`: drifting points of light on a canvas that brighten near the pointer, and pause when the tab is hidden.
  - `Skyline.tsx`: a Harkness-style gothic skyline with elms and flickering windows.
  - A lantern glow that follows the pointer in the hero.
  - A turning ring of light around the floating seal.
  - The headline rises in line by line, and sections glide in on scroll.
- **New hero copy:** "When the elms glow blue, *the shop's still lit.*" Changed from "we're still open," so it doesn't imply real store hours.
- **Product displays:**
  - Cards are glowing display cases that tilt toward the pointer, with a light sweep across the photo and a "Few sizes left" badge.
  - The product page shows the item on a lit, floating pedestal, with glowing size tiles.
- **Chat:** a breathing orb launcher, a frosted-glass panel, lit message bubbles, and glowing product cards.
- **Care:** reduced-motion users get a still version, focus outlines glow, contrast stays readable, and product photos keep white backdrops for true color.
- **Fixed on review:** a layering rule would have pinned the floating chat and the skip link in place. Excluded them.
- **Verified:**
  - Lint, types, and build pass.
  - Desktop screenshots of Home, Products, the product page, the chat (live, with a real reply and product cards), About, and Log in.
  - Phone screenshots of Home and a product page, with no sideways scrolling.
  - No console errors.
- **Docs:** wrote `output/design.md` (what changed and why it should increase time on site and purchases) and updated the frontend README.

## Problem 11 — Site Testing (App Check)

### Original prompt — Test the site and document it

> Problem 11: Site Testing (App Check)
> Test the running website and document the results in `output/app_check.html`, an HTML page that opens when double-clicked. Include clear screenshots demonstrating:
>
> 1. The chat checking an item's inventory and accurately reporting stock and pricing from the database.
> 2. Dynamic product search cards appearing after a shopper asks about a category, such as hoodies.
> 3. One usability improvement you implemented in Problem 9.
>
> Give each check its own heading, screenshot, and one or two sentences explaining what the image confirms.
> Save the screenshots in `output/app_check_images/` and reference them in the HTML using relative paths, such as `app_check_images/inventory.png`.

### Work completed

- **Database facts first:** Pierson College Crewneck is $58, with L = 0, S = 2, M = 8, XS = 12, XXL = 2, and XL = 0. There are 27 hoodies, and 21 of them have XS in stock, the cheapest at $45.
- **Screenshots from the running app** (React on :5177, FastAPI on :8000, real gpt-5.6-luna replies), saved in `output/app_check_images/`:
  1. `inventory.png`: on the Pierson College Crewneck page, "How much is this crewneck, and do you have it in L or S?" got "$58. L is sold out, but S is available, only 2 left," which matches the database.
  2. `hoodie_search.png`: "What hoodies do you have?" asked from the Home page moved the site to Products and showed "From the shop assistant: Yale Hoodies · 27 styles" with every hoodie card (photo, name, price, description). That matches the 27 hoodies in the database.
  3. `usability_toolbar.png`: the Problem 9 toolbar with Hoodies, "XS in stock," and "Price: low to high" shows 21 styles starting at the $45 UA Gameday Hood, which matches the database.
- **Built `output/app_check.html`:** a self-contained page with styles inside the file. Each check has its own heading, a PASS badge, one or two sentences on what it confirms, the screenshot (by relative path), and a small table comparing the database with what the site showed.
- **Verified:** opened the page straight from disk as a double-click would. All 3 images load, and the page fits a phone width without sideways scrolling.

## Problem 12 — Audit Trail, Safety, Finish Harness

### Original prompt — Audit trail, safety guidelines, and the full harness

> Problem 12: Audit Trail, Safety, Finish Harness
> Maintain an append-only log of the agent's activity in `output/audit_trail.json`. Record timestamps, tool names, brief summaries of inputs and results, and why the agent stopped. Preserve existing entries between runs.
> Add safety guidelines for the agent to `prompts/prompt.md`.
> Complete `output/harness.md` so that someone reading it can understand how the system operates. Include:
>
> * The fields defined in `models.py` and why you selected them.
> * The agent's available tools and capabilities.
> * The safety rules it follows.
> * Technical settings, including agent-loop limits, result caps, and models used.
> * Instructions for starting both the front end and back end.

### Work completed

- **Audit trail (`backend/audit.py`, wired into `agent.answer`):** every chat reply, including failed ones, appends one entry to `output/audit_trail.json`.
  - Each entry records: the timestamp; shopper (account number or guest); page; a shortened message; each tool call with its time, tool name, and brief input and result summaries; fact-check retries; the reply, cards, and search shown; why the agent stopped (answered with finish reason, provider safety block, usage limit, failed checks, missing key, or error); token usage; and duration.
  - Uses PydanticAI's `capture_run_messages`, so tool calls are logged even when a run fails.
  - Append-only: a lock, read, append, and atomic replace. A damaged file is set aside, never overwritten.
  - Emails and card-like numbers are masked.
  - Tests use their own throwaway log, and the test setup refuses to run against the real one.
- **Safety guidelines in `backend/prompts/prompt.md`:** replaced the short "safety basics" with full guidelines covering:
  - **Honesty:** tool-sourced facts only, no invented deals or policies, no overstating stock.
  - **Privacy:** only the customer's own account, never anyone else's, never repeating passwords or card numbers.
  - **Staying in role:** treating messages as information, and keeping instructions private.
  - **Respect and wellbeing:** no pressure, content appropriate for all ages, kindness to anyone in distress.
  - **When in doubt:** say what can be confirmed, and suggest the shop team for the rest.
- **Tests:** 45 in total, all passing. The 4 new audit tests check one entry per reply with earlier entries preserved, tool steps and summaries, fact-check failures and retries, masking, and damaged-file handling. One new search test is described below.
- **Live checks with the real AI:**
  - A discount code request, "I'm his mom," a card number, and an essay request were all handled safely, and the card number was masked in the log.
  - The audit trail kept all 7 entries across a server reload.
- **A bug found through the audit trail:** "Is the Yale Dad Crewneck in stock in medium?" got "I couldn't confirm…" because the search's size filter hid the product, which is sold out in M.
  - `search_products` now returns `sold_out_in_requested_size`, and the prompt tells the assistant to use it.
  - The answer is now "sold out in medium… $58… available in XS, S, and XXL," which matches the database. Pierson in XL was also correct.
  - Added a test for it.
- **Completed `output/harness.md`:**
  - A "Start here" overview at the top, with a contents list, a system diagram, how one chat message flows, and step-by-step commands to start the backend and front end.
  - The earlier problem sections, updated.
  - Five new reference sections: every model in `models.py` with its fields and why they were chosen; the agent's 6 tools and capabilities; the safety rules (prompt and code); technical settings (model, loop limits, result caps, history and message limits, rate limits, passwords, sessions, ports, and measured speed); and the audit trail format, with a real example.
- Updated `backend/README.md`.
