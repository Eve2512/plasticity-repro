from envs.hex import BLUE, RED
from envs.hex_engine import AlphaBetaEngine
from envs.hex_match import play_from
from envs.hex_openings import opening_bank, split_banks


def test_openings_leave_actor_to_move():
    for actor, plies in ((RED, 10), (BLUE, 11)):
        for o in opening_bank("train", actor, 5):
            s = o.state()
            assert len(o.moves) == plies
            assert s.to_move == actor and not s.is_over()


def test_banks_are_deterministic():
    assert opening_bank("id", RED, 4) == opening_bank("id", RED, 4)


def test_splits_are_disjoint_and_sized():
    banks = split_banks({"train": 8, "id": 8, "ood": 6})
    assert {k: len(v) for k, v in banks.items()} == {"train": 8, "id": 8, "ood": 6}
    keys = [o.key for bank in banks.values() for o in bank]
    assert len(keys) == len(set(keys))
    assert sum(o.actor == RED for o in banks["train"]) == 4


def test_match_runs_to_a_winner():
    opening = opening_bank("train", RED, 1)[0]
    engine = AlphaBetaEngine(300)
    record = play_from(opening, lambda s: s.legal_actions()[0], engine.choose)
    assert record.winner in (RED, BLUE)
    assert record.opening == opening.moves
