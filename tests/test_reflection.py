import itertools
import json
import shlex

import pytest

from harness.episode import GameResult
from harness.inventory import empty_inventory
from harness.ledger import Ledger
from harness.model import ModelTurn, ScriptedModel, ToolCall
from harness.reflection import ReflectionConfig, reflect, write_feedback
from plasticity.pricing import PriceTable

_ids = itertools.count()
GOOD_TOOL = "def pick(actions):\n    return actions[0]\n"
TRACKING = {
    "failure_modes.json": {"schema_version": "failure_modes.v1", "failure_modes": [
        {"id": "FM-0001", "description": "lost", "status": "active", "trajectory_ids": ["g1"]}]},
    "artifacts.json": {"schema_version": "artifacts.v1", "artifacts": [
        {"id": "AR-0001", "description": "picker", "kind": "tool", "paths": ["tools/pick.py"],
         "entrypoints": ["tools/pick.py:pick"], "failure_mode_ids": ["FM-0001"], "status": "active"}]},
}


def bash(cmd):
    return ToolCall(f"c{next(_ids)}", "bash", {"command": cmd})


def writer(tool_source):
    """Scripted reflection: write a tool and tracking files, run the validator, stop."""
    def policy(system, messages, tools):
        n = sum(m["role"] == "assistant" for m in messages)
        if n == 0:
            cmds = ["mkdir -p inventory/tools", f"printf %s {shlex.quote(tool_source)} > inventory/tools/pick.py"]
            cmds += [f"printf %s {shlex.quote(json.dumps(v))} > inventory/tracking/{k}" for k, v in TRACKING.items()]
            return ModelTurn("", (bash(" && ".join(cmds)),))
        if n == 1:
            cmd = messages[0]["content"].split("run the validator (")[1].split(")")[0]
            return ModelTurn("", (bash(cmd),))
        return ModelTurn("done")
    return policy


@pytest.fixture
def setup(tmp_path):
    parent = empty_inventory(tmp_path / "inv0")
    feedback = tmp_path / "feedback"
    result = GameResult("g1", "X", "O", 0.0, "finished", 3,
                        moves=[{"before": ["c3", "d3", "c4", "d4", "b5", "e2", "e3", "a4", "f1", "b2"],
                                "action": "a1", "opponent_action": "d5"}])
    write_feedback(feedback, [(result, None, None)])
    return parent, feedback, tmp_path


def test_feedback_has_diagnostics_and_summary(setup):
    _, feedback, _ = setup
    game = json.loads((feedback / "games" / "g1.json").read_text())
    assert game["diagnostics"][0]["action"] == "a1"
    assert json.loads((feedback / "summary.json").read_text())["mean_score"] == 0.0


def test_accepted_reflection(setup):
    parent, feedback, root = setup
    ledger = Ledger(PriceTable(1.0, 5.0))
    out = reflect(ScriptedModel(writer(GOOD_TOOL)), parent, feedback, root / "r", [root], ledger, 0)
    assert out.accepted, out.attempts
    assert (out.inventory / "tools" / "pick.py").exists()
    assert len(out.attempts) == 1 and ledger.round_cost(0, "reflect") > 0
    # the validator the model ran printed OK
    log = json.loads((root / "r" / "attempt_1" / "attempt_1.json").read_text())
    assert any(m["role"] == "tool" and m["content"].strip() == "OK" for m in log["messages"])


def test_rejected_attempts_keep_parent_and_record_errors(setup):
    parent, feedback, root = setup
    bad = "import os\ndef pick(actions):\n    return actions[0]\n"
    out = reflect(ScriptedModel(writer(bad)), parent, feedback, root / "r", [root], Ledger(PriceTable(1, 1)), 0,
                  ReflectionConfig(max_attempts=2))
    assert not out.accepted and out.inventory == parent
    assert len(out.attempts) == 2 and "persistent tool load failed" in out.attempts[0]["error"]
    retry_ws = root / "r" / "attempt_2" / "workspace" / "feedback"
    assert (retry_ws / "reflection_retry_history.json").exists()
    assert (retry_ws / "reflection_attempts" / "attempt_1.json").exists()


def test_final_call_message(setup):
    parent, feedback, root = setup
    seen = []

    def policy(system, messages, tools):
        seen.append(messages[-1]["content"])
        return ModelTurn("", (bash("true"),))

    reflect(ScriptedModel(policy), parent, feedback, root / "r", [root], Ledger(PriceTable(1, 1)), 0,
            ReflectionConfig(max_calls=2, max_attempts=1))
    assert seen[0].startswith("Reflection budget: 0/2")
    assert "Final reflection call 2/2" in seen[1]


def test_reflection_cannot_read_outside_workspace(setup):
    parent, feedback, root = setup
    (root / "heldout").mkdir()
    (root / "heldout" / "secret.json").write_text("{}")
    outputs = []

    def policy(system, messages, tools):
        if any(m["role"] == "tool" for m in messages):
            outputs.append([m for m in messages if m["role"] == "tool"][-1]["content"])
            return ModelTurn("stop")
        return ModelTurn("", (bash(f"cat {root / 'heldout' / 'secret.json'}"),))

    reflect(ScriptedModel(policy), parent, feedback, root / "r", [root], Ledger(PriceTable(1, 1)), 0,
            ReflectionConfig(max_attempts=1))
    assert "Operation not permitted" in outputs[0]
