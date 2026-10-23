"""Append-only audit trail of everything the shop assistant does.

Every chat reply adds one entry to output/audit_trail.json (a JSON array):
- when it ran and who asked (account number or "guest")
- each tool the agent called, with brief summaries of the input and result
- any fact-check retries
- the reply, the product cards, and any search shown on the page
- why the agent stopped
- how many model calls and tokens it used

Entries are never edited or removed: each write reads the existing array, adds
one entry, and atomically replaces the file, under a lock. Emails and long
digit runs (such as card numbers) are masked, and texts are shortened, so the
log never holds passwords, full messages, or contact details.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage, ModelResponse, RetryPromptPart, ToolCallPart, ToolReturnPart

from models import CurrentPage, CustomerProfile, ProductInfo, ProductSearch, SizeStock, StyleSummary

AUDIT_PATH = Path(
    os.getenv("CAMPUS_CUSTOMS_AUDIT_LOG", Path(__file__).resolve().parent.parent / "output" / "audit_trail.json")
)
OUTPUT_TOOL = "final_result"  # PydanticAI's name for the tool that returns the structured reply
SUMMARY_LENGTH = 160

_lock = threading.Lock()
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
LONG_NUMBER = re.compile(r"\b(?:\d[ -]?){12,}\b")


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def mask(text: str) -> str:
    return LONG_NUMBER.sub("[number removed]", EMAIL.sub("[email removed]", text))


def brief(value: Any, limit: int = SUMMARY_LENGTH) -> str:
    text = mask(" ".join(str(value).split()))
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _summarize_input(args: Any) -> str:
    if isinstance(args, str):
        try:
            args = json.loads(args) if args else {}
        except json.JSONDecodeError:
            return brief(args)
    if isinstance(args, dict):
        return brief(", ".join(f"{key}={value!r}" for key, value in args.items() if value not in (None, "")) or "(none)")
    return brief(args)


def _summarize_result(content: Any) -> str:
    """A short, human-readable result, without personal details."""
    if isinstance(content, ProductSearch):
        top = ", ".join(f"{m.name} ${m.price:g}" for m in content.top_matches[:3])
        hidden = ", ".join(m.name for m in content.sold_out_in_requested_size)
        text = f"{content.total_matches} matches" + (f"; top: {top}" if top else "")
        return brief(text + (f"; sold out in that size: {hidden}" if hidden else ""), 240)
    if isinstance(content, ProductInfo):
        sold_out = ", ".join(content.sold_out_sizes) or "none"
        return brief(f"{content.name}, ${content.price:g}; in stock: {', '.join(content.sizes_in_stock)}; sold out: {sold_out}")
    if isinstance(content, SizeStock):
        status = "sold out" if not content.in_stock else f"{content.quantity} in stock"
        return brief(f"{content.name} size {content.size}: {status}, ${content.price:g}")
    if isinstance(content, CustomerProfile):
        return "customer is logged in (name and email returned to the agent, not logged here)" if content.logged_in else "guest"
    if isinstance(content, CurrentPage):
        return brief(content.page_name)
    if isinstance(content, list) and content and isinstance(content[0], StyleSummary):
        return brief(f"{len(content)} styles: " + ", ".join(f"{s.style} ({s.product_count})" for s in content))
    if isinstance(content, BaseModel):
        return brief(content.model_dump_json())
    return brief(content)


def steps_from(messages: list[ModelMessage]) -> list[dict]:
    """Tool calls (with their results) and fact-check retries, in the order they happened."""
    steps: list[dict] = []
    calls: dict[str, dict] = {}
    for message in messages:
        for part in message.parts:
            if isinstance(part, ToolCallPart) and part.tool_name != OUTPUT_TOOL:
                step = {
                    "step": len(steps) + 1,
                    "type": "tool_call",
                    "tool": part.tool_name,
                    "input": _summarize_input(part.args),
                    "result": None,
                    "at": message.timestamp.isoformat(timespec="milliseconds") if isinstance(message, ModelResponse) else now(),
                }
                calls[part.tool_call_id] = step
                steps.append(step)
            elif isinstance(part, ToolReturnPart) and getattr(part, "outcome", None) == "retried":
                # PydanticAI 2.60+ reports a rejected answer or bad tool call as a "retried" tool return.
                if part.tool_call_id in calls:
                    calls[part.tool_call_id]["result"] = "retry requested: " + brief(part.content, 200)
                else:
                    steps.append(
                        {
                            "step": len(steps) + 1,
                            "type": "retry",
                            "tool": part.tool_name or OUTPUT_TOOL,
                            "input": None,
                            "result": brief(part.content, 220),
                            "at": part.timestamp.isoformat(timespec="milliseconds"),
                        }
                    )
            elif isinstance(part, ToolReturnPart) and part.tool_call_id in calls:
                calls[part.tool_call_id]["result"] = _summarize_result(part.content)
            elif isinstance(part, RetryPromptPart):  # how PydanticAI 2.57 and earlier report retries
                detail = part.content if isinstance(part.content, str) else json.dumps(part.content, default=str)
                steps.append(
                    {
                        "step": len(steps) + 1,
                        "type": "retry",
                        "tool": part.tool_name or OUTPUT_TOOL,
                        "input": None,
                        "result": brief(detail, 220),
                        "at": part.timestamp.isoformat(timespec="milliseconds"),
                    }
                )
    return steps


def record(entry: dict) -> None:
    """Appends one entry, keeping every earlier entry exactly as it was."""
    with _lock:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        entries: list = []
        if AUDIT_PATH.exists():
            try:
                loaded = json.loads(AUDIT_PATH.read_text(encoding="utf-8") or "[]")
                entries = loaded if isinstance(loaded, list) else [loaded]
            except json.JSONDecodeError:
                # Never overwrite a damaged log: set it aside, then start a fresh one.
                AUDIT_PATH.rename(AUDIT_PATH.with_name(f"{AUDIT_PATH.stem}.damaged-{datetime.now(UTC):%Y%m%dT%H%M%S}.json"))
        entries.append(entry)
        handle, temp = tempfile.mkstemp(dir=AUDIT_PATH.parent, prefix=".audit-", suffix=".json")
        with os.fdopen(handle, "w", encoding="utf-8") as file:
            json.dump(entries, file, indent=2, ensure_ascii=False)
            file.write("\n")
        os.replace(temp, AUDIT_PATH)
