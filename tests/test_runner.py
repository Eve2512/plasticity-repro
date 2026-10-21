import itertools
import json

from harness.episode import EpisodeConfig
from harness.model import ModelTurn, ScriptedModel, ToolCall
from harness.reflection import ReflectionConfig
from harness.runner import RunConfig, run_lineage

_ids = itertools.count()


def naive(system, messages, tools):
    """Actor: play the first legal action. Reflector: change nothing."""
    if messages[0]["content"].startswith("A new hex game"):
        if any(m["role"] == "assistant" for m in messages):
            return ModelTurn("done")
        code = "s = game_api['get_state']()\nwhile not s['winner']:\n    s = game_api['submit_action'](game_api['get_legal_actions']()[0])"
        return ModelTurn("", (ToolCall(f"c{next(_ids)}", "python", {"code": code}),))
    return ModelTurn("nothing to change")


def test_spending_cap_stops_the_run_cleanly(tmp_path):
    cfg = RunConfig(
        rounds=2,
        games={"train": 2, "id": 2, "ood": 2},
        train_id_levels=(200,),
        ood_levels=(400,),
        episode=EpisodeConfig(max_calls=4, tool_timeout=30),
        reflection=ReflectionConfig(max_calls=3, max_attempts=1),
        cap=1e-6,
    )
    results = run_lineage(ScriptedModel(naive), tmp_path / "run", cfg)
    assert results["stopped"] and "cap" in results["stopped"]
    assert results["checkpoints"] == []  # no checkpoint finished
    assert json.loads((tmp_path / "run" / "results.json").read_text())["stopped"]


def test_lineage_layout_and_results(tmp_path):
    cfg = RunConfig(
        rounds=1,
        games={"train": 2, "id": 2, "ood": 2},
        train_id_levels=(200,),
        ood_levels=(400,),
        episode=EpisodeConfig(max_calls=4, tool_timeout=30),
        reflection=ReflectionConfig(max_calls=3, max_attempts=1),
    )
    results = run_lineage(ScriptedModel(naive), tmp_path / "run", cfg)
    run = tmp_path / "run"
    assert [c["t"] for c in results["checkpoints"]] == [0, 1]
    assert results["checkpoints"][0]["cost_cumulative"] == 0.0
    assert results["checkpoints"][1]["cost_cumulative"] > 0
    assert results["checkpoints"][0]["reflection"]["accepted"]
    assert (run / "inventories" / "checkpoint_001" / "tracking" / "artifacts.json").exists()
    # held-out games are recorded but never copied into the reflection feedback
    assert len(list((run / "games" / "checkpoint_000" / "id").glob("*.json"))) == 2
    feedback_games = [p.name for p in (run / "feedback" / "checkpoint_000" / "games").glob("*.json")]
    assert feedback_games and all("_train_" in name for name in feedback_games)
    # learning cost excludes held-out evaluation
    assert results["learning_cost"] < results["total_cost"]
    assert json.loads((run / "results.json").read_text())["plasticity"]["split"] == "id"
