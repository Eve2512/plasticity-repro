"""Synthetic learning curves with a known true saturation curve."""

from dataclasses import dataclass

import numpy as np

from plasticity.fit import SaturationFit
from plasticity.metrics import cumulative_cost


@dataclass(frozen=True)
class Lineage:
    costs: np.ndarray  # cumulative cost per checkpoint
    points: np.ndarray  # W + 0.5 D per checkpoint (here: wins only)
    games: int


def cost_schedule(rounds: int, cost_per_round: float, jitter: float = 0.2, rng=None) -> np.ndarray:
    """Cumulative costs for `rounds` learning rounds with +-jitter variation per round."""
    rng = rng or np.random.default_rng(0)
    per_round = cost_per_round * rng.uniform(1 - jitter, 1 + jitter, rounds)
    return cumulative_cost(per_round, np.zeros(rounds))


def simulate_lineage(truth: SaturationFit, costs, games: int, rng) -> Lineage:
    """Draw each checkpoint's points as Binomial(games, truth(C))."""
    costs = np.asarray(costs, dtype=float)
    points = rng.binomial(games, np.clip(truth.predict(costs), 0, 1)).astype(float)
    return Lineage(costs, points, games)
