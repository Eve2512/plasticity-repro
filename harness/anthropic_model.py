"""Claude through the Anthropic Messages API, with client-side tools.

Earlier assistant turns are sent back exactly as the API returned them
(thinking blocks included): current models reject or ignore edited history.
Automatic prompt caching keeps the growing, append-only history cheap.
"""

import anthropic

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
}

OPENROUTER_BASE_URL = "https://openrouter.ai/api"  # the SDK appends /v1/messages


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
    ):
        """`base_url` + `auth_token` (sent as a Bearer token) point the SDK at another
        Messages-API endpoint such as OpenRouter's."""
        if model not in BILLING:
            raise ValueError(f"no price table for {model}; add one to BILLING")
        self.name = model
        self.effort = effort
        self.max_tokens = max_tokens
        if client is None and base_url:
            # api_key="" keeps any ANTHROPIC_API_KEY in the environment from being sent to a third party.
            client = anthropic.Anthropic(base_url=base_url, auth_token=auth_token, api_key="", max_retries=4)
        self.client = client or anthropic.Anthropic(max_retries=4)

    @property
    def billing(self) -> PriceTable:
        return BILLING[self.name]

    def step(self, system: str, messages: list[dict], tools: list[ToolSpec]) -> ModelTurn:
        try:
            response = self.client.messages.create(
                model=self.name,
                max_tokens=self.max_tokens,
                system=system,
                messages=to_api_messages(messages),
                tools=to_api_tools(tools),
                output_config={"effort": self.effort},
                cache_control={"type": "ephemeral"},
            )
        except anthropic.APIStatusError as exc:
            if exc.status_code == 402:  # out of credits or over the key's limit
                raise BudgetExceeded(f"provider refused for lack of credit (HTTP 402) on {self.name}") from exc
            raise
        u = response.usage
        self.last_usage_fields = set(u.model_dump()) if hasattr(u, "model_dump") else set(vars(u))
        read = getattr(u, "cache_read_input_tokens", 0) or 0
        write = getattr(u, "cache_creation_input_tokens", 0) or 0
        cost = getattr(u, "cost", None)  # OpenRouter may report the charged amount
        usage = Usage(
            u.input_tokens + read + write, u.output_tokens, read, write,
            reported_cost=float(cost) if isinstance(cost, (int, float)) else None,
        )

        if response.stop_reason == "refusal":
            # No tool calls: the episode ends as "no_action" and counts as a loss.
            return ModelTurn("[refusal]", (), usage, raw=response.content, stop_reason="refusal")
        text = "".join(b.text for b in response.content if b.type == "text")
        calls = tuple(
            ToolCall(b.id, b.name, dict(b.input)) for b in response.content if b.type == "tool_use"
        )
        return ModelTurn(text, calls, usage, raw=response.content, stop_reason=response.stop_reason)
