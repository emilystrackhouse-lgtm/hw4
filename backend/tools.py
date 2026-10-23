"""Tools the shop assistant can call.

They only read. The product tools read the catalogue and stock; the customer
and page tools read what this request already knows (the logged-in customer's
own name and email, and the page they're on). No tool can see passwords or
other customers, and none can change anything.
"""

from __future__ import annotations

import re

from pydantic_ai import RunContext

import catalogue
from models import ChatDeps, CurrentPage, CustomerProfile, ProductInfo, ProductMatch, ProductSearch, Size, SizeCount, SizeStock, StyleName, StyleSummary

MAX_RESULTS = 8  # matches the model reads
MAX_PAGE_RESULTS = 48  # matches the website can show on the page
MAX_SOLD_OUT_MATCHES = 3  # word matches hidden by the size filter, reported so nothing is missed

# Shopper words mapped to the words the catalogue uses. A query word matches if
# any of its alternatives appears in a product's name, tags, colors, or description.
SYNONYMS: dict[str, list[str]] = {
    "grey": ["gray"],
    "tee": ["t-shirt"],
    "tees": ["t-shirt"],
    "tshirt": ["t-shirt"],
    "shirt": ["t-shirt", "shirt"],
    "hoody": ["hoodie"],
    "hoodies": ["hoodie"],
    "hooded": ["hoodie", "hood"],
    "sweatshirt": ["sweatshirt", "crewneck", "hoodie"],
    "crew": ["crewneck"],
    "crewnecks": ["crewneck"],
    "fleece": ["fleece"],
    "jacket": ["jacket", "fleece"],
    "mom": ["mom"],
    "mother": ["mom"],
    "dad": ["dad"],
    "father": ["dad"],
    "parent": ["mom", "dad"],
    "parents": ["mom", "dad"],
    "grandparent": ["grandma", "grandpa"],
    "grandparents": ["grandma", "grandpa"],
    "dan": ["bulldog"],  # Handsome Dan, Yale's bulldog mascot
    "bulldogs": ["bulldog"],
    "mascot": ["bulldog"],
    "vintage": ["vintage", "retro"],
    "harvard": ["harvard", "the game"],
}

PHRASES = {
    "handsome dan": "bulldog",
    "quarter zip": "quarter-zip",
    "1/4 zip": "quarter-zip",
    "t shirt": "t-shirt",
    "track and field": "track",
    "long sleeve": "long-sleeve",
}

# Words that don't help tell products apart.
STOP_WORDS = {
    "a", "an", "and", "any", "anything", "do", "does", "for", "have", "i", "in", "is", "it", "me",
    "my", "of", "on", "or", "show", "some", "something", "that", "the", "to", "what", "with",
    "you", "yale", "university", "college", "please", "got", "want", "looking", "need",
}

# Where a word is found, and how much that counts.
FIELD_WEIGHTS = {"name": 3, "tags": 2, "colors": 2, "type": 2, "description": 1}


def _query_terms(text: str) -> list[list[str]]:
    text = text.lower()
    for phrase, replacement in PHRASES.items():
        text = text.replace(phrase, replacement)
    words = re.findall(r"[a-z0-9][a-z0-9'/-]*", text)
    return [SYNONYMS.get(word, [word]) for word in words if word not in STOP_WORDS]


def _score(fields: dict[str, str], terms: list[list[str]]) -> int:
    total = 0
    for alternatives in terms:
        best = max(
            (weight for name, weight in FIELD_WEIGHTS.items() for alt in alternatives if alt in fields[name]),
            default=0,
        )
        total += best
    return total


def search_products(
    ctx: RunContext[ChatDeps],
    query: str = "",
    style: StyleName | None = None,
    max_price: float | None = None,
    size_in_stock: Size | None = None,
) -> ProductSearch:
    """Search the Campus Customs catalogue. Use this before naming any product, price, color, or size.

    Args:
        query: What the shopper is after, in plain words, such as "Saybrook crewneck", "yale dad",
            "bulldog", or "gray hoodie". Leave empty to browse by the other filters.
        style: Limit results to one style group.
        max_price: Only include products at or under this price in US dollars.
        size_in_stock: Only include products that have this size in stock right now.

    Returns:
        total_matches (how many products match in all) and top_matches (the best 8, each with its
        price, colors in the design, and sizes in stock). total_matches of 0 means nothing matches.
        Every match is kept so the website can show them all on the Products page.
    """
    products = catalogue.list_products()
    tags = catalogue.search_tags_by_product()
    in_stock = catalogue.sizes_in_stock_by_product()
    terms = _query_terms(query)

    scored: list[tuple[int, ProductMatch]] = []
    hidden_by_size: list[tuple[int, ProductMatch]] = []  # match the words, but not in that size
    for product in products:
        if style and product.garment_type not in catalogue.STYLES[style]:
            continue
        if max_price is not None and product.price > max_price:
            continue
        sizes = in_stock.get(product.product_id, [])
        score = 0
        if terms:
            fields = {
                "name": product.name.lower(),
                "tags": " ".join(tags.get(product.product_id, [])).lower(),
                "colors": " ".join(product.colors).lower(),
                "type": product.garment_type.lower(),
                "description": product.description.lower(),
            }
            score = _score(fields, terms)
            if score == 0:
                continue
        match = ProductMatch(
            product_id=product.product_id,
            name=product.name,
            garment_type=product.garment_type,
            price=product.price,
            colors_in_design=product.colors,
            sizes_in_stock=sizes,
            description=product.description,
        )
        if size_in_stock and size_in_stock not in sizes:
            if terms:
                hidden_by_size.append((score, match))
            continue
        scored.append((score, match))

    scored.sort(key=lambda item: (-item[0], item[1].name))
    hidden_by_size.sort(key=lambda item: (-item[0], item[1].name))
    sold_out = [match for _, match in hidden_by_size[:MAX_SOLD_OUT_MATCHES]]
    ctx.deps.seen_product_ids.update(match.product_id for match in sold_out)
    ctx.deps.known_prices.update(match.price for match in sold_out)
    results = [match for _, match in scored[:MAX_RESULTS]]
    ctx.deps.seen_product_ids.update(match.product_id for match in results)
    ctx.deps.search_matches = [match.product_id for _, match in scored[:MAX_PAGE_RESULTS]]
    ctx.deps.known_prices.update(match.price for match in results)
    return ProductSearch(total_matches=len(scored), top_matches=results, sold_out_in_requested_size=sold_out)


