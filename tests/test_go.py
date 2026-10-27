import pytest

from envs.go import BLACK, WHITE, GoState


def board(moves, **kw):
    s = GoState(**kw)
    for m in moves:
        s.play(m)
    return s


def test_coordinates_round_trip_and_pass():
    s = GoState()
    assert s.index("A1") == 0 and s.index("e5") == 24 and s.index("PASS") == 25
    assert [s.name(i) for i in (0, 4, 20, 25)] == ["A1", "E1", "A5", "pass"]
    for bad in ("F1", "A6", "I3", "z"):
        with pytest.raises(ValueError):
            s.index(bad)


def test_capture_in_the_corner():
    s = board(["A2", "A1", "B1"])  # White's A1 has no liberties left
    assert s.cells[0] == "." and s.captures[BLACK] == 1


def test_suicide_is_illegal():
    s = board(["A2", "E5", "B1"])  # White to move; A1 has no liberties and captures nothing
    assert "A1" not in s.legal_actions()
    with pytest.raises(ValueError):
        s.play("A1")


def test_capture_that_looks_like_suicide_is_legal():
    # White A2 and B1 each have one liberty, A1. Black's A1 has no empty neighbour
    # but captures both, so it is legal.
    s = board(["A3", "A2", "B2", "B1", "C1", "pass"])
    assert "A1" in s.legal_actions()
    s.play("A1")
    assert s.cells[s.index("A2")] == s.cells[s.index("B1")] == "." and s.captures[BLACK] == 2


def test_ko_recapture_is_refused():
    # Black B3 A2 B1 surround White B2; White C3 C1 D2 surround C2. Black C2 takes B2.
    moves = ["B3", "C3", "A2", "C1", "B1", "D2", "pass", "B2", "C2"]  # Black C2 captures White B2
    s = board(moves)
    assert s.cells[s.index("B2")] == "." and s.captures[BLACK] == 1
    # White would recapture at B2 (capturing C2) and recreate the position before Black's C2.
    assert "B2" not in s.legal_actions()
    s.play("E5")  # a ko threat elsewhere
    s.play("E4")
    assert "B2" in s.legal_actions()  # the board differs now, so the recapture is legal


def test_two_passes_end_the_game():
    s = board(["C3", "pass"])
    assert not s.is_over()
    s.play("pass")
    assert s.is_over() and s.legal_actions() == []
    with pytest.raises(ValueError):
        s.play("A1")


def test_action_cap_ends_the_game():
    s = GoState(max_actions=4)
    for m in ["C3", "C2", "B3", "pass"]:
        s.play(m)
    assert s.is_over()


def test_area_scoring_with_komi():
    s = board(["C3", "pass", "pass"])  # one black stone owns the whole board
    assert s.area() == {BLACK: 25, WHITE: 0}
    assert s.area_margin(BLACK) == 25 - 9.5
    assert s.winner() == BLACK
    empty = board(["pass", "pass"])  # nobody owns anything: komi decides
    assert empty.area_margin(BLACK) == -9.5 and empty.winner() == WHITE


def test_shared_region_is_neutral():
    s = board(["A3", "E3", "pass", "pass"])
    assert s.area() == {BLACK: 1, WHITE: 1}


def test_adjudicator_decides_finished_games_only():
    s = GoState(adjudicator=lambda st: 3.0)
    s.play("C3")
    assert s.winner() is None
    s.play("pass")
    s.play("pass")
    assert s.final_margin() == 3.0 and s.winner() == BLACK


def test_undo_restores_everything():
    s = board(["A2", "A1"])
    before = (s.cells.copy(), s.to_move, dict(s.captures), dict(s._seen), s.passes)
    s.play("B1")  # captures A1
    s.undo()
    assert (s.cells, s.to_move, s.captures, s._seen, s.passes) == before
    s.play("pass")
    s.undo()
    assert s.passes == 0 and s.to_move == BLACK


def test_copy_is_independent():
    s = board(["C3"])
    c = s.copy()
    c.play("C2")
    assert s.history == [s.index("C3")] and s.to_move == WHITE


def test_legal_actions_put_pass_last():
    assert GoState().legal_actions()[0] == "A1"
    assert GoState().legal_actions()[-1] == "pass"
