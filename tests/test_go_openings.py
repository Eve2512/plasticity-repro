import json

import pytest

from envs.go import BLACK, WHITE
from envs.go_engine import available
from envs.go_openings import Opening, _candidates, _stratified, split_banks
from harness.game_api import GameSession


@pytest.fixture
def bank_file(tmp_path):
    def entries(prefix, n):
        return [{"moves": [f"{prefix}{i}"], "difficulty": i} for i in range(n)]

    banks = {split: {BLACK: entries(f"{split}-b", n), WHITE: entries(f"{split}-w", n)}
             for split, n in {"train": 12, "id": 5, "ood": 3}.items()}
    path = tmp_path / "go.json"
    path.write_text(json.dumps({"banks": banks}))
    return path


def test_held_out_banks_and_seeds_are_fixed(bank_file):
    a = split_banks({"id": 4, "ood": 2}, checkpoint=0, bank_file=bank_file)
    b = split_banks({"id": 4, "ood": 2}, checkpoint=5, bank_file=bank_file)
    assert a == b
    assert [o.actor for o in a["id"]] == [BLACK, BLACK, WHITE, WHITE]
    assert len({o.seed for o in a["id"] + a["ood"]}) == 6


def test_training_openings_and_seeds_change_per_checkpoint(bank_file):
    draws = [split_banks({"train": 6}, checkpoint=t, bank_file=bank_file)["train"] for t in range(4)]
    assert len({tuple(o.moves for o in d) for d in draws}) > 1
    assert len({o.seed for d in draws for o in d}) == 24
    assert draws[2] == split_banks({"train": 6}, checkpoint=2, bank_file=bank_file)["train"]  # reproducible


def test_stratified_draw_covers_the_difficulty_range():
    import random

    picks = _stratified(list(range(40)), 4, random.Random(0))
    assert sorted(p // 10 for p in picks) == [0, 1, 2, 3]


def test_too_few_openings_is_an_error(bank_file):
    with pytest.raises(ValueError):
        split_banks({"id": 12}, bank_file=bank_file)


def test_candidates_leave_the_actor_to_move():
    for actor, plies in ((BLACK, 2), (WHITE, 3)):
        o = next(_candidates(actor, plies))
        assert len(o.moves) == plies and o.state(adjudicate=False).to_move == actor


def test_session_analysis_board_is_not_adjudicated():
    g = GameSession(Opening(("C3",), WHITE), lambda s: "pass")
    assert g.real.adjudicator is not None and g.analysis.adjudicator is None
    assert g.get_legal_actions()[-1] == "pass"
    assert g.apply_action("pass")["ok"] and g.apply_action("pass")["winner"] == BLACK  # plain area count
    g.undo_action()
    g.undo_action()
    assert g.get_state()["analysis_depth"] == 0


@pytest.mark.skipif(not available(), reason="gnugo not installed")
def test_session_plays_a_game_to_the_end_with_gnugo():
    from envs.go_engine import GnuGoEngine

    g = GameSession(Opening(("C3", "B2"), BLACK), GnuGoEngine(5).choose)
    while not g.done:
        res = g.submit_action(g.get_legal_actions()[0])
        assert res["accepted"]
    assert g.real.winner() in (BLACK, WHITE)
    assert not g.submit_action("pass")["accepted"]



def test_deal_gives_every_split_the_same_quantiles():
    from envs.go_openings import _deal_order

    order = _deal_order({"id": 10, "ood": 6, "train": 40})
    assert len(order) == 56
    for split in ("id", "ood", "train"):
        positions = [i for i, s in enumerate(order) if s == split]
        assert abs(sum(positions) / len(positions) - 27.5) < 1.5  # centred on the pool's middle
        assert positions[0] < 6 and positions[-1] > 49  # reaches both ends
