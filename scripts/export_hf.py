"""Build a Hugging Face dataset from the model runs, locally. Nothing is uploaded.

    uv run python scripts/export_hf.py

Writes export/agent-plasticity-hex/ (git-ignored): data/*.jsonl and README.md.
Every string is scrubbed of local paths and the user name, and the export stops
if anything that looks like a key, token or email address is left.
"""

import json
import re
import shutil
import sys
from pathlib import Path

from envs.hex_feedback import diagnose_game
from envs.hex_openings import BANK_FILE, OOD_LEVELS, POOLED_FILE, TRAIN_ID_LEVELS, split_banks

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "export" / "agent-plasticity-hex"
CARD = Path(__file__).with_name("hf_dataset_card.md")

# Model runs only; scripted dry runs are not model data.
RUNS = [
    {"run_id": "smoke", "dir": "smoke_anthropic_claude-sonnet-5.5", "openings": "legacy",
     "report": "reports/07_smoke_run.md", "note": "Smoke run: 2 checkpoints, 4/4/2 games per checkpoint."},
    {"run_id": "lineage_a", "dir": "lineage_a", "openings": "contested", "report": "reports/10_lineage_a.md",
     "note": "Stopped by hand after checkpoint 0: the ID opening bank was harder than train. "
             "A few checkpoint-1 games were played before the stop; they are flagged checkpoint_complete = false."},
    {"run_id": "lineage_a2", "dir": "lineage_a2", "openings": "pooled", "report": "reports/10_lineage_a2.md",
     "note": "Main run: 8 checkpoints, 8/12/4 games per checkpoint, pooled openings."},
    {"run_id": "sonnet_reflect_high", "dir": "sonnet_reflect_high", "openings": "pooled",
     "report": "reports/12_comparison.md", "reflect_effort": "high",
     "note": "As lineage_a2, but reflection at effort high (games at medium)."},
    {"run_id": "sonnet_reflect_high_rep2", "dir": "sonnet_reflect_high_rep2", "openings": "pooled",
     "report": "reports/12_comparison.md", "reflect_effort": "high",
     "note": "Replicate of sonnet_reflect_high (same settings, new model samples)."},
    {"run_id": "sonnet_medium_rep2", "dir": "sonnet_medium_rep2", "openings": "pooled",
     "report": "reports/12_comparison.md",
     "note": "Replicate of lineage_a2 (reflection at medium effort), played with 3 workers."},
    {"run_id": "haiku_r20", "dir": "haiku_r20", "openings": "pooled", "report": "reports/12_comparison.md",
     "note": "Claude Haiku 5.5, 20 rounds (the paper's checkpoint count), 20/24/8 games per checkpoint."},
]
EFFORT = "medium"  # actor effort in every run
PROVIDER = "openrouter"

# --- scrubbing --------------------------------------------------------------

