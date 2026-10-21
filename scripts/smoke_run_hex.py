"""Paid smoke run: one Claude model, two checkpoints, a few Hex games.

Purpose: measure real tokens and cost per game and per reflection before
planning larger runs. Spending stops before any call once the billed amount
reaches --cap (never above $5). Without --yes the script only prints the plan.

    uv run python scripts/smoke_run_hex.py --model claude-haiku-5-5          # plan only
    uv run python scripts/smoke_run_hex.py --model claude-haiku-5-5 --yes    # run

The API key comes from ANTHROPIC_API_KEY, or from a git-ignored .env file in the
repository root with the line ANTHROPIC_API_KEY=...
"""

import argparse
import json
import os
import sys
from pathlib import Path

from harness.anthropic_model import BILLING, AnthropicModel
from harness.episode import EpisodeConfig
from harness.reflection import ReflectionConfig
from harness.runner import RunConfig, reset, run_lineage

ROOT = Path(__file__).resolve().parent.parent
HARD_CAP = 5.00
GAMES = {"train": 4, "id": 4, "ood": 2}
ROUNDS = 1  # checkpoints 0 and 1


def load_key() -> bool:
    if os.environ.get("ANTHROPIC_API_KEY"):
        return True
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            name, _, value = line.partition("=")
            if name.strip() == "ANTHROPIC_API_KEY" and value.strip():
                os.environ["ANTHROPIC_API_KEY"] = value.strip().strip("'\"")
                return True
    return False


def report(results: dict, path: Path) -> None:
    lines = [
        f"# 07 Smoke run: {results['model']} on 6x6 Hex",
        "",
        f"Games per checkpoint: {GAMES}. Billed: ${results['billed']:.2f} (cap ${results['config']['cap']:.2f}).",
        f"Learning cost, undiscounted as in the paper: ${results['learning_cost']:.2f}.",
        "",
        "| Checkpoint | Train | Held-out ID | Held-out OOD | Unfinished games | Reflection |",
        "|---|---|---|---|---|---|",
    ]
    for c in results["checkpoints"]:
        refl = c.get("reflection")
        refl_text = "–" if refl is None else ("accepted" if refl["accepted"] else "rejected") + \
            f" ({len(refl['attempts'])} attempt(s))"
        cells = [f"{100 * c[s]['points'] / c[s]['games']:.0f} %" for s in ("train", "id", "ood")]
        unfinished = sum(c[s]["unfinished"] for s in ("train", "id", "ood"))
        lines.append(f"| {c['t']} | " + " | ".join(cells) + f" | {unfinished} | {refl_text} |")
    if results["stopped"]:
        lines += ["", f"Stopped early: {results['stopped']}."]
    lines.append("")
    path.write_text("\n".join(lines))


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=sorted(BILLING))
    parser.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    parser.add_argument("--cap", type=float, default=4.50)
    parser.add_argument("--yes", action="store_true", help="actually call the API")
    args = parser.parse_args(argv)
    if not 0 < args.cap <= HARD_CAP:
        parser.error(f"--cap must be between 0 and {HARD_CAP:.2f}")

    billing = BILLING[args.model]
    games = sum(GAMES.values()) * (ROUNDS + 1)
    print(f"model {args.model}, effort {args.effort}")
    print(f"{games} games (32 model calls max each) + {ROUNDS} reflection(s) (50 calls, up to 3 attempts)")
    print(f"billing ${billing.input_per_mtok}/${billing.output_per_mtok} per M input/output tokens; "
          f"stops before any call once ${args.cap:.2f} is spent")
    if not args.yes:
        print("plan only: add --yes to run")
        return 0
    if not load_key():
        print("no ANTHROPIC_API_KEY in the environment or .env")
        return 1

    run_dir = ROOT / "runs" / f"smoke_{args.model}"
    reset(run_dir)
    cfg = RunConfig(
        rounds=ROUNDS,
        games=GAMES,
        episode=EpisodeConfig(max_calls=32, tool_timeout=240),
        reflection=ReflectionConfig(max_calls=50, bash_timeout=300, max_attempts=3),
        prices=billing.undiscounted(),
        billing=billing,
        cap=args.cap,
    )
    results = run_lineage(AnthropicModel(args.model, effort=args.effort), run_dir, cfg)
    report(results, ROOT / "reports" / "07_smoke_run.md")
    print(json.dumps({k: results[k] for k in ("billed", "learning_cost", "stopped")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
