"""Paid smoke run: one Claude model, two checkpoints, a few Hex games.

Purpose: measure real tokens and cost per game and per reflection before
planning larger runs. Spending stops before any call once the billed amount
reaches --cap (never above $20). Without --yes the script only prints the plan.

    uv run python scripts/smoke_run_hex.py --model anthropic/claude-sonnet-5.5          # plan only
    uv run python scripts/smoke_run_hex.py --model anthropic/claude-sonnet-5.5 --yes    # run

Keys come from the environment or the git-ignored .env file in the repository
root: OPENROUTER_API_KEY for --provider openrouter (the default), ANTHROPIC_API_KEY
for --provider anthropic.
"""

import argparse
import json
import sys
from pathlib import Path

from harness.anthropic_model import BILLING, OPENROUTER_BASE_URL, AnthropicModel
from harness.episode import EpisodeConfig
from harness.keys import load_key
from harness.reflection import ReflectionConfig
from harness.runner import RunConfig, reset, run_lineage

ROOT = Path(__file__).resolve().parent.parent
HARD_CAP = 20.00
GAMES = {"train": 4, "id": 4, "ood": 2}
ROUNDS = 1  # checkpoints 0 and 1
PROVIDERS = {
    "openrouter": ("OPENROUTER_API_KEY", lambda m: m.startswith("anthropic/")),
    "anthropic": ("ANTHROPIC_API_KEY", lambda m: m.startswith("claude-")),
}


def report(results: dict, path: Path) -> None:
    lines = [
        f"# 07 Smoke run: {results['model']} on 6x6 Hex",
        "",
        f"Games per checkpoint: {GAMES}, openings: {results['config']['openings']}. Billed: ${results['billed']:.2f} (cap ${results['config']['cap']:.2f}).",
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
    parser.add_argument("--provider", default="openrouter", choices=sorted(PROVIDERS))
    parser.add_argument("--model", required=True, choices=sorted(BILLING))
    parser.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    parser.add_argument("--cap", type=float, default=19.00)
    parser.add_argument("--train", type=int, default=GAMES["train"], help="training games per checkpoint")
    parser.add_argument("--id", type=int, default=GAMES["id"], help="held-out ID games per checkpoint")
    parser.add_argument("--ood", type=int, default=GAMES["ood"], help="held-out OOD games per checkpoint")
    parser.add_argument("--openings", default="pooled", choices=["pooled", "contested", "legacy"])
    parser.add_argument("--yes", action="store_true", help="actually call the API")
    args = parser.parse_args(argv)
    if not 0 < args.cap <= HARD_CAP:
        parser.error(f"--cap must be between 0 and {HARD_CAP:.2f}")
    key_name, model_matches = PROVIDERS[args.provider]
    if not model_matches(args.model):
        parser.error(f"{args.model} is not a {args.provider} model id")
    if min(args.train, args.id, args.ood) < 1:
        parser.error("every split needs at least one game")
    GAMES.update(train=args.train, id=args.id, ood=args.ood)

    billing = BILLING[args.model]
    games = sum(GAMES.values()) * (ROUNDS + 1)
    print(f"provider {args.provider}, model {args.model}, effort {args.effort}")
    print(f"games per checkpoint: {GAMES}, openings: {args.openings}")
    print(f"{games} games (32 model calls max each) + {ROUNDS} reflection(s) (50 calls, up to 3 attempts)")
    print(f"billing ${billing.input_per_mtok}/${billing.output_per_mtok} per M input/output tokens; "
          f"stops before any call once ${args.cap:.2f} is spent")
    if not args.yes:
        print("plan only: add --yes to run")
        return 0
    key = load_key(key_name)
    if not key:
        print(f"no {key_name} in the environment or .env")
        return 1

    if args.provider == "openrouter":
        model = AnthropicModel(args.model, effort=args.effort, base_url=OPENROUTER_BASE_URL, auth_token=key)
    else:
        from anthropic import Anthropic
        model = AnthropicModel(args.model, effort=args.effort, client=Anthropic(api_key=key, max_retries=4))

    run_dir = ROOT / "runs" / f"smoke_{args.model.replace('/', '_')}"
    reset(run_dir)
    cfg = RunConfig(
        rounds=ROUNDS,
        games=GAMES,
        openings=args.openings,
        episode=EpisodeConfig(max_calls=32, tool_timeout=240),
        reflection=ReflectionConfig(max_calls=50, bash_timeout=300, max_attempts=3),
        prices=billing.undiscounted(),
        billing=billing,
        cap=args.cap,
    )
    results = run_lineage(model, run_dir, cfg)
    report(results, ROOT / "reports" / "07_smoke_run.md")
    print(json.dumps({k: results[k] for k in ("billed", "learning_cost", "stopped")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
