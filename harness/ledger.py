"""Token and cost ledger.

Learning cost (Eq. 2) counts the training games and reflection of each round,
including rejected reflection attempts. Held-out evaluation calls are recorded
but are not learning cost.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from harness.model import Usage
from plasticity.pricing import PriceTable

LEARNING_PHASES = ("train", "reflect")


@dataclass(frozen=True)
class Entry:
    checkpoint: int
    phase: str  # train | reflect | eval
    episode: str  # game id or reflection attempt id
    input_tokens: int
    output_tokens: int
    cached_input_tokens: int


class Ledger:
    def __init__(self, prices: PriceTable, path=None):
        self.prices = prices
        self.entries: list[Entry] = []
        self.path = Path(path) if path else None

    def add(self, checkpoint: int, phase: str, episode: str, usage: Usage) -> None:
        if phase not in ("train", "reflect", "eval"):
            raise ValueError(f"unknown phase {phase!r}")
        entry = Entry(checkpoint, phase, episode, usage.input_tokens, usage.output_tokens, usage.cached_input_tokens)
        self.entries.append(entry)
        if self.path:
            with self.path.open("a") as fh:
                fh.write(json.dumps(asdict(entry)) + "\n")

    def cost(self, entries=None) -> float:
        return sum(
            self.prices.cost(e.input_tokens, e.output_tokens, e.cached_input_tokens)
            for e in (self.entries if entries is None else entries)
        )

    def round_cost(self, checkpoint: int, phase: str) -> float:
        return self.cost([e for e in self.entries if e.checkpoint == checkpoint and e.phase == phase])

    def total_cost(self) -> float:
        return self.cost()

    def learning_cost(self) -> float:
        return self.cost([e for e in self.entries if e.phase in LEARNING_PHASES])
