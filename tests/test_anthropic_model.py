"""Adapter tests with a fake client: no API calls."""

from types import SimpleNamespace as NS

import pytest

from harness.anthropic_model import AnthropicModel, to_api_messages
from harness.model import BASH, ToolCall


def test_tool_results_and_budget_note_share_one_user_message():
    raw = [NS(type="tool_use", id="t1", name="bash", input={"command": "ls"})]
    msgs = [
        {"role": "user", "content": "intro"},
        {"role": "user", "content": "budget 0/32"},
        {"role": "assistant", "content": "", "tool_calls": [ToolCall("t1", "bash", {"command": "ls"})], "raw": raw},
        {"role": "tool", "tool_call_id": "t1", "content": ""},
        {"role": "user", "content": "budget 1/32"},
    ]
    api = to_api_messages(msgs)
    assert [m["role"] for m in api] == ["user", "assistant", "user"]
    assert [b["type"] for b in api[0]["content"]] == ["text", "text"]
    assert api[1]["content"] is raw  # sent back unchanged
    assert api[2]["content"][0] == {"type": "tool_result", "tool_use_id": "t1", "content": "(no output)"}
    assert api[2]["content"][1]["text"] == "budget 1/32"


def test_assistant_without_raw_is_rebuilt():
    msgs = [{"role": "user", "content": "x"},
            {"role": "assistant", "content": "hi", "tool_calls": [ToolCall("a", "bash", {"command": "pwd"})]}]
    content = to_api_messages(msgs)[1]["content"]
    assert content[0] == {"type": "text", "text": "hi"}
    assert content[1]["type"] == "tool_use" and content[1]["input"] == {"command": "pwd"}


class FakeClient:
    def __init__(self, response):
        self.response, self.kwargs = response, None
        self.messages = self

    def create(self, **kwargs):
        self.kwargs = kwargs
        return self.response


def response(stop_reason, content):
    usage = NS(input_tokens=100, output_tokens=50, cache_read_input_tokens=900, cache_creation_input_tokens=200)
    return NS(stop_reason=stop_reason, content=content, usage=usage)


def test_step_parses_tool_calls_and_usage():
    content = [NS(type="thinking", thinking=""), NS(type="text", text="ok"),
               NS(type="tool_use", id="t9", name="bash", input={"command": "ls"})]
    client = FakeClient(response("tool_use", content))
    turn = AnthropicModel("claude-haiku-5-5", client=client).step("sys", [{"role": "user", "content": "go"}], [BASH])
    assert turn.text == "ok" and turn.tool_calls == (ToolCall("t9", "bash", {"command": "ls"}),)
    assert turn.usage.input_tokens == 1200 and turn.usage.cached_input_tokens == 900
    assert turn.usage.cache_write_tokens == 200 and turn.raw is content
    assert client.kwargs["cache_control"] == {"type": "ephemeral"}
    assert client.kwargs["tools"][0]["name"] == "bash"
    assert "thinking" not in client.kwargs  # adaptive by default; never disabled


def test_refusal_returns_no_tool_calls():
    client = FakeClient(response("refusal", [NS(type="text", text="")]))
    turn = AnthropicModel("claude-haiku-5-5", client=client).step("s", [{"role": "user", "content": "x"}], [BASH])
    assert turn.tool_calls == () and turn.stop_reason == "refusal"


def test_unknown_model_needs_a_price_table():
    with pytest.raises(ValueError):
        AnthropicModel("claude-unknown", client=FakeClient(None))
