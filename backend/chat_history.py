"""Saved chat history for logged-in customers, in the existing chat_messages table.

Each row belongs to one account (user_id), so every customer only ever sees and
continues their own conversation. Guests' chats are never saved.
"""

from __future__ import annotations

import json

import catalogue
from db import query, transaction
from models import ChatHistoryMessage, ChatResponse, ChatTurn, ProductCard

# How many earlier messages the agent reads as context, and how many the website shows on return.
CONTEXT_MESSAGES = 20
DISPLAY_MESSAGES = 50
MAX_CARDS = 4


def save_exchange(user_id: int, message: str, response: ChatResponse) -> None:
    """Stores the customer's message and the assistant's reply (with the IDs of any product cards)."""
    product_ids = json.dumps([{"product_id": card.product_id} for card in response.products])
    with transaction() as con:
        con.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'user', ?, NULL)",
            (user_id, message),
        )
        con.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'assistant', ?, ?)",
            (user_id, response.reply, product_ids),
        )


def _recent_rows(user_id: int, limit: int):
    rows = query(
        """
        SELECT role, content, products_json, created_at FROM chat_messages
        WHERE user_id = ? ORDER BY id DESC LIMIT ?
        """,
        (user_id, limit),
    )
    return list(reversed(rows))


def recent_turns(user_id: int) -> list[ChatTurn]:
    """The customer's latest messages, oldest first, for the agent to use as context."""
    return [ChatTurn(role=row["role"], content=row["content"]) for row in _recent_rows(user_id, CONTEXT_MESSAGES)]


def _cards(products_json: str | None) -> list[ProductCard]:
    """Rebuilds product cards from saved product IDs, with today's price and stock."""
    if not products_json:
        return []
    try:
        saved = json.loads(products_json)
    except json.JSONDecodeError:
        return []
    cards = []
    for item in saved if isinstance(saved, list) else []:
        product_id = item.get("product_id") if isinstance(item, dict) else None
        product = catalogue.get_product(product_id) if product_id else None
        if product is None:
            continue
        cards.append(
            ProductCard(
                product_id=product.product_id,
                name=product.name,
                price=product.price,
                image_url=product.image_url,
                url=f"/products/{product.product_id}",
                color=product.colors[0] if product.colors else "",
                sizes_in_stock=[i.size for i in product.inventory if i.quantity > 0],
            )
        )
        if len(cards) == MAX_CARDS:
            break
    return cards


def history_for_display(user_id: int) -> list[ChatHistoryMessage]:
    """The customer's latest messages, oldest first, with product cards, for the website to restore."""
    return [
        ChatHistoryMessage(
            role=row["role"],
            content=row["content"],
            products=_cards(row["products_json"]) if row["role"] == "assistant" else [],
            created_at=row["created_at"],
        )
        for row in _recent_rows(user_id, DISPLAY_MESSAGES)
    ]
