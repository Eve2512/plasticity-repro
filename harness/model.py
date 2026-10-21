"""Provider-neutral model interface.

Messages are dicts: {"role": "user", "content": str},
{"role": "assistant", "content": str, "tool_calls": [ToolCall]}, and
{"role": "tool", "tool_call_id": str, "content": str}. Provider adapters convert
these; ScriptedModel is used in tests and the no-cost dry run.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict  # JSON schema of the arguments


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    args: dict


@dataclass(frozen=True)
class Usage:
    input_tokens: int = 0  # all prompt tokens, including cached and cache-write parts
    output_tokens: int = 0
    cached_input_tokens: int = 0  # part of input_tokens served from a cache
    cache_write_tokens: int = 0  # part of input_tokens written to a cache
    reported_cost: float | None = None  # USD the provider says it charged, when it reports one


@dataclass(frozen=True)
class ModelTurn:
    text: str
    tool_calls: tuple[ToolCall, ...] = ()
    usage: Usage = field(default_factory=Usage)
    raw: object = None  # provider content to send back unchanged (e.g. thinking blocks)
    stop_reason: str | None = None


class Model(Protocol):
    name: str

    def step(self, system: str, messages: list[dict], tools: list[ToolSpec]) -> ModelTurn: ...


BASH = ToolSpec(
    "bash",
    "Run a Bash command in the sandbox and return its output.",
    {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
)
PYTHON = ToolSpec(
    "python",
    "Run code in the persistent sandboxed Python interpreter (game_api and load_python are defined). "
    "The value of a final expression is printed.",
    {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]},
)
SUBMIT_ACTION = ToolSpec(
    "submit_action",
    "Commit one legal action on the real board; the opponent replies.",
    {"type": "object", "properties": {"action": {"type": "string"}}, "required": ["action"]},
)
GET_STATE = ToolSpec("get_state", "Return the current real game state.", {"type": "object", "properties": {}})
GET_LEGAL_ACTIONS = ToolSpec(
    "get_legal_actions", "Return the legal actions on the real board.", {"type": "object", "properties": {}}
)


def serialise_messages(messages: list[dict]) -> list[dict]:
    """JSON-ready copy: tool calls as dicts, provider raw content dropped."""
    out = []
    for m in messages:
        m = {k: v for k, v in m.items() if k != "raw"}
        if "tool_calls" in m:
            m["tool_calls"] = [{"id": c.id, "name": c.name, "args": c.args} for c in m["tool_calls"]]
        out.append(m)
    return out


def estimate_tokens(text: str) -> int:
    """Rough count (4 characters per token) for scripted runs."""
    return max(1, len(text) // 4)


class ScriptedModel:
    """Calls `policy(system, messages, tools)` and fills in estimated usage."""

    def __init__(self, policy: Callable[[str, list, list], ModelTurn], name: str = "scripted"):
        self.policy = policy
        self.name = name
        self.calls = 0

    def step(self, system, messages, tools):
        self.calls += 1
        turn = self.policy(system, messages, tools)
        prompt = system + "".join(str(m.get("content", "")) for m in messages)
        written = turn.text + "".join(str(c.args) for c in turn.tool_calls)
        return ModelTurn(turn.text, turn.tool_calls, Usage(estimate_tokens(prompt), estimate_tokens(written)))
