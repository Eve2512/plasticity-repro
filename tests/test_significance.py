import numpy as np

from plasticity.fit import fit_saturation
from plasticity.significance import flat_nll, rise_p_value

COSTS = np.linspace(0, 1000, 11)


def test_clear_rise_is_significant():
    points = np.array([2, 4, 8, 12, 15, 17, 18, 18, 19, 18, 19], dtype=float)
    fit = fit_saturation(COSTS, points, 20)
    assert rise_p_value(fit, points, 20) < 0.001


def test_flat_curve_is_not_significant():
    points = np.full(11, 7.0)
    fit = fit_saturation(COSTS, points, 20)
    assert rise_p_value(fit, points, 20) > 0.5


def test_flat_nll_is_never_below_saturation_nll():
    rng = np.random.default_rng(0)
    for _ in range(5):
        points = rng.binomial(12, 0.4, 11).astype(float)
        fit = fit_saturation(COSTS, points, 12)
        assert flat_nll(points, 12) >= fit.nll - 1e-6
