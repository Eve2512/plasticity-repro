"""Fixed opening banks and opponent levels for Hex.

The paper starts red actors after a deterministic 10-ply opening and blue actors
after an 11-ply opening, from fixed banks (Appendix B). The banks are not
published. Two kinds of bank are available here:

- "legacy": random 10/11-ply openings from seeds, filtered to balanced positions.
  Used by the smoke run (reports 07 and 08). Those games were short (2-7 actor
  moves) and blue openings were much harder (a strong engine won 2/5 as blue).
- "contested": 4/5-ply openings kept only if a weak player (always the
  first legal action) loses from them and a reference engine wins from them,
  against the weakest train opponent. Every kept opening has room to improve,
  for both colours. Built once by scripts/build_hex_openings.py into BANK_FILE.
  Used by lineage A (report 10): each split had its own seed, and the ID bank came
  out harder than the train bank (Sonnet 5.5: train 8/8, ID 2/12).
- "pooled" (default): one pool of contested openings, scored for difficulty by
  engines only and dealt to the splits by colour and difficulty, so train and
  held-out ID are the same kind of game. Saved in POOLED_FILE.
"""

import json
import random
from dataclasses import dataclass
from pathlib import Path

from envs.hex import BLUE, RED, HexState
from envs.hex_engine import AlphaBetaEngine, connection_distance

# Splits and their seeds. Seeds differ so the banks do not overlap. "pool" feeds the
# pooled banks, which are dealt to the splits afterwards.
SPLIT_SEEDS = {"train": 1001, "id": 2002, "ood": 3003, "pool": 4004}

# Opponent node budgets per move. The paper uses 10k-1M for train and ID and
# 10M for OOD; a pure-Python engine runs about 20-30k nodes per second, so these
# are scaled down. Calibration: reports/05_hex_engine_calibration.md.
TRAIN_ID_LEVELS = (3_000, 10_000, 30_000, 100_000)
OOD_LEVELS = (1_000_000,)

PAPER_PLIES = {RED: 10, BLUE: 11}
SHORT_PLIES = {RED: 4, BLUE: 5}
REFERENCE_NODES = 30_000  # the engine that must win a contested opening
BANK_FILE = Path(__file__).resolve().parent.parent / "data" / "hex_openings_contested.json"
POOLED_FILE = BANK_FILE.with_name("hex_openings_pooled.json")
DIFFICULTY_LEVELS = TRAIN_ID_LEVELS[:3]  # 3k, 10k, 30k: the reference's wins against these score an opening


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


def difficulty(opening: Opening) -> int:
    """How many of the DIFFICULTY_LEVELS opponents the reference engine beats from here (higher = easier)."""
    reference = AlphaBetaEngine(REFERENCE_NODES).choose
    return sum(_actor_wins(opening, reference, AlphaBetaEngine(n).choose) for n in DIFFICULTY_LEVELS)


def _van_der_corput(k: int) -> float:
    x, denom = 0.0, 1.0
    while k:
        denom *= 2
        k, bit = divmod(k, 2)
        x += bit / denom
    return x


def spread_order(n: int) -> list[int]:
    """Positions 0..n-1 in an order whose every prefix spreads over the whole range."""
    order, seen, k = [], set(), 0
    while len(order) < n:
        p = int(_van_der_corput(k) * n)
        k += 1
        if p not in seen:
            seen.add(p)
            order.append(p)
    return order


def _score(opening: Opening) -> int | None:
    """Difficulty of a contested opening, or None when it is not contested."""
    return difficulty(opening) if is_contested(opening) else None


def _scored_stream(actor: str, plies: int, workers: int):
    """(opening, difficulty) for contested candidates, in candidate order.

    Candidates are scored in parallel batches; the order kept is the candidate
    order, so the result does not depend on `workers`.
    """
    seen: set[str] = set()
    stream = _candidates("pool", actor, plies)

    def batch(n):
        out = []
        while len(out) < n:
            o = next(stream)
            if o.key not in seen:
                seen.add(o.key)
                out.append(o)
        return out

    if workers <= 1:
        while True:
            for o in batch(1):
                yield o, _score(o)
    from multiprocessing import get_context

    with get_context("spawn").Pool(workers) as pool:
        while True:
            chunk = batch(workers)
            yield from zip(chunk, pool.map(_score, chunk))


def build_pooled_banks(games: dict[str, int], plies=SHORT_PLIES, progress=None, workers: int = 1) -> dict:
    """One pool of contested openings, dealt to the splits by colour and difficulty.

    Openings are sorted by difficulty and each goes to the split that is furthest
    behind its target, so every split gets the same difficulty mix. Within a split
    the stored order is spread_order over that sorted list, so the first k
    openings of a split (as a run with fewer games uses) are also balanced.
    """
    banks: dict[str, dict[str, list[dict]]] = {split: {RED: [], BLUE: []} for split in games}
    tried = 0
    for actor in (RED, BLUE):
        targets = {split: (n // 2 if actor == RED else n - n // 2) for split, n in games.items()}
        pool = []
        for opening, score in _scored_stream(actor, plies[actor], workers):
            if len(pool) == sum(targets.values()):
                break
            tried += 1
            if score is not None:
                pool.append((opening, score))
                if progress:
                    progress(actor, len(pool), sum(targets.values()), tried)
        rng = random.Random(f"deal-{actor}")
        pool.sort(key=lambda od: (od[1], rng.random()))
        dealt: dict[str, list] = {split: [] for split in games}
        order = list(games)
        for item in pool:
            open_splits = [s for s in order if len(dealt[s]) < targets[s]]
            split = min(open_splits, key=lambda s: (len(dealt[s]) / targets[s], order.index(s)))
            dealt[split].append(item)
        for split, items in dealt.items():
            banks[split][actor] = [
                {"moves": list(items[p][0].moves), "difficulty": items[p][1]} for p in spread_order(len(items))
            ]
    return {
        "version": 2,
        "plies": plies,
        "rule": f"contested (first-legal player loses and {REFERENCE_NODES:,}-node engine wins vs "
                f"{TRAIN_ID_LEVELS[0]:,} nodes); difficulty = opponents in {list(DIFFICULTY_LEVELS)} "
                "the reference beats; dealt to splits by colour and difficulty",
        "candidates_tried": tried,
        "banks": banks,
    }


def split_banks(games: dict[str, int], source: str = "pooled", bank_file: Path | None = None) -> dict[str, list[Opening]]:
    """Openings per split, half the games for each colour (red first).

    `games` maps split name to games per checkpoint, e.g. the paper's
    {"train": 40, "id": 40, "ood": 32}. Sources: "pooled" (default), "contested"
    (lineage A), "legacy" (smoke run).
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
    files = {"contested": BANK_FILE, "pooled": POOLED_FILE}
    if source not in files:
        raise ValueError(f"unknown opening source {source!r}")
    bank_file = bank_file or files[source]
    if not bank_file.exists():
        raise FileNotFoundError(f"{bank_file} missing; run scripts/build_hex_openings.py --kind {source}")
    stored = json.loads(bank_file.read_text())["banks"]
    out = {}
    for split, n in games.items():
        need = {RED: n // 2, BLUE: n - n // 2}
        bank = []
        for actor, count in need.items():
            have = stored.get(split, {}).get(actor, [])
            if len(have) < count:
                raise ValueError(f"{bank_file.name} has {len(have)} {actor} openings for {split}, need {count}")
            bank += [Opening(tuple(m["moves"] if isinstance(m, dict) else m), actor) for m in have[:count]]
        out[split] = bank
    return out
