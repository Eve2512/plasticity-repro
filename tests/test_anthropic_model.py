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


def test_openrouter_client_never_sends_the_anthropic_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-should-not-leak")
    model = AnthropicModel("anthropic/claude-sonnet-5.5", base_url="https://openrouter.ai/api", auth_token="or-x")
    headers = {k.lower(): v for k, v in model.client.auth_headers.items()}
    assert headers["authorization"] == "Bearer or-x"
    assert "sk-ant-should-not-leak" not in str(headers)


def test_reported_cost_is_recorded():
    resp = response("end_turn", [NS(type="text", text="hi")])
    resp.usage.cost = 0.0042
    turn = AnthropicModel("claude-haiku-5-5", client=FakeClient(resp)).step("s", [{"role": "user", "content": "x"}], [])
    assert turn.usage.reported_cost == 0.0042


def test_out_of_credit_stops_like_the_cap():
    import anthropic
    import httpx2

    from harness.ledger import BudgetExceeded

    class Broke:
        def __init__(self):
            self.messages = self

        def create(self, **kwargs):
            req = httpx2.Request("POST", "https://openrouter.ai/api/v1/messages")
            raise anthropic.APIStatusError("no credit", response=httpx2.Response(402, request=req), body=None)

    with pytest.raises(BudgetExceeded, match="402"):
        AnthropicModel("anthropic/claude-sonnet-5.5", client=Broke()).step("s", [{"role": "user", "content": "x"}], [])


class Flaky:
    """Fails `n` times with `error`, then answers."""

    def __init__(self, n, error):
        self.n, self.error, self.calls = n, error, 0
        self.messages = self

    def create(self, **kwargs):
        self.calls += 1
        if self.calls <= self.n:
            raise self.error()
        return response("end_turn", [NS(type="text", text="ok")])


def _connection_error():
    import anthropic
    import httpx2

    return anthropic.APIConnectionError(request=httpx2.Request("POST", "https://openrouter.ai/api/v1/messages"))


def _status_error(code):
    import anthropic
    import httpx2

    req = httpx2.Request("POST", "https://openrouter.ai/api/v1/messages")
    return lambda: anthropic.APIStatusError("x", response=httpx2.Response(code, request=req), body=None)


def test_waits_out_a_connection_outage():
    client = Flaky(3, _connection_error)
    model = AnthropicModel("anthropic/claude-sonnet-5.5", client=client)
    waits = []
    model.sleep = waits.append
    turn = model.step("s", [{"role": "user", "content": "x"}], [])
    assert turn.text == "ok" and client.calls == 4 and waits == [30, 60, 120]


def test_gives_up_after_the_last_wait():
    import anthropic

    from harness.anthropic_model import OUTAGE_WAITS

    client = Flaky(100, _connection_error)
    model = AnthropicModel("anthropic/claude-sonnet-5.5", client=client)
    model.sleep = lambda s: None
    with pytest.raises(anthropic.APIConnectionError):
        model.step("s", [{"role": "user", "content": "x"}], [])
    assert client.calls == len(OUTAGE_WAITS) + 1


def test_retries_transient_status_but_not_bad_request():
    import anthropic

    model = AnthropicModel("anthropic/claude-sonnet-5.5", client=Flaky(2, _status_error(503)))
    model.sleep = lambda s: None
    assert model.step("s", [{"role": "user", "content": "x"}], []).text == "ok"
    model = AnthropicModel("anthropic/claude-sonnet-5.5", client=Flaky(1, _status_error(400)))
    model.sleep = lambda s: None
    with pytest.raises(anthropic.APIStatusError):
        model.step("s", [{"role": "user", "content": "x"}], [])


def test_model_spec_pickles_and_hides_the_key():
    import pickle

    from harness.anthropic_model import ModelSpec

    spec = ModelSpec("anthropic/claude-haiku-5.5", key="sk-or-secret", effort="low")
    assert "sk-or-secret" not in repr(spec)
    model = pickle.loads(pickle.dumps(spec))()
    assert model.name == "anthropic/claude-haiku-5.5" and model.effort == "low"


def test_unknown_model_needs_a_price_table():
    with pytest.raises(ValueError):
        AnthropicModel("claude-unknown", client=FakeClient(None))


def test_thinking_summary_is_requested_and_kept():
    content = [NS(type="thinking", thinking="B3 connects both stones."), NS(type="text", text=""),
               NS(type="tool_use", id="t1", name="bash", input={"command": "echo B3"})]
    client = FakeClient(response("tool_use", content))
    model = AnthropicModel("claude-haiku-5-5", client=client, thinking_display="summarized")
    turn = model.step("sys", [{"role": "user", "content": "go"}], [BASH])
    assert client.kwargs["thinking"] == {"type": "adaptive", "display": "summarized"}
    assert turn.thinking == "B3 connects both stones." and turn.raw is content
