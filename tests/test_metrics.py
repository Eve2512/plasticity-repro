import math

import numpy as np
import pytest

from plasticity.metrics import average_plasticity, cumulative_cost, game_score


def test_game_score_counts_draws_as_half():
    assert game_score(4, 1, 12) == pytest.approx(37.5)


def test_game_score_rejects_impossible_counts():
    with pytest.raises(ValueError):
        game_score(10, 3, 12)


def test_cumulative_cost_starts_at_zero_and_excludes_current_round():
    c = cumulative_cost([1.0, 2.0, 3.0], [0.5, 0.5, 0.5])
    np.testing.assert_allclose(c, [0.0, 1.5, 4.0, 7.5])


def test_cumulative_cost_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        cumulative_cost([1.0], [1.0, 2.0])


def test_average_plasticity_per_thousand_dollars():
    # 30 pp gain for $600 = 50 pp per $1,000
    assert average_plasticity([20, 35, 50], [0, 300, 600]) == pytest.approx(50.0)


def test_average_plasticity_can_be_negative():
    assert average_plasticity([40, 30], [0, 500]) == pytest.approx(-20.0)


def test_average_plasticity_nan_at_zero_cost():
    assert math.isnan(average_plasticity([10, 20], [0, 300], t=0))
