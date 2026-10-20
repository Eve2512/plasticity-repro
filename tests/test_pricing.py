import pytest

from plasticity.pricing import PriceTable


def test_undiscounted_bills_cached_tokens_as_input():
    table = PriceTable(3.0, 15.0)
    assert table.cost(1_000_000, 100_000, cached_input_tokens=900_000) == pytest.approx(4.5)


def test_cache_discount_applies_to_cached_part_only():
    table = PriceTable(3.0, 15.0, cached_input_per_mtok=0.3)
    # 0.1M fresh x $3 + 0.9M cached x $0.3 + 0.1M output x $15
    assert table.cost(1_000_000, 100_000, cached_input_tokens=900_000) == pytest.approx(2.07)


def test_rejects_more_cached_than_input():
    with pytest.raises(ValueError):
        PriceTable(1.0, 1.0).cost(10, 0, cached_input_tokens=20)
