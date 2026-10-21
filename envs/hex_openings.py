"""Fixed opening banks and opponent levels for Hex.

The paper starts red actors after a deterministic 10-ply opening and blue actors
after an 11-ply opening, from fixed banks (Appendix B). The banks themselves
are not published, so these are generated from seeds, kept disjoint across
splits, and filtered to positions where neither side is already close to winning.
"""

import random
from dataclasses import dataclass

from envs.hex import BLUE, RED, HexState
from envs.hex_engine import connection_distance

# Splits and their seeds. Seeds differ so the banks do not overlap.
SPLIT_SEEDS = {"train": 1001, "id": 2002, "ood": 3003}

# Opponent node budgets per move. The paper uses 10k-1M for train and ID and
# 10M for OOD; a pure-Python engine runs about 20-30k nodes per second, so these
# are scaled down. Calibration: reports/05_hex_engine_calibration.md.
TRAIN_ID_LEVELS = (3_000, 10_000, 30_000, 100_000)
OOD_LEVELS = (1_000_000,)


@dataclass(frozen=True)
class Opening:
    moves: tuple[str, ...]
    actor: str  # RED or BLUE: the side the actor plays

    @property
    def key(self) -> str:
        return " ".join(self.moves)

    def state(self) -> HexState:
        s = HexState()
        for m in self.moves:
            s.play(m)
        return s


def _balanced(state: HexState) -> bool:
    red, blue = connection_distance(state, RED), connection_distance(state, BLUE)
    return not state.is_over() and min(red, blue) >= 2 and abs(red - blue) <= 1


def opening_bank(split: str, actor: str, count: int, exclude: set[str] = frozenset()) -> list[Opening]:
    """`count` distinct balanced openings that leave `actor` to move."""
    plies = 10 if actor == RED else 11
    rng = random.Random(f"{SPLIT_SEEDS[split]}-{actor}")
    bank, seen = [], set(exclude)
    while len(bank) < count:
        s = HexState()
        for _ in range(plies):
            s.play(rng.choice(s.legal_indices()))
            if s.is_over():
                break
        if not _balanced(s):
            continue
        opening = Opening(tuple(s.name(i) for i in s.history), actor)
        if opening.key not in seen:
            seen.add(opening.key)
            bank.append(opening)
    return bank


def split_banks(games: dict[str, int]) -> dict[str, list[Opening]]:
    """Disjoint banks per split, half the games for each colour.

    `games` maps split name to games per checkpoint, e.g. the paper's
    {"train": 40, "id": 40, "ood": 32}.
    """
    used: set[str] = set()
    banks = {}
    for split, n in games.items():
        half = n // 2
        bank = opening_bank(split, RED, half, used) + opening_bank(split, BLUE, n - half, used)
        used |= {o.key for o in bank}
        banks[split] = bank
    return banks
