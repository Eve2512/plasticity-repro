import numpy as np

from plasticity.fit import SaturationFit
from plasticity.synthetic import cost_schedule, simulate_lineage


def test_cost_schedule_is_cumulative_from_zero():
    c = cost_schedule(10, 100.0, rng=np.random.default_rng(3))
    assert c[0] == 0.0
    assert len(c) == 11
    assert np.all(np.diff(c) > 0)
    assert 800 <= c[-1] <= 1200


def test_simulated_points_stay_within_game_count():
    truth = SaturationFit(0.2, 0.6, 300.0, 2.0, 0.0)
    lin = simulate_lineage(truth, np.linspace(0, 1000, 11), 12, np.random.default_rng(0))
    assert lin.points.min() >= 0 and lin.points.max() <= 12
