"""Claude through the Anthropic Messages API, with client-side tools.

Earlier assistant turns are sent back exactly as the API returned them
(thinking blocks included): current models reject or ignore edited history.
Automatic prompt caching keeps the growing, append-only history cheap.
"""

import anthropic

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
}


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
    def __init__(self, model: str, effort: str = "medium", max_tokens: int = 16000, client=None):
        if model not in BILLING:
            raise ValueError(f"no price table for {model}; add one to BILLING")
        self.name = model
        self.effort = effort
        self.max_tokens = max_tokens
        self.client = client or anthropic.Anthropic(max_retries=4)

    @property
    def billing(self) -> PriceTable:
        return BILLING[self.name]

    def step(self, system: str, messages: list[dict], tools: list[ToolSpec]) -> ModelTurn:
        response = self.client.messages.create(
            model=self.name,
            max_tokens=self.max_tokens,
            system=system,
            messages=to_api_messages(messages),
            tools=to_api_tools(tools),
            output_config={"effort": self.effort},
            cache_control={"type": "ephemeral"},
        )
        u = response.usage
        read = getattr(u, "cache_read_input_tokens", 0) or 0
        write = getattr(u, "cache_creation_input_tokens", 0) or 0
        usage = Usage(u.input_tokens + read + write, u.output_tokens, read, write)

        if response.stop_reason == "refusal":
            # No tool calls: the episode ends as "no_action" and counts as a loss.
            return ModelTurn("[refusal]", (), usage, raw=response.content, stop_reason="refusal")
        text = "".join(b.text for b in response.content if b.type == "text")
        calls = tuple(
            ToolCall(b.id, b.name, dict(b.input)) for b in response.content if b.type == "tool_use"
        )
        return ModelTurn(text, calls, usage, raw=response.content, stop_reason=response.stop_reason)
