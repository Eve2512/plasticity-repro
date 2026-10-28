"""Paid probe (about $0.02): does OpenRouter's Messages endpoint pass `thinking.display` through?

Three calls, each asking for a short reasoning step and then a bash tool call:
Sonnet 5.5 without a display setting (as in every run so far), Sonnet 5.5 and
Haiku 5.5 with display "summarized". A Sonnet follow-up sends the raw content
back, thinking blocks included, to check the history is accepted. Prints block
types, summary lengths and the first characters of each summary; never the key.

    uv run python scripts/probe_thinking.py
"""

import sys

from harness.anthropic_model import OPENROUTER_BASE_URL, AnthropicModel
from harness.keys import load_key
from harness.model import BASH

SYSTEM = "You test a tool interface. Be brief."
TASK = ("A 5x5 Go board has Black stones at B2 and C3. Think about which empty point next to both "
        "stones would connect them best, then run `echo <point>` with the bash tool.")


def call(key, model, display):
    m = AnthropicModel(model, effort="medium", max_tokens=4000, base_url=OPENROUTER_BASE_URL, auth_token=key,
                       thinking_display=display)
    messages = [{"role": "user", "content": TASK}]
    turn = m.step(SYSTEM, messages, [BASH])
    blocks = [b.type for b in turn.raw]
    print(f"{model}, display={display}: blocks {blocks}, summary {len(turn.thinking)} chars, "
          f"output tokens {turn.usage.output_tokens}, cost {turn.usage.reported_cost}")
    if turn.thinking:
        print("   summary starts:", repr(turn.thinking[:300]))
    return m, messages, turn


def main():
    key = load_key("OPENROUTER_API_KEY")
    if not key:
        print("no OPENROUTER_API_KEY in the environment or .env")
        return 1
    call(key, "anthropic/claude-sonnet-5.5", None)
    m, messages, turn = call(key, "anthropic/claude-sonnet-5.5", "summarized")
    call(key, "anthropic/claude-haiku-5.5", "summarized")
    if turn.tool_calls:
        messages.append({"role": "assistant", "content": turn.text, "tool_calls": list(turn.tool_calls),
                         "raw": turn.raw})
        messages.append({"role": "tool", "tool_call_id": turn.tool_calls[0].id, "content": "ok"})
        follow = m.step(SYSTEM, messages, [BASH])
        print(f"follow-up with thinking blocks sent back: {follow.stop_reason}, summary {len(follow.thinking)} chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
