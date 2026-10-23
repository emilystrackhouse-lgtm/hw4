# Campus Customs: Homework 4 (hw4)

This is a shopping website for **Campus Customs**, the family-run Yale apparel shop across from campus since 1975, with an AI shop assistant built on **PydanticAI** and **FastAPI**. Shoppers can browse and filter 102 products, open product pages with live stock, create an account and log in, and chat with an assistant that:
- looks up prices and per-size stock in the database
- puts category searches on the page as cards
- remembers logged-in customers
- knows which product they're viewing

The design theme is "Elm City After Dark," Yale at night as a glowing, bioluminescent world.

**For the full explanation of how it all works, read [`output/harness.md`](output/harness.md).**

## Project structure

```text
hw4/
├── README.md               this file
├── AI_prompts.md           every prompt used to build the project, problem by problem
├── requirements.txt        Python packages for the backend
├── .env.example            settings template (placeholders only; copy to .env)
├── .gitignore              keeps .env, the database, product images, and build files out of Git
├── backend/                FastAPI application
│   ├── main.py             the FastAPI app: products, images, accounts, chat, and chat history routes
│   ├── agent.py            ┐
│   ├── tools.py            │ the shop assistant agent: four files
│   ├── models.py           │ (system prompt, agent wiring, tools, and Pydantic types)
│   ├── prompts/prompt.md   ┘
│   ├── auth.py, passwords.py, db.py, catalogue.py, chat_history.py, audit.py   supporting modules
│   ├── set_password.py, benchmark_chat.py                                     admin and benchmark scripts
│   └── tests/              45 automated tests
├── frontend/               Vite + React + TypeScript website
├── output/
│   ├── harness.md          how the system works: fields, tools, safety, settings, and how to run it
│   ├── design.md           the visual design and why it should help sales
│   ├── usability.md        the four usability improvements
│   ├── app_check.html      site test report (open it by double-clicking)
│   ├── app_check_images/   screenshots used by the report
│   └── audit_trail.json    append-only log of the agent's activity
├── data/                   the local data pack goes here (not in Git, see below)
├── campus_customs_db_reference.md   a field-by-field guide to the database
└── fix_catalogue_data.py, normalize_catalogue_labels.py, prepare_product_images.py   data cleanup scripts
```

## 1. Put the local data pack in place

The database and product photos are **not in Git**. Copy them into `hw4/data/`:

```text
hw4/data/campus_customs.db     the SQLite database (catalogue, inventory, users, chat_messages)
hw4/data/products/             the product photos (.jpg), named as in catalogue.image_file_path
```

The backend also creates a `sessions` table in the database for logins, and makes `data/products_web/` (white-background copies of the photos) in step 3.

## 2. Add your settings

From the `hw4/` folder:

```bash
cp .env.example .env
```

Open `.env` and set your own `PORTKEY_API_KEY`. `OPENAI_MODEL` is already set to `gpt-5.6-luna`. Never commit `.env`.

## 3. Start the backend (FastAPI, port 8000)

Use Python 3.13 or newer. From the `backend/` folder:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
python ../prepare_product_images.py
uvicorn main:app --reload --port 8000
```

- You only need the `venv`, `pip`, and `prepare_product_images.py` steps the first time. After that, just run `source .venv/bin/activate` and `uvicorn main:app --reload --port 8000`.
- On a Mac with iCloud Desktop sync, run `xattr -w 'com.apple.fileprovider.ignore#P' 1 .venv` right after creating the venv to keep it out of sync.
- Check it at http://127.0.0.1:8000/api/health. Interactive API docs are at http://127.0.0.1:8000/docs.

## 4. Start the front end (Vite + React, port 5177)

Use Node 20 or newer. In a second terminal, from the `frontend/` folder:

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5177**. The website forwards `/api` and `/media` requests to the backend on port 8000, so start the backend first.

**Test account:** the seeded Test User, `test@campuscustoms.yale.edu`, with the seed password from the data pack. You can also create a new account on the site.

## Tests

From `backend/`, with the virtual environment active:

```bash
pip install -r requirements-dev.txt
python -m pytest
```

The 45 tests run against a throwaway copy of the database and a throwaway audit log, so they never change your data.

## More documentation

- [`output/harness.md`](output/harness.md): the complete guide to the system
- [`output/app_check.html`](output/app_check.html): screenshots confirming the chat's stock answers, chat search cards, and a usability improvement
- [`backend/README.md`](backend/README.md) and [`frontend/README.md`](frontend/README.md): details for each part
