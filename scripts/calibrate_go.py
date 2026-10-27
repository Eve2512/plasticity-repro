"""Calibrate the 5x5 Go opponents and opening pool, engines only (no API calls).

1. Levels: each GNU Go level plays the weakest train level (5) and the
   strongest (9) from the same held-out openings, both colours.
2. The first-legal player against the runner's opponent for every slot of the
   splits a run uses: it must lose every game.
3. Train vs held-out ID: stored difficulty, and the results of a check player
   not used to build the pool (GNU Go level 1) against the runner's opponent per
   slot. Training draws from several checkpoints are pooled, since Go draws new
   training games at each checkpoint.

Writes reports/13_go_calibration.md.
"""

import json
import sys
import time
from math import sqrt
from multiprocessing import Pool
from pathlib import Path
from statistics import mean

from envs.go import BLACK
from envs.go_engine import GnuGoEngine
from envs.go_openings import OOD_LEVELS, POOLED_FILE, TRAIN_ID_LEVELS, _margin, first_legal, split_banks

REPORT = Path(__file__).resolve().parent.parent / "reports" / "13_go_calibration.md"
RUN_GAMES = {"train": 8, "id": 12, "ood": 4}  # the Hex runs' sizes
CHECKPOINTS = 8  # training draws pooled over checkpoints 0..7
CHECK_LEVEL = 1
LEVELS = (1, 3, 5, 7, 9, 10)


def _actor(name):
    return first_legal if name == "first" else GnuGoEngine(name).choose


def _game(job):
    opening, actor, opponent_level = job
    t = time.time()
    m = _margin(opening, _actor(actor), GnuGoEngine(opponent_level, opening.seed).choose)
    return m, time.time() - t


def run(pool, jobs):
    return pool.map(_game, jobs)


def stored_difficulty():
    banks = json.loads(POOLED_FILE.read_text())["banks"]
    return {(tuple(e["moves"]), a): e["difficulty"] for by in banks.values() for a, es in by.items() for e in es}


def slots(banks):
    """(split, opening, opponent level) as the runner assigns them."""
    out = []
    for split, bank in banks.items():
        levels = OOD_LEVELS if split == "ood" else TRAIN_ID_LEVELS
        out += [(split, o, levels[i % len(levels)]) for i, o in enumerate(bank)]
    return out


def z_two(a, n, b, m):
    p = (a + b) / (n + m)
    se = sqrt(p * (1 - p) * (1 / n + 1 / m)) if 0 < p < 1 else 0
    return (a / n - b / m) / se if se else float("nan")


