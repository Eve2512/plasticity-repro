"""Game score, cumulative learning cost (Eq. 2) and average plasticity (Eq. 3)."""

import numpy as np

PER = 1000.0  # the paper reports plasticity per $1,000


def game_score(wins: float, draws: float, games: int) -> float:
    """Score in [0, 100]: 100 (W + 0.5 D) / N. Unfinished games count as losses."""
    if games <= 0:
        raise ValueError("games must be positive")
    if wins < 0 or draws < 0 or wins + draws > games:
        raise ValueError("need 0 <= wins + draws <= games")
    return 100.0 * (wins + 0.5 * draws) / games


def cumulative_cost(train_costs, reflect_costs) -> np.ndarray:
    """Eq. 2: C_0 = 0 and C_t = sum over u < t of (train_u + reflect_u).

    Inputs have one entry per learning round u = 0..T-1. The result has T + 1
    entries, one per checkpoint 0..T.
    """
    train = np.asarray(train_costs, dtype=float)
    reflect = np.asarray(reflect_costs, dtype=float)
    if train.shape != reflect.shape or train.ndim != 1:
        raise ValueError("train_costs and reflect_costs must be 1-D and the same length")
    if (train < 0).any() or (reflect < 0).any():
        raise ValueError("costs must be non-negative")
    return np.concatenate([[0.0], np.cumsum(train + reflect)])


def average_plasticity(scores, costs, t: int | None = None, per: float = PER) -> float:
    """Eq. 3: (S_T - S_0) / C_T, in score points per `per` dollars.

    `t` defaults to the last checkpoint. Returns nan when C_T is zero.
    """
    s = np.asarray(scores, dtype=float)
    c = np.asarray(costs, dtype=float)
    if s.shape != c.shape:
        raise ValueError("scores and costs must be the same length")
    t = len(s) - 1 if t is None else t
    if c[t] == 0:
        return float("nan")
    return per * (s[t] - s[0]) / c[t]
