# Homework 4 — Usability Improvements (Problem 9)

The core shop works: the catalogue, product pages, accounts, and a chatbot that searches, checks stock, and remembers customers. Problem 9 adds four improvements, two for shoppers on the website and two in the assistant's backend. All four are running in the app.

| # | Improvement | Type | Where to see it |
|---|---|---|---|
| 1 | Find-it-fast toolbar: search, "In my size", and sort | Front end | **Products** page, under the style buttons |
| 2 | "You might also like" and "Recently viewed" | Front end | Bottom of every **product page**, and bottom of the **Products** page |
| 3 | Faster, cheaper assistant replies | Agent / backend | Any chat. Measured with `backend/benchmark_chat.py` |
| 4 | Fact-check guardrail on prices and stock counts | Agent / backend | Every chat reply. Covered by automated tests |

---

## 1. Find-it-fast toolbar on the Products page (front end)

### What changed

A toolbar now sits above the product grid with three controls that work together and with the style buttons:

- **Search box:** filters as you type, across product names, descriptions, colors, and garment types. "saybrook" shows the 3 Saybrook items. "gray" shows gray designs. Several words must all match ("gray hoodie").
- **In my size:** shows only products with that size **in stock right now**. To support this, `GET /api/products` now includes each product's `sizes_in_stock`, read from the inventory table.
- **Sort by:** Featured, Price low to high, Price high to low, or Name A to Z.

Other details:
- A live line, read aloud by screen readers, explains what's showing: "Showing 21 styles in Hoodies with XS in stock."
- If nothing matches, a friendly message offers a **Clear search and size** button.
- Every choice is saved in the web address (for example, `/products?style=hoodies&size=XS&sort=price-asc`), so a filtered view can be bookmarked, shared, or reached with the Back button.
- The toolbar also refines the results of a chat search ("What hoodies do you have?").

### How it helps

- **Shoppers find what they want in seconds** instead of scrolling 102 products. Size is the biggest time-saver: a shopper who wears XS never sees, or falls for, a style that's sold out in their size. That avoids the frustration of picking something and then hitting "Sold out."
- **Budget shoppers** can sort by price, and parents shopping for a student can search a college name.
- **For the business**, shoppers who find an in-stock item in their size are much more likely to buy, and shared links ("here are all the Saybrook pieces") bring friends to the site.

**Checked in the running app:**
- "saybrook" showed exactly 3 items.
- Hoodies with XS in stock showed 21, which matches the database.
- Price low to high started with the $45 UA Gameday Hood, and high to low started with the $88 full-zip.
- A search for nonsense showed the empty message, and Clear restored the list.

---

## 2. "You might also like" and "Recently viewed" (front end)

### What changed

- **You might also like:** a row of 4 related products at the bottom of every product page, each with its photo, name, and price, linking to its page.
  - Picks share a theme first (the same residential college, family member, sport, or school), then the same style group, then the closest price.
  - Only in-stock items are suggested.
  - For example, the Yale Dad Hoodie suggests the Yale Dad Crewneck and Yale Dad T-Shirt. The Saybrook Logo T-Shirt suggests the Saybrook Crewneck and Saybrook Fleece.
- **Recently viewed:** the last products a shopper opened, newest first, shown on product pages (without the product being viewed or repeating suggestions) and at the bottom of the Products page.
  - It's remembered in the shopper's own browser (`localStorage`), never on the server, and simply shows nothing if storage is turned off.
- Both rows scroll sideways on phones.

### How it helps

- **Shoppers compare and decide faster.** Someone looking at the Dad hoodie usually wants to see the Dad crewneck or tee next, and they're one tap away instead of a new search.
- **Shoppers get back to what they liked.** "Recently viewed" saves digging back through the catalogue after browsing a dozen items.
- **For the business,** related suggestions are a proven way to raise items per order (a matching Mom and Dad set, or a tee plus a crewneck from the same college), and they keep shoppers on the site longer.

**Checked in the running app:**
- The Yale Dad Hoodie suggested the Dad Crewneck, Dad T-Shirt, Basic Hoodie, and Champion Hoodie.
- Clicking a suggestion opened that product's page.
- After viewing three products, the Products page listed them newest first.

---

## 3. Faster, cheaper assistant replies (agent / backend)

### What changed