def main(workers: int):
    diff = stored_difficulty()
    lines = ["# 13 Go calibration: GNU Go levels, first-legal player, train vs held-out ID", "",
             "Engines only, no model calls. Openings: data/go_openings_pooled.json "
             "(scripts/build_go_openings.py; rule in envs/go_openings.py). Margins are the actor's "
             "final margin after komi 9.5, scored by GNU Go's final_score (dead stones removed).", ""]
    with Pool(workers) as pool:
        # 1. levels
        held = split_banks({"id": 20}, checkpoint=0)["id"]
        lines += ["## 1. GNU Go levels from the 20 held-out ID openings (10 per colour)", "",
                  "| Actor level | Wins vs level 5 | Wins vs level 9 | Mean margin vs 5 | Seconds per game |",
                  "|---|---|---|---|---|"]
        for level in LEVELS:
            res5 = run(pool, [(o, level, 5) for o in held])
            res9 = run(pool, [(o, level, 9) for o in held])
            w5, w9 = sum(m > 0 for m, _ in res5), sum(m > 0 for m, _ in res9)
            secs = mean(s for _, s in res5 + res9)
            lines.append(f"| {level} | {w5}/20 | {w9}/20 | {mean(m for m, _ in res5):+.1f} | {secs:.1f} |")
            print(f"level {level}: {w5}/20 vs 5, {w9}/20 vs 9", flush=True)

        # 2 and 3: the slots a run uses
        train = [s for t in range(CHECKPOINTS) for s in slots(split_banks({"train": RUN_GAMES["train"]}, checkpoint=t))]
        held_slots = slots(split_banks({"id": RUN_GAMES["id"], "ood": RUN_GAMES["ood"]}, checkpoint=0))
        full_id = slots(split_banks({"id": 20}, checkpoint=0))
        all_slots = train + held_slots
        first = run(pool, [(o, "first", lvl) for _, o, lvl in all_slots])
        check = run(pool, [(o, CHECK_LEVEL, lvl) for _, o, lvl in all_slots + full_id])
    first_wins = sum(m > 0 for m, _ in first)
    lines += ["", "## 2. First-legal player (always the first legal action: A1, B1, ...)", "",
              f"Against the runner's opponent in every slot below: {first_wins} wins in {len(first)} games "
              f"(mean margin {mean(m for m, _ in first):+.1f}).", ""]

    def table(title, rows):
        out = [f"### {title}", "",
               "| Split | Games | Mean difficulty (black / white) | Level-1 check wins (black / white) | Total |",
               "|---|---|---|---|---|"]
        tally = {}
        for split in dict.fromkeys(r[0] for r in rows):
            rs = [r for r in rows if r[0] == split]
            b = [r for r in rs if r[1].actor == BLACK]
            w = [r for r in rs if r[1].actor != BLACK]
            def d(xs):
                return mean(diff[(x[1].moves, x[1].actor)] for x in xs)
            def wins(xs):
                return sum(x[2] > 0 for x in xs)
            out.append(f"| {split} | {len(rs)} | {d(b):.1f} / {d(w):.1f} | {wins(b)}/{len(b)} / {wins(w)}/{len(w)} | "
                       f"{wins(rs)}/{len(rs)} |")
            tally[split] = (wins(rs), len(rs))
        if "train" in tally and "id" in tally:
            z = z_two(*tally["train"], *tally["id"])
            out += ["", f"Train vs ID, level-1 check player: z = {z:.2f} (|z| < 2: no detectable difference).", ""]
        return out, tally

    n_run = len(all_slots)
    rows_run = [(s, o, m) for (s, o, _), (m, _) in zip(all_slots, check[:n_run])]
    rows_full = [(s, o, m) for (s, o, _), (m, _) in zip(full_id, check[n_run:])]
    t_run, _ = table(f"Run sizes: train {RUN_GAMES['train']} per checkpoint (pooled over checkpoints 0–{CHECKPOINTS - 1}), "
                     f"ID {RUN_GAMES['id']}, OOD {RUN_GAMES['ood']}", rows_run)
    t_full, _ = table("Training draws above vs the full 20-game ID bank",
                      [r for r in rows_run if r[0] == "train"] + rows_full)
    lines += ["## 3. Train vs held-out ID", "",
              f"Difficulty: GNU Go level 10's mean final margin against levels 5, 7 and 9 from the opening "
              f"(higher is easier). Check player: GNU Go level {CHECK_LEVEL}, not used to build the pool, against "
              "the runner's opponent per slot.", ""] + t_run + t_full
    lines += [
        "## Reading", "",
        "- GNU Go levels 5–10 (and even 1 and 3) play almost alike on 5×5: from these openings every level",
        "  wins most games against level 5 and level 9. The paper's level split (5–9 train/ID, 10 OOD) is kept,",
        "  but OOD is barely harder than ID here; Go OOD results say little about a stronger opponent.",
        "- Openings are contested by construction (the first-legal player loses, GNU Go 10 wins), so each game",
        "  has room to improve. The bar is GNU Go strength: a model must play about as well as GNU Go to win.",
        "- White openings score easier than Black ones (3 random plies leave Black's random first stone weak);",
        "  results should be reported per colour.",
        "- The full 20-game ID bank matches the training draws in difficulty; a 12-game prefix is a little",
        "  harder. Go runs should use ID 20 (10 per colour), the paper's count.",
        "",
    ]
    REPORT.write_text("\n".join(lines) + "\n")
    print(f"wrote {REPORT.relative_to(REPORT.parent.parent)}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
