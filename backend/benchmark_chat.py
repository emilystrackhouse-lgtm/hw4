"""Measures the shop assistant's speed and AI usage on a fixed set of shopper questions.

Run from backend/ (makes real AI calls; reads the database but never writes to it):
    .venv/bin/python benchmark_chat.py [label]
"""

from __future__ import annotations

import asyncio
import statistics
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")  # hw4/.env

import agent as shop_agent  # noqa: E402
from models import PageContext  # noqa: E402

QUESTIONS = [
    ("What hoodies do you have?", "/"),
    ("Is the Football Left Chest T-Shirt available in medium?", "/"),
    ("How much is the Saybrook Sweater Fleece Jacket?", "/"),
    ("Do you have this in XL?", "/products/yale-mom-hoodie"),
    ("Gift ideas for a Yale parent under $60?", "/"),
]


async def main(label: str) -> None:
    times, model_calls, input_tokens, output_tokens, cached = [], [], [], [], []
    for question, path in QUESTIONS:
        product_id = path.removeprefix("/products/") if path.startswith("/products/") else None
        deps = shop_agent.make_deps(None, PageContext(path=path, product_id=product_id))
        start = time.perf_counter()
        result = await shop_agent.agent.run(
            question,
            deps=deps,
            model=shop_agent.build_model(),
            model_settings=getattr(shop_agent, "MODEL_SETTINGS", None),
            usage_limits=shop_agent.USAGE_LIMITS,
        )
        seconds = time.perf_counter() - start
        usage = result.usage
        times.append(seconds)
        model_calls.append(usage.requests)
        input_tokens.append(usage.input_tokens)
        output_tokens.append(usage.output_tokens)
        cached.append(usage.cache_read_tokens)
        print(f"{seconds:5.1f}s  calls={usage.requests}  in={usage.input_tokens:6}  out={usage.output_tokens:5}  {question}")
    print(
        f"\n{label}: average {statistics.mean(times):.1f}s per reply, "
        f"{statistics.mean(model_calls):.1f} model calls, "
        f"{statistics.mean(input_tokens):,.0f} input tokens ({statistics.mean(cached):,.0f} cached), "
        f"{statistics.mean(output_tokens):,.0f} output tokens"
    )


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "run"))
