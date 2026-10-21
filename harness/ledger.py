"""Token and cost ledger.

Learning cost (Eq. 2) counts the training games and reflection of each round,
including rejected reflection attempts. Held-out evaluation calls are recorded
but are not learning cost. Learning cost uses `prices` (undiscounted, as in the
paper); the spending cap uses `billing` (with cache rates), which is what the
provider charges.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from harness.model import Usage
from plasticity.pricing import PriceTable

LEARNING_PHASES = ("train", "reflect")


class BudgetExceeded(RuntimeError):
    pass


@dataclass(frozen=True)
class Entry:
    checkpoint: int
    phase: str  # train | reflect | eval
    episode: str  # game id or reflection attempt id
    input_tokens: int
    output_tokens: int
    cached_input_tokens: int
    cache_write_tokens: int = 0


class Ledger:
    def __init__(self, prices: PriceTable, path=None, billing: PriceTable | None = None, cap: float | None = None):
        self.prices = prices
        self.billing = billing or prices
        self.cap = cap
        self.entries: list[Entry] = []
        self.path = Path(path) if path else None

    def add(self, checkpoint: int, phase: str, episode: str, usage: Usage) -> None:
        if phase not in ("train", "reflect", "eval"):
            raise ValueError(f"unknown phase {phase!r}")
        entry = Entry(
            checkpoint, phase, episode, usage.input_tokens, usage.output_tokens,
            usage.cached_input_tokens, usage.cache_write_tokens,
        )
        self.entries.append(entry)
        if self.path:
            with self.path.open("a") as fh:
                fh.write(json.dumps(asdict(entry)) + "\n")

    @staticmethod
    def _sum(table: PriceTable, entries) -> float:
        return sum(
            table.cost(e.input_tokens, e.output_tokens, e.cached_input_tokens, e.cache_write_tokens)
            for e in entries
        )

    def cost(self, entries=None) -> float:
        return self._sum(self.prices, self.entries if entries is None else entries)

    def round_cost(self, checkpoint: int, phase: str) -> float:
        return self.cost([e for e in self.entries if e.checkpoint == checkpoint and e.phase == phase])

    def total_cost(self) -> float:
        return self.cost()

    def learning_cost(self) -> float:
        return self.cost([e for e in self.entries if e.phase in LEARNING_PHASES])

    def billed(self) -> float:
        return self._sum(self.billing, self.entries)

    def check_budget(self) -> None:
        """Raise before a model call once billed spend has reached the cap."""
        if self.cap is not None and self.billed() >= self.cap:
            raise BudgetExceeded(f"spent ${self.billed():.2f} of the ${self.cap:.2f} cap")
