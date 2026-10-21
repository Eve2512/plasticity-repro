import pytest

from envs.hex import BLUE, RED, HexState


def test_coordinates_round_trip():
    s = HexState()
    for i in range(36):
        assert s.index(s.name(i)) == i
    assert s.name(0) == "a1" and s.name(35) == "f6"


def test_rejects_bad_coordinates():
    s = HexState()
    for bad in ("g1", "a7", "a0", "1a", "", "zz"):
        with pytest.raises(ValueError):
            s.index(bad)


def test_corner_neighbours():
    s = HexState()
    assert sorted(s.name(i) for i in s.neighbours(s.index("a1"))) == ["a2", "b1"]
    assert sorted(s.name(i) for i in s.neighbours(s.index("f1"))) == ["e1", "e2", "f2"]
    assert len(s.neighbours(s.index("c3"))) == 6


def play_line(s, red, blue):
    for r, b in zip(red, blue):
        s.play(r)
        if s.is_over():
            return
        s.play(b)


def test_red_wins_north_to_south():
    s = HexState()
    play_line(s, ["c1", "c2", "c3", "c4", "c5", "c6"], ["a1", "a2", "a3", "a4", "a5", "a6"])
    assert s.winner() == RED


def test_blue_wins_west_to_east():
    s = HexState()
    play_line(s, ["a1", "b1", "c1", "d1", "a3", "f6"], ["a2", "b2", "c2", "d2", "e2", "f2"])
    assert s.winner() == BLUE


def test_diagonal_neighbour_connects_but_other_diagonal_does_not():
    # In this layout b1 touches a2 (row+1, col-1) but not c2.
    s = HexState()
    assert s.index("a2") in s.neighbours(s.index("b1"))
    assert s.index("c2") not in s.neighbours(s.index("b1"))


def test_illegal_moves_and_game_over():
    s = HexState()
    s.play("a1")
    with pytest.raises(ValueError):
        s.play("a1")
    s.undo()
    play_line(s, ["a1", "a2", "a3", "a4", "a5", "a6"], ["b1", "b2", "b3", "b4", "b5", "c1"])
    assert s.winner() == RED
    assert s.legal_actions() == []
    with pytest.raises(ValueError):
        s.play("f1")


def test_undo_restores_turn_and_clears_winner():
    s = HexState()
    play_line(s, ["c1", "c2", "c3", "c4", "c5", "c6"], ["a1", "a2", "a3", "a4", "a5", "a6"])
    assert s.winner() == RED
    s.undo()
    assert s.winner() is None and s.to_move == RED
    assert "c6" in s.legal_actions()


def test_board_full_always_has_a_winner():
    import random

    for seed in range(20):
        rng = random.Random(seed)
        s = HexState()
        while not s.is_over():
            s.play(rng.choice(s.legal_indices()))
        assert s.winner() in (RED, BLUE)


def test_render_shape():
    lines = HexState().render().splitlines()
    assert len(lines) == 7 and lines[0].strip() == "a b c d e f"
