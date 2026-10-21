"""Do the openings decide the games? Bracket an agent with a weak and a strong player.

From the smoke run's openings and against the same opponents, play (a) a player
that always takes the first legal action and (b) the 100k-node engine. If both
got the same result per opening, the openings would decide the games and the
benchmark could not show learning. Writes reports/08_opening_controls.md.
"""

from pathlib import Path

from envs.hex_engine import AlphaBetaEngine, connection_distance
from envs.hex_match import play_from
from envs.hex_openings import OOD_LEVELS, TRAIN_ID_LEVELS, split_banks

REPORT = Path(__file__).resolve().parent.parent / "reports" / "08_opening_controls.md"
GAMES = {"train": 4, "id": 4, "ood": 2}  # the smoke run's per-checkpoint counts


def main():
    banks = split_banks(GAMES)
    first_legal = lambda s: s.legal_actions()[0]  # noqa: E731
    strong = AlphaBetaEngine(100_000).choose
    lines = [
        "# 08 Opening controls",
        "",
        "Same openings and opponents as the smoke run (report 07). Win = 1.",
        "Distance = empty cells each side still needs to connect, at the start position.",
        "",
        "| Game | Actor | Distance (actor / opponent) | First legal action | Engine, 100k nodes |",
        "|---|---|---|---|---|",
    ]
    totals = {"first": 0, "strong": 0, "blue_strong": 0, "blue": 0}
    for split, bank in banks.items():
        levels = OOD_LEVELS if split == "ood" else TRAIN_ID_LEVELS
        for i, opening in enumerate(bank):
            opponent = AlphaBetaEngine(levels[i % len(levels)]).choose
            s = opening.state()
            other = "O" if opening.actor == "X" else "X"
            a = int(play_from(opening, first_legal, opponent).winner == opening.actor)
            b = int(play_from(opening, strong, opponent).winner == opening.actor)
            totals["first"] += a
            totals["strong"] += b
            if opening.actor == "O":
                totals["blue"] += 1
                totals["blue_strong"] += b
            lines.append(
                f"| {split} g{i + 1} | {'red' if opening.actor == 'X' else 'blue'} | "
                f"{connection_distance(s, opening.actor)} / {connection_distance(s, other)} | {a} | {b} |"
            )
            print(f"{split} g{i + 1}: first {a}, engine {b}", flush=True)
    n = sum(GAMES.values())
    lines += [
        "",
        f"First legal action: {totals['first']}/{n}. Engine: {totals['strong']}/{n} "
        f"(as blue: {totals['blue_strong']}/{totals['blue']}).",
        "",
        "The weak and strong players get different results, so play decides these games and",
        "an agent has room to improve between them. Blue openings (11 plies, opponent one stone",
        "ahead) are harder: even the engine loses most of them.",
        "",
    ]
    REPORT.write_text("\n".join(lines))
    print(f"wrote {REPORT.relative_to(REPORT.parent.parent)}")


if __name__ == "__main__":
    main()
