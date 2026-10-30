"""Chat-completions adapter tests with a fake POST: no API calls."""

import pytest

from harness.anthropic_model import ModelSpec
from harness.chat_model import ChatModel, ProviderError, to_chat_messages
from harness.ledger import BudgetExceeded
from harness.model import BASH, ToolCall, assistant_message


def reply(message, finish="tool_calls", usage=None):
    return {"choices": [{"message": message, "finish_reason": finish}],
            "usage": usage or {"prompt_tokens": 1000, "completion_tokens": 50,
                               "prompt_tokens_details": {"cached_tokens": 800}, "cost": 0.0012}}


class FakePost:
    def __init__(self, *replies):
        self.replies, self.bodies = list(replies), []

    def __call__(self, body):
        self.bodies.append(body)
        r = self.replies.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def test_step_parses_tool_calls_usage_and_reasoning():
    details = [{"type": "reasoning.text", "text": "think"}]
    post = FakePost(reply({"content": "", "reasoning": "I should list files.", "reasoning_details": details,
                           "tool_calls": [{"id": "c1", "type": "function",
                                           "function": {"name": "bash", "arguments": '{"command": "ls"}'}}]}))
    model = ChatModel("z-ai/glm-5.3", "k", effort="xhigh", thinking_display="summarized", post=post)
    turn = model.step("sys", [{"role": "user", "content": "go"}], [BASH])
    assert turn.tool_calls == (ToolCall("c1", "bash", {"command": "ls"}),)
    assert turn.stop_reason == "tool_use" and turn.thinking == "I should list files."
    assert turn.usage.input_tokens == 1000 and turn.usage.cached_input_tokens == 800
    assert turn.usage.reported_cost == 0.0012
    body = post.bodies[0]
    assert body["reasoning"] == {"effort": "high", "exclude": False}  # xhigh is sent as high
    assert body["usage"] == {"include": True}
    assert body["messages"][0] == {"role": "system", "content": "sys"}
    assert body["tools"][0]["function"]["name"] == "bash"


def test_history_sends_reasoning_details_and_tool_results_back():
    details = [{"type": "reasoning.encrypted", "data": "x"}]
    post = FakePost(reply({"content": "", "reasoning_details": details,
                           "tool_calls": [{"id": "c1", "function": {"name": "bash", "arguments": "{}"}}]}))
    turn = ChatModel("meta/muse-spark-1.3", "k", post=post).step("s", [{"role": "user", "content": "go"}], [BASH])
    msgs = [{"role": "user", "content": "go"}, assistant_message(turn),
            {"role": "tool", "tool_call_id": "c1", "content": ""}, {"role": "user", "content": "budget 1/32"}]
    api = to_chat_messages("s", msgs)
    assert [m["role"] for m in api] == ["system", "user", "assistant", "tool", "user"]
    assert api[2]["reasoning_details"] == details
    assert api[2]["tool_calls"][0]["function"] == {"name": "bash", "arguments": "{}"}
    assert api[3] == {"role": "tool", "tool_call_id": "c1", "content": "(no output)"}


def test_bad_arguments_and_missing_ids():
    post = FakePost(reply({"content": "hm", "tool_calls": [{"function": {"name": "python", "arguments": "{oops"}}]}))
    turn = ChatModel("z-ai/glm-5.3", "k", post=post).step("s", [{"role": "user", "content": "go"}], [BASH])
    assert turn.tool_calls[0].args == {} and turn.tool_calls[0].id.startswith("call_")
    assert turn.text == "hm"
    assert post.bodies[0]["reasoning"]["exclude"] is True  # no display asked: reasoning not returned


def test_retries_transient_errors_and_stops_on_402():
    post = FakePost(ProviderError(429, "slow down"), reply({"content": "done"}, finish="stop"))
    model = ChatModel("z-ai/glm-5.3", "k", post=post)
    model.sleep = lambda s: None
    turn = model.step("s", [{"role": "user", "content": "go"}], [BASH])
    assert turn.stop_reason == "end_turn" and len(post.bodies) == 2

    model = ChatModel("z-ai/glm-5.3", "k", post=FakePost(ProviderError(402, "no credit")))
    with pytest.raises(BudgetExceeded):
        model.step("s", [{"role": "user", "content": "go"}], [BASH])


def test_model_spec_builds_the_right_adapter():
    assert isinstance(ModelSpec("z-ai/glm-5.3", key="k", effort="high")(), ChatModel)
    assert type(ModelSpec("anthropic/claude-haiku-5.5", key="k")()).__name__ == "AnthropicModel"
