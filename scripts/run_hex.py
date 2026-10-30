"""Run one Hex or Go lineage with a Claude model (or, via harness/chat_model.py, Muse Spark or GLM) and write a report.

    uv run python scripts/run_hex.py --model anthropic/claude-sonnet-5.5 --rounds 7 \
        --train 8 --id 12 --ood 4 --cap 17 --name lineage_a          # plan only
    ... --yes                                                          # paid run
    ... --dry                                                          # scripted model, no API calls
    ... --game go                                                      # 5x5 Go (scripts/run_go.py)

Spending stops before any call once the billed amount reaches --cap (never
above $45); completed checkpoints are kept. Keys come from the environment or
the git-ignored .env: OPENROUTER_API_KEY (default provider) or ANTHROPIC_API_KEY.
The paid report goes to reports/10_<name>.md; a dry run writes only to runs/.
"""

import argparse
import json
import sys
from pathlib import Path

from envs.games import GAMES
from harness.anthropic_model import BILLING, ModelSpec
from harness.episode import EpisodeConfig
from harness.keys import load_key
from harness.reflection import ReflectionConfig
from harness.runner import RunConfig, reset, run_lineage
from harness.scripted import first_legal_factory

ROOT = Path(__file__).resolve().parent.parent
HARD_CAP = 45.00  # the user's approved budget for this phase (2026-10-25)
PROVIDERS = {
    "openrouter": ("OPENROUTER_API_KEY", lambda m: "/" in m),
    "anthropic": ("ANTHROPIC_API_KEY", lambda m: m.startswith("claude-")),
}
def artifact_use(run_dir: Path, t: int) -> tuple[int, int, int, int]:
    """Games at checkpoint t that read, loaded, or called an entrypoint of a saved artifact; and the game count.

    Read: a Bash command names an artifact path. Loaded: Python calls load_python on the
    inventory. Called: Python code calls an entrypoint function (definitions excluded).
    """
    arts = json.loads((run_dir / "inventories" / f"checkpoint_{t:03d}" / "tracking" / "artifacts.json").read_text())
    active = [a for a in arts["artifacts"] if a["status"] == "active"]
    paths = [p for a in active for p in a["paths"]]
    funcs = [e.partition(":")[2] for a in active for e in a["entrypoints"]]
    read = loaded = called = games = 0
    for f in (run_dir / "games" / f"checkpoint_{t:03d}").glob("*/*.json"):
        games += 1
        calls = [c for m in json.loads(f.read_text())["messages"] if m["role"] == "assistant"
                 for c in m.get("tool_calls", [])]
        bash = " ".join(str(c["args"].get("command", "")) for c in calls if c["name"] == "bash")
        code = " ".join(str(c["args"].get("code", "")) for c in calls if c["name"] == "python")
        read += any(p in bash for p in paths)
        loaded += "load_python(" in code and "inventor" in code
        called += any(f"{fn}(" in code.replace(f"def {fn}(", "") for fn in funcs)
    return read, loaded, called, games


