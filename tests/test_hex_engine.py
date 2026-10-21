from envs.hex import BLUE, RED, HexState
from envs.hex_engine import AlphaBetaEngine, connection_distance, evaluate


def position(moves):
    s = HexState()
    for m in moves:
        s.play(m)
    return s


def test_distance_on_empty_board_is_board_size():
    s = HexState()
    assert connection_distance(s, RED) == 6
    assert connection_distance(s, BLUE) == 6


def test_distance_counts_only_missing_cells():
    s = position(["c1", "a1", "c2", "a2", "c3", "a3"])  # red column c1-c3
    assert connection_distance(s, RED) == 3


def test_evaluate_is_from_side_to_move():
    s = position(["c1", "a1", "c2", "a2", "c3"])  # blue to move, red is closer
    assert evaluate(s) < 0


def test_takes_immediate_win():
    s = position(["c1", "a1", "c2", "a2", "c3", "a3", "c4", "a4", "c5", "a5"])
    assert AlphaBetaEngine(2_000).choose(s) == "c6"


def test_blocks_immediate_loss():
    # Red threatens c6; blue to move must block it.
    s = position(["c1", "a1", "c2", "a2", "c3", "a3", "c4", "b6", "c5"])
    assert AlphaBetaEngine(5_000).choose(s) == "c6"


def test_deterministic_for_same_budget():
    s = position(["c3", "d3", "c4"])
    assert AlphaBetaEngine(3_000).choose(s) == AlphaBetaEngine(3_000).choose(s)


def test_respects_node_budget_after_depth_one():
    engine = AlphaBetaEngine(500)
    engine.choose(HexState())
    assert engine.last_depth >= 1
    assert engine.nodes <= 500 + 1
