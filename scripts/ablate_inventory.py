"""Limitation test 6: artifact ablation on finished lineages.

Plays held-out ID games from a lineage's final checkpoint three ways, with the same
model, effort, openings and opponents as the run:

    with    the final inventory, as the run would have used it
    empty   an empty inventory (only the tracking files)
    forced  the final inventory, and the actor is told to load and use its saved tools

If "with" beats "empty", the gain lives in the artifacts; if "forced" beats "with",
the agent under-uses what it built. No reflection: only games.

    uv run python scripts/ablate_inventory.py --dry                     # scripted model, no API calls
    uv run python scripts/ablate_inventory.py --plan                    # cost estimate
    uv run python scripts/ablate_inventory.py --yes --cap 8             # paid
    uv run python scripts/ablate_inventory.py --report                  # writes reports/17_artifact_ablation.md

Output (git-ignored): runs/<run>/ablation_checkpoint_NNN/<arm>/ with transcripts and
a ledger. A second paid call skips games already played. Ablation spend is not
learning cost.
"""

import argparse
import json
import sys
from pathlib import Path

from envs.games import GAMES
from harness.anthropic_model import BILLING, ModelSpec
from harness.episode import EpisodeConfig, GameResult
from harness.inventory import empty_inventory
from harness.keys import load_key
from harness.ledger import BudgetExceeded, Ledger
from harness.runner import RunConfig, _Job, _play_checkpoint
from harness.scripted import first_legal_factory

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "17_artifact_ablation.md"
HARD_CAP = 15.0
ARMS = ("with", "empty", "forced")
FORCED = ("Your inventory holds tools you saved in earlier rounds. Load them with load_python and use "
          "them to choose your moves in this game.")
# The two high-effort Hex Sonnet lineages: the ones that improved (report 12).
DEFAULT_RUNS = ("sonnet_reflect_high", "sonnet_reflect_high_rep2")
EFFORT = "medium"  # actor effort in every run


def final_checkpoint(run_dir: Path) -> int:
    return len(json.loads((run_dir / "results.json").read_text())["checkpoints"]) - 1


def arm_dir(run_dir: Path, t: int, arm: str) -> Path:
    return run_dir / f"ablation_checkpoint_{t:03d}" / arm


def jobs(run_dir: Path, t: int, arm: str, n_id: int) -> list[_Job]:
    cfg = json.loads((run_dir / "results.json").read_text())["config"]
    spec = GAMES[cfg.get("game", "hex")]
    bank = spec.banks({"train": 1, "id": n_id, "ood": 1}, cfg["openings"], t)["id"]
    levels = cfg["train_id_levels"]
    base = arm_dir(run_dir, t, arm) / "games"
    out = []
    for i, opening in enumerate(bank):
        game_id = f"ablation_{t:03d}_{arm}_g{i + 1:02d}_{spec.colours[opening.actor]}"
        out.append(_Job("id", i, game_id, opening, levels[i % len(levels)], base / "sessions" / game_id,
                        base / f"{game_id}.json"))
    return out


def inventory_for(run_dir: Path, t: int, arm: str) -> Path:
    if arm == "empty":
        path = arm_dir(run_dir, t, arm) / "inventory"
        return path if path.exists() else empty_inventory(path)
    return run_dir / "inventories" / f"checkpoint_{t:03d}"


def eval_cost_per_game(run_dir: Path, t: int) -> float:
    """Billed cost of one held-out game at checkpoint t in the original run."""
    entries = [json.loads(x) for x in (run_dir / "ledger.jsonl").read_text().splitlines()]
    entries = [e for e in entries if e["checkpoint"] == t and e["phase"] == "eval"]
    games = len({e["episode"] for e in entries})
    return sum(e.get("reported_cost") or 0 for e in entries) / max(1, games)


def tool_use(inventory: Path, transcripts: list[Path]) -> int:
    """Games whose Python code calls an entrypoint of an active artifact (as report 10 counts it)."""
    arts = json.loads((inventory / "tracking" / "artifacts.json").read_text())["artifacts"]
    funcs = [e.partition(":")[2] for a in arts if a["status"] == "active" for e in a["entrypoints"]]
    n = 0
    for f in transcripts:
        code = " ".join(str(c["args"].get("code", "")) for m in json.loads(f.read_text())["messages"]
                        if m["role"] == "assistant" for c in m.get("tool_calls", []) if c["name"] == "python")
        n += any(f"{fn}(" in code.replace(f"def {fn}(", "") for fn in funcs)
    return n


def play_arm(run_dir: Path, t: int, arm: str, n_id: int, factory, ledger: Ledger, workers: int) -> None:
    cfg = json.loads((run_dir / "results.json").read_text())["config"]
    todo = [j for j in jobs(run_dir, t, arm, n_id) if not j.transcript.exists()]
    if not todo:
        return
    run_cfg = RunConfig(
        game=cfg.get("game", "hex"), train_id_levels=tuple(cfg["train_id_levels"]),
        ood_levels=tuple(cfg["ood_levels"]), workers=workers,
        episode=EpisodeConfig(max_calls=cfg["episode"]["max_calls"], tool_timeout=cfg["episode"]["tool_timeout"],
                              extra_instruction=FORCED if arm == "forced" else ""),
    )
    # `run_dir` hides the whole original run from the actor, as in the run itself.
    _play_checkpoint(factory(), factory, todo, inventory_for(run_dir, t, arm), run_dir, t, ledger, run_cfg)


