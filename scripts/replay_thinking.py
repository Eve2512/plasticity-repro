"""Replay saved reflection turns to get thinking summaries for runs that kept none.

The runs up to plan A did not save the model's thinking (docs/PROTOCOL_NOTES.md,
"Thinking"). This script sends each saved reflection context again, exactly up
to one assistant turn, with `display: "summarized"`, and stores the new thinking
summary next to the call the model made then and the call it makes now. The
summary is a fresh sample on the same input, not the original reasoning; where
the replayed call matches the recorded one it is the closest proxy available.
Nothing is executed: only the model's next turn is asked for.

    uv run python scripts/replay_thinking.py --dry               # plan and cost estimate, no calls
    uv run python scripts/replay_thinking.py --yes --cap 9       # paid
    uv run python scripts/replay_thinking.py --report            # writes reports/16_thinking_replay.md

Output (git-ignored): runs/<run>/thinking_replay/checkpoint_NNN_attempt_N.jsonl,
one line per replayed turn, and runs/<run>/thinking_replay/ledger.jsonl. A second
paid call resumes where the first stopped. Replay spend is not learning cost.
"""

import argparse
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from harness.anthropic_model import BILLING, ModelSpec
from harness.keys import load_key
from harness.ledger import BudgetExceeded, Ledger
from harness.model import BASH, ToolCall
from harness.prompts import SYSTEM

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "16_thinking_replay.md"
HARD_CAP = 15.0

# Model runs with reflection logs, and the reflection effort each used (the export's list, scripts/export_hf.py).
RUNS = {
    "smoke_anthropic_claude-sonnet-5.5": "medium", "lineage_a": "medium", "lineage_a2": "medium",
    "sonnet_medium_rep2": "medium", "sonnet_reflect_high": "high", "sonnet_reflect_high_rep2": "high",
    "haiku_r20": "medium", "hex_haiku_reflect_high": "high", "hex_haiku_reflect_high_rep2": "high",
    "go_sonnet_reflect_high": "high", "go_sonnet_reflect_high_rep2": "high",
    "go_haiku_reflect_high": "high", "go_haiku_reflect_high_rep2": "high",
}


def attempts(run: str) -> list[Path]:
    return sorted((ROOT / "runs" / run / "reflect").glob("checkpoint_*/attempt_*/attempt_*.json"))


def out_path(log: Path) -> Path:
    run_dir = log.parents[3]
    return run_dir / "thinking_replay" / f"{log.parents[1].name}_{log.parent.name}.jsonl"


def contexts(messages: list[dict]):
    """(index, context before the assistant turn, the recorded turn) for every assistant turn."""
    for i, m in enumerate(messages):
        if m["role"] == "assistant":
            context = [dict(x, tool_calls=[ToolCall(c["id"], c["name"], c["args"]) for c in x["tool_calls"]])
                       if x["role"] == "assistant" else x for x in messages[:i]]
            yield i, context, m


def same_calls(recorded: list[dict], replayed) -> bool:
    return [(c["name"], c["args"]) for c in recorded] == [(c.name, c.args) for c in replayed]


def recorded_cost(run: str) -> float:
    """What the original reflections were billed: the replay sends the same contexts."""
    lines = (ROOT / "runs" / run / "ledger.jsonl").read_text().splitlines()
    return sum(e.get("reported_cost") or 0 for e in map(json.loads, lines) if e["phase"] == "reflect")


def replay_attempt(model, log: Path, ledger: Ledger, lock: threading.Lock) -> int:
    messages = json.loads(log.read_text())["messages"]
    out = out_path(log)
    done = len(out.read_text().splitlines()) if out.exists() else 0
    checkpoint = int(log.parents[1].name.split("_")[1])
    n = 0
    for k, (i, context, recorded) in enumerate(contexts(messages)):
        if k < done:
            continue
        with lock:
            ledger.check_budget()
        turn = model.step(SYSTEM, context, [BASH])
        row = {
            "message_index": i, "turn": k + 1,
            "recorded": {"text": recorded["content"], "tool_calls": recorded["tool_calls"]},
            "replayed": {"text": turn.text, "tool_calls": [{"id": c.id, "name": c.name, "args": c.args}
                                                           for c in turn.tool_calls]},
            "same_call": same_calls(recorded["tool_calls"], turn.tool_calls),
            "thinking": turn.thinking,
            "output_tokens": turn.usage.output_tokens,
        }
        with lock:
            ledger.add(checkpoint, "reflect", out.stem, turn.usage)  # own ledger file, never learning cost
            out.parent.mkdir(exist_ok=True)
            with out.open("a") as fh:
                fh.write(json.dumps(row) + "\n")
        n += 1
    return n


