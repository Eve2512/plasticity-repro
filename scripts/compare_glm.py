"""GLM 5.3 vs Sonnet 5.5 and Haiku 5.5 on Hex and Go, reflection effort high. Writes reports/21_glm_vs_claude.md.

Same settings as report 15 (games, opponents, budgets, reflection effort high) and the same
early / late split, fixed before the GLM results were seen. GLM ran 2 games at a time per
lineage, the Claude lineages 4, and its lineages were interrupted and resumed (PROTOCOL_NOTES).

    uv run python scripts/compare_glm.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare_models import EARLY, ROOT, behaviour, id_games, pct, rate, z_test  # noqa: E402
from compare_runs import summarize  # noqa: E402

REPORT = ROOT / "reports" / "21_glm_vs_claude.md"
CELLS = {
    ("Hex", "GLM 5.3"): ["hex_glm_reflect_high", "hex_glm_reflect_high_rep2"],
    ("Hex", "Sonnet 5.5"): ["sonnet_reflect_high", "sonnet_reflect_high_rep2"],
    ("Hex", "Haiku 5.5"): ["hex_haiku_reflect_high", "hex_haiku_reflect_high_rep2"],
    ("Go", "GLM 5.3"): ["go_glm_reflect_high", "go_glm_reflect_high_rep2"],
    ("Go", "Sonnet 5.5"): ["go_sonnet_reflect_high", "go_sonnet_reflect_high_rep2"],
    ("Go", "Haiku 5.5"): ["go_haiku_reflect_high", "go_haiku_reflect_high_rep2"],
}


def learning_cost(name: str) -> float:
    """Learning cost at the last checkpoint, priced the paper's way (Eq. 2, no cache discount)."""
    cps = json.loads((ROOT / "runs" / name / "results.json").read_text())["checkpoints"]
    return cps[-1]["cost_cumulative"]


def discarded(name: str) -> float:
    """Billed for calls of checkpoints that were replayed after an interruption."""
    f = ROOT / "runs" / name / "ledger_discarded.jsonl"
    if not f.exists():
        return 0.0
    return sum(json.loads(x).get("reported_cost") or 0 for x in f.read_text().splitlines() if x.strip())


READING = [
    "", "## Reading",
    "",
    "- GLM plays worse than both Claude models on Hex (late 24 % vs Sonnet 83 % and Haiku 40 %) and level with",
    "  Haiku on Go (46 % vs 47 %), below Sonnet (60 %). Its pooled early → late change is +3 pp on both games.",
    "- GLM's checkpoint 0 is not a normal start. Every Claude game at checkpoint 0 finished; GLM lost 32 of 48",
    "  Hex games and 29 of 64 Go games there to the limits, mostly tool calls past 240 s on Hex and the 32-call",
    "  budget on Go. Its held-out ID at checkpoint 0 was 2/24 (Hex) and 5/40 (Go). After the first reflection",
    "  nearly every game finished, and ID jumped to 12/24 and 23/40.",
    "- That jump is what the metric sees. Three of the four GLM lineages pass the p < 0.05 flat-curve gate,",
    "  against one of the eight Claude lineages here, and the two Go lineages get P_sat of 48,000–60,000 points",
    "  per $1,000, over ten times the one Claude lineage that passes (3,798): a 33–39-point rise bought with $5–7 of learning cost at",
    "  GLM's prices. After checkpoint 1 GLM does not improve: pooled ID from checkpoints 1–2 to 3–10 goes 27 %",
    "  → 24 % on Hex (p = 0.65) and 58 % → 46 % on Go (p = 0.064); `go_glm_reflect_high` ends at 25 %, below",
    "  its checkpoint-1 score of 60 %. Eq. 4–5 reward a low start and a cheap first fix as plasticity. A",
    "  baseline that starts from games the agent can finish (or a fit that leaves out checkpoint 0) would not.",
    "- GLM reflects at the edge of its budget: 39–49 of 50 calls per round, against 7–9 for Hex Sonnet and",
    "  15–24 for Go Sonnet, and it revised code at 8–9 of 10 reflections. More reflection did not mean better",
    "  reflection here, as with Haiku at effort high (report 15).",
    "- Hex run 1's fall from 75 % to 0 % at checkpoints 2–3 is a bug its own reflection wrote into its search",
    "  tool; model-free replays reproduce it, and a one-line fix of the checkpoint-2 tool scores 12/12 (report",
    "  20). Hex run 2 never passed 25 %.",
    "- At the paper's pricing GLM's learning cost was $5–7 per lineage, against $12–34 for Sonnet and $3 for",
    "  Haiku, but its lineages billed $11–15 each in total, close to Hex Sonnet: held-out games and replayed",
    "  checkpoints ($0.29–1.86 per lineage) are not learning cost.",
    "- Per colour, GLM's Hex gain is first-player only (22 % → 36 %); as second player it fell (19 % → 11 %).",
    "- Caveats: GLM ran 2 games at a time per lineage, Claude 4, so GLM's tool calls had less CPU contention",
    "  under the 240 s limit, which would favour GLM, not explain its lower scores. Every GLM lineage was",
    "  interrupted and resumed, replaying one checkpoint as a new sample.",
]


