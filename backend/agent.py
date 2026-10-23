"""The Campus Customs shop assistant, built as a PydanticAI agent.

How it's put together:
- Instructions: prompts/prompt.md, re-read whenever the file changes, plus one
  line saying whether the shopper is logged in (and their first name).
- Model: OPENAI_MODEL (default gpt-5.6-luna), called through Portkey's
  OpenAI-compatible API with PORTKEY_API_KEY. Both come from hw4/.env.
- Tools: tools.py (read-only product search and stock lookups).
- Output: a ChatReply (models.py). The reply text, plus the product IDs to show as cards.
"""

from __future__ import annotations

import logging
import os
import time
import re
from types import SimpleNamespace
from functools import cache
from pathlib import Path

from openai import AsyncOpenAI
from pydantic_ai import Agent, ModelRetry, RunContext, capture_run_messages
from pydantic_ai.exceptions import ModelHTTPError, UnexpectedModelBehavior, UsageLimitExceeded
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.usage import UsageLimits

import audit
import catalogue
from models import ProductInfo, ChatDeps, ChatReply, ChatResponse, ChatTurn, Customer, PageContext, ProductCard, SearchResults
from tools import TOOLS, get_product_info

DEFAULT_MODEL = "gpt-5.6-luna"
DEFAULT_PORTKEY_BASE_URL = "https://api.portkey.ai/v1"
PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "prompt.md"
MAX_CARDS = 4
# Said when the AI provider's own safety filter blocks a message (for example, a jailbreak attempt).
BLOCKED_REPLY = (
    "Sorry, I can't help with that. I'm here to help you find Campus Customs gear. "
    "Want to see our hoodies, crewnecks, or tees?"
)
# The system prompt is the same long text on every call, so a stable cache key lets
# the provider reuse it (cached input tokens are billed at a fraction of the price).
MODEL_SETTINGS = OpenAIResponsesModelSettings(openai_prompt_cache_key="campus-customs-assistant")
# Caps on model calls and tool calls per reply, to bound cost and time.
USAGE_LIMITS = UsageLimits(request_limit=6, tool_calls_limit=8)


class ChatNotConfigured(RuntimeError):
    """PORTKEY_API_KEY is missing, so the assistant can't reach the AI model."""


def model_name() -> str:
    return os.getenv("OPENAI_MODEL", DEFAULT_MODEL)


@cache
def build_model() -> OpenAIResponsesModel:
    """The AI model connection, routed through Portkey (built once, on the first chat)."""
    api_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise ChatNotConfigured("Add PORTKEY_API_KEY to hw4/.env to turn on the shop assistant.")
    headers = {"x-portkey-api-key": api_key}
    if os.getenv("PORTKEY_FORCE_REFRESH") == "1":
        headers["x-portkey-cache-force-refresh"] = "true"  # skip Portkey's response cache (for benchmarks)
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=os.getenv("PORTKEY_BASE_URL", DEFAULT_PORTKEY_BASE_URL),
        default_headers=headers,
        timeout=60,
        max_retries=1,
    )
    return OpenAIResponsesModel(model_name(), provider=OpenAIProvider(openai_client=client))


_prompt_cache: tuple[float, str] | None = None


def load_prompt() -> str:
    """Reads prompts/prompt.md, re-reading only when the file changes, so prompt edits apply without a restart."""
    global _prompt_cache
    modified = PROMPT_PATH.stat().st_mtime
    if _prompt_cache is None or _prompt_cache[0] != modified:
        _prompt_cache = (modified, PROMPT_PATH.read_text(encoding="utf-8"))
    return _prompt_cache[1]


agent = Agent(
    output_type=ChatReply,
    deps_type=ChatDeps,
    tools=TOOLS,
    name="campus_customs_assistant",
    retries=2,
)