def plan(runs) -> float:
    total = 0.0
    print(f"{'run':38} {'effort':6} {'attempts':>8} {'turns':>6} {'done':>6} {'est. $':>7}")
    for run in runs:
        logs = attempts(run)
        turns = sum(sum(m["role"] == "assistant" for m in json.loads(f.read_text())["messages"]) for f in logs)
        done = sum(len(out_path(f).read_text().splitlines()) for f in logs if out_path(f).exists())
        est = recorded_cost(run) * (1 - done / turns) if turns else 0.0
        total += est
        print(f"{run:38} {RUNS[run]:6} {len(logs):8} {turns:6} {done:6} {est:7.2f}")
    print(f"estimated total ${total:.2f} (the original reflections' billed cost, minus turns already replayed)")
    return total


def report(runs) -> None:
    lines = [
        "# 16 Thinking replay of past reflections",
        "",
        "Each saved reflection turn was sent again with the same context and `display: \"summarized\"`",
        "(scripts/replay_thinking.py). The summary is a new sample on identical input, not the original",
        "reasoning. \"Same call\" = the replayed turn makes exactly the recorded Bash calls (or none).",
        "",
        "| Run | Reflection effort | Turns replayed | Same call | Turns with a summary | Mean summary length (chars) |",
        "|---|---|---|---|---|---|",
    ]
    for run in runs:
        rows = [json.loads(line) for f in attempts(run) if out_path(f).exists()
                for line in out_path(f).read_text().splitlines()]
        if not rows:
            continue
        with_summary = [r for r in rows if r["thinking"]]
        mean = sum(len(r["thinking"]) for r in with_summary) / len(with_summary) if with_summary else 0
        lines.append(f"| `{run}` | {RUNS[run]} | {len(rows)} | {100 * sum(r['same_call'] for r in rows) / len(rows):.0f} % | "
                     f"{100 * len(with_summary) / len(rows):.0f} % | {mean:.0f} |")
    REPORT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", nargs="*", help="default: every model run with reflection logs")
    parser.add_argument("--cap", type=float, default=11.0)
    parser.add_argument("--workers", type=int, default=4, help="attempts replayed at once")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry", action="store_true", help="plan and cost estimate only")
    mode.add_argument("--yes", action="store_true", help="paid replay")
    mode.add_argument("--report", action="store_true", help="summarise what was replayed")
    args = parser.parse_args(argv)
    runs = args.runs or [r for r in RUNS if attempts(r)]
    unknown = [r for r in runs if r not in RUNS]
    if unknown:
        parser.error(f"not a model run with reflections: {', '.join(unknown)}")
    if not 0 < args.cap <= HARD_CAP:
        parser.error(f"--cap must be between 0 and {HARD_CAP:.2f}")
    if args.report:
        report(runs)
        return 0
    plan(runs)
    if args.dry:
        return 0
    key = load_key("OPENROUTER_API_KEY")
    if not key:
        print("no OPENROUTER_API_KEY in the environment or .env")
        return 1
    def replay_ledger(run):
        model_id = json.loads((ROOT / "runs" / run / "results.json").read_text())["model"]
        ledger = Ledger(BILLING[model_id], ROOT / "runs" / run / "thinking_replay" / "ledger.jsonl",
                        billing=BILLING[model_id], cap=args.cap)
        for e in Ledger.read(ledger.path):
            ledger.add_entry(e, write=False)
        return model_id, ledger

    # The cap covers every replay so far, across runs and earlier launches.
    spent = {run: replay_ledger(run)[1].billed() for run in RUNS if attempts(run)}
    for run in runs:
        model_id, ledger = replay_ledger(run)
        ledger.prior_billed = sum(v for r, v in spent.items() if r != run)
        ledger.path.parent.mkdir(parents=True, exist_ok=True)
        model = ModelSpec(model_id, key=key, effort=RUNS[run], thinking_display="summarized")()
        lock = threading.Lock()
        try:
            with ThreadPoolExecutor(args.workers) as pool:
                done = sum(pool.map(lambda f: replay_attempt(model, f, ledger, lock), attempts(run)))
        except BudgetExceeded as exc:
            print(f"stopped: {exc}")
            return 0
        spent[run] = ledger.billed() - ledger.prior_billed
        print(f"{run}: {done} turns replayed; ${ledger.billed():.2f} of replay billed so far")
    report(runs)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
