"""Saturation curve (Eq. 4) fitted by binomial maximum likelihood.

S(C) = S0 + A C^h / (C^h + C50^h). Scores are fractions in [0, 1] here; the
paper's percentage points are 100 times these values.
"""

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, logit

_P_CLIP = 1e-6
_LOG_H_BOUNDS = (np.log(0.2), np.log(10.0))


@dataclass(frozen=True)
class SaturationFit:
    s0: float  # initial score, fraction
    rise: float  # A, fraction; S0 + A <= 1
    c50: float  # cost at half of the rise
    h: float  # shape
    nll: float  # negative log-likelihood at the optimum

    def rise_fraction(self, cost) -> np.ndarray:
        """Share of the rise reached at `cost`: C^h / (C^h + C50^h)."""
        c = np.asarray(cost, dtype=float)
        with np.errstate(divide="ignore", over="ignore"):
            ratio = np.power(self.c50 / c, self.h)
        return np.where(c > 0, 1.0 / (1.0 + ratio), 0.0)

    def predict(self, cost) -> np.ndarray:
        return self.s0 + self.rise * self.rise_fraction(cost)

    def cost_at_fraction(self, q: float) -> float:
        """Cost at which the fit reaches share q of its rise."""
        return self.c50 * (q / (1.0 - q)) ** (1.0 / self.h)


def _unpack(theta):
    s0 = expit(theta[0])
    rise = (1.0 - s0) * expit(theta[1])
    return s0, rise, np.exp(theta[2]), np.exp(theta[3])


def _nll(theta, costs, points, games):
    s0, rise, c50, h = _unpack(theta)
    fit = SaturationFit(s0, rise, c50, h, 0.0)
    p = np.clip(fit.predict(costs), _P_CLIP, 1.0 - _P_CLIP)
    return -np.sum(points * np.log(p) + (games - points) * np.log(1.0 - p))


def fit_saturation(costs, points, games) -> SaturationFit:
    """Fit Eq. 4 to one learning curve.

    costs:  cumulative learning cost per checkpoint (checkpoint 0 has cost 0)
    points: W + 0.5 D per checkpoint (may be fractional)
    games:  games played per checkpoint
    """
    costs = np.asarray(costs, dtype=float)
    points = np.asarray(points, dtype=float)
    games = np.broadcast_to(np.asarray(games, dtype=float), costs.shape)
    if not (costs.shape == points.shape and costs.ndim == 1):
        raise ValueError("costs and points must be 1-D and the same length")
    positive = costs[costs > 0]
    if positive.size < 2:
        raise ValueError("need at least two checkpoints with positive cost")

    log_c50_bounds = (np.log(positive.min() / 100.0), np.log(positive.max() * 100.0))
    bounds = [(-12.0, 12.0), (-12.0, 12.0), log_c50_bounds, _LOG_H_BOUNDS]

    first = np.clip(points[0] / games[0], 0.02, 0.98)
    rates = points / games
    gain = np.clip((rates.max() - first) / (1.0 - first), 0.02, 0.98)
    best = None
    for b0 in (logit(gain), 0.0, -3.0):
        for c0 in np.quantile(positive, [0.1, 0.4, 0.8]):
            for h0 in (0.7, 1.5, 3.0):
                x0 = [logit(first), b0, np.log(c0), np.log(h0)]
                res = minimize(
                    _nll, x0, args=(costs, points, games), method="L-BFGS-B", bounds=bounds
                )
                if best is None or res.fun < best.fun:
                    best = res
    s0, rise, c50, h = _unpack(best.x)
    return SaturationFit(float(s0), float(rise), float(c50), float(h), float(best.fun))
