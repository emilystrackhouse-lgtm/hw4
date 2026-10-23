# Campus Customs — Front End

A React + Vite + TypeScript site for Campus Customs, the family-run Yale apparel shop across from campus since 1975. It was built in Homework 4, Problem 3.

## Run it

The product pages need the API, so start the backend first (see `../backend/README.md`), then:

```bash
npm install
npm run dev
```

Then open http://localhost:5177. Vite forwards `/api` and `/media` requests to the FastAPI backend on port 8000.

Other commands:

- `npm run build`: type-checks the code and builds the production site into `dist/`.
- `npm run lint`: checks the code with oxlint.

## Pages

| Path | Page |
|---|---|
| `/` | Home: hero, store facts, collections, story teaser |
| `/products` | Products: every item with its photo, name, price, short description, and color. Filter by style (`?style=hoodies`), search (`?q=`), size in stock (`?size=XS`), and sort (`?sort=price-asc`). A "Recently viewed" row is at the bottom |
| `/products/:productId` | A single product: large photo on one side; description, price, sizes and stock, colors, and tags on the other. "You might also like" and "Recently viewed" rows are at the bottom |
| `/about` | About Us: the family story, services, and values |
| `/login` | Log in with email and password |
| `/create-account` | Create an account: first name, last name, email, password, and confirm password |
| `/account` | The logged-in shopper's details and a Log out button. Logged-out visitors are sent to Log in |

## Accounts

Creating an account or logging in calls the backend (`/api/auth/...`). The backend stores the password as a salted PBKDF2-HMAC-SHA256 hash (the same format as the seed data) and keeps the session in an HttpOnly cookie that page scripts can't read. `src/auth.ts` and `components/AuthProvider.tsx` share the logged-in shopper with every page. Once someone is logged in, the nav bar shows "Hi, {first name}" and Log out, and the chat greets them by name. Both forms check every field before sending and show the server's message under the right field (for example, "An account with this email already exists").

## Chat panel

An **Ask us** button sits in the bottom right corner of every page and opens a floating chat panel connected to the shop assistant (`POST /api/chat`).

- Each message is sent with the last 20 messages of the conversation.
- While waiting, the panel shows a typing indicator.
- The reply appears with up to 4 product cards. Each card has a photo, price, and sizes in stock, and links to the product page.
- Errors (busy, offline, or trouble answering) appear as a short message in the chat.
- **Memory and page awareness:** each message includes the current page (`path`, plus `product_id` on a product page), so "Do you have this in pink?" means the product on screen. When a customer logs in, their saved conversation is loaded from `/api/chat/history` and shown under "Earlier conversation." Logging out clears the panel. Guests' chats last only for the visit.
- **Chat search:** when the reply includes `search` (the shopper asked to browse a category, such as "What hoodies do you have?"), the results are saved in shared chat state, the site goes to `/products`, and the page shows every match under a "From the shop assistant" banner. Each card opens its product page as usual. "Show all products" or any style button clears the search.
- The **Ask about this item** button on a product page opens the panel with a question about that product already filled in.

## Where things live

- `src/api.ts`: API types, fetch helpers, and the `useApi` hook (loading, error, and retry states)
- `src/chat.ts`: shared chat state, so any page can open the panel
- `src/auth.ts`: shared login state (`useAuth`)
- `src/components/`: the nav bar, footer, logo, seal badge, page layout, form field (with Show/Hide for passwords), product card, color list, chat panel, and the auth and chat providers
- `src/pages/`: one file per page
- `src/data/shop.ts`: store facts and the style groups used by the filters
- `src/format.ts`: price formatting and color swatches
- `src/index.css`: brand colors, typography, and all styles

## Brand and design

- **Theme:** "Elm City After Dark" (Problem 10, see `../output/design.md`). Yale at night as a bioluminescent world: a deep night background, glowing Yale blue `#6fd3ff` with touches of aqua and violet, and white product photos in lit display cases. It's built on the original Campus Customs navy `#0c233f` and steel blue `#7ba0c5`.
- **Type:** Archivo Narrow (condensed headings), Archivo (body text), and Fraunces italic (the hero's accent line), from Google Fonts.
- **Effects:**
  - `components/Spores.tsx`: drifting points of light that react to the pointer.
  - `components/Skyline.tsx`: the glowing gothic skyline.
  - Product cards tilt and glow, and the chat button is a breathing orb.
  - Sections glide in on scroll.
  - All motion stops when "reduce motion" is set.
- **Styles:** `src/index.css` holds the base layout. `src/theme.css` is the night theme, loaded after it.
