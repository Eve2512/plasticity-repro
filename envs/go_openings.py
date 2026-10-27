"""Openings, seeds and opponent levels for 5×5 Go.

The paper says only that Go training seeds change per checkpoint and held-out
seeds are fixed. From the empty board GNU Go as Black wins every game by 15.5
(5×5 Go is a known Black win by 25 points under area scoring), so a game must
start from a seeded opening for White to have a chance. As in Hex
(envs/hex_openings.py), openings are short random sequences kept only when
contested: the first-legal player loses from them and the reference (GNU Go
level 10) wins from them, both against the weakest train opponent.

GNU Go levels 5-9 play almost alike on 5×5, so a win count against them hardly
grades an opening. The difficulty is instead the reference's mean final
margin over games against levels 5, 7 and 9 (higher is easier). Contested
openings form one pool per colour, which is sorted by difficulty and dealt to
the splits: held-out ID and OOD banks are fixed; the rest is a training
reservoir. Each checkpoint draws its training games from the reservoir with a
seed that depends on the checkpoint, one from each difficulty stratum, so
training games change per checkpoint and stay the same kind of game as ID.
"""

import json
import random
from dataclasses import dataclass, replace
from pathlib import Path
from statistics import mean

from envs.go import BLACK, WHITE, GoState
from envs.go_engine import GnuGoEngine, gnugo_final_margin
from envs.hex_openings import spread_order

TRAIN_ID_LEVELS = (5, 6, 7, 8, 9)
OOD_LEVELS = (10,)
REFERENCE_LEVEL = 10
DIFFICULTY_LEVELS = (5, 7, 9)
PLIES = {BLACK: 2, WHITE: 3}  # actor Black after 2 random moves, White after 3
POOL_SEED = 5005
POOLED_FILE = Path(__file__).resolve().parent.parent / "data" / "go_openings_pooled.json"
# Pool sizes per colour: held-out banks for the paper's counts (20 ID, 12 OOD, half
# per colour) and a training reservoir several times the paper's 20 train games.
POOL_TARGETS = {"id": 10, "ood": 6, "train": 40}


@dataclass(frozen=True)
class Opening:
    moves: tuple[str, ...]
    actor: str  # BLACK or WHITE: the side the actor plays
    seed: int = 0  # GNU Go's random seed for this game

    @property
    def key(self) -> str:
        return " ".join(self.moves)

    def state(self, adjudicate: bool = True) -> GoState:
        s = GoState(adjudicator=gnugo_final_margin if adjudicate else None)
        for m in self.moves:
            s.play(m)
        return s


def _candidates(actor: str, plies: int, seed: int = POOL_SEED):
    """Endless stream of random openings (board points only) that leave `actor` to move."""
    rng = random.Random(f"{seed}-{actor}")
    while True:
        s = GoState()
        for _ in range(plies):
            s.play(rng.choice(s.legal_indices()[:-1]))
        yield Opening(tuple(s.name(i) for i in s.history), actor)


def _margin(opening: Opening, actor_choose, opponent_choose) -> float:
    """The actor's final margin (positive = actor wins) from this opening."""
    state = opening.state()
    while not state.is_over():
        mover = actor_choose if state.to_move == opening.actor else opponent_choose
        state.play(mover(state.copy()))
    m = state.final_margin()
    return m if opening.actor == BLACK else -m


def first_legal(state: GoState) -> str:
    return state.legal_actions()[0]


def score(opening: Opening) -> float | None:
    """Difficulty (reference's mean margin) of a contested opening; None if not contested."""
    weakest = GnuGoEngine(TRAIN_ID_LEVELS[0]).choose
    if _margin(opening, first_legal, weakest) > 0:
        return None
    reference = GnuGoEngine(REFERENCE_LEVEL).choose
    margins = [_margin(opening, reference, GnuGoEngine(level).choose) for level in DIFFICULTY_LEVELS]
    if margins[0] <= 0:  # DIFFICULTY_LEVELS[0] is the weakest train level
        return None
    return mean(margins)


def _scored_stream(actor: str, workers: int):
    """(opening, difficulty) in candidate order, scored in parallel batches."""
    seen: set[str] = set()
    stream = _candidates(actor, PLIES[actor])

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
            (o,) = batch(1)
            yield o, score(o)
    from multiprocessing import get_context

    with get_context("spawn").Pool(workers) as pool:
        while True:
            chunk = batch(workers)
            yield from zip(chunk, pool.map(score, chunk))


def _deal_order(targets: dict[str, int]) -> list[str]:
    """Which split each item of the difficulty-sorted pool goes to: centred systematic sampling."""
    total = sum(targets.values())
    slots = [((j + 0.5) * total / n, k, split) for k, (split, n) in enumerate(targets.items()) for j in range(n)]
    return [split for _, _, split in sorted(slots)]