def summary(run_dir: Path, t: int, arm: str) -> dict:
    files = sorted((arm_dir(run_dir, t, arm) / "games").glob("*.json"))
    results = [GameResult(**json.loads(f.read_text())["result"]) for f in files]
    inv = inventory_for(run_dir, t, "with")
    return {"games": len(results), "wins": sum(r.score for r in results),
            "lost_to_limits": sum(r.end_reason != "finished" for r in results),
            "tool_use": tool_use(inv, files) if files else 0}


def report(runs, n_id) -> None:
    lines = [
        "# 17 Artifact ablation (limitation test 6)",
        "",
        f"Held-out ID games from each lineage's final checkpoint, {n_id} per arm, same model, effort, openings",
        "and opponents as the run. `with`: final inventory; `empty`: empty inventory; `forced`: final inventory",
        "and the actor is told to load and use its tools. Tool use counts games that call an active entrypoint.",
        "",
        "| Lineage | Checkpoint | Arm | Held-out ID | Lost to limits | Games calling a saved tool |",
        "|---|---|---|---|---|---|",
    ]
    for run in runs:
        run_dir = ROOT / "runs" / run
        t = final_checkpoint(run_dir)
        for arm in ARMS:
            s = summary(run_dir, t, arm)
            if s["games"]:
                lines.append(f"| `{run}` | {t} | {arm} | {s['wins']:g}/{s['games']} = {100 * s['wins'] / s['games']:.0f} % | "
                             f"{s['lost_to_limits']} | {s['tool_use']} |")
    REPORT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", nargs="*", default=list(DEFAULT_RUNS))
    parser.add_argument("--id", type=int, default=24, help="held-out ID games per arm (both colours)")
    parser.add_argument("--cap", type=float, default=8.0)
    parser.add_argument("--workers", type=int, default=4)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true", help="cost estimate only")
    mode.add_argument("--dry", action="store_true", help="scripted model, no API calls; writes to runs/<run>_ablation_dry")
    mode.add_argument("--yes", action="store_true", help="paid")
    mode.add_argument("--report", action="store_true")
    args = parser.parse_args(argv)
    if not 0 < args.cap <= HARD_CAP:
        parser.error(f"--cap must be between 0 and {HARD_CAP:.2f}")
    if args.report:
        report(args.runs, args.id)
        return 0
    total = 0.0
    for run in args.runs:
        run_dir = ROOT / "runs" / run
        t = final_checkpoint(run_dir)
        per_game = eval_cost_per_game(run_dir, t)
        left = sum(1 for arm in ARMS for j in jobs(run_dir, t, arm, args.id) if not j.transcript.exists())
        total += left * per_game
        print(f"{run}: checkpoint {t}, {left} games to play at ~${per_game:.3f} each = ${left * per_game:.2f}")
    print(f"estimated total ${total:.2f}; the forced arm may cost more per game (more tool calls)")
    if args.plan:
        return 0
    key = None if args.dry else load_key("OPENROUTER_API_KEY")
    if not args.dry and not key:
        print("no OPENROUTER_API_KEY in the environment or .env")
        return 1
    plans = []
    for run in args.runs:
        run_dir = ROOT / "runs" / run
        model_id = json.loads((run_dir / "results.json").read_text())["model"]
        t = final_checkpoint(run_dir)
        if args.dry:
            # A scripted copy: the original run is read, nothing is written into it.
            import shutil

            dry_dir = ROOT / "runs" / f"{run}_ablation_dry"
            if not dry_dir.exists():
                dry_dir.mkdir(parents=True)
                for name in ("results.json", "ledger.jsonl"):
                    shutil.copy(run_dir / name, dry_dir / name)
                shutil.copytree(run_dir / "inventories" / f"checkpoint_{t:03d}",
                                dry_dir / "inventories" / f"checkpoint_{t:03d}")
            run_dir, factory = dry_dir, first_legal_factory(name="scripted")
        else:
            factory = ModelSpec(model_id, key=key, effort=EFFORT, thinking_display="summarized")
        for arm in ARMS:
            ledger = Ledger(BILLING[model_id], arm_dir(run_dir, t, arm) / "ledger.jsonl", billing=BILLING[model_id],
                            cap=args.cap)
            for e in Ledger.read(ledger.path):
                ledger.add_entry(e, write=False)
            plans.append((run, run_dir, t, arm, factory, ledger))
    # The cap covers every arm of every run, including earlier launches.
    total = sum(p[-1].billed() for p in plans)
    for run, run_dir, t, arm, factory, ledger in plans:
        ledger.prior_billed = total - ledger.billed()
        ledger.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            play_arm(run_dir, t, arm, args.id, factory, ledger, args.workers)
        except BudgetExceeded as exc:
            print(f"stopped: {exc}")
            return 0
        total = ledger.billed()
        s = summary(run_dir, t, arm)
        print(f"{run} {arm}: {s['wins']:g}/{s['games']} held-out ID; ${total:.2f} of ablation billed")
    if not args.dry:
        report(args.runs, args.id)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
