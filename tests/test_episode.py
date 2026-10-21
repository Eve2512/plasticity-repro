import itertools
import json

import pytest

from envs.hex_openings import opening_bank
from harness.episode import EpisodeConfig, play_game
from harness.inventory import empty_inventory
from harness.ledger import Ledger
from harness.model import ModelTurn, ScriptedModel, ToolCall
from plasticity.pricing import PriceTable

_ids = itertools.count()


def call(name, **args):
    return ToolCall(f"c{next(_ids)}", name, args)


def first_legal(state):
    return state.legal_actions()[0]


@pytest.fixture
def env(tmp_path):
    inv = empty_inventory(tmp_path / "inventory")
    return inv, tmp_path / "session", Ledger(PriceTable(1.0, 5.0)), tmp_path


def run(model, env, cfg=EpisodeConfig(max_calls=32, tool_timeout=10), transcript=None):
    inv, ses, ledger, root = env
    opening = opening_bank("train", "X", 1)[0]
    return play_game(model, "g1", opening, first_legal, inv, ses, [root], ledger, 0, "train", cfg, transcript)


def test_python_player_finishes_in_one_call(env):
    code = "while not game_api['get_state']()['winner']:\n    game_api['submit_action'](game_api['get_legal_actions']()[-1])"
    model = ScriptedModel(lambda s, m, t: ModelTurn("", (call("python", code=code),)))
    res = run(model, env, transcript=env[3] / "t.json")
    assert res.end_reason == "finished" and res.model_calls == 1
    assert res.winner in ("X", "O") and len(res.moves) > 0
    saved = json.loads((env[3] / "t.json").read_text())
    assert saved["result"]["game_id"] == "g1"
    assert env[2].learning_cost() > 0


def test_native_submit_one_move_per_call(env):
    def policy(system, messages, tools):
        outputs = [m["content"] for m in messages if m["role"] == "tool"]
        if len(outputs) % 2 == 0:
            return ModelTurn("", (call("python", code="game_api['get_legal_actions']()[0]"),))
        return ModelTurn("", (call("submit_action", action=outputs[-1].strip().strip("'")),))

    res = run(ScriptedModel(policy), env)
    assert res.end_reason == "finished" and res.model_calls % 2 == 0


def test_no_tool_call_ends_game_as_loss(env):
    res = run(ScriptedModel(lambda s, m, t: ModelTurn("I resign")), env)
    assert res.end_reason == "no_action" and res.score == 0.0


def test_budget_exhaustion_is_a_loss(env):
    model = ScriptedModel(lambda s, m, t: ModelTurn("", (call("bash", command="echo thinking"),)))
    res = run(model, env, EpisodeConfig(max_calls=3, tool_timeout=10))
    assert res.end_reason == "budget" and res.model_calls == 3 and res.score == 0.0


def test_budget_message_precedes_every_call(env):
    seen = []

    def policy(system, messages, tools):
        seen.append(messages[-1]["content"])
        return ModelTurn("", (call("bash", command="true"),))

    run(ScriptedModel(policy), env, EpisodeConfig(max_calls=2, tool_timeout=10))
    assert seen == [
        "Game model-call budget: 0/2 calls used; 2 remain.",
        "Game model-call budget: 1/2 calls used; 1 remain.",
    ]


def test_timeout_gets_one_recovery_call_with_native_tools_only(env):
    tools_seen = []

    def policy(system, messages, tools):
        tools_seen.append([t.name for t in tools])
        if len(tools_seen) == 1:
            return ModelTurn("", (call("python", code="while True:\n    pass"),))
        return ModelTurn("", (call("get_legal_actions"),))  # recovery call without a submit

    res = run(ScriptedModel(policy), env, EpisodeConfig(max_calls=32, tool_timeout=0.5))
    assert tools_seen[1] == ["get_state", "get_legal_actions", "submit_action"]
    assert res.end_reason == "timeout" and res.score == 0.0
