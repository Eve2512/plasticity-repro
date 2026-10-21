import pytest

from harness.ledger import BudgetExceeded, Ledger
from harness.model import Usage
from plasticity.pricing import PriceTable

BILLING = PriceTable(1.0, 5.0, cached_input_per_mtok=0.1, cache_write_per_mtok=1.25)


def test_learning_cost_is_undiscounted_and_excludes_eval():
    ledger = Ledger(BILLING.undiscounted(), billing=BILLING)
    ledger.add(0, "train", "g1", Usage(1_000_000, 0, cached_input_tokens=900_000))
    ledger.add(0, "eval", "g2", Usage(1_000_000, 0))
    assert ledger.learning_cost() == pytest.approx(1.0)
    assert ledger.billed() == pytest.approx(0.1 + 0.09 + 1.0)


def test_cap_raises_once_reached():
    ledger = Ledger(BILLING.undiscounted(), billing=BILLING, cap=0.5)
    ledger.check_budget()
    ledger.add(0, "train", "g1", Usage(400_000, 20_000))
    with pytest.raises(BudgetExceeded):
        ledger.check_budget()


def test_reported_cost_overrides_estimate():
    ledger = Ledger(BILLING.undiscounted(), billing=BILLING)
    ledger.add(0, "train", "g1", Usage(1_000_000, 0, reported_cost=0.42))
    ledger.add(0, "train", "g2", Usage(1_000_000, 0))
    assert ledger.billed() == pytest.approx(0.42 + 1.0)
    assert ledger.learning_cost() == pytest.approx(2.0)  # learning cost still uses token prices


def test_unknown_phase_rejected():
    with pytest.raises(ValueError):
        Ledger(BILLING).add(0, "play", "g", Usage())