_USERS = re.compile(r"/Users/[^/\s\"'\\]+")
_UNSCRUBBED = re.compile(r"/Users/(?!<user>)[^/\s\"'\\]+|/var/folders/(?!<tmp>)[^/\s\"'\\]+")
_TEMP = re.compile(r"/var/folders/[^/\s\"'\\]+/[^/\s\"'\\]+")  # per-user macOS temp folder
_SECRETS = {
    "openrouter key": re.compile(r"sk-or-[A-Za-z0-9_-]{8,}"),
    "anthropic key": re.compile(r"sk-ant-[A-Za-z0-9_-]{8,}"),
    "bearer token": re.compile(r"Bearer\s+[A-Za-z0-9._-]{16,}"),
    "key assignment": re.compile(r"(OPENROUTER|ANTHROPIC)_API_KEY\s*=\s*\S+"),
    "aws key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "github token": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    # not right after a backslash, so "\n@decorator.name" in escaped code is not an address
    "email": re.compile(r"(?<![\\A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
}


def scrub(value):
    if isinstance(value, str):
        value = value.replace(str(ROOT), "<repo>")
        value = _USERS.sub("/Users/<user>", value)
        value = _TEMP.sub("/var/folders/<tmp>", value)
        return value.replace("evahill", "<user>")
    if isinstance(value, list):
        return [scrub(v) for v in value]
    if isinstance(value, dict):
        return {k: scrub(v) for k, v in value.items()}
    return value


def secret_hits(text: str) -> list[str]:
    return [name for name, pattern in _SECRETS.items() if pattern.search(text)]


# --- tables -----------------------------------------------------------------

def ledger_by_episode(run_dir: Path) -> dict:
    out = {}
    for line in (run_dir / "ledger.jsonl").read_text().splitlines():
        e = json.loads(line)
        u = out.setdefault(e["episode"], {"calls": 0, "input_tokens": 0, "cached_input_tokens": 0,
                                          "cache_write_tokens": 0, "output_tokens": 0, "cost_usd": 0.0})
        u["calls"] += 1
        for k in ("input_tokens", "cached_input_tokens", "cache_write_tokens", "output_tokens"):
            u[k] += e.get(k, 0) or 0
        u["cost_usd"] = round(u["cost_usd"] + (e.get("reported_cost") or 0), 6)
    return out


def calls_rows(run):
    run_dir = ROOT / "runs" / run["dir"]
    for line in (run_dir / "ledger.jsonl").read_text().splitlines():
        e = json.loads(line)
        yield {"run_id": run["run_id"], **{k: e.get(k) for k in (
            "checkpoint", "phase", "episode", "input_tokens", "cached_input_tokens",
            "cache_write_tokens", "output_tokens")}, "cost_usd": e.get("reported_cost")}


def run_row(run, results):
    cfg = results["config"]
    return {
        "run_id": run["run_id"], "model": results["model"], "provider": PROVIDER, "effort": EFFORT,
        "reflect_effort": run.get("reflect_effort", EFFORT),
        "openings": run["openings"], "rounds": cfg["rounds"], "games_per_checkpoint": cfg["games"],
        "train_id_levels": cfg["train_id_levels"], "ood_levels": cfg["ood_levels"],
        "actor_max_calls": cfg["episode"]["max_calls"], "reflection_max_calls": cfg["reflection"]["max_calls"],
        "reflection_max_attempts": cfg["reflection"]["max_attempts"],
        "checkpoints_completed": len(results["checkpoints"]), "stopped": results.get("stopped"),
        "billed_usd": round(results.get("billed", 0.0), 4), "learning_cost_usd": round(results["learning_cost"], 4),
        "plasticity": results.get("plasticity"), "report": run["report"], "note": run["note"],
    }


def checkpoint_rows(run, results):
    for c in results["checkpoints"]:
        refl = c.get("reflection")
        yield {
            "run_id": run["run_id"], "checkpoint": c["t"], "learning_cost_usd": round(c["cost_cumulative"], 4),
            **{f"{s}_wins": c[s]["points"] for s in ("train", "id", "ood")},
            **{f"{s}_games": c[s]["games"] for s in ("train", "id", "ood")},
            "unfinished_games": sum(c[s]["unfinished"] for s in ("train", "id", "ood")),
            "reflection_accepted": None if refl is None else refl["accepted"],
            "reflection_attempts": None if refl is None else refl["attempts"],
        }


def game_rows(run, results, usage):
    run_dir = ROOT / "runs" / run["dir"]
    complete = {c["t"] for c in results["checkpoints"]}
    for f in sorted(run_dir.glob("games/checkpoint_*/*/*.json")):
        g = json.loads(f.read_text())
        r = g["result"]
        t = int(r["game_id"].split("_")[1])
        split = r["game_id"].split("_")[2]
        index = int(r["game_id"].split("_g")[1][:2]) - 1
        levels = OOD_LEVELS if split == "ood" else TRAIN_ID_LEVELS
        yield {
            "run_id": run["run_id"], "checkpoint": t, "checkpoint_complete": t in complete, "split": split,
            "game_id": r["game_id"], "actor": "red" if r["actor"] == "X" else "blue",
            "opponent_nodes_per_move": levels[index % len(levels)], "opening": g["opening"],
            "moves": r["moves"], "winner": r["winner"], "score": r["score"], "end_reason": r["end_reason"],
            "model_calls": r["model_calls"], "invalid_submissions": r["invalid_submissions"],
            "diagnostics": diagnose_game([(m["before"], m["action"]) for m in r["moves"]]),
            "usage": usage.get(r["game_id"]), "messages": g["messages"],
        }


def reflection_rows(run, usage):
    run_dir = ROOT / "runs" / run["dir"]
    for f in sorted(run_dir.glob("reflect/checkpoint_*/attempt_*/attempt_*.json")):
        d = json.loads(f.read_text())
        t = int(f.parts[-3].split("_")[1])
        episode = f"checkpoint_{t:03d}_attempt_{d['attempt']}"
        yield {"run_id": run["run_id"], "checkpoint": t, "attempt": d["attempt"], "calls": d["calls"],
               "accepted": d["accepted"], "errors": d["errors"], "usage": usage.get(episode),
               "messages": d["messages"]}


def inventory_rows(run):
    run_dir = ROOT / "runs" / run["dir"]
    for inv in sorted(run_dir.glob("inventories/checkpoint_*")):
        t = int(inv.name.split("_")[1])
        for p in sorted(inv.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                yield {"run_id": run["run_id"], "checkpoint": t, "path": p.relative_to(inv).as_posix(),
                       "content": p.read_text(errors="replace")}


def opening_rows():
    for bank, path in (("contested", BANK_FILE), ("pooled", POOLED_FILE)):
        for split, by in json.loads(path.read_text())["banks"].items():
            for actor, entries in by.items():
                for i, e in enumerate(entries):
                    moves = e["moves"] if isinstance(e, dict) else e
                    yield {"bank": bank, "split": split, "actor": "red" if actor == "X" else "blue", "index": i,
                           "moves": moves, "difficulty": e.get("difficulty") if isinstance(e, dict) else None}
    for split, bank in split_banks({"train": 4, "id": 4, "ood": 2}, source="legacy").items():  # the smoke run's
        for i, o in enumerate(bank):
            yield {"bank": "legacy", "split": split, "actor": "red" if o.actor == "X" else "blue", "index": i,
                   "moves": list(o.moves), "difficulty": None}


# --- main -------------------------------------------------------------------

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "data").mkdir(parents=True)
    tables = {name: [] for name in ("runs", "checkpoints", "games", "reflections", "inventories", "calls", "openings")}
    for run in RUNS:
        run_dir = ROOT / "runs" / run["dir"]
        if not (run_dir / "results.json").exists():
            print(f"skipping {run['run_id']}: no results yet")
            continue
        results = json.loads((run_dir / "results.json").read_text())
        usage = ledger_by_episode(run_dir)
        tables["runs"].append(run_row(run, results))
        tables["checkpoints"] += checkpoint_rows(run, results)
        tables["games"] += game_rows(run, results, usage)
        tables["reflections"] += reflection_rows(run, usage)
        tables["inventories"] += inventory_rows(run)
        tables["calls"] += calls_rows(run)
    tables["openings"] += opening_rows()

    problems = []
    for name, rows in tables.items():
        lines = [json.dumps(scrub(r), ensure_ascii=False) for r in rows]
        for i, line in enumerate(lines):
            if "evahill" in line or _UNSCRUBBED.search(line):
                problems.append(f"{name} row {i}: unscrubbed path or name")
            for hit in secret_hits(line):
                problems.append(f"{name} row {i}: {hit}")
        (OUT / "data" / f"{name}.jsonl").write_text("\n".join(lines) + "\n")
        print(f"{name}: {len(rows)} rows, {(OUT / 'data' / f'{name}.jsonl').stat().st_size / 1e6:.1f} MB")
    if problems:
        shutil.rmtree(OUT)
        print("EXPORT STOPPED, nothing written:\n  " + "\n  ".join(problems[:20]))
        return 1
    shutil.copy(CARD, OUT / "README.md")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
