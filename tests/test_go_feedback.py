from envs.go import GoState
from envs.go_feedback import diagnose_game, diagnose_move


def board(moves):
    s = GoState()
    for m in moves:
        s.play(m)
    return s


def test_capture_is_counted():
    d = diagnose_move(board(["A2", "A1"]), "B1")
    assert d["captured"] == 1 and d["largest_capture_available"] == 1
    assert d["severity"] == "ok"


def test_missed_capture_is_visible():
    d = diagnose_move(board(["A2", "A1"]), "E5")
    assert d["captured"] == 0 and d["largest_capture_available"] == 1
    assert d["opponent_stones_in_atari"] == 1


def test_self_atari_is_flagged():
    # Black B1 between White A1 and C1: its only liberty is B2.
    s = board(["E5", "A1", "E4", "C1"])
    d = diagnose_move(s, "B1")
    assert d["liberties_after"] == 1 and "self_atari" in d["labels"] and d["severity"] == "flagged"
    assert d["own_stones_in_atari"] == 1


def test_passing_while_behind_is_flagged_but_not_when_ahead():
    behind = diagnose_move(board(["pass", "C3"]), "pass")  # Black passes with nothing on the board
    assert "pass_while_behind" in behind["labels"] and behind["liberties_after"] is None
    ahead = diagnose_move(board(["C3", "pass"]), "pass")
    assert ahead["labels"] == [] and ahead["area_margin"] == [15.5, 15.5]


def test_area_margin_is_from_the_movers_side():
    d = diagnose_move(board(["C3"]), "pass")  # White, behind by 15.5
    assert d["area_margin"][0] == -15.5


def test_diagnose_game_replays_histories():
    out = diagnose_game([([], "C3"), (["C3", "C2"], "B2")])
    assert [d["action"] for d in out] == ["C3", "B2"]
