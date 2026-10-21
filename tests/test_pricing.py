import pytest

from plasticity.pricing import PriceTable


def test_undiscounted_bills_cached_tokens_as_input():
    table = PriceTable(3.0, 15.0)
    assert table.cost(1_000_000, 100_000, cached_input_tokens=900_000) == pytest.approx(4.5)


def test_cache_discount_applies_to_cached_part_only():
    table = PriceTable(3.0, 15.0, cached_input_per_mtok=0.3)
    # 0.1M fresh x $3 + 0.9M cached x $0.3 + 0.1M output x $15
    assert table.cost(1_000_000, 100_000, cached_input_tokens=900_000) == pytest.approx(2.07)


def test_cache_writes_and_undiscounted_view():
    table = PriceTable(4.0, 20.0, cached_input_per_mtok=0.4, cache_write_per_mtok=5.0)
    # 0.2M fresh x $4 + 0.5M read x $0.4 + 0.3M write x $5 + 0.01M out x $20
    assert table.cost(1_000_000, 10_000, 500_000, 300_000) == pytest.approx(0.8 + 0.2 + 1.5 + 0.2)
    assert table.undiscounted().cost(1_000_000, 10_000, 500_000, 300_000) == pytest.approx(4.2)


def test_long_context_rates_apply_above_threshold():
    table = PriceTable(0.1, 0.5, long_context=(100_000, 0.5, 2.5))
    assert table.cost(100_000, 0) == pytest.approx(0.01)
    assert table.cost(200_000, 1_000_000) == pytest.approx(0.1 + 2.5)


def test_rejects_more_cached_than_input():
    with pytest.raises(ValueError):
        PriceTable(1.0, 1.0).cost(10, 0, cached_input_tokens=20)
