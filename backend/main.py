"""Campus Customs API: products, product images, shopper accounts, and the shop chatbot.

Run from backend/ (with the virtual environment active):
    uvicorn main:app --reload --port 8000
API docs: http://127.0.0.1:8000/docs

The website (Vite, port 5177) forwards /api and /media requests here.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

# Load settings and the AI key from hw4/.env before the modules that read them.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")  # hw4/.env

from fastapi import FastAPI, HTTPException, Request, status  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

import catalogue  # noqa: E402
import chat_history  # noqa: E402
from agent import ChatNotConfigured, answer  # noqa: E402
from auth import AttemptLimiter, client_ip, current_user, problem, too_many_tries  # noqa: E402
from auth import router as auth_router  # noqa: E402
from db import DATA_DIR, ensure_schema  # noqa: E402
from models import ChatHistoryMessage, ChatRequest, ChatResponse, Customer, Product, ProductDetail  # noqa: E402

logger = logging.getLogger("campus_customs")

# White-background copies made by ../prepare_product_images.py, with the
# original photos as a fallback. Both use the filenames stored in the database.
WEB_IMAGE_DIR = DATA_DIR / "products_web"
IMAGE_DIR = WEB_IMAGE_DIR if WEB_IMAGE_DIR.is_dir() else DATA_DIR / "products"

# Each chat message costs an AI call, so cap how often one visitor can send them.
chat_messages_by_ip = AttemptLimiter(limit=30, window_seconds=10 * 60)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    ensure_schema()
    yield


app = FastAPI(title="Campus Customs API", version="0.3.0", lifespan=lifespan)
app.include_router(auth_router)
app.mount("/media/products", StaticFiles(directory=IMAGE_DIR), name="product-images")


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "products": len(catalogue.list_products()), "images": IMAGE_DIR.name}


@app.get("/api/products", response_model=list[Product])
def list_products() -> list[Product]:
    return catalogue.list_products()


@app.get("/api/products/{product_id}", response_model=ProductDetail)
def get_product(product_id: str) -> ProductDetail:
    product = catalogue.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.get("/api/chat/history", response_model=list[ChatHistoryMessage])
def chat_history_for_me(request: Request) -> list[ChatHistoryMessage]:
    """The logged-in customer's saved conversation, so the chat can pick up where they left off. Guests get []."""
    user = current_user(request)
    return chat_history.history_for_display(user.id) if user else []


@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, request: Request) -> ChatResponse:
    """Sends one shopper message to the shop assistant.

    Logged-in customers: the conversation so far comes from their saved history, and
    this exchange is saved too. Guests: the website sends the conversation, and nothing is saved.
    """
    ip = client_ip(request)
    wait = chat_messages_by_ip.seconds_until_allowed(ip)
    if wait:
        raise too_many_tries(wait)
    chat_messages_by_ip.record(ip)

    user = current_user(request)  # who's chatting comes from the session cookie, never the request body
    customer = (
        Customer(id=user.id, first_name=user.first_name, last_name=user.last_name, email=user.email) if user else None
    )
    history = chat_history.recent_turns(user.id) if user else body.history
    try:
        response = await answer(body.message, history, customer, body.page)
    except ChatNotConfigured as error:
        logger.error("Chat is off: %s", error)
        raise problem(status.HTTP_503_SERVICE_UNAVAILABLE, "The shop assistant is offline right now.") from None
    except Exception:
        logger.exception("The shop assistant failed to answer")
        raise problem(
            status.HTTP_502_BAD_GATEWAY, "The shop assistant had trouble answering. Please try again in a moment."
        ) from None
    if user:
        chat_history.save_exchange(user.id, body.message, response)
    return response