def report(results: dict, run_dir: Path, path: Path) -> None:
    cfg = results["config"]
    done = len(results["checkpoints"]) - 1
    span = f"0–{done}" if done == cfg["rounds"] else f"0–{done} completed of 0–{cfg['rounds']} planned"
    lines = [
        f"# 10 Lineage `{run_dir.name}`: {results['model']} on {GAMES[cfg.get('game', 'hex')].title}",
        "",
        f"Checkpoints {span}; games per checkpoint {cfg['games']}; openings: {cfg['openings']}.",
        *(["Reflection saw no game records (limitation test 5: experience vs compute)."]
          if cfg.get("reflection_feedback") == "none" else []),
        f"Billed ${results['billed']:.2f} (cap ${cfg['cap']:.2f}); learning cost priced the paper's way "
        f"${results['learning_cost']:.2f}.",
        "",
        "| Checkpoint | Learning cost so far | Train | Held-out ID | Held-out OOD | Unfinished | "
        "Inventory files | Games reading / loading / calling saved artifacts | Reflection |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for c in results["checkpoints"]:
        t = c["t"]
        inv = run_dir / "inventories" / f"checkpoint_{t:03d}"
        files = sum(1 for p in inv.rglob("*") if p.is_file() and "tracking" not in p.parts)
        read, loaded, called, games = artifact_use(run_dir, t)
        refl = c.get("reflection")
        refl_text = "–" if refl is None else ("accepted" if refl["accepted"] else "rejected") + \
            f" ({len(refl['attempts'])})"
        cells = [f"{100 * c[s]['points'] / c[s]['games']:.0f} %" for s in ("train", "id", "ood")]
        unfinished = sum(c[s]["unfinished"] for s in ("train", "id", "ood"))
        lines.append(f"| {t} | ${c['cost_cumulative']:.2f} | " + " | ".join(cells) +
                     f" | {unfinished} | {files} | {read} / {loaded} / {called} of {games} | {refl_text} |")
    p = results.get("plasticity") or {}
    lines += ["", "## Plasticity (held-out ID)", ""]
    if "p_sat" in p:
        gate = "passes" if p["rise_p_value"] < 0.05 else "does not pass"
        lines += [
            f"- Average plasticity (Eq. 3, last checkpoint): {p['average_plasticity']:.1f} points per $1,000.",
            f"- Saturation fit (Eq. 4): S0 = {100 * p['fit']['s0']:.1f} %, rise = {100 * p['fit']['rise']:.1f} points, "
            f"h = {p['fit']['h']:.2f}.",
            f"- P_sat (Eq. 5, paper rules): {p['p_sat']:.1f} points per $1,000 ({p['p_sat_kind']}).",
            f"- Rise against a flat curve: p = {p['rise_p_value']:.3g}; it {gate} the p < 0.05 gate from report 03.",
        ]
    else:
        lines.append("- Not enough checkpoints with learning cost to fit Eq. 4.")
    if results["stopped"]:
        lines += ["", f"Stopped early: {results['stopped']}."]
    lines.append("")
    path.write_text("\n".join(lines))


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--game", default="hex", choices=sorted(GAMES))
    parser.add_argument("--provider", default="openrouter", choices=sorted(PROVIDERS))
    parser.add_argument("--model", default="anthropic/claude-sonnet-5.5", choices=sorted(BILLING))
    parser.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    parser.add_argument("--reflect-effort", default=None, choices=["low", "medium", "high", "xhigh", "max"],
                        help="effort for reflection only (default: same as --effort); needs --workers > 1")
    parser.add_argument("--thinking-display", default="summarized", choices=["summarized", "omitted", "unset"],
                        help="ask for thinking summaries, saved in transcripts but hidden from reflection; "
                             "'unset' sends no thinking field, as in the runs before 2026-10-28")
    parser.add_argument("--no-feedback", action="store_true",
                        help="reflection gets no game records (limitation test 5: experience vs compute)")
    parser.add_argument("--rounds", type=int, default=7, help="learning rounds: checkpoints 0..rounds")
    parser.add_argument("--train", type=int, default=8)
    parser.add_argument("--id", type=int, default=12)
    parser.add_argument("--ood", type=int, default=4)
    parser.add_argument("--openings", default="pooled", choices=["pooled", "contested", "legacy"],
                        help="Go has only pooled openings")
    parser.add_argument("--cap", type=float, default=17.00)
    parser.add_argument("--name", default="lineage_a")
    parser.add_argument("--workers", type=int, default=1, help="games played at once")
    parser.add_argument("--resume", action="store_true", help="continue runs/<name> after a crash")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--yes", action="store_true", help="paid run")
    group.add_argument("--dry", action="store_true", help="scripted model, no API calls")
    args = parser.parse_args(argv)
    if not 0 < args.cap <= HARD_CAP:
        parser.error(f"--cap must be between 0 and {HARD_CAP:.2f}")
    key_name, model_matches = PROVIDERS[args.provider]
    if not model_matches(args.model):
        parser.error(f"{args.model} is not a {args.provider} model id")
    if args.openings not in GAMES[args.game].openings:
        parser.error(f"{args.game} openings: {', '.join(GAMES[args.game].openings)}")
    if args.rounds < 1 or min(args.train, args.id, args.ood) < 1:
        parser.error("need at least one round and one game per split")

    games = {"train": args.train, "id": args.id, "ood": args.ood}
    total = sum(games.values()) * (args.rounds + 1)
    print(f"{GAMES[args.game].title}: {args.model} via {args.provider}, effort {args.effort} (reflection {args.reflect_effort or args.effort}), thinking display {args.thinking_display}, "
          f"openings {args.openings}")
    print(f"checkpoints 0-{args.rounds}, games per checkpoint {games}: {total} games + {args.rounds} reflections")
    print(f"stops before any call once ${args.cap:.2f} is billed; {args.workers} game(s) at once")
    if not (args.yes or args.dry):
        print("plan only: add --yes for the paid run or --dry for a scripted run")
        return 0

    billing = BILLING[args.model]
    if args.dry:
        factory = first_legal_factory(name=f"scripted ({args.model} prices)")
    else:
        key = load_key(key_name)
        if not key:
            print(f"no {key_name} in the environment or .env")
            return 1
        display = None if args.thinking_display == "unset" else args.thinking_display
        factory = ModelSpec(args.model, key=key, effort=args.effort, provider=args.provider, thinking_display=display)
    # Games use `factory` (workers > 1); reflection uses `model`.
    if args.reflect_effort and not args.dry:
        if args.workers < 2:
            parser.error("--reflect-effort needs --workers > 1 (games then use their own model)")
        model = ModelSpec(args.model, key=key, effort=args.reflect_effort, provider=args.provider,
                          thinking_display=display)()
    else:
        model = factory()

    run_dir = ROOT / "runs" / (f"{args.name}_dry" if args.dry else args.name)
    if not args.resume:
        reset(run_dir)
    cfg = RunConfig(
        game=args.game,
        rounds=args.rounds,
        games=games,
        openings=args.openings,
        episode=EpisodeConfig(max_calls=32, tool_timeout=240),
        reflection=ReflectionConfig(max_calls=50, bash_timeout=300, max_attempts=3),
        prices=billing.undiscounted(),
        billing=billing,
        cap=args.cap,
        workers=args.workers,
        reflection_feedback="none" if args.no_feedback else "full",
    )
    results = run_lineage(model, run_dir, cfg, model_factory=factory, resume=args.resume)
    out = run_dir / "report.md" if args.dry else ROOT / "reports" / f"10_{args.name}.md"
    report(results, run_dir, out)
    print(f"wrote {out.relative_to(ROOT)}")
    print(json.dumps({k: results[k] for k in ("billed", "learning_cost", "stopped")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