def main():
    lines = [
        "# 21 GLM 5.3 vs Sonnet 5.5 and Haiku 5.5 on Hex and Go (reflection effort high)",
        "",
        "Plan C ran GLM 5.3 (`z-ai/glm-5.3`) with the settings of report 15: actor effort medium, reflection",
        "effort high, two lineages per game, checkpoints 0–10; Hex 8 / 12 / 4 games per checkpoint, Go 8 / 20 / 4.",
        f"Early = checkpoints 0–{EARLY - 1}; late = checkpoint {EARLY} onward. GLM ran 2 games at a time per lineage",
        "(Claude 4), and all four GLM lineages were stopped by the key's spending limit and resumed with",
        "the unfinished checkpoint replayed (docs/PROTOCOL_NOTES.md).",
        "",
        "## Held-out ID, early → late",
        "",
        "| Game | Model | Early | Late | Change | z | p |",
        "|---|---|---|---|---|---|---|",
    ]
    late, games_by_cell, summaries = {}, {}, {}
    for (game, model), names in CELLS.items():
        games = [g for n in names for g in id_games(n)]
        for n in names:
            summaries[n] = summarize(n)
        e, l_ = rate([g for g in games if g[0] < EARLY]), rate([g for g in games if g[0] >= EARLY])
        z, p = z_test(*e, *l_)
        late[(game, model)] = l_
        games_by_cell[(game, model)] = games
        lines.append(f"| {game} | {model} | {pct(*e)} | {pct(*l_)} | "
                     f"{100 * (l_[0] / l_[1] - e[0] / e[1]):+.0f} pp | {z:.2f} | {p:.2g} |")

    lines += ["", "## GLM against each Claude model, late checkpoints", "",
              "| Game | GLM late | Against | Their late | z | p |", "|---|---|---|---|---|---|"]
    for game in ("Hex", "Go"):
        g = late[(game, "GLM 5.3")]
        for other in ("Sonnet 5.5", "Haiku 5.5"):
            o = late[(game, other)]
            z, p = z_test(*o, *g)
            lines.append(f"| {game} | {pct(*g)} | {other} | {pct(*o)} | {z:.2f} | {p:.2g} |")

    lines += ["", "## Per colour, GLM (first player: Hex red, Go Black)", "",
              "| Game | Colour | Early | Late |", "|---|---|---|---|"]
    for game in ("Hex", "Go"):
        games = games_by_cell[(game, "GLM 5.3")]
        for actor, label in (("X", "first player"), ("O", "second player")):
            g = [x for x in games if x[1] == actor]
            lines.append(f"| {game} | {label} | {pct(*rate([x for x in g if x[0] < EARLY]))} | "
                         f"{pct(*rate([x for x in g if x[0] >= EARLY]))} |")

    lines += ["", "## Per lineage", "",
              "| Lineage | Held-out ID per checkpoint (%) | Fit rise (pp) | p | P_sat | Reflection calls | Code revisions | "
              "Games calling a saved tool | Billed | Of which replayed | Learning cost, paper's pricing |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for names in CELLS.values():
        for n in names:
            r = summaries[n]
            rise = "–" if r["rise"] is None else f"{r['rise']:.1f}"
            pv = "–" if r["p"] is None else f"{r['p']:.2g}"
            psat = "–" if r["psat"] is None else f"{r['psat']:.0f} ({r['kind']})"
            lines.append(f"| `{n}` | {', '.join(f'{x:.0f}' for x in r['ids'])} | {rise} | {pv} | {psat} | "
                         f"{r['reflect_calls']:.1f} | {r['code_revisions']} | {100 * r['tool_called_share']:.0f} % | "
                         f"${r['billed']:.2f} | ${discarded(n):.2f} | ${learning_cost(n):.2f} |")

    lines += ["", "## GLM behaviour under constraints", "",
              "All splits, both lineages pooled per checkpoint; columns as in report 15.", "",
              "| Game | Checkpoint | Games | Calls per game | Near budget | Lost to limits | Illegal submissions | "
              "Moves per call |", "|---|---|---|---|---|---|---|---|"]
    for game in ("Hex", "Go"):
        per = [behaviour(n) for n in CELLS[(game, "GLM 5.3")]]
        for t in range(max(len(p) for p in per)):
            rows = [p[t] for p in per if len(p) > t]
            g = sum(r["games"] for r in rows)

            def w(key):
                return sum(r[key] * r["games"] for r in rows) / g

            lines.append(f"| {game} | {t} | {g} | {w('calls'):.1f} | {100 * w('near'):.0f} % | "
                         f"{sum(r['lost_to_limits'] for r in rows)} | {sum(r['invalid'] for r in rows)} | "
                         f"{w('moves_per_call'):.2f} |")
    lines += READING
    lines.append("")
    REPORT.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
