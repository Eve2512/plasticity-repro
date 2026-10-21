"""Check the contested banks against the legacy banks with a player outside the rule.

A mid-strength actor (10k-node engine, not used to build the banks) plays the
runner's opponent for each game slot. Reported per colour: win rate and actor
moves per game. OOD games are slow (1M nodes per move), so only the first
OOD_SAMPLE per colour are played. Writes reports/09_opening_balance.md.
"""

from pathlib import Path
from statistics import mean

from envs.hex import BLUE, RED
from envs.hex_engine import AlphaBetaEngine
from envs.hex_match import play_from
from envs.hex_openings import OOD_LEVELS, TRAIN_ID_LEVELS, split_banks

REPORT = Path(__file__).resolve().parent.parent / "reports" / "09_opening_balance.md"
GAMES = {"train": 40, "id": 40, "ood": 32}
OOD_SAMPLE = 2
MID = 10_000


def measure(source):
    banks = split_banks(GAMES, source=source)
    rows = {}
    for split, bank in banks.items():
        levels = OOD_LEVELS if split == "ood" else TRAIN_ID_LEVELS
        per_colour = {RED: [], BLUE: []}
        for i, opening in enumerate(bank):
            if split == "ood" and len(per_colour[opening.actor]) >= OOD_SAMPLE:
                continue
            opponent = AlphaBetaEngine(levels[i % len(levels)]).choose
            record = play_from(opening, AlphaBetaEngine(MID).choose, opponent)
            per_colour[opening.actor].append((record.winner == opening.actor, (len(record.moves) + 1) // 2))
        rows[split] = per_colour
        print(f"{source} {split}: " + ", ".join(
            f"{c} {sum(w for w, _ in v)}/{len(v)}" for c, v in per_colour.items()), flush=True)
    return rows


def main():
    lines = [
        "# 09 Opening balance: contested vs legacy banks",
        "",
        f"Actor: {MID:,}-node engine (not used to build either bank), against the runner's",
        f"opponent for each slot. OOD: first {OOD_SAMPLE} openings per colour only (1M nodes per move is slow).",
        "",
        "| Bank | Split | Red wins | Blue wins | Actor moves per game (red / blue) |",
        "|---|---|---|---|---|",
    ]
    for source in ("legacy", "contested"):
        for split, per_colour in measure(source).items():
            r, b = per_colour[RED], per_colour[BLUE]
            lines.append(
                f"| {source} | {split} | {sum(w for w, _ in r)}/{len(r)} | {sum(w for w, _ in b)}/{len(b)} | "
                f"{mean(m for _, m in r):.1f} / {mean(m for _, m in b):.1f} |"
            )
    lines.append("")
    REPORT.write_text("\n".join(lines))
    print(f"wrote {REPORT.relative_to(REPORT.parent.parent)}")


if __name__ == "__main__":
    main()
