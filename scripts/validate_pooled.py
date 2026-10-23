"""Are train and held-out ID the same kind of game in the pooled banks?

For the openings a run actually uses (the first games of each split) and for the
full train and ID banks: the engine difficulty score stored with each opening,
and the results of a 10k-node engine (not used to build the banks) against the
runner's opponent for each slot. Writes reports/11_pooled_balance.md.
"""

import json
from math import sqrt
from pathlib import Path
from statistics import mean

from envs.hex import RED
from envs.hex_engine import AlphaBetaEngine
from envs.hex_match import play_from
from envs.hex_openings import OOD_LEVELS, POOLED_FILE, TRAIN_ID_LEVELS, split_banks

REPORT = Path(__file__).resolve().parent.parent / "reports" / "11_pooled_balance.md"
RUN_GAMES = {"train": 8, "id": 12, "ood": 4}  # option A
FULL_GAMES = {"train": 40, "id": 40}
MID = 10_000


def stored_difficulty():
    banks = json.loads(POOLED_FILE.read_text())["banks"]
    return {(split, tuple(e["moves"])): e["difficulty"] for split, by in banks.items() for es in by.values() for e in es}


def play(games):
    diff = stored_difficulty()
    out = {}
    for split, bank in split_banks(games).items():
        levels = OOD_LEVELS if split == "ood" else TRAIN_ID_LEVELS
        rows = []
        for i, o in enumerate(bank):
            won = play_from(o, AlphaBetaEngine(MID).choose, AlphaBetaEngine(levels[i % len(levels)]).choose).winner == o.actor
            rows.append({"red": o.actor == RED, "won": won, "difficulty": diff[(split, o.moves)]})
        out[split] = rows
        print(f"{split} ({len(rows)}): mid engine {sum(r['won'] for r in rows)}/{len(rows)}", flush=True)
    return out


def z_two(a, n, b, m):
    p = (a + b) / (n + m)
    se = sqrt(p * (1 - p) * (1 / n + 1 / m)) if 0 < p < 1 else float("nan")
    return (a / n - b / m) / se if se == se and se > 0 else float("nan")


def table(title, result):
    lines = [f"## {title}", "", "| Split | Games | Mean difficulty (red / blue) | Mid engine wins (red / blue) | Total |",
             "|---|---|---|---|---|"]
    for split, rows in result.items():
        red = [r for r in rows if r["red"]]
        blue = [r for r in rows if not r["red"]]
        lines.append(
            f"| {split} | {len(rows)} | {mean(r['difficulty'] for r in red):.2f} / {mean(r['difficulty'] for r in blue):.2f} | "
            f"{sum(r['won'] for r in red)}/{len(red)} / {sum(r['won'] for r in blue)}/{len(blue)} | "
            f"{sum(r['won'] for r in rows)}/{len(rows)} |"
        )
    t, i = result["train"], result["id"]
    z = z_two(sum(r["won"] for r in t), len(t), sum(r["won"] for r in i), len(i))
    lines += ["", f"Train vs ID, mid engine: z = {z:.2f} (|z| < 2: no detectable difference).", ""]
    return lines


def main():
    lines = [
        "# 11 Pooled opening banks: is held-out ID the same kind of game as train?",
        "",
        "Difficulty: how many of the 3k, 10k and 30k opponents the 30k reference engine beats",
        "from the opening (1–3, higher is easier; engines only, no model results used).",
        f"Mid engine: {MID:,} nodes, not used to build the banks, against the runner's opponent per slot.",
        "",
    ]
    lines += table("Games option A uses (8 train, 12 ID, 4 OOD)", play(RUN_GAMES))
    lines += table("Full train and ID banks (40 each)", play(FULL_GAMES))
    lines += [
        "For comparison, lineage A's per-seed banks gave Sonnet 5.5 train 8/8 and ID 2/12 (z ≈ 3.7),",
        "and the mid engine 29/40 train vs 22/40 ID on the full banks (report 09).",
        "",
    ]
    REPORT.write_text("\n".join(lines))
    print(f"wrote {REPORT.relative_to(REPORT.parent.parent)}")


if __name__ == "__main__":
    main()
