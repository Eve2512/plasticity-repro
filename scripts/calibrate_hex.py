"""Check that larger node budgets play stronger Hex.

Every train/ID level and the OOD level plays the weakest train/ID level and a
fixed baseline (connection-distance greedy, one ply) from the same openings,
both colours. Writes reports/05_hex_engine_calibration.md.
"""

import time
from pathlib import Path

from envs.hex_engine import AlphaBetaEngine, evaluate
from envs.hex_match import play_from
from envs.hex_openings import OOD_LEVELS, TRAIN_ID_LEVELS, split_banks

REPORT = Path(__file__).resolve().parent.parent / "reports" / "05_hex_engine_calibration.md"
GAMES = 12  # openings from the training bank, half per colour


def greedy(state):
    """One-ply baseline: the move that leaves the opponent worst off."""
    best, best_score = None, None
    for move in state.legal_actions():
        state.play(move)
        score = -evaluate(state) if not state.is_over() else 10**6
        state.undo()
        if best_score is None or score > best_score:
            best, best_score = move, score
    return best


def score_vs(level, opponent, openings):
    engine = AlphaBetaEngine(level)
    wins = sum(play_from(o, engine.choose, opponent).winner == o.actor for o in openings)
    return 100 * wins / len(openings)


def main():
    openings = split_banks({"train": GAMES}, source="legacy")["train"]  # report 05 used these
    weakest = AlphaBetaEngine(TRAIN_ID_LEVELS[0]).choose
    lines = [
        "# 05 Hex engine calibration",
        "",
        f"{GAMES} openings from the training bank (half per colour). Score = share of games",
        "won by the listed level. A stronger level should score higher against both",
        "references.",
        "",
        "| Nodes per move | Split | vs greedy 1-ply | vs weakest train level | Seconds per game |",
        "|---|---|---|---|---|",
    ]
    levels = [(lvl, "train / ID") for lvl in TRAIN_ID_LEVELS] + [(lvl, "OOD") for lvl in OOD_LEVELS]
    for level, split in levels:
        t0 = time.time()
        vs_greedy = score_vs(level, greedy, openings)
        vs_weakest = score_vs(level, weakest, openings)
        per_game = (time.time() - t0) / (2 * GAMES)
        lines.append(f"| {level:,} | {split} | {vs_greedy:.0f} % | {vs_weakest:.0f} % | {per_game:.1f} |")
        print(f"level {level}: {vs_greedy:.0f} % vs greedy, {vs_weakest:.0f} % vs weakest, {per_game:.1f}s/game")
    strongest = TRAIN_ID_LEVELS[-1]
    head_to_head = [score_vs(level, AlphaBetaEngine(strongest).choose, openings) for level in OOD_LEVELS]
    lines += [
        "",
        "Both references above are beaten almost every time by the stronger levels, so they",
        "cannot separate them. Head to head against the strongest train/ID level",
        f"({strongest:,} nodes), same openings, both colours:",
        "",
        "| OOD nodes per move | Score vs strongest train/ID level |",
        "|---|---|",
        *[f"| {lvl:,} | {s:.0f} % |" for lvl, s in zip(OOD_LEVELS, head_to_head)],
        "",
        "The paper's budgets are 10k–1M nodes (train and ID) and 10M (OOD) in a native",
        "engine. This pure-Python engine is scaled down to keep games under a minute.",
        "",
    ]
    print(f"head to head vs {strongest}: {head_to_head}")
    REPORT.write_text("\n".join(lines))
    print(f"wrote {REPORT.relative_to(REPORT.parent.parent)}")


if __name__ == "__main__":
    main()
