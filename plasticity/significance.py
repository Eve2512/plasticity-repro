"""Likelihood-ratio test of a rise against a flat curve.

The paper reports a p-value for NetHack (Appendix C) but does not name the test.
This is one candidate: the flat model fits one rate to all checkpoints, and
2 x (NLL_flat - NLL_saturation) is compared to chi-square with 3 degrees of
freedom (A, C50 and h). Under the flat null, C50 and h are not identified and A
sits on its boundary, so the chi-square reference is only an approximation;
scripts/fit_sensitivity.py measures its actual false-alarm rate.
"""

import numpy as np
from scipy.stats import chi2

from plasticity.fit import SaturationFit

_P_CLIP = 1e-6


def flat_nll(points, games) -> float:
    points = np.asarray(points, dtype=float)
    games = np.broadcast_to(np.asarray(games, dtype=float), points.shape)
    p = np.clip(points.sum() / games.sum(), _P_CLIP, 1.0 - _P_CLIP)
    return float(-np.sum(points * np.log(p) + (games - points) * np.log(1.0 - p)))


def rise_p_value(fit: SaturationFit, points, games, df: int = 3) -> float:
    stat = max(0.0, 2.0 * (flat_nll(points, games) - fit.nll))
    return float(chi2.sf(stat, df))
