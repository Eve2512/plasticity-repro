"""Fixed opening banks and opponent levels for Hex.

The paper starts red actors after a deterministic 10-ply opening and blue actors
after an 11-ply opening, from fixed banks (Appendix B). The banks are not
published. Two kinds of bank are available here:

- "legacy": random 10/11-ply openings from seeds, filtered to balanced positions.
  Used by the smoke run (reports 07 and 08). Those games were short (2-7 actor
  moves) and blue openings were much harder (a strong engine won 2/5 as blue).
- "contested" (default): 4/5-ply openings kept only if a weak player (always the
  first legal action) loses from them and a reference engine wins from them,
  against the weakest train opponent. Every kept opening has room to improve,
  for both colours. Built once by scripts/build_hex_openings.py into BANK_FILE.
"""

import json
import random
from dataclasses import dataclass
from pathlib import Path

from envs.hex import BLUE, RED, HexState
from envs.hex_engine import AlphaBetaEngine, connection_distance

# Splits and their seeds. Seeds differ so the banks do not overlap.
SPLIT_SEEDS = {"train": 1001, "id": 2002, "ood": 3003}

# Opponent node budgets per move. The paper uses 10k-1M for train and ID and
# 10M for OOD; a pure-Python engine runs about 20-30k nodes per second, so these
# are scaled down. Calibration: reports/05_hex_engine_calibration.md.
TRAIN_ID_LEVELS = (3_000, 10_000, 30_000, 100_000)
OOD_LEVELS = (1_000_000,)

PAPER_PLIES = {RED: 10, BLUE: 11}
SHORT_PLIES = {RED: 4, BLUE: 5}
REFERENCE_NODES = 30_000  # the engine that must win a contested opening
BANK_FILE = Path(__file__).resolve().parent.parent / "data" / "hex_openings_contested.json"


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


def _candidates(split: str, actor: str, plies: int, tag: str = ""):
    """Endless stream of balanced random openings that leave `actor` to move."""
    rng = random.Random(f"{SPLIT_SEEDS[split]}-{actor}{tag}")
    while True:
        s = HexState()
        for _ in range(plies):
            s.play(rng.choice(s.legal_indices()))
            if s.is_over():
                break
        if _balanced(s):
            yield Opening(tuple(s.name(i) for i in s.history), actor)


def opening_bank(split: str, actor: str, count: int, exclude: set[str] = frozenset()) -> list[Opening]:
    """Legacy bank: `count` distinct balanced 10/11-ply openings."""
    bank, seen = [], set(exclude)
    for opening in _candidates(split, actor, PAPER_PLIES[actor]):
        if len(bank) == count:
            break
        if opening.key not in seen:
            seen.add(opening.key)
            bank.append(opening)
    return bank


def _actor_wins(opening: Opening, actor_choose, opponent_choose) -> bool:
    state = opening.state()
    while not state.is_over():
        mover = actor_choose if state.to_move == opening.actor else opponent_choose
        state.play(mover(state.copy()))
    return state.winner() == opening.actor


def is_contested(opening: Opening, opponent_nodes: int = TRAIN_ID_LEVELS[0],
                 reference_nodes: int = REFERENCE_NODES) -> bool:
    """A weak player loses from here and the reference engine wins from here."""
    opponent = AlphaBetaEngine(opponent_nodes).choose
    if _actor_wins(opening, lambda s: s.legal_actions()[0], opponent):
        return False
    return _actor_wins(opening, AlphaBetaEngine(reference_nodes).choose, opponent)


def build_contested_banks(games: dict[str, int], plies=SHORT_PLIES, progress=None) -> dict:
    """Disjoint contested banks: per split, half the games red and half blue."""
    used: set[str] = set()
    banks: dict[str, dict[str, list[list[str]]]] = {}
    tried = 0
    for split, n in games.items():
        banks[split] = {}
        for actor, count in ((RED, n // 2), (BLUE, n - n // 2)):
            kept = []
            for opening in _candidates(split, actor, plies[actor], tag="-contested"):
                if len(kept) == count:
                    break
                if opening.key in used:
                    continue
                tried += 1
                if is_contested(opening):
                    used.add(opening.key)
                    kept.append(list(opening.moves))
                    if progress:
                        progress(split, actor, len(kept), count, tried)
            banks[split][actor] = kept
    return {
        "version": 1,
        "plies": plies,
        "rule": f"first-legal player loses and {REFERENCE_NODES:,}-node engine wins, "
                f"vs the {TRAIN_ID_LEVELS[0]:,}-node opponent",
        "candidates_tried": tried,
        "banks": banks,
    }


def split_banks(games: dict[str, int], source: str = "contested", bank_file: Path = BANK_FILE) -> dict[str, list[Opening]]:
    """Openings per split, half the games for each colour (red first).

    `games` maps split name to games per checkpoint, e.g. the paper's
    {"train": 40, "id": 40, "ood": 32}.
    """
    if source == "legacy":
        used: set[str] = set()
        out = {}
        for split, n in games.items():
            half = n // 2
            bank = opening_bank(split, RED, half, used) + opening_bank(split, BLUE, n - half, used)
            used |= {o.key for o in bank}
            out[split] = bank
        return out
    if source != "contested":
        raise ValueError(f"unknown opening source {source!r}")
    if not bank_file.exists():
        raise FileNotFoundError(f"{bank_file} missing; run scripts/build_hex_openings.py")
    stored = json.loads(bank_file.read_text())["banks"]
    out = {}
    for split, n in games.items():
        need = {RED: n // 2, BLUE: n - n // 2}
        bank = []
        for actor, count in need.items():
            have = stored.get(split, {}).get(actor, [])
            if len(have) < count:
                raise ValueError(f"{bank_file.name} has {len(have)} {actor} openings for {split}, need {count}")
            bank += [Opening(tuple(m), actor) for m in have[:count]]
        out[split] = bank
    return out
