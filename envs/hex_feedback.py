"""Rule-based move diagnostics for Hex reflection (Table 2).

For each actor move: missed immediate wins, preventable immediate losses
(both count as blunders), and the change in own and opponent connection
distance. No engine evaluation is given to the reflector, as in the paper.
"""

from envs.hex import HexState, other
from envs.hex_engine import connection_distance


def winning_moves(state: HexState) -> list[int]:
    """Moves that win at once for the side to move."""
    wins = []
    for move in state.legal_indices():
        state.play(move)
        if state.winner():
            wins.append(move)
        state.undo()
    return wins


def _safe_moves(state: HexState) -> list[int]:
    """Moves after which the opponent has no immediate win."""
    safe = []
    for move in state.legal_indices():
        state.play(move)
        if state.winner() or not winning_moves(state):
            safe.append(move)
        state.undo()
    return safe


def diagnose_move(before: HexState, action: str) -> dict:
    """Diagnostics for the side to move in `before` playing `action`."""
    state = before.copy()
    me, opp = state.to_move, other(state.to_move)
    move = state.index(action)
    own_before, opp_before = connection_distance(state, me), connection_distance(state, opp)
    wins = winning_moves(state)
    safe = _safe_moves(state) if not wins else []
    state.play(move)
    allowed = [] if state.winner() else winning_moves(state)
    labels = []
    if wins and move not in wins:
        labels.append("missed_immediate_win")
    if allowed and safe:
        labels.append("preventable_immediate_loss")
    return {
        "action": action,
        "severity": "blunder" if labels else "ok",
        "labels": labels,
        "winning_moves_available": [state.name(i) for i in wins],
        "opponent_wins_allowed": [state.name(i) for i in allowed],
        "own_distance": [own_before, connection_distance(state, me)],
        "opponent_distance": [opp_before, connection_distance(state, opp)],
    }


def diagnose_game(actor_moves_before) -> list[dict]:
    """`actor_moves_before`: (history before the move, action) pairs, in order."""
    out = []
    for history, action in actor_moves_before:
        s = HexState()
        for m in history:
            s.play(m)
        out.append(diagnose_move(s, action))
    return out
