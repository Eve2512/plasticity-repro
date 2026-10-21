"""One tiny paid call (well under $0.01) to check the OpenRouter Messages endpoint.

Checks: the endpoint answers, a tool call comes back as tool_use, a follow-up
with the raw assistant content is accepted, and which usage fields are reported.
Prints field names and numbers only, never the key.

    uv run python scripts/probe_openrouter.py
"""

import sys

from harness.anthropic_model import OPENROUTER_BASE_URL, AnthropicModel
from harness.keys import load_key
from harness.model import BASH


def main():
    key = load_key("OPENROUTER_API_KEY")
    if not key:
        print("no OPENROUTER_API_KEY in the environment or .env")
        return 1
    model = AnthropicModel("anthropic/claude-sonnet-5.5", effort="low", max_tokens=2000,
                           base_url=OPENROUTER_BASE_URL, auth_token=key)
    messages = [{"role": "user", "content": "Run the shell command `echo probe` with the bash tool, then stop."}]
    first = model.step("You test a tool interface. Be brief.", messages, [BASH])
    print("call 1:", first.stop_reason, [c.name for c in first.tool_calls], first.usage)
    if not first.tool_calls:
        print("no tool call returned")
        return 1
    messages.append({"role": "assistant", "content": first.text, "tool_calls": list(first.tool_calls), "raw": first.raw})
    messages.append({"role": "tool", "tool_call_id": first.tool_calls[0].id, "content": "probe"})
    second = model.step("You test a tool interface. Be brief.", messages, [BASH])
    print("call 2:", second.stop_reason, repr(second.text[:80]), second.usage)
    print("raw usage fields:", sorted(model.last_usage_fields))
    return 0


if __name__ == "__main__":
    sys.exit(main())
