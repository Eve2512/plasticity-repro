import numpy as np

from plasticity.bootstrap import bootstrap_psat
from plasticity.fit import SaturationFit
from plasticity.psat import plasticity_to_saturation

COSTS = np.linspace(0, 1000, 11)


def test_interval_contains_point_estimate():
    fit = SaturationFit(s0=0.2, rise=0.5, c50=150.0, h=2.0, nll=0.0)
    point = plasticity_to_saturation(fit, COSTS).value
    res = bootstrap_psat(fit, COSTS, 40, n_boot=60, seed=1)
    assert res.low <= point <= res.high
    assert sum(res.kinds.values()) == 60


def test_more_games_give_narrower_interval():
    fit = SaturationFit(s0=0.2, rise=0.5, c50=150.0, h=2.0, nll=0.0)
    few = bootstrap_psat(fit, COSTS, 12, n_boot=60, seed=2)
    many = bootstrap_psat(fit, COSTS, 200, n_boot=60, seed=2)
    assert (many.high - many.low) < (few.high - few.low)


def test_same_seed_is_reproducible():
    fit = SaturationFit(s0=0.3, rise=0.4, c50=200.0, h=1.5, nll=0.0)
    a = bootstrap_psat(fit, COSTS, 20, n_boot=20, seed=7)
    b = bootstrap_psat(fit, COSTS, 20, n_boot=20, seed=7)
    np.testing.assert_array_equal(a.estimates, b.estimates)
