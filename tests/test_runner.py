import itertools
import json
from dataclasses import replace

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


def test_no_feedback_reflection_sees_no_game_records(tmp_path):
    cfg = RunConfig(
        rounds=1,
        games={"train": 2, "id": 2, "ood": 2},
        train_id_levels=(200,),
        ood_levels=(400,),
        episode=EpisodeConfig(max_calls=4, tool_timeout=30),
        reflection=ReflectionConfig(max_calls=3, max_attempts=1),
        reflection_feedback="none",
    )
    results = run_lineage(ScriptedModel(naive), tmp_path / "run", cfg)
    feedback = tmp_path / "run" / "feedback" / "checkpoint_000"
    assert [p.name for p in feedback.iterdir()] == ["README.md"]
    assert results["checkpoints"][0]["train"]["games"] == 2  # training games are still played and paid for
    assert results["checkpoints"][1]["cost_cumulative"] > 0
    workspace = tmp_path / "run" / "reflect" / "checkpoint_000" / "attempt_1" / "workspace" / "feedback"
    assert not (workspace / "games").exists() and (workspace / "protocol" / "SCHEMA.md").exists()


def test_resume_extends_a_finished_lineage(tmp_path):
    cfg = RunConfig(
        rounds=1,
        games={"train": 2, "id": 2, "ood": 1},
        train_id_levels=(200,),
        ood_levels=(400,),
        episode=EpisodeConfig(max_calls=4, tool_timeout=30),
        reflection=ReflectionConfig(max_calls=3, max_attempts=1),
    )
    run_dir = tmp_path / "run"
    first = run_lineage(ScriptedModel(naive), run_dir, cfg)
    assert [c["t"] for c in first["checkpoints"]] == [0, 1]
    assert "reflection" not in first["checkpoints"][-1]  # the final checkpoint has no reflection

    results = run_lineage(ScriptedModel(naive), run_dir, replace(cfg, rounds=3), resume=True)
    assert [c["t"] for c in results["checkpoints"]] == [0, 1, 2, 3]
    assert results["checkpoints"][1]["reflection"]["attempts"]  # reflected on the saved games
    assert (run_dir / "feedback" / "checkpoint_001" / "summary.json").exists()
    assert (run_dir / "inventories" / "checkpoint_003").exists()
    assert results["config"]["rounds"] == 3
    costs = [c["cost_cumulative"] for c in results["checkpoints"]]
    assert costs == sorted(costs) and costs[2] > costs[1]  # the extra reflection is a learning cost
