from envs.hex import HexState
from envs.hex_feedback import diagnose_move, winning_moves


def position(moves):
    s = HexState()
    for m in moves:
        s.play(m)
    return s


RED_THREAT = ["c1", "a1", "c2", "a2", "c3", "a3", "c4", "a4", "c5", "b6"]  # red to play c6 wins


def test_winning_moves_found():
    s = position(RED_THREAT)
    assert [s.name(i) for i in winning_moves(s)] == ["c6"]


def test_missed_win_is_a_blunder():
    d = diagnose_move(position(RED_THREAT), "f1")
    assert "missed_immediate_win" in d["labels"] and d["severity"] == "blunder"


def test_taking_the_win_is_ok():
    d = diagnose_move(position(RED_THREAT), "c6")
    assert d["severity"] == "ok" and d["own_distance"][1] == 0


def test_double_threat_is_not_preventable():
    s = position(RED_THREAT[:-1])  # blue to move; red threatens both b6 and c6
    assert diagnose_move(s, "c6")["labels"] == []


def test_failing_to_block_is_preventable_loss():
    s = position(["c1", "a1", "c2", "a2", "c3", "a3", "c4", "b6", "c5"])  # only c6 threatens
    d = diagnose_move(s, "f1")
    assert "preventable_immediate_loss" in d["labels"]
    assert d["opponent_wins_allowed"] == ["c6"]
    assert diagnose_move(s, "c6")["severity"] == "ok"


def test_quiet_move_reports_distances():
    d = diagnose_move(HexState(), "c3")
    assert d["severity"] == "ok"
    assert d["own_distance"] == [6, 5] and d["opponent_distance"] == [6, 6]
