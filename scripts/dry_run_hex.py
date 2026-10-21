"""End-to-end Hex lineage with a scripted model: no API calls, no cost.

The scripted actor plays the first legal action until its inventory has
tools/greedy.py, then loads and uses that tool. The scripted reflector writes the
tool (and tracking files) at its first reflection and changes nothing after.
This checks the pipeline (sandbox, inventory validation, ledger, metrics), not
any model. Writes reports/06_dry_run.md; run files go to runs/dry_run (git-ignored).
"""

import itertools
import json
import re
import shlex
from pathlib import Path

from harness.episode import EpisodeConfig
from harness.model import ModelTurn, ScriptedModel, ToolCall
from harness.reflection import ReflectionConfig
from harness.runner import RunConfig, reset, run_lineage
from plasticity.pricing import PriceTable

ROOT = Path(__file__).resolve().parent.parent
RUN = ROOT / "runs" / "dry_run"
REPORT = ROOT / "reports" / "06_dry_run.md"
_ids = itertools.count()

GREEDY = '''\
N = 6
COLS = "abcdef"


def _neighbours(i):
    r, c = divmod(i, N)
    out = []
    for dr, dc in ((-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)):
        if 0 <= r + dr < N and 0 <= c + dc < N:
            out.append((r + dr) * N + c + dc)
    return out


def _index(name):
    return (int(name[1:]) - 1) * N + COLS.index(name[0])


def _distance(cells, player):
    """Empty cells `player` still needs: Dijkstra over cell costs 0/1."""
    big = 10 ** 6
    dist = [big] * (N * N)
    starts = range(N) if player == "X" else range(0, N * N, N)
    frontier = []
    for i in starts:
        if cells[i] in (".", player):
            dist[i] = 0 if cells[i] == player else 1
            frontier.append(i)
    while frontier:
        frontier.sort(key=lambda i: dist[i])
        i = frontier.pop(0)
        for j in _neighbours(i):
            if cells[j] not in (".", player):
                continue
            d = dist[i] + (0 if cells[j] == player else 1)
            if d < dist[j]:
                dist[j] = d
                frontier.append(j)
    ends = range(N * (N - 1), N * N) if player == "X" else range(N - 1, N * N, N)
    return min(dist[i] for i in ends)


def choose(moves, me):
    cells = ["."] * (N * N)
    for k, m in enumerate(moves):
        cells[_index(m)] = "X" if k % 2 == 0 else "O"
    them = "O" if me == "X" else "X"
    best, best_score = None, None
    for i in range(N * N):
        if cells[i] != ".":
            continue
        cells[i] = me
        mine = _distance(cells, me)
        score = 10 ** 6 if mine == 0 else _distance(cells, them) - mine
        cells[i] = "."
        if best_score is None or score > best_score:
            best, best_score = i, score
    r, c = divmod(best, N)
    return COLS[c] + str(r + 1)


def play(api):
    state = api["get_state"]()
    while not state["winner"]:
        state = api["submit_action"](choose(state["moves"], state["you_play"]))
    return state["winner"]
'''

TRACKING = {
    "failure_modes.json": {"schema_version": "failure_modes.v1", "failure_modes": [
        {"id": "FM-0001", "description": "Moves ignore connection distance; opponent connects first.",
         "status": "active", "trajectory_ids": []}]},
    "artifacts.json": {"schema_version": "artifacts.v1", "artifacts": [
        {"id": "AR-0001", "description": "Greedy one-ply connection-distance player.", "kind": "tool",
         "paths": ["tools/greedy.py"], "entrypoints": ["tools/greedy.py:play"],
         "failure_mode_ids": ["FM-0001"], "status": "active"}]},
}


def call(name, **args):
    return ToolCall(f"c{next(_ids)}", name, args)


