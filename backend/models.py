"""Pydantic types shared by the API, the chatbot agent, and its tools."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

Size = Literal["XS", "S", "M", "L", "XL", "XXL"]
StyleName = Literal["T-Shirts", "Long Sleeves", "Crewnecks", "Hoodies", "Quarter-Zips", "Fleece & Outerwear"]

# --- Products (product pages and chatbot tools) ---------------------------------------


class InventoryItem(BaseModel):
    size: str
    quantity: int


class Product(BaseModel):
    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    price: float
    image_url: str
    total_stock: int
    sizes_in_stock: list[str] = Field(default_factory=list)


class ProductDetail(Product):
    search_tags: list[str]
    inventory: list[InventoryItem]


# --- What the chatbot's tools return --------------------------------------------------


class ProductMatch(BaseModel):
    """One search result, with just enough for the assistant to describe and recommend it."""

    product_id: str
    name: str
    garment_type: str
    price: float
    colors_in_design: list[str] = Field(description="Colors visible in the design. Not a choice of colorways.")
    sizes_in_stock: list[str]
    description: str


class ProductSearch(BaseModel):
    """The result of one catalog search."""

    total_matches: int = Field(description="How many products match in all. The website can show all of them.")
    top_matches: list[ProductMatch] = Field(description="The best matches (up to 8), for you to describe.")
    sold_out_in_requested_size: list[ProductMatch] = Field(
        default_factory=list,
        description=(
            "Products that match the words but are sold out in the size_in_stock you asked for (up to 3). "
            "If the shopper named one of these, tell them it's sold out in that size and offer its sizes_in_stock."
        ),
    )


class SizeCount(BaseModel):
    size: str
    quantity: int = Field(description="Units on hand right now. 0 means sold out in this size.")


class ProductInfo(BaseModel):
    """Everything the assistant needs to describe and price one product, straight from the database."""

    product_id: str
    name: str
    garment_type: str
    price: float = Field(description="Retail price in US dollars, from the catalogue.")
    description: str
    colors_in_design: list[str] = Field(description="Colors visible in the design. Not a choice of colorways.")
    stock_by_size: list[SizeCount] = Field(description="Every size XS to XXL with its current count, including 0s.")
    sizes_in_stock: list[str]
    sold_out_sizes: list[str]
    total_in_stock: int


class SizeStock(BaseModel):
    """The answer to "do you have this in my size?" for one product and one size."""

    product_id: str
    name: str
    price: float
    size: str
    quantity: int = Field(description="Units of this size on hand right now.")
    in_stock: bool
    low_stock: bool = Field(description="True when 1 to 5 are left, worth mentioning to the shopper.")
    other_sizes_in_stock: list[str] = Field(description="Sizes of this product that are available instead.")


class StyleSummary(BaseModel):
    style: StyleName
    product_count: int
    lowest_price: float
    highest_price: float


# --- Chat API (website <-> FastAPI) ---------------------------------------------------

MessageText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]


class ChatTurn(BaseModel):
    """One earlier message in the conversation, sent back by the website for context."""

    role: Literal["user", "assistant"]
    content: Annotated[str, StringConstraints(max_length=4000)]


class PageContext(BaseModel):
    """Where the shopper is on the website when they send a message."""

    path: Annotated[str, StringConstraints(max_length=200)] = "/"
    # Set on a product page (/products/{product_id}), so "this" can refer to that product.
    product_id: Annotated[str, StringConstraints(max_length=120)] | None = None


class ChatRequest(BaseModel):
    message: MessageText
    # Used for guests only. Logged-in customers' history is loaded from the database instead.
    history: list[ChatTurn] = Field(default_factory=list, max_length=20)
    page: PageContext = Field(default_factory=PageContext)


class ProductCard(BaseModel):
    """A product the website shows under the assistant's reply. Built from the database, never by the AI."""

    product_id: str
    name: str
    price: float
    image_url: str
    url: str
    color: str
    sizes_in_stock: list[str]


class SearchResults(BaseModel):
    """Products from the assistant's catalog search, for the website to show on the Products page."""

    title: str = Field(description="A short heading for the results, such as 'Hoodies'.")
    products: list[Product] = Field(description="Every match from the search, best first, straight from the database.")


class ChatHistoryMessage(BaseModel):
    """One saved message, as the website shows it when a customer returns."""

    role: Literal["user", "assistant"]
    content: str
    products: list[ProductCard]
    created_at: str


class ChatResponse(BaseModel):
    reply: str
    products: list[ProductCard]
    # Set when the shopper asked to browse a category; the website shows these on the Products page.
    search: SearchResults | None = None


# --- The agent's structured output ----------------------------------------------------


class ChatReply(BaseModel):
    """The assistant's answer to the shopper."""

    reply: str = Field(
        description=(
            "What to say to the shopper: friendly, plain text (no markdown symbols), usually under 120 words. "
            "Put each listed product on its own line starting with '• '."
        )
    )
    product_ids: list[str] = Field(
        default_factory=list,
        max_length=4,
        description=(
            "IDs of up to 4 products you recommend or mention, in the order you mention them, so the website "
            "can show them as cards. Only use product_id values returned by your tools. Leave empty if none."
        ),
    )
    show_search_on_page: bool = Field(
        default=False,
        description=(
            "True when the shopper wants to browse or see options for a category or kind of product (for example "
            "'What hoodies do you have?' or 'show me Saybrook gear') and you called search_products for it. The "
            "website then shows every match from your latest search_products call on the Products page."
        ),
    )
    page_title: str = Field(
        default="",
        max_length=60,
        description="When show_search_on_page is true, a short heading for those results, such as 'Hoodies'.",
    )


# --- What every tool call can see ------------------------------------------------------


class Customer(BaseModel):
    """The logged-in customer, taken from their session cookie (never from what they type)."""

    id: int
    first_name: str
    last_name: str
    email: str


class CustomerProfile(BaseModel):
    """What the get_customer_profile tool tells the assistant."""

    logged_in: bool
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None


class CurrentPage(BaseModel):
    """What the get_current_page tool tells the assistant about the page the shopper is viewing."""

    path: str
    page_name: str
    product: ProductInfo | None = Field(
        default=None, description="The product shown on this page, when the shopper is on a product page."
    )


@dataclass
class ChatDeps:
    customer: Customer | None = None  # None for guests
    page: PageContext = field(default_factory=PageContext)
    page_product_name: str | None = None  # set when page.product_id is a real product
    page_product: ProductInfo | None = None  # that product's details, put in the instructions
    # Products the tools returned during this reply; only these can become product cards.
    seen_product_ids: set[str] = field(default_factory=set)
    # Every match from the latest search_products call (best first), for showing on the page.
    search_matches: list[str] = field(default_factory=list)
    # Every price and stock count a tool returned in this reply, so the fact-check can verify the reply.
    known_prices: set[float] = field(default_factory=set)
    known_counts: set[int] = field(default_factory=set)
    fact_check_retries: int = 0
