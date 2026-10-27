import pytest

from envs.go import BLACK, GoState
from envs.go_engine import GnuGoEngine, available, gnugo_final_margin

pytestmark = pytest.mark.skipif(not available(), reason="gnugo not installed (brew install gnu-go)")


def test_engine_returns_a_legal_move_and_is_deterministic():
    s = GoState()
    s.play("C3")
    a, b = GnuGoEngine(5, seed=1).choose(s), GnuGoEngine(5, seed=1).choose(s)
    assert a == b and a in s.legal_actions()


def test_engine_replays_captures_and_passes():
    s = GoState()
    for m in ["A2", "A1", "B1", "pass", "C3"]:
        s.play(m)
    assert s.to_move == "O"
    assert GnuGoEngine(7).choose(s) in s.legal_actions()


def test_engine_refuses_finished_games():
    s = GoState()
    s.play("pass")
    s.play("pass")
    with pytest.raises(ValueError):
        GnuGoEngine(5).choose(s)


def test_final_score_matches_area_count_when_nothing_is_dead():
    s = GoState()
    for m in ["C3", "pass", "pass"]:
        s.play(m)
    assert gnugo_final_margin(s) == s.area_margin(BLACK) == 15.5


def test_final_score_removes_dead_stones():
    # A lone White stone inside Black's area is dead; the plain area count calls it alive.
    s = GoState()
    for m in ["C3", "A1", "B3", "pass", "D3", "pass", "pass"]:
        s.play(m)
    assert s.area_margin(BLACK) < gnugo_final_margin(s) == 15.5


def test_engine_plays_a_whole_game_against_itself():
    s = GoState(adjudicator=gnugo_final_margin)
    black, white = GnuGoEngine(10, 0), GnuGoEngine(5, 0)
    while not s.is_over():
        s.play((black if s.to_move == BLACK else white).choose(s.copy()))
    assert s.winner() == BLACK  # 5x5 Go from the empty board is a Black win
