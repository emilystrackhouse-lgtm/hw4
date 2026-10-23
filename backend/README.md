# Campus Customs — API

A FastAPI app that reads `../data/campus_customs.db`. It serves products and product images, handles shopper accounts, and runs the shop chatbot, a PydanticAI agent. Products were added in Homework 4, Problem 3, accounts in Problem 4, and the chatbot in Problem 5.

## Set up and run

First put the data pack in `../data/` (see `../README.md`), copy `../.env.example` to `../.env`, and add your `PORTKEY_API_KEY`. Then, from `backend/`:

```bash
python3 -m venv .venv
xattr -w 'com.apple.fileprovider.ignore#P' 1 .venv
source .venv/bin/activate
pip install -r ../requirements.txt
python ../prepare_product_images.py
uvicorn main:app --reload --port 8000
```

The `xattr` line keeps the virtual environment out of iCloud sync, as `AGENTS.md` requires. Interactive API docs are at http://127.0.0.1:8000/docs. The website forwards its `/api` and `/media` requests to port 8000.

`hw4/.env` (git-ignored) holds:

| Setting | What it's for |
|---|---|
| `PORTKEY_API_KEY` | The AI model key for the chatbot, used through Portkey. Without it, the chatbot answers "offline" and the rest of the site still works. |
| `OPENAI_MODEL` | The chatbot's model, `gpt-5.6-luna` by default |
| `PORTKEY_BASE_URL` | Portkey's API address |
| `COOKIE_SECURE` | `true` when the site is served over HTTPS, so the login cookie is only ever sent encrypted. `false` for local development. |

## Endpoints

| Method and path | Returns |
|---|---|
| `GET /api/health` | `{ok, products, images}`: a quick check that the database can be read |
| `GET /api/products` | Every product: ID, name, garment type, description, colors, price, image URL, and total stock |
| `GET /api/products/{product_id}` | One product with its search tags and stock for each size (XS–XXL). Returns 404 if the ID doesn't exist |
| `GET /media/products/{file}.jpg` | A product photo. The URL comes from `image_file_path` in the database |
| `POST /api/auth/signup` | Creates a user from `{first_name, last_name, email, password, confirm_password}`, logs them in, and returns the user (201). Returns 400 for a field problem and 409 if the email already has an account |
| `POST /api/auth/login` | Logs in with `{email, password}` and returns the user. Returns 401 with one generic message, or 429 after too many failed tries |
| `POST /api/auth/logout` | Ends the session (204) |
| `GET /api/auth/me` | The logged-in user, or `null` for visitors |
| `GET /api/chat/history` | The logged-in customer's latest 50 saved messages (with product cards rebuilt from the database), or `[]` for guests |
| `POST /api/chat` | Sends `{message, history, page}` to the shop assistant. Logged-in customers' history comes from the database, and each exchange is saved to `chat_messages`. Guests' `history` comes from the request and isn't saved. It and returns `{reply, products, search}`. `products` holds up to 4 product cards built from the database. `search` is `{title, products}` with every match when the shopper asked to browse a category, and `null` otherwise. Returns 429 if a visitor sends too many messages, 503 if the AI key is missing, and 502 if the model fails |

Errors that a shopper can fix come back as `{"detail": {"message": ..., "field": ...}}`, so the site can show each message under the right field. The API never returns a password or password hash.

## The shop chatbot

