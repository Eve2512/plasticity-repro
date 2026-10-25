"""Parallel games give the same results as serial ones; resume continues a run."""

import json

from harness.episode import EpisodeConfig
from harness.reflection import ReflectionConfig
from harness.runner import RunConfig, run_lineage
from harness.scripted import first_legal_factory


def config(**kw):
    base = dict(
        rounds=1,
        games={"train": 2, "id": 2, "ood": 2},
        train_id_levels=(200,),
        ood_levels=(400,),
        episode=EpisodeConfig(max_calls=4, tool_timeout=30),
        reflection=ReflectionConfig(max_calls=3, max_attempts=1),
    )
    base.update(kw)
    return RunConfig(**base)


def outcomes(checkpoints):
    """Checkpoint rows without cost: the scripted model's token estimates depend on path lengths."""
    return [{k: v for k, v in c.items() if k != "cost_cumulative"} for c in checkpoints]


def game_moves(run_dir):
    return {f.name: json.loads(f.read_text())["result"]["moves"] for f in run_dir.glob("games/*/*/*.json")}


def test_parallel_matches_serial(tmp_path):
    factory = first_legal_factory()
    serial = run_lineage(factory(), tmp_path / "serial", config())
    parallel = run_lineage(factory(), tmp_path / "parallel", config(workers=2), model_factory=factory)
    assert outcomes(serial["checkpoints"]) == outcomes(parallel["checkpoints"])
    assert game_moves(tmp_path / "serial") == game_moves(tmp_path / "parallel")
    assert abs(serial["learning_cost"] - parallel["learning_cost"]) / serial["learning_cost"] < 0.02


def test_parallel_records_spend_when_the_cap_stops_it(tmp_path):
    factory = first_legal_factory()
    res = run_lineage(factory(), tmp_path / "run", config(workers=2, cap=1e-6), model_factory=factory)
    assert res["stopped"] and "cap" in res["stopped"]
    assert len((tmp_path / "run" / "ledger.jsonl").read_text().splitlines()) >= 1


def test_resume_finishes_like_an_uninterrupted_run(tmp_path):
    factory = first_legal_factory()
    full = run_lineage(factory(), tmp_path / "full", config(rounds=2))

    run = tmp_path / "crashed"
    run_lineage(factory(), run, config(rounds=2))
    # Simulate a crash during checkpoint 1: only checkpoint 0 was recorded.
    results = json.loads((run / "results.json").read_text())
    results["checkpoints"] = results["checkpoints"][:1]
    (run / "results.json").write_text(json.dumps(results))

    resumed = run_lineage(factory(), run, config(rounds=2), resume=True)
    assert outcomes(resumed["checkpoints"]) == outcomes(full["checkpoints"])
    discarded = (run / "ledger_discarded.jsonl").read_text().splitlines()
    assert discarded and all(json.loads(line)["checkpoint"] >= 1 for line in discarded)
    assert resumed["billed"] > full["billed"]  # the discarded work was paid for
    assert abs(resumed["learning_cost"] - full["learning_cost"]) / full["learning_cost"] < 0.02


def test_resume_refuses_a_changed_config(tmp_path):
    import pytest

    factory = first_legal_factory()
    run_lineage(factory(), tmp_path / "run", config())
    with pytest.raises(ValueError, match="cannot resume"):
        run_lineage(factory(), tmp_path / "run", config(games={"train": 4, "id": 2, "ood": 2}), resume=True)
