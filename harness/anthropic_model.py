"""Claude through the Anthropic Messages API, with client-side tools.

Earlier assistant turns are sent back exactly as the API returned them
(thinking blocks included): current models reject or ignore edited history.
Automatic prompt caching keeps the growing, append-only history cheap.

Current models always think (adaptive thinking) and are billed for it, but by
default the API returns the thinking blocks empty. `thinking_display="summarized"`
asks for a readable summary of that reasoning at no extra cost; it is kept on
the turn as `ModelTurn.thinking`. The raw chain of thought is never returned.
"""

import time
from dataclasses import dataclass, field

import anthropic

from harness.chat_model import CHAT_BILLING, ChatModel
from harness.ledger import BudgetExceeded
from harness.model import ModelTurn, ToolCall, ToolSpec, Usage
from plasticity.pricing import PriceTable

# Billed rates in USD per million tokens (cached 2026-10-06 model table).
# Cache writes use the 5-minute rate (1.25x input). The Haiku cache rates are
# not in that table; the long-prompt rates (x5) are used for them to stay on the
# safe side of the spending cap.
BILLING = {
    "claude-opus-5-5": PriceTable(4.0, 20.0, cached_input_per_mtok=0.20, cache_write_per_mtok=5.0),
    "claude-sonnet-5-5": PriceTable(2.0, 10.0, cached_input_per_mtok=0.20, cache_write_per_mtok=2.5),
    "claude-haiku-5-5": PriceTable(
        0.10, 0.50, cached_input_per_mtok=0.05, cache_write_per_mtok=0.625, long_context=(100_000, 0.50, 2.50)
    ),
    # OpenRouter ids and prices (openrouter.ai/api/v1/models, read 2026-10-21).
    "anthropic/claude-opus-5.5": PriceTable(4.0, 20.0, cached_input_per_mtok=0.20, cache_write_per_mtok=5.0),
    "anthropic/claude-sonnet-5.5": PriceTable(2.0, 10.0, cached_input_per_mtok=0.10, cache_write_per_mtok=2.5),
    "anthropic/claude-haiku-5.5": PriceTable(0.10, 0.50, cached_input_per_mtok=0.01, cache_write_per_mtok=0.125),
    **CHAT_BILLING,  # non-Claude models, served by harness/chat_model.py
}

OPENROUTER_BASE_URL = "https://openrouter.ai/api"  # the SDK appends /v1/messages

OUTAGE_WAITS = (30, 60, 120, 240, 300, 300, 300, 300, 300)  # seconds between extra attempts, ~32 min in total
RETRY_STATUS = {408, 409, 429, 500, 502, 503, 504, 529}  # transient provider errors


@dataclass(frozen=True)
class ModelSpec:
    """Picklable recipe for an AnthropicModel, so worker processes can build their own."""

    model: str
    key: str = field(repr=False)
    effort: str = "medium"
    provider: str = "openrouter"  # or "anthropic"
    thinking_display: str | None = None  # "summarized" to record thinking summaries

    def __call__(self) -> "AnthropicModel | ChatModel":
        if self.model in CHAT_BILLING:
            return ChatModel(self.model, self.key, effort=self.effort, thinking_display=self.thinking_display)
        if self.provider == "openrouter":
            return AnthropicModel(self.model, effort=self.effort, base_url=OPENROUTER_BASE_URL, auth_token=self.key,
                                  thinking_display=self.thinking_display)
        return AnthropicModel(self.model, effort=self.effort, thinking_display=self.thinking_display,
                              client=anthropic.Anthropic(api_key=self.key, max_retries=4))


def to_api_messages(messages: list[dict]) -> list[dict]:
    """Neutral messages to Messages API messages.

    Tool results and the user text that follows them (budget notes) are merged
    into one user message, tool results first, as the API expects.
    """
    out: list[dict] = []
    for m in messages:
        role = m["role"]
        if role == "assistant":
            if m.get("raw") is not None:
                content = m["raw"]
            else:
                content = [{"type": "text", "text": m["content"]}] if m["content"] else []
                content += [
                    {"type": "tool_use", "id": c.id, "name": c.name, "input": c.args} for c in m.get("tool_calls", [])
                ]
            out.append({"role": "assistant", "content": content})
            continue
        if role == "tool":
            block = {"type": "tool_result", "tool_use_id": m["tool_call_id"], "content": m["content"] or "(no output)"}
        else:
            block = {"type": "text", "text": m["content"]}
        if out and out[-1]["role"] == "user":
            out[-1]["content"].append(block)
        else:
            out.append({"role": "user", "content": [block]})
    return out


