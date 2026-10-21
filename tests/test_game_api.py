import pytest

from envs.hex import BLUE, RED
from envs.hex_openings import opening_bank
from harness.game_api import HexGameSession


def session(actor=RED):
    opening = opening_bank("train", actor, 1)[0]
    return HexGameSession(opening, lambda s: s.legal_actions()[0])


def test_analysis_moves_do_not_touch_real_board():
    g = session()
    real_moves = g.get_state()["moves"]
    move = g.get_legal_actions()[0]
    assert g.apply_action(move)["analysis_depth"] == 1
    assert g.current_player() == BLUE
    assert g.undo_action()["ok"]
    assert g.get_state()["moves"] == real_moves
    assert not g.undo_action()["ok"]  # cannot undo past the real position


def test_submit_plays_opponent_reply_and_resets_analysis():
    g = session()
    g.apply_action(g.get_legal_actions()[0])
    move = g.get_legal_actions()[-1]
    g.undo_action()
    res = g.submit_action(move)
    assert res["accepted"] and res["submitted_action"] == move
    assert res["opponent_action"] is not None
    assert g.get_state()["analysis_depth"] == 0
    assert g.current_player() == RED
    assert g.log[0].action == move


def test_illegal_submission_is_rejected_not_forfeited():
    g = session()
    taken = g.get_state()["moves"][0]
    res = g.submit_action(taken)
    assert not res["accepted"]
    assert g.invalid_submissions == 1 and not g.done


def test_dispatch_allows_only_api_methods():
    g = session(BLUE)
    assert g.dispatch("current_player", []) == BLUE
    with pytest.raises(ValueError):
        g.dispatch("__init__", [])
    with pytest.raises(ValueError):
        g.dispatch("real", [])


def test_game_ends_with_a_winner():
    g = session()
    while not g.done:
        g.submit_action(g.get_legal_actions()[0])
    assert g.real.winner() in (RED, BLUE)
    assert not g.submit_action("a1")["accepted"]