| File | Job |
|---|---|
| `agent.py` | Creates the PydanticAI agent. Loads `prompts/prompt.md` (re-read whenever it changes) and the model (`OPENAI_MODEL` through Portkey with `PORTKEY_API_KEY`), runs it, and builds product cards from the database |
| `prompts/prompt.md` | The system prompt: brand voice, product facts, and safety basics |
| `tools.py` | Read-only tools: `search_products` (words, style, max price, size in stock), `get_product_info` (description, price, stock for every size), `check_size_stock` (one size: count, sold out, low stock, other sizes), `list_styles`, `get_customer_profile` (the logged-in customer's own name and email), and `get_current_page` (the page, with full product info on a product page) |
| `models.py` | Pydantic types for chat requests and replies, product cards, the agent's `ChatReply` output, and tool results |
| `catalogue.py` | Product reading shared by the product pages and the tools |
| `chat_history.py` | Saves and reloads each logged-in customer's conversation in `chat_messages`, by account |

`output/harness.md` explains the full flow, from the website to FastAPI to the agent and back.

## How passwords are stored and checked

Signup and login use **one recipe**, the same one as the seed database (`passwords.py`):

- **Stored as:** `pbkdf2_sha256$<salt>$<hash>`
- **Hash:** PBKDF2-HMAC-SHA256 with **120,000 iterations**, written as 64 hex characters
- **Salt:** random for each account, made at signup with `secrets.token_hex(16)` and used as UTF-8 text

**At login:**
1. Read the salt from the middle of the stored string. A new salt is never made at login.
2. Re-hash the typed password with that salt and the same iteration count.
3. Compare the result with the stored hash using `hmac.compare_digest`, a constant-time comparison.

A stored hash is never "un-hashed," because that isn't possible. If signup and login ever used different settings, even the right password would stop matching, so both call the same functions.

The seeded Test User (`test@campuscustoms.yale.edu`) logs in with its known seed password. The other two seeded accounts use the same format.

| Threat | Protection |
|---|---|
| The database file is copied or leaked | Only salted one-way hashes are stored. 120,000 rounds of PBKDF2 make each guess slow, and per-account salts make precomputed tables useless. |
| Password guessing on the login form | 5 failed tries per email, or 20 per IP address, within 15 minutes triggers a temporary block (429 with `Retry-After`). Very common passwords, and passwords equal to the email, are refused at signup. |
| Timing attacks on the comparison | `hmac.compare_digest` takes the same time wherever two hashes differ. |
| Finding out who has an account | A wrong password and an unknown email get the same message, and take the same time, because a dummy hash is checked when the email doesn't exist. |
| Stealing a login session | The session token is random (256 bits) and kept in an **HttpOnly**, `SameSite=Lax` cookie that page scripts can't read. The database stores only a SHA-256 hash of the token. Sessions expire after 7 days, and logging out deletes them. |
| SQL injection | Every query uses parameters. User input is never pasted into SQL. |
| Passwords showing up in logs | Passwords are received as `SecretStr`, which hides them in logs and error output. |

The code is in `passwords.py` (hashing), `auth.py` (endpoints, sessions, and rate limits), and `db.py` (connections and the `sessions` table). Product pages use a read-only connection. Only account actions write to the database.

**For a real deployment:**
- Serve the site over HTTPS with `COOKIE_SECURE=true`.
- Move the rate-limit counters into a shared store such as Redis. They're kept in memory now, so they reset when the server restarts.
- Raise the iteration count. Current OWASP guidance for PBKDF2-HMAC-SHA256 is 600,000. Raising it means storing the count inside each hash, so existing accounts keep working.

## Setting or resetting a password

Nobody can see an existing password, because only the hash is stored. To give an account a new password, run `set_password.py` from `backend/`:

```bash
.venv/bin/python set_password.py ada.1789818990@yale.edu
```

That prompts you to type the new password twice. Your typing is hidden, and the same rules as signup apply. Add `--generate` to have the tool create a strong random password (20 characters with no look-alike characters) and show it once:

```bash
.venv/bin/python set_password.py ada.1789818990@yale.edu --generate
```

Either way, the password is stored with the same recipe as signup, and the account is logged out everywhere.

## Tests

```bash
pip install -r requirements-dev.txt
.venv/bin/python -m pytest
```

The tests run against a throwaway copy of the database, so they never touch real accounts. `tests/conftest.py` points the backend at the copy before any test loads, and stops the run if it would ever use the real file. The chat tests use a scripted stand-in for the AI, so they run offline. There are 45 tests. They check:
- that the seeded Test User can log in
- that the hash recipe matches the seed format exactly, including rejecting malformed or foreign hash strings
- that a brand-new account can log in with the same settings
- the stored format, and that the password is nowhere in the database
- different salts for identical passwords
- the HttpOnly cookie, and that only the token's hash is stored
- login, the current-user check, and logout
- identical answers for a wrong password and an unknown email
- case-insensitive duplicate emails
- field checks, rate limiting, injection attempts
- the `set_password.py` tool
- the chat route: replies, cards built only from products the tools returned, history and the shopper's name reaching the model, bad requests, the "offline" and error responses, and the polite decline when the provider's safety filter blocks a message
- the fact-check guardrail: a made-up price is sent back and corrected; real prices, counts, and typed budgets pass
- the chatbot's tools, checked against direct database queries: shopper-word search, filters, product info, sold-out, low-stock, and in-stock sizes, and the style summary

## Notes

- **Display names:** the catalogue's names were generated from URL slugs ("Morse 1 4 Zip"). `display_name()` in `main.py` turns them into storefront names ("Morse ¼-Zip") without changing the data. Set `CAMPUS_CUSTOMS_DB` to use a different database file.
- **Photos:** 76 of the 102 photos have black backgrounds left over from transparent images. `../prepare_product_images.py` makes white-background copies in `../data/products_web/`, and the API serves those when the folder exists. The originals in `../data/products/` are never changed. Re-run the script after adding photos:

  ```bash
  .venv/bin/python ../prepare_product_images.py
  ```

## Speed benchmark and fact-check (Problem 9)

- `benchmark_chat.py` asks 5 typical shopper questions with the real AI and prints the time, AI calls, and tokens for each. Set `PORTKEY_FORCE_REFRESH=1` to skip Portkey's response cache, so each question really calls the model:

  ```bash
  PORTKEY_FORCE_REFRESH=1 .venv/bin/python benchmark_chat.py after
  ```

- `fact_check` in `agent.py` is a PydanticAI output validator. It blocks any price or stock count in a reply that no tool returned during that reply, and sends the model back to fix it. Catches are logged as warnings (`campus_customs.fact_check`).

See `../output/usability.md` for the before and after numbers.

## Audit trail (Problem 12)

Every chat reply appends one entry to `../output/audit_trail.json` (set `CAMPUS_CUSTOMS_AUDIT_LOG` to change where).
- **What it records:** the time, who asked (account number or guest), the page, each tool call with brief input and result summaries, fact-check retries, the reply, why the agent stopped, and tokens used.
- **Append-only:** earlier entries are never changed. Each write is atomic and locked, and a damaged file is set aside rather than overwritten.
- **Privacy:** emails and card-like numbers are masked.
- **Code and tests:** the code is in `audit.py`, and the tests in `tests/test_audit.py` write to a throwaway log.

`../output/harness.md` is the full guide to the system: fields, tools, safety rules, settings, and how to run it.
