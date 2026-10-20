import numpy as np
import pytest

from plasticity.fit import SaturationFit, fit_saturation


def test_predict_starts_at_s0_and_hits_half_rise_at_c50():
    fit = SaturationFit(s0=0.2, rise=0.5, c50=100.0, h=2.0, nll=0.0)
    assert fit.predict(0.0) == pytest.approx(0.2)
    assert fit.predict(100.0) == pytest.approx(0.45)


def test_cost_at_fraction_inverts_the_curve():
    fit = SaturationFit(s0=0.1, rise=0.6, c50=250.0, h=1.7, nll=0.0)
    c90 = fit.cost_at_fraction(0.9)
    assert fit.rise_fraction(c90) == pytest.approx(0.9)


def test_fit_recovers_noise_free_curve():
    truth = SaturationFit(s0=0.25, rise=0.5, c50=300.0, h=2.0, nll=0.0)
    costs = np.linspace(0, 2000, 21)
    games = 10_000  # large n makes the observed rates almost exact
    points = truth.predict(costs) * games
    fit = fit_saturation(costs, points, games)
    assert fit.s0 == pytest.approx(0.25, abs=0.01)
    assert fit.rise == pytest.approx(0.5, abs=0.01)
    assert fit.c50 == pytest.approx(300.0, rel=0.05)
    assert fit.h == pytest.approx(2.0, rel=0.1)


def test_fit_keeps_score_inside_unit_interval():
    costs = np.linspace(0, 1000, 11)
    points = np.array([0, 2, 6, 10, 12, 12, 12, 12, 12, 12, 12], dtype=float)
    fit = fit_saturation(costs, points, 12)
    assert 0.0 <= fit.s0 <= fit.s0 + fit.rise <= 1.0


def test_fit_flat_curve_has_small_rise():
    costs = np.linspace(0, 1000, 11)
    points = np.full(11, 6.0)
    fit = fit_saturation(costs, points, 12)
    assert fit.rise < 0.05


def test_fit_needs_two_positive_costs():
    with pytest.raises(ValueError):
        fit_saturation([0.0, 10.0], [1.0, 2.0], 4)
