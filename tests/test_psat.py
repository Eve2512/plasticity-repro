import numpy as np
import pytest

from plasticity.fit import SaturationFit
from plasticity.psat import (
    EXTRAPOLATED,
    NO_RISE,
    SATURATED,
    TO_DATE,
    plasticity_to_saturation,
)

COSTS = np.linspace(0, 1000, 11)  # checkpoints every $100


def fit_with(rise=0.5, c50=100.0, h=2.0):
    return SaturationFit(s0=0.2, rise=rise, c50=c50, h=h, nll=0.0)


def test_saturated_uses_first_checkpoint_past_ninety_percent():
    fit = fit_with()  # 90 % point is at 100 * 3 = $300
    res = plasticity_to_saturation(fit, COSTS)
    assert res.kind == SATURATED
    assert res.c_star == pytest.approx(300.0)
    assert res.gain_pp == pytest.approx(45.0)
    assert res.value == pytest.approx(150.0)  # 45 pp / $300 * $1,000


def test_small_rise_gives_zero():
    res = plasticity_to_saturation(fit_with(rise=0.11), COSTS)  # 0.9 * 11 pp < 10 pp
    assert res.kind == NO_RISE
    assert res.value == 0.0


def test_extrapolates_up_to_three_times_final_cost():
    fit = fit_with(c50=600.0, h=1.0)  # 90 % point at $5,400, beyond 3 x $1,000
    assert plasticity_to_saturation(fit, COSTS).kind == TO_DATE
    fit = fit_with(c50=250.0, h=1.0)  # 90 % point at $2,250, inside 3 x $1,000
    res = plasticity_to_saturation(fit, COSTS)
    assert res.kind == EXTRAPOLATED
    assert res.c_star == pytest.approx(2250.0)
    assert res.gain_pp == pytest.approx(45.0)


def test_to_date_uses_final_cost():
    fit = fit_with(c50=600.0, h=1.0)
    res = plasticity_to_saturation(fit, COSTS)
    expected_gain = 100 * 0.5 * 1000 / 1600
    assert res.c_star == pytest.approx(1000.0)
    assert res.gain_pp == pytest.approx(expected_gain)
    assert res.value == pytest.approx(expected_gain)


def test_rules_are_adjustable():
    fit = fit_with(rise=0.11)
    assert plasticity_to_saturation(fit, COSTS, min_rise_pp=5.0).kind == SATURATED