def _deal(pool: list[tuple[list[str], float]], targets: dict[str, int]) -> dict[str, list[dict]]:
    """(moves, difficulty) pairs of one colour, dealt to the splits by difficulty."""
    pool = sorted(pool, key=lambda md: (md[1], " ".join(md[0])))
    dealt: dict[str, list] = {split: [] for split in targets}
    for split, item in zip(_deal_order(targets), pool):
        dealt[split].append(item)
    out = {}
    for split, items in dealt.items():
        positions = range(len(items)) if split == "train" else spread_order(len(items))
        out[split] = [{"moves": items[p][0], "difficulty": items[p][1]} for p in positions]
    return out


def redeal(data: dict, targets: dict[str, int] = POOL_TARGETS) -> dict:
    """Deal a saved pool again (same openings and scores) under the current rule."""
    banks: dict[str, dict[str, list[dict]]] = {split: {} for split in targets}
    for actor in (BLACK, WHITE):
        pool = [(e["moves"], e["difficulty"]) for by in data["banks"].values() for e in by.get(actor, [])]
        for split, entries in _deal(pool, targets).items():
            banks[split][actor] = entries
    return {**data, "banks": banks}


def build_pooled_banks(targets: dict[str, int] = POOL_TARGETS, workers: int = 1, progress=None) -> dict:
    """One contested pool per colour, sorted by difficulty and dealt to the splits.

    The j-th of a split's n openings is the one at quantile (j + 0.5) / n of the
    sorted pool (_deal_order), so every split gets the same difficulty mix; within a split the stored order is spread_order over
    the sorted list, so a prefix (fewer held-out games) is also balanced. The train
    reservoir is stored sorted by difficulty, for stratified draws.
    """
    banks: dict[str, dict[str, list[dict]]] = {split: {BLACK: [], WHITE: []} for split in targets}
    tried = 0
    need = sum(targets.values())
    for actor in (BLACK, WHITE):
        pool = []
        for opening, difficulty in _scored_stream(actor, workers):
            if len(pool) == need:
                break
            tried += 1
            if difficulty is not None:
                pool.append((opening, difficulty))
                if progress:
                    progress(actor, len(pool), need, tried)
        for split, entries in _deal([(list(o.moves), round(d, 2)) for o, d in pool], targets).items():
            banks[split][actor] = entries
    return {
        "version": 1,
        "plies": PLIES,
        "rule": f"contested (first-legal player loses and GNU Go level {REFERENCE_LEVEL} wins vs level "
                f"{TRAIN_ID_LEVELS[0]}); difficulty = level {REFERENCE_LEVEL}'s mean final margin vs levels "
                f"{list(DIFFICULTY_LEVELS)}; dealt to splits by colour and difficulty; train is a reservoir",
        "candidates_tried": tried,
        "banks": banks,
    }


def _stratified(reservoir: list, k: int, rng: random.Random) -> list:
    """k items, one from each of k equal slices of the (difficulty-sorted) reservoir."""
    n = len(reservoir)
    picks = []
    for j in range(k):
        lo, hi = j * n // k, max(j * n // k + 1, (j + 1) * n // k)
        picks.append(reservoir[rng.randrange(lo, hi)])
    rng.shuffle(picks)
    return picks


def split_banks(games: dict[str, int], checkpoint: int = 0, bank_file: Path = POOLED_FILE) -> dict[str, list[Opening]]:
    """Openings per split for one checkpoint, half the games for each colour (Black first).

    Held-out banks and their GNU Go seeds are the same at every checkpoint. Train
    openings and seeds are drawn afresh from the reservoir for each checkpoint.
    """
    if not bank_file.exists():
        raise FileNotFoundError(f"{bank_file} missing; run scripts/build_go_openings.py")
    stored = json.loads(bank_file.read_text())["banks"]
    out = {}
    for split, n in games.items():
        need = {BLACK: n // 2, WHITE: n - n // 2}
        bank = []
        for actor, count in need.items():
            have = [Opening(tuple(e["moves"]), actor) for e in stored.get(split, {}).get(actor, [])]
            if len(have) < count:
                raise ValueError(f"{bank_file.name} has {len(have)} {actor} openings for {split}, need {count}")
            if split == "train":
                rng = random.Random(f"train-{checkpoint}-{actor}")
                have = _stratified(have, count, rng)
            bank += have[:count]
        base = 1000 * (checkpoint + 1) if split == "train" else {"id": 0, "ood": 500}.get(split, 0)
        out[split] = [replace(o, seed=base + i) for i, o in enumerate(bank)]
    return out
