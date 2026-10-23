"""Tests for the append-only audit trail (audit.py). Uses the test log, never output/audit_trail.json."""

import json

from pydantic_ai.messages import ModelResponse, ToolCallPart, ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

import agent as shop_agent
import audit


def entries(audit_log):
    return json.loads(audit_log.read_text()) if audit_log.exists() else []


def stock_then_answer(reply: str) -> FunctionModel:
    def respond(messages, info: AgentInfo) -> ModelResponse:
        checked = any(isinstance(p, ToolReturnPart) for m in messages for p in m.parts)
        if not checked:
            return ModelResponse(parts=[ToolCallPart("check_size_stock", {"product_id": "football-left-chest-t-shirt", "size": "M"})])
        output = {"reply": reply, "product_ids": ["football-left-chest-t-shirt"]}
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, output)])

    return FunctionModel(respond)


def test_each_reply_appends_one_entry_and_keeps_the_old_ones(client, audit_log):
    before = entries(audit_log)
    with shop_agent.agent.override(model=stock_then_answer("Sold out in medium. It's $32.")):
        client.post("/api/chat", json={"message": "Football tee in medium?", "page": {"path": "/products", "product_id": None}})
        client.post("/api/chat", json={"message": "And again?"})

    after = entries(audit_log)
    assert after[: len(before)] == before  # earlier entries untouched
    assert len(after) == len(before) + 2
    entry = after[-2]
    assert entry["shopper"] == "guest"
    assert entry["page"] == "/products"
    assert entry["message"] == "Football tee in medium?"
    assert entry["stop_reason"].startswith("answered")
    assert entry["reply"] == "Sold out in medium. It's $32."
    assert entry["product_cards"] == ["football-left-chest-t-shirt"]
    assert entry["usage"]["model_calls"] == 2
    [step] = entry["steps"]
    assert step["tool"] == "check_size_stock"
    assert step["input"] == "product_id='football-left-chest-t-shirt', size='M'"
    assert step["result"] == "Football Left Chest T-Shirt size M: sold out, $32"
    assert entry["timestamp"].endswith("Z") and step["at"]


def test_fact_check_retries_and_failures_are_recorded(client, audit_log):
    def always_wrong(messages, info: AgentInfo) -> ModelResponse:
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, {"reply": "It's $999.", "product_ids": []})])

    with shop_agent.agent.override(model=FunctionModel(always_wrong)):
        response = client.post("/api/chat", json={"message": "How much is it?"})
    assert response.status_code == 502
    entry = entries(audit_log)[-1]
    assert entry["stop_reason"].startswith("stopped: the model's answer kept failing checks")
    assert entry["fact_check_retries"] >= 2
    assert [s["type"] for s in entry["steps"]].count("retry") >= 2
    assert "$999" in entry["steps"][0]["result"]


def test_personal_details_are_masked(client, audit_log):
    with shop_agent.agent.override(model=stock_then_answer("Got it.")):
        client.post("/api/chat", json={"message": "I'm ada@example.com, card 4242 4242 4242 4242"})
    message = entries(audit_log)[-1]["message"]
    assert "ada@example.com" not in message and "4242 4242" not in message
    assert "[email removed]" in message and "[number removed]" in message


def test_a_damaged_log_is_set_aside_not_overwritten(tmp_path, monkeypatch):
    log = tmp_path / "audit_trail.json"
    log.write_text("{ not json")
    monkeypatch.setattr(audit, "AUDIT_PATH", log)
    audit.record({"timestamp": "now", "stop_reason": "answered"})
    assert json.loads(log.read_text()) == [{"timestamp": "now", "stop_reason": "answered"}]
    [damaged] = list(tmp_path.glob("audit_trail.damaged-*.json"))
    assert damaged.read_text() == "{ not json"
