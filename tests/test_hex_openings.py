import json

import pytest

from envs.hex import BLUE, RED
from envs.hex_engine import AlphaBetaEngine
from envs.hex_match import play_from
from envs.hex_openings import (
    BANK_FILE,
    POOLED_FILE,
    SHORT_PLIES,
    spread_order,
    Opening,
    build_contested_banks,
    is_contested,
    opening_bank,
    split_banks,
)


def test_legacy_openings_leave_actor_to_move():
    for actor, plies in ((RED, 10), (BLUE, 11)):
        for o in opening_bank("train", actor, 5):
            s = o.state()
            assert len(o.moves) == plies
            assert s.to_move == actor and not s.is_over()


def test_legacy_banks_are_deterministic_and_disjoint():
    assert opening_bank("id", RED, 4) == opening_bank("id", RED, 4)
    banks = split_banks({"train": 8, "id": 8, "ood": 6}, source="legacy")
    keys = [o.key for bank in banks.values() for o in bank]
    assert len(keys) == len(set(keys))
    assert sum(o.actor == RED for o in banks["train"]) == 4


def test_lost_position_is_not_contested():
    # Blue to move; red threatens both b6 and c6, so blue loses whatever it plays.
    lost = Opening(("c1", "a1", "c2", "a2", "c3", "a3", "c4", "a4", "c5"), BLUE)
    assert not is_contested(lost)


def test_built_banks_follow_the_rule(tmp_path):
    data = build_contested_banks({"train": 2, "id": 2})
    for split, by_colour in data["banks"].items():
        for actor, games in by_colour.items():
            assert len(games) == 1
            o = Opening(tuple(games[0]), actor)
            assert len(o.moves) == SHORT_PLIES[actor] and o.state().to_move == actor
            assert is_contested(o)
    path = tmp_path / "banks.json"
    path.write_text(json.dumps(data))
    loaded = split_banks({"train": 2}, bank_file=path)
    assert [o.actor for o in loaded["train"]] == [RED, BLUE]
    with pytest.raises(ValueError):
        split_banks({"train": 4}, bank_file=path)


def test_saved_banks_cover_the_paper_sizes():
    banks = split_banks({"train": 40, "id": 40, "ood": 32})
    keys = [o.key for bank in banks.values() for o in bank]
    assert len(keys) == len(set(keys)) == 112
    assert all(len(o.moves) == SHORT_PLIES[o.actor] for o in banks["train"])


def test_spread_order_prefixes_span_the_range():
    for n in (4, 6, 12, 20):
        order = spread_order(n)
        assert sorted(order) == list(range(n))
        first = order[: max(2, n // 4)]
        assert min(first) < n / 4 and max(first) >= n / 2


def test_pooled_banks_are_disjoint_and_difficulty_balanced():
    data = json.loads(POOLED_FILE.read_text())
    banks = data["banks"]
    keys = [tuple(e["moves"]) for by in banks.values() for es in by.values() for e in es]
    assert len(keys) == len(set(keys)) == 112
    for actor in (RED, BLUE):
        means = [sum(e["difficulty"] for e in banks[s][actor]) / len(banks[s][actor]) for s in ("train", "id", "ood")]
        assert max(means) - min(means) < 0.25
    # the first games a run takes are mixed too, not only the easy end
    for split in ("train", "id"):
        first = [e["difficulty"] for e in banks[split][RED][:4]]
        assert min(first) < max(first)


def test_default_source_is_pooled():
    banks = split_banks({"train": 8, "id": 12})
    stored = json.loads(POOLED_FILE.read_text())["banks"]
    assert [list(o.moves) for o in banks["train"][:4]] == [e["moves"] for e in stored["train"][RED][:4]]


def test_missing_bank_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        split_banks({"train": 2}, bank_file=tmp_path / "none.json")
    assert BANK_FILE.name == "hex_openings_contested.json"


def test_match_runs_to_a_winner():
    opening = opening_bank("train", RED, 1)[0]
    record = play_from(opening, lambda s: s.legal_actions()[0], AlphaBetaEngine(300).choose)
    assert record.winner in (RED, BLUE)
    assert record.opening == opening.moves
