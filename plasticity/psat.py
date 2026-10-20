"""Plasticity to estimated saturation (Eq. 5) and its fallback rules (Section 2.2)."""

from dataclasses import dataclass

import numpy as np

from plasticity.fit import SaturationFit
from plasticity.metrics import PER

# The kinds of result Eq. 5 and its rules can give.
SATURATED = "saturated"  # an observed checkpoint reaches q of the fitted rise
EXTRAPOLATED = "extrapolated"  # the q point lies within `extrapolate` x the final cost
TO_DATE = "to_date"  # saturation cannot be established; plasticity to date
NO_RISE = "no_rise"  # q x rise below min_rise_pp; P_sat = 0


@dataclass(frozen=True)
class PlasticityResult:
    value: float  # score points per `per` dollars
    kind: str
    c_star: float | None
    gain_pp: float


def plasticity_to_saturation(
    fit: SaturationFit,
    costs,
    *,
    q: float = 0.9,
    min_rise_pp: float = 10.0,
    extrapolate: float = 3.0,
    per: float = PER,
) -> PlasticityResult:
    """Eq. 5 with the paper's defaults: q = 0.9, 10 pp minimum, 3x extrapolation."""
    costs = np.sort(np.asarray(costs, dtype=float))
    if 100.0 * q * fit.rise < min_rise_pp:
        return PlasticityResult(0.0, NO_RISE, None, 0.0)

    observed = costs[costs > 0]
    reached = observed[fit.rise_fraction(observed) >= q - 1e-12]
    final = observed.max()
    if reached.size:
        c_star, kind = float(reached[0]), SATURATED
    else:
        c_q = fit.cost_at_fraction(q)
        if c_q <= extrapolate * final:
            c_star, kind = c_q, EXTRAPOLATED
        else:
            c_star, kind = float(final), TO_DATE

    gain_pp = 100.0 * float(fit.predict(c_star) - fit.s0)
    return PlasticityResult(per * gain_pp / c_star, kind, c_star, gain_pp)
