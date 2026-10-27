"""Rule-based move diagnostics for Go reflection (Table 2, Appendix B).

For each actor move: stones captured, the largest capture that was available,
liberties of the moved group, self-atari, own and opponent stones left in
atari, avoidable passing while behind, and the change in area margin. All are
descriptive, from the rules alone; the paper gives the reflector no engine
evaluation and no expert severity label. The area margin counts every stone as
alive (the final result removes dead stones, so the two can differ).
Labels: "self_atari" and "pass_while_behind"; a move with a label is "flagged".
"""

from envs.go import GoState, other


def _in_atari(state: GoState, colour: str) -> int:
    """Stones of `colour` in groups with exactly one liberty."""
    seen: set[int] = set()
    count = 0
    for i, c in enumerate(state.cells):
        if c == colour and i not in seen:
            stones, libs = state.group(i)
            seen |= stones
            if len(libs) == 1:
                count += len(stones)
    return count


def _best_capture(state: GoState) -> int:
    """Most stones the side to move could capture with one move."""
    best = 0
    me = state.to_move
    for move in state.legal_indices()[:-1]:
        before = state.captures[me]
        state.play(move)
        best = max(best, state.captures[me] - before)
        state.undo()
    return best


def diagnose_move(before: GoState, action: str) -> dict:
    """Diagnostics for the side to move in `before` playing `action`."""
    state = before.copy()
    state.adjudicator = None
    me, opp = state.to_move, other(state.to_move)
    move = state.index(action)
    margin_before = state.area_margin(me)
    capture_available = _best_capture(state)
    could_play = len(state.legal_indices()) > 1
    captured_before = state.captures[me]
    state.play(move)
    labels = []
    liberties = None
    if move == state.pass_index:
        if margin_before < 0 and could_play:
            labels.append("pass_while_behind")
    else:
        liberties = len(state.group(move)[1])
        if liberties == 1:
            labels.append("self_atari")
    return {
        "action": action,
        "severity": "flagged" if labels else "ok",
        "labels": labels,
        "captured": state.captures[me] - captured_before,
        "largest_capture_available": capture_available,
        "liberties_after": liberties,
        "own_stones_in_atari": _in_atari(state, me),
        "opponent_stones_in_atari": _in_atari(state, opp),
        "area_margin": [margin_before, state.area_margin(me)],
    }


def diagnose_game(actor_moves_before) -> list[dict]:
    """`actor_moves_before`: (history before the move, action) pairs, in order."""
    out = []
    for history, action in actor_moves_before:
        s = GoState()
        for m in history:
            s.play(m)
        out.append(diagnose_move(s, action))
    return out