LOW_STOCK = 5


def _lookup(ctx: RunContext[ChatDeps], product_id: str):
    product = catalogue.get_product(product_id)
    if product is not None:
        ctx.deps.seen_product_ids.add(product.product_id)
    return product


def get_product_info(ctx: RunContext[ChatDeps], product_id: str) -> ProductInfo | str:
    """Look up one product's description, price, colors, and stock count for every size (XS to XXL).

    Use this before stating a product's price, describing it in detail, or saying which sizes are available.

    Args:
        product_id: The product_id from a search result, such as "yale-dad-hoodie".
    """
    product = _lookup(ctx, product_id)
    if product is None:
        return f"No product has the ID {product_id!r}. Search for it by name instead."
    counts = [SizeCount(size=item.size, quantity=item.quantity) for item in product.inventory]
    ctx.deps.known_prices.add(product.price)
    ctx.deps.known_counts.update(c.quantity for c in counts)
    ctx.deps.known_counts.add(sum(c.quantity for c in counts))
    return ProductInfo(
        product_id=product.product_id,
        name=product.name,
        garment_type=product.garment_type,
        price=product.price,
        description=product.description,
        colors_in_design=product.colors,
        stock_by_size=counts,
        sizes_in_stock=[c.size for c in counts if c.quantity > 0],
        sold_out_sizes=[c.size for c in counts if c.quantity == 0],
        total_in_stock=sum(c.quantity for c in counts),
    )


def check_size_stock(ctx: RunContext[ChatDeps], product_id: str, size: Size) -> SizeStock | str:
    """Check how many of one product are in stock in one size.

    Use this whenever a shopper asks about a specific size ("Do you have it in a medium?").

    Args:
        product_id: The product_id from a search result.
        size: The size to check: XS, S, M, L, XL, or XXL.
    """
    product = _lookup(ctx, product_id)
    if product is None:
        return f"No product has the ID {product_id!r}. Search for it by name instead."
    stock = {item.size: item.quantity for item in product.inventory}
    quantity = stock.get(size, 0)
    ctx.deps.known_prices.add(product.price)
    ctx.deps.known_counts.add(quantity)
    return SizeStock(
        product_id=product.product_id,
        name=product.name,
        price=product.price,
        size=size,
        quantity=quantity,
        in_stock=quantity > 0,
        low_stock=0 < quantity <= LOW_STOCK,
        other_sizes_in_stock=[s for s, q in stock.items() if q > 0 and s != size],
    )


def list_styles(ctx: RunContext[ChatDeps]) -> list[StyleSummary]:
    """Summarize what the shop carries: each style group with its number of products and price range."""
    products = catalogue.list_products()
    summaries = []
    for style, garment_types in catalogue.STYLES.items():
        prices = [p.price for p in products if p.garment_type in garment_types]
        if prices:
            ctx.deps.known_prices.update({min(prices), max(prices)})
            summaries.append(
                StyleSummary(style=style, product_count=len(prices), lowest_price=min(prices), highest_price=max(prices))
            )
    return summaries


def get_customer_profile(ctx: RunContext[ChatDeps]) -> CustomerProfile:
    """Get the logged-in customer's own name and email. Use this when they ask about their account,
    such as "What email am I signed in with?". Guests aren't logged in, so there's nothing to return."""
    customer = ctx.deps.customer
    if customer is None:
        return CustomerProfile(logged_in=False)
    return CustomerProfile(
        logged_in=True, first_name=customer.first_name, last_name=customer.last_name, email=customer.email
    )


PAGE_NAMES = {
    "/": "Home",
    "/products": "Products",
    "/about": "About Us",
    "/login": "Log in",
    "/create-account": "Create account",
    "/account": "My account",
}


def get_current_page(ctx: RunContext[ChatDeps]) -> CurrentPage:
    """Get the page the shopper is looking at right now. On a product page, this includes that product's
    full info (price, description, colors, and stock by size). Use it when they say "this", "it", or
    "this one" without naming a product."""
    page = ctx.deps.page
    product = get_product_info(ctx, page.product_id) if page.product_id else None
    if isinstance(product, ProductInfo):
        return CurrentPage(path=page.path, page_name=f"Product page: {product.name}", product=product)
    return CurrentPage(path=page.path, page_name=PAGE_NAMES.get(page.path, "Another page"))


TOOLS = [search_products, get_product_info, check_size_stock, list_styles, get_customer_profile, get_current_page]