@agent.instructions
def instructions(ctx: RunContext[ChatDeps]) -> str:
    customer = ctx.deps.customer
    if customer:
        shopper = (
            f"The shopper is logged in as {customer.first_name}. Earlier messages are their saved history "
            "with you, possibly from a past visit. For their full name or email, call get_customer_profile."
        )
    else:
        shopper = "The shopper is a guest (not logged in), so you don't know their name and nothing is saved."
    if ctx.deps.page_product_name:
        page = (
            f"They are viewing the product page for {ctx.deps.page_product_name} "
            f"(product_id {ctx.deps.page.product_id}). Words like \"this\" or \"it\" mean this product "
            "unless they name another one."
        )
        if ctx.deps.page_product:
            # Saves a tool call for the most common product-page questions ("Do you have this in XL?").
            page += f"\n\nThis product's details, fresh from the database:\n{ctx.deps.page_product.model_dump_json()}"
    else:
        page = f"They are on the website page {ctx.deps.page.path!r}, not a product page."
    return f"{load_prompt()}\n\n## This conversation\n\n{shopper}\n\n{page}"


logger = logging.getLogger("campus_customs.fact_check")

PRICE = re.compile(r"\$\s?(\d+(?:\.\d{1,2})?)")
COUNT = re.compile(r"\b(\d+)\s+(?:left|available|in stock|remaining|on hand)\b|\bonly\s+(\d+)\b", re.IGNORECASE)
NUMBER = re.compile(r"\d+(?:\.\d+)?")


@agent.output_validator
def fact_check(ctx: RunContext[ChatDeps], output: ChatReply) -> ChatReply:
    """Blocks any price or stock count that no tool returned in this reply.

    Every "$" amount must be a price a tool returned (or a budget the shopper typed), and every
    "N left" or "N available" must be a count a tool returned. Otherwise the model is sent back to
    look it up or remove it, so a wrong number never reaches the shopper.
    """
    typed = {float(n) for n in NUMBER.findall(ctx.prompt if isinstance(ctx.prompt, str) else "")}
    prices = ctx.deps.known_prices | typed
    counts = ctx.deps.known_counts | {int(n) for n in typed if n == int(n)}
    wrong_prices = sorted({f"${p}" for p in PRICE.findall(output.reply) if float(p) not in prices})
    wrong_counts = sorted({int(a or b) for a, b in COUNT.findall(output.reply) if int(a or b) not in counts})
    if not (wrong_prices or wrong_counts):
        return output
    ctx.deps.fact_check_retries += 1
    problems = ", ".join([*wrong_prices, *(f"{n} in stock" for n in wrong_counts)])
    logger.warning("Fact-check caught %s; asking the model to fix it", problems)
    raise ModelRetry(
        f"Your reply mentions {problems}, which doesn't match any price or stock count your tools returned "
        "in this reply. Look it up with a tool, or remove it, then answer again."
    )


def to_message_history(turns: list[ChatTurn]) -> list[ModelMessage]:
    """Turns the earlier messages the website sends back into PydanticAI's message format."""
    history: list[ModelMessage] = []
    for turn in turns:
        if not turn.content.strip():
            continue
        if turn.role == "user":
            history.append(ModelRequest(parts=[UserPromptPart(content=turn.content)]))
        else:
            history.append(ModelResponse(parts=[TextPart(content=turn.content)]))
    # A conversation has to start with something the shopper said.
    while history and isinstance(history[0], ModelResponse):
        history.pop(0)
    return history


def product_cards(product_ids: list[str], seen: set[str]) -> list[ProductCard]:
    """Builds cards from the database, only for products the tools actually returned during this reply."""
    cards: list[ProductCard] = []
    for product_id in dict.fromkeys(product_ids):
        if product_id not in seen or len(cards) == MAX_CARDS:
            continue
        product = catalogue.get_product(product_id)
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
                sizes_in_stock=[item.size for item in product.inventory if item.quantity > 0],
            )
        )
    return cards


def blocked_by_content_filter(error: ModelHTTPError) -> bool:
    body = error.body if isinstance(error.body, dict) else {}
    return error.status_code == 400 and body.get("code") == "content_filter"