def to_api_tools(tools: list[ToolSpec]) -> list[dict]:
    return [{"name": t.name, "description": t.description, "input_schema": t.parameters} for t in tools]


class AnthropicModel:
    def __init__(
        self,
        model: str,
        effort: str = "medium",
        max_tokens: int = 16000,
        client=None,
        base_url: str | None = None,
        auth_token: str | None = None,
        thinking_display: str | None = None,
    ):
        """`base_url` + `auth_token` (sent as a Bearer token) point the SDK at another
        Messages-API endpoint such as OpenRouter's."""
        if model not in BILLING or model in CHAT_BILLING:
            raise ValueError(f"no Claude price table for {model}; add one to BILLING")
        self.name = model
        self.effort = effort
        self.max_tokens = max_tokens
        self.thinking_display = thinking_display
        if client is None and base_url:
            # api_key="" keeps any ANTHROPIC_API_KEY in the environment from being sent to a third party.
            client = anthropic.Anthropic(base_url=base_url, auth_token=auth_token, api_key="", max_retries=4)
        self.client = client or anthropic.Anthropic(max_retries=4)
        self.sleep = time.sleep  # replaced in tests

    @property
    def billing(self) -> PriceTable:
        return BILLING[self.name]

    def step(self, system: str, messages: list[dict], tools: list[ToolSpec]) -> ModelTurn:
        # The SDK already retries a few times within about a minute; these longer waits
        # ride out a lost connection (a train tunnel, a sleeping laptop) of up to ~30 minutes.
        # Without a display setting no `thinking` field is sent, as in the runs before 2026-10-28.
        extra = {"thinking": {"type": "adaptive", "display": self.thinking_display}} if self.thinking_display else {}
        for wait in (*OUTAGE_WAITS, None):
            try:
                response = self.client.messages.create(
                    model=self.name,
                    max_tokens=self.max_tokens,
                    system=system,
                    messages=to_api_messages(messages),
                    tools=to_api_tools(tools),
                    output_config={"effort": self.effort},
                    cache_control={"type": "ephemeral"},
                    **extra,
                )
                break
            except anthropic.APIConnectionError as exc:  # includes timeouts
                if wait is None:
                    raise
                problem = type(exc).__name__
            except anthropic.APIStatusError as exc:
                if exc.status_code == 402:  # out of credits or over the key's limit
                    raise BudgetExceeded(f"provider refused for lack of credit (HTTP 402) on {self.name}") from exc
                if exc.status_code not in RETRY_STATUS or wait is None:
                    raise
                problem = f"HTTP {exc.status_code}"
            print(f"[{self.name}] {problem}; retrying in {wait} s", flush=True)
            self.sleep(wait)
        u = response.usage
        self.last_usage_fields = set(u.model_dump()) if hasattr(u, "model_dump") else set(vars(u))
        read = getattr(u, "cache_read_input_tokens", 0) or 0
        write = getattr(u, "cache_creation_input_tokens", 0) or 0
        cost = getattr(u, "cost", None)  # OpenRouter may report the charged amount
        usage = Usage(
            u.input_tokens + read + write, u.output_tokens, read, write,
            reported_cost=float(cost) if isinstance(cost, (int, float)) else None,
        )

        thinking = "\n\n".join(b.thinking for b in response.content if b.type == "thinking" and b.thinking)
        if response.stop_reason == "refusal":
            # No tool calls: the episode ends as "no_action" and counts as a loss.
            return ModelTurn("[refusal]", (), usage, raw=response.content, stop_reason="refusal", thinking=thinking)
        text = "".join(b.text for b in response.content if b.type == "text")
        calls = tuple(
            ToolCall(b.id, b.name, dict(b.input)) for b in response.content if b.type == "tool_use"
        )
        return ModelTurn(text, calls, usage, raw=response.content, stop_reason=response.stop_reason, thinking=thinking)
