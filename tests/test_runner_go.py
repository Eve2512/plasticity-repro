"""A scripted Go lineage runs end to end: prompts, GNU Go, adjudication, feedback, reflection."""

import json

import pytest

from envs.go_engine import available
from envs.go_openings import POOLED_FILE
from harness.episode import EpisodeConfig
from harness.reflection import ReflectionConfig
from harness.runner import RunConfig, run_lineage
from harness.scripted import first_legal_factory

pytestmark = pytest.mark.skipif(not (available() and POOLED_FILE.exists()),
                                reason="needs gnugo and data/go_openings_pooled.json")


def test_go_lineage_with_first_legal_player(tmp_path):
    cfg = RunConfig(
        game="go",
        rounds=1,
        games={"train": 2, "id": 2, "ood": 2},
        episode=EpisodeConfig(max_calls=4, tool_timeout=60),
        reflection=ReflectionConfig(max_calls=3, max_attempts=1),
    )
    results = run_lineage(first_legal_factory()(), tmp_path / "run", cfg)
    run = tmp_path / "run"
    assert tuple(results["config"]["train_id_levels"]) == (5, 6, 7, 8, 9)
    assert [c["t"] for c in results["checkpoints"]] == [0, 1]
    for c in results["checkpoints"]:
        assert c["id"]["points"] == 0 and c["id"]["unfinished"] == 0  # first-legal loses every game
    names = sorted(p.name for p in (run / "games" / "checkpoint_000" / "id").glob("*.json"))
    assert names == ["checkpoint_000_id_g01_black.json", "checkpoint_000_id_g02_white.json"]
    transcript = json.loads((run / "games" / "checkpoint_000" / "id" / names[0]).read_text())
    assert transcript["messages"][0]["content"].startswith("A new Go game has started. You play Black (X).")
    assert "75 actions" in transcript["messages"][0]["content"]
    feedback = json.loads(next((run / "feedback" / "checkpoint_000" / "games").glob("*.json")).read_text())
    assert "liberties_after" in feedback["diagnostics"][0]
    summary = json.loads((run / "feedback" / "checkpoint_000" / "summary.json").read_text())
    assert "flagged_moves" in summary["games"][0]
    # training openings differ between checkpoints; held-out openings do not
    def openings(t, split):
        return [json.loads(p.read_text())["opening"] for p in sorted((run / "games" / f"checkpoint_{t:03d}" / split).glob("*.json"))]
    assert openings(0, "id") == openings(1, "id")
    assert openings(0, "train") != openings(1, "train")