def make_deps(customer: Customer | None, page: PageContext | None) -> ChatDeps:
    """Everything one reply needs to know: who is chatting and which page they're on."""
    page = page or PageContext()
    page_product = catalogue.get_product(page.product_id) if page.product_id else None
    if page_product is None:
        page = PageContext(path=page.path)  # ignore product IDs that don't exist
    deps = ChatDeps(customer=customer, page=page, page_product_name=page_product.name if page_product else None)
    if page_product:
        info = get_product_info(SimpleNamespace(deps=deps), page_product.product_id)  # also marks it as seen
        deps.page_product = info if isinstance(info, ProductInfo) else None
    return deps


async def answer(
    message: str,
    history: list[ChatTurn],
    customer: Customer | None = None,
    page: PageContext | None = None,
) -> ChatResponse:
    """Runs the agent for one shopper message and returns the reply with any product cards.

    Every run, including failed ones, adds an entry to the audit trail (audit.py).
    """
    deps = make_deps(customer, page)
    started = time.perf_counter()
    entry: dict = {
        "timestamp": audit.now(),
        "shopper": f"customer #{customer.id}" if customer else "guest",
        "page": deps.page.path + (f" (product {deps.page.product_id})" if deps.page.product_id else ""),
        "message": audit.brief(message, 200),
        "earlier_messages": len(history),
        "model": model_name(),
    }
    result = None
    response: ChatResponse | None = None
    with capture_run_messages() as messages:
        try:
            result = await agent.run(
                message,
                deps=deps,
                message_history=to_message_history(history),
                model=build_model(),
                usage_limits=USAGE_LIMITS,
                model_settings=MODEL_SETTINGS,
            )
            output = result.output
            response = ChatResponse(
                reply=output.reply.strip(),
                products=product_cards(output.product_ids, deps.seen_product_ids),
                search=search_results(output, deps),
            )
            finish = getattr(result.response, "finish_reason", None)
            entry["stop_reason"] = "answered: the agent returned its final reply" + (f" (finish reason: {finish})" if finish else "")
        except ModelHTTPError as error:
            if not blocked_by_content_filter(error):
                entry["stop_reason"] = f"error: the AI provider returned HTTP {error.status_code}"
                raise
            response = ChatResponse(reply=BLOCKED_REPLY, products=[])
            entry["stop_reason"] = "blocked: the AI provider's safety filter refused the message; a polite decline was sent"
        except UsageLimitExceeded as error:
            entry["stop_reason"] = f"stopped: usage limit reached ({error})"
            raise
        except UnexpectedModelBehavior as error:
            entry["stop_reason"] = f"stopped: the model's answer kept failing checks ({audit.brief(error, 120)})"
            raise
        except ChatNotConfigured:
            entry["stop_reason"] = "not run: PORTKEY_API_KEY is missing"
            raise
        except Exception as error:
            entry["stop_reason"] = f"error: {type(error).__name__}"
            raise
        finally:
            entry["steps"] = audit.steps_from(messages)
            entry["fact_check_retries"] = deps.fact_check_retries
            if response is not None:
                entry["reply"] = audit.brief(response.reply, 200)
                entry["product_cards"] = [card.product_id for card in response.products]
                entry["search_on_page"] = (
                    f"{response.search.title} ({len(response.search.products)} products)" if response.search else None
                )
            if result is not None:
                usage = result.usage
                entry["usage"] = {
                    "model_calls": usage.requests,
                    "tool_calls": usage.tool_calls,
                    "input_tokens": usage.input_tokens,
                    "cached_input_tokens": usage.cache_read_tokens,
                    "output_tokens": usage.output_tokens,
                }
            entry["duration_ms"] = round((time.perf_counter() - started) * 1000)
            audit.record(entry)
    return response


def search_results(output: ChatReply, deps: ChatDeps) -> SearchResults | None:
    """The latest search's matches, built from the database, when the agent asked to show them on the page."""
    if not (output.show_search_on_page and deps.search_matches):
        return None
    by_id = {product.product_id: product for product in catalogue.list_products()}
    products = [by_id[pid] for pid in deps.search_matches if pid in by_id]
    return SearchResults(title=output.page_title.strip() or "Search results", products=products)
