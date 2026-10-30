"""Non-Claude models through OpenRouter's chat-completions API, with client-side tools.

Muse Spark and GLM are not served on OpenRouter's Anthropic-style Messages endpoint,
so they get this adapter. The differences from harness/anthropic_model.py:

- Effort goes in `reasoning.effort`; "xhigh" and "max" are sent as "high", the
  highest level these models accept.
- Earlier assistant turns are sent back with their `reasoning_details`, which
  OpenRouter asks for so the model keeps its reasoning across tool calls.
- Caching is the provider's own (no cache_control field); cached prompt tokens and
  the charged cost come back in `usage`.
- `thinking` is whatever text the provider returns as reasoning. For these models
  that may be the full reasoning, not a summary like Claude's.
"""

import json
import time

import httpx2

from harness.ledger import BudgetExceeded
from harness.model import ModelTurn, ToolCall, ToolSpec, Usage
from plasticity.pricing import PriceTable

# OpenRouter ids and prices (openrouter.ai/api/v1/models, read 2026-10-30). No cache-write price
# is listed, so cache writes are billed as input.
CHAT_BILLING = {
    "meta/muse-spark-1.3": PriceTable(1.25, 4.25, cached_input_per_mtok=0.15),
    "z-ai/glm-5.3": PriceTable(0.08, 3.60, cached_input_per_mtok=0.076),
}

CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
EFFORT = {"low": "low", "medium": "medium", "high": "high", "xhigh": "high", "max": "high"}
STOP = {"tool_calls": "tool_use", "stop": "end_turn", "length": "max_tokens", "content_filter": "refusal"}

OUTAGE_WAITS = (30, 60, 120, 240, 300, 300, 300, 300, 300)  # as in anthropic_model.py, ~32 min in total
RETRY_STATUS = {408, 409, 429, 500, 502, 503, 504, 529}


class ProviderError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status


def to_chat_messages(system: str, messages: list[dict]) -> list[dict]:
    """Neutral messages to chat-completions messages."""
    out = [{"role": "system", "content": system}]
    for m in messages:
        if m["role"] == "assistant":
            raw = m.get("raw") or {}
            msg = {"role": "assistant", "content": m["content"] or None}
            if m.get("tool_calls"):
                msg["tool_calls"] = [
                    {"id": c.id, "type": "function", "function": {"name": c.name, "arguments": json.dumps(c.args)}}
                    for c in m["tool_calls"]
                ]
            if raw.get("reasoning_details"):
                msg["reasoning_details"] = raw["reasoning_details"]
            out.append(msg)
        elif m["role"] == "tool":
            out.append({"role": "tool", "tool_call_id": m["tool_call_id"], "content": m["content"] or "(no output)"})
        else:
            out.append({"role": "user", "content": m["content"]})
    return out


def to_chat_tools(tools: list[ToolSpec]) -> list[dict]:
    return [{"type": "function", "function": {"name": t.name, "description": t.description,
                                              "parameters": t.parameters}} for t in tools]


def parse_arguments(text: str | None) -> dict:
    """Tool arguments as a dict; malformed JSON gives {} (the tool then runs with empty input)."""
    try:
        args = json.loads(text or "{}")
    except json.JSONDecodeError:
        return {}
    return args if isinstance(args, dict) else {}


class ChatModel:
    def __init__(self, model: str, key: str, effort: str = "medium", max_tokens: int = 16000,
                 thinking_display: str | None = None, post=None):
        if model not in CHAT_BILLING:
            raise ValueError(f"no price table for {model}; add one to CHAT_BILLING")
        self.name = model
        self.effort = effort
        self.max_tokens = max_tokens
        self.thinking_display = thinking_display
        self.key = key
        self.post = post or self._post  # replaced in tests
        self.sleep = time.sleep
        self.calls = 0

    @property
    def billing(self) -> PriceTable:
        return CHAT_BILLING[self.name]

    def _post(self, body: dict) -> dict:
        response = httpx2.post(CHAT_URL, json=body, headers={"Authorization": f"Bearer {self.key}"},
                               timeout=httpx2.Timeout(600, connect=30))
        data = response.json() if response.content else {}
        if response.status_code != 200:
            raise ProviderError(response.status_code, str(data.get("error", data))[:300])
        if "error" in data:  # OpenRouter can answer 200 with an upstream error in the body
            err, code = data["error"], data["error"].get("code")
            raise ProviderError(code if isinstance(code, int) else 502, str(err.get("message"))[:300])
        if not data.get("choices"):
            raise ProviderError(502, "no choices in the response")
        return data

    def step(self, system: str, messages: list[dict], tools: list[ToolSpec]) -> ModelTurn:
        body = {
            "model": self.name,
            "messages": to_chat_messages(system, messages),
            "tools": to_chat_tools(tools),
            "max_tokens": self.max_tokens,
            "reasoning": {"effort": EFFORT[self.effort], "exclude": self.thinking_display is None},
            "usage": {"include": True},
        }
        for wait in (*OUTAGE_WAITS, None):
            try:
                data = self.post(body)
                break
            except httpx2.TransportError as exc:  # includes timeouts
                if wait is None:
                    raise
                problem = type(exc).__name__
            except ProviderError as exc:
                if exc.status == 402:  # out of credits or over the key's limit
                    raise BudgetExceeded(f"provider refused for lack of credit (HTTP 402) on {self.name}") from exc
                if exc.status not in RETRY_STATUS or wait is None:
                    raise
                problem = str(exc)
            print(f"[{self.name}] {problem}; retrying in {wait} s", flush=True)
            self.sleep(wait)
        self.calls += 1

        u = data.get("usage") or {}
        details = u.get("prompt_tokens_details") or {}
        cost = u.get("cost")
        usage = Usage(
            u.get("prompt_tokens", 0), u.get("completion_tokens", 0),
            details.get("cached_tokens") or 0, details.get("cache_write_tokens") or 0,
            reported_cost=float(cost) if isinstance(cost, (int, float)) else None,
        )
        choice = data["choices"][0]
        msg = choice.get("message") or {}
        thinking = msg.get("reasoning") or ""
        stop = STOP.get(choice.get("finish_reason"), choice.get("finish_reason"))
        raw = {"reasoning_details": msg.get("reasoning_details")}
        if stop == "refusal":
            # No tool calls: the episode ends as "no_action" and counts as a loss.
            return ModelTurn("[refusal]", (), usage, raw=raw, stop_reason=stop, thinking=thinking)
        calls = tuple(
            ToolCall(c.get("id") or f"call_{self.calls}_{i}", c["function"]["name"],
                     parse_arguments(c["function"].get("arguments")))
            for i, c in enumerate(msg.get("tool_calls") or [])
        )
        return ModelTurn(msg.get("content") or "", calls, usage, raw=raw, stop_reason=stop, thinking=thinking)
