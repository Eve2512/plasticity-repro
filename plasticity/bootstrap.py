"""Parametric bootstrap intervals for P_sat (Section 2.2)."""

from collections import Counter
from dataclasses import dataclass

import numpy as np

from plasticity.fit import SaturationFit, fit_saturation
from plasticity.psat import plasticity_to_saturation


@dataclass(frozen=True)
class BootstrapResult:
    estimates: np.ndarray  # P_sat of every resample
    low: float
    high: float
    kinds: dict[str, int]  # how often each P_sat rule applied


def bootstrap_psat(
    fit: SaturationFit,
    costs,
    games,
    *,
    n_boot: int = 500,
    level: float = 0.95,
    seed: int = 0,
    **psat_kwargs,
) -> BootstrapResult:
    """Resample scores from the fitted curve, refit, and recompute P_sat.

    Each checkpoint's points are drawn as Binomial(games, S_hat(C)). Draws are
    not modelled separately, so chess games with many draws get slightly wider
    intervals than they would with a trinomial model.
    """
    rng = np.random.default_rng(seed)
    costs = np.asarray(costs, dtype=float)
    games = np.broadcast_to(np.asarray(games, dtype=int), costs.shape)
    p_hat = np.clip(fit.predict(costs), 0.0, 1.0)

    values, kinds = [], Counter()
    for _ in range(n_boot):
        points = rng.binomial(games, p_hat)
        res = plasticity_to_saturation(fit_saturation(costs, points, games), costs, **psat_kwargs)
        values.append(res.value)
        kinds[res.kind] += 1

    values = np.array(values)
    tail = 100.0 * (1.0 - level) / 2.0
    low, high = np.percentile(values, [tail, 100.0 - tail])
    return BootstrapResult(values, float(low), float(high), dict(kinds))