def actor_or_reflector(system, messages, tools):
    first = messages[0]["content"]
    assistant_turns = sum(m["role"] == "assistant" for m in messages)
    if first.startswith("A new hex game"):
        inventory = re.search(r"infrastructure is under (\S+) and is read-only", first).group(1)
        if assistant_turns == 0:
            return ModelTurn("", (call("bash", command=f"ls {inventory}/tools 2>/dev/null"),))
        listing = [m for m in messages if m["role"] == "tool"][0]["content"]
        if "greedy.py" in listing:
            code = f"load_python('{inventory}/tools/greedy.py')\nplay(game_api)"
        else:
            code = ("s = game_api['get_state']()\nwhile not s['winner']:\n"
                    "    s = game_api['submit_action'](game_api['get_legal_actions']()[0])")
        return ModelTurn("", (call("python", code=code),))

    # reflection
    workspace = re.search(r"infrastructure is under (\S+)/inventory\.", first).group(1)
    if assistant_turns == 0:
        exists = f"test -f {workspace}/inventory/tools/greedy.py"
        writes = [f"mkdir -p {workspace}/inventory/tools",
                  f"printf %s {shlex.quote(GREEDY)} > {workspace}/inventory/tools/greedy.py"]
        writes += [f"printf %s {shlex.quote(json.dumps(v, indent=1))} > {workspace}/inventory/tracking/{k}"
                   for k, v in TRACKING.items()]
        return ModelTurn("", (call("bash", command=f"{exists} || ({' && '.join(writes)})"),))
    if assistant_turns == 1:
        validator = first.split("run the validator (")[1].split(")")[0]
        return ModelTurn("", (call("bash", command=validator),))
    return ModelTurn("Inventory updated and validated.")


def main():
    reset(RUN)
    cfg = RunConfig(
        rounds=3,
        games={"train": 6, "id": 8, "ood": 4},
        openings="legacy",  # report 06 was made with the legacy banks
        ood_levels=(100_000,),  # 1M nodes would make the dry run slow; the real run uses OOD_LEVELS
        episode=EpisodeConfig(max_calls=32, tool_timeout=240),
        reflection=ReflectionConfig(max_calls=50, bash_timeout=300, max_attempts=3),
        prices=PriceTable(3.0, 15.0),  # hypothetical; the scripted model's tokens are estimates
    )
    results = run_lineage(ScriptedModel(actor_or_reflector, name="scripted-dry-run"), RUN, cfg)

    lines = [
        "# 06 Dry run of the Hex harness (scripted model, no API calls)",
        "",
        "A scripted model plays the first legal action until its inventory has a tool; its first",
        "reflection writes a greedy connection-distance tool. This tests the pipeline, not a model.",
        "Token counts are estimates (4 characters per token) priced at a hypothetical $3 / $15 per",
        "million input / output tokens.",
        "",
        "| Checkpoint | Cumulative learning cost | Train | Held-out ID | Held-out OOD | Reflection |",
        "|---|---|---|---|---|---|",
    ]
    for c in results["checkpoints"]:
        refl = c.get("reflection")
        refl_text = "–" if refl is None else ("accepted" if refl["accepted"] else "rejected") + \
            f" after {len(refl['attempts'])} attempt(s)"
        cells = [f"{100 * c[s]['points'] / c[s]['games']:.0f} % ({c[s]['games']})" for s in ("train", "id", "ood")]
        lines.append(f"| {c['t']} | ${c['cost_cumulative']:.3f} | " + " | ".join(cells) + f" | {refl_text} |")
    p = results["plasticity"]
    lines += [
        "",
        f"Held-out ID P_sat: {p.get('p_sat', float('nan')):.0f} points per $1,000 ({p.get('p_sat_kind')}), "
        f"rise p-value {p.get('rise_p_value', float('nan')):.3g}.",
        "The P_sat value is meaningless here: the scripted model's cost is a few cents, so any",
        "gain divided by it is huge, and with 8 held-out games the rise is not significant.",
        "What the run shows: the reflection wrote a tool, the validator accepted it, the next",
        "checkpoint's actor loaded and used it, held-out games stayed hidden, and the costs",
        "and scores reached Eq. 2–5. Checkpoints 1–3 match because the engine is deterministic",
        "and the inventory did not change.",
        "",
    ]
    REPORT.write_text("\n".join(lines))
    print(f"wrote {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
