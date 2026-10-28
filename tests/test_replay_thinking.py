import json
import sys
import threading
from pathlib import Path

from harness.ledger import Ledger
from harness.model import ModelTurn, ToolCall, Usage
from plasticity.pricing import PriceTable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import replay_thinking as rt  # noqa: E402

SAVED = [
    {"role": "user", "content": "reflect"},
    {"role": "user", "content": "budget 0/50"},
    {"role": "assistant", "content": "", "tool_calls": [{"id": "a", "name": "bash", "args": {"command": "ls"}}]},
    {"role": "tool", "tool_call_id": "a", "content": "inventory"},
    {"role": "user", "content": "budget 1/50"},
    {"role": "assistant", "content": "done", "tool_calls": []},
]


class Fake:
    name = "fake"

    def __init__(self):
        self.contexts = []

    def step(self, system, messages, tools):
        self.contexts.append(messages)
        calls = (ToolCall("b", "bash", {"command": "ls"}),) if len(self.contexts) == 1 else ()
        return ModelTurn("", calls, Usage(10, 5, reported_cost=0.01), thinking=f"summary {len(self.contexts)}")


def test_contexts_stop_before_each_assistant_turn():
    got = list(rt.contexts(SAVED))
    assert [i for i, _, _ in got] == [2, 5]
    _, context, recorded = got[1]
    assert len(context) == 5 and isinstance(context[2]["tool_calls"][0], ToolCall)
    assert recorded["content"] == "done"


def test_replay_attempt_records_and_resumes(tmp_path):
    log = tmp_path / "run" / "reflect" / "checkpoint_002" / "attempt_1" / "attempt_1.json"
    log.parent.mkdir(parents=True)
    log.write_text(json.dumps({"messages": SAVED}))
    ledger = Ledger(PriceTable(1, 5), billing=PriceTable(1, 5), cap=1.0)
    model = Fake()
    assert rt.replay_attempt(model, log, ledger, threading.Lock()) == 2
    rows = [json.loads(x) for x in rt.out_path(log).read_text().splitlines()]
    assert rt.out_path(log).name == "checkpoint_002_attempt_1.jsonl"
    assert [r["same_call"] for r in rows] == [True, True]
    assert rows[0]["thinking"] == "summary 1" and ledger.billed() == 0.02
    assert rt.replay_attempt(model, log, ledger, threading.Lock()) == 0  # already done