Most of a chat's waiting time and cost comes from **round trips to the AI model**, and each round trip re-sends the long system prompt. Three changes cut both:

1. **Fewer lookups.** Search results already come fresh from the database with each product's price, description, and sizes in stock. The prompt now tells the assistant to answer straight from them, and to search only once, instead of always doing a second lookup.
2. **The page's product is handed over up front.** On a product page, that product's full details (price, description, colors, and the count for every size) go into the assistant's instructions, so "Do you have this in XL?" needs no tool call.
3. **Prompt caching.** A fixed `openai_prompt_cache_key` lets the AI provider reuse the unchanging system prompt between calls. Cached input tokens are billed at a small fraction of the normal price.

`backend/benchmark_chat.py` asks the same 5 typical questions (a category, a size check, a price, "this" on a product page, and gift ideas with a budget) and reports time, AI calls, and tokens. Portkey's response cache was bypassed so each run really called the model.

| Measure (average per reply) | Before | After | Change |
|---|---|---|---|
| Time to answer | 5.8 s | 4.1 s | **29% faster** |
| AI round trips | 2.6 | 2.0 | **23% fewer** |
| Input tokens sent | 7,879 | 6,141 | **22% fewer** |
| Input tokens served from the prompt cache | not measured | 5,532 (90%) | billed at a fraction of the price |

The numbers come from separate benchmark runs. Times vary by a few tenths of a second from run to run, but the drop to 2.0 calls held in every run.

### How it helps

- **Shoppers wait about a third less** for an answer, which matters most on phones and for quick questions like "Is this in my size?"
- **The shop pays less for every conversation:** fewer calls, fewer tokens, and most of the remaining input tokens are billed at the cached rate. As chat traffic grows, that saving grows with it.
- **Answers are no less accurate:** the shortcuts only reuse data that came fresh from the database in the same reply.

---

## 4. Fact-check guardrail on prices and stock counts (agent / backend)

### What changed

Before any reply reaches a shopper, a PydanticAI **output validator** (`fact_check` in `backend/agent.py`) checks its numbers:

- **During the reply,** every tool records each price and stock count it returned in the agent's dependencies (`ChatDeps.known_prices` and `known_counts`). The page product's details count too.
- **Prices:** every `$` amount in the reply must be one of those prices, or a budget the shopper typed ("under $60").
- **Counts:** every count like "2 left", "12 available", or "only 3" must be one of those counts.
- **If anything doesn't match,** the reply is blocked and the model is told exactly what was wrong ("Your reply mentions $99, which doesn't match any price… Look it up with a tool, or remove it"). It then gets another try. The shopper only ever sees a corrected answer. Each catch is logged on the server.

### How it helps

- **Shoppers can trust the numbers.** A chatbot that invents a price or says "plenty left" when a size is sold out causes real problems: disappointed customers, staff having to honor or walk back a quoted price, and lost trust. The prompt already says "never make up prices or stock," and the guardrail **enforces** it in code, even if the model slips or a shopper tries to talk it into a fake price.
- **For the business,** it protects against pricing mistakes and false stock promises.

**Checked:**
- A scripted test model that first answers "$99, only 3 left" for the $68 Yale Dad Hoodie is sent back, and its corrected "$68" answer is the one returned.
- Real prices, real counts, and typed budgets pass.
- Live, "I heard the Yale Dad Hoodie is $40 now, is that right?" got "No, it's currently $68."
- On the full benchmark, real answers passed on the first try, with no extra calls and no slowdown.

---

### Where the code lives

| Improvement | Files |
|---|---|
| 1 | `frontend/src/pages/Products.tsx`, `backend/catalogue.py` (`sizes_in_stock`), `frontend/src/index.css` (`.toolbar`) |
| 2 | `frontend/src/components/ProductStrip.tsx`, `frontend/src/recentlyViewed.ts`, `frontend/src/pages/ProductDetail.tsx`, `frontend/src/pages/Products.tsx` |
| 3 | `backend/agent.py` (`make_deps`, `MODEL_SETTINGS`), `backend/prompts/prompt.md`, `backend/benchmark_chat.py` |
| 4 | `backend/agent.py` (`fact_check`), `backend/tools.py` (recording prices and counts), `backend/models.py` (`ChatDeps`), `backend/tests/test_chat.py` |

All 40 automated tests pass, and they run against a throwaway copy of the database.
