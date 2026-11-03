"""Go at reflection effort medium vs high, Sonnet 5.5 and Haiku 5.5. Writes reports/22_go_effort.md.

Plan C added two Go lineages per model at reflection effort medium (scripts/plan_c.sh), with
the settings of the high-effort Go lineages of report 15 apart from reflection effort: actor
effort medium, Go 8 / 20 / 4 games per checkpoint, checkpoints 0-10, 4 games at a time.
Same early / late split as report 15 (checkpoints 0-2 / 3-10), fixed before these results were seen.

    uv run python scripts/compare_go_effort.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare_models import EARLY, ROOT, behaviour, id_games, pct, rate, z_test  # noqa: E402
from compare_runs import summarize  # noqa: E402

REPORT = ROOT / "reports" / "22_go_effort.md"
CELLS = {
    ("Sonnet 5.5", "medium"): ["go_sonnet_medium", "go_sonnet_medium_rep2"],
    ("Sonnet 5.5", "high"): ["go_sonnet_reflect_high", "go_sonnet_reflect_high_rep2"],
    ("Haiku 5.5", "medium"): ["go_haiku_medium", "go_haiku_medium_rep2"],
    ("Haiku 5.5", "high"): ["go_haiku_reflect_high", "go_haiku_reflect_high_rep2"],
}

READING = [
    "", "## Reading",
    "",
    "- On Go, reflection effort makes no measurable difference. Late held-out ID is 61 % at medium and 60 % at",
    "  high for Sonnet (p = 0.69), 52 % and 47 % for Haiku (p = 0.24), from the same start (checkpoint 0: Sonnet",
    "  60 % and 65 %, Haiku 48 % and 52 %). No cell's pooled early → late change is significant. On Hex, high",
    "  effort ended at 83 % against 65 % for medium (z = 3.75, p = 0.0002; report 12), so the Hex effort",
    "  result does not carry over to Go.",
    "- Sonnet at medium effort reflects on Go as it did on Hex: 5.6–6.7 calls per round, code changed at 1–2",
    "  of 10 reflections, and the actor ran a saved tool in 1–6 % of games. Held-out ID stays within 55–70 %",
    "  in both lineages and neither passes the flat-curve gate. Play does not change either: 10–13 model calls",
    "  per game, under 0.9 moves per call, and 4–13 illegal submissions per checkpoint to the end, where",
    "  Sonnet at high effort moved play into its tool (about 1 move per call) and stopped submitting",
    "  illegal moves after checkpoint 2 (0–1 per checkpoint, report 15).",
    "- High effort changed what Sonnet does on Go, but not its pooled score. Its two lineages split:",
    "  `go_sonnet_reflect_high_rep2` holds 85–90 % from checkpoint 2, above every medium checkpoint, and",
    "  `go_sonnet_reflect_high` falls to 15–20 % at checkpoints 6–9 after its time-limit failure (report 15).",
    "  Pooled, they land on the medium lineages' score. With two lineages per cell, high effort here",
    "  widened the spread of outcomes rather than moving the mean.",
    "- Haiku at medium effort is busy, as at high: 11–14 reflection calls per round and code changed at 6–8",
    "  of 10 reflections, but its actor ran a saved tool in 0–7 % of games (21–61 % at high effort). Much of",
    "  the saved code checks Haiku's own moves and reflections (legality guards, a pass gate, loss audits).",
    "- `go_haiku_medium` gets P_sat 23,266 (\"saturated\") from a 14-point fitted rise with p = 0.33: ID",
    "  jumped to 65 % at checkpoints 4–5 and fell back to 40–45 %. It passes the paper's 10-point rule",
    "  alone and fails the flat-curve gate, like the Haiku false positives of report 15.",
    "- Medium effort was cheaper: billed $15.69–16.76 per Sonnet lineage (high: $17.95–20.93) and $2.14–2.26",
    "  per Haiku lineage (high: $2.85–2.97).",
]


def main():
    lines = [
        "# 22 Go: reflection effort medium vs high (Sonnet 5.5 and Haiku 5.5)",
        "",
        "Plan C ran two Go lineages per model at reflection effort medium, with every other setting as in the",
        "high-effort Go lineages of report 15: actor effort medium, 8 / 20 / 4 games per checkpoint (train /",
        "held-out ID / OOD), checkpoints 0–10, GNU Go levels 5–9 (ID) and 10 (OOD).",
        f"Early = checkpoints 0–{EARLY - 1}; late = checkpoint {EARLY} onward.",
        "",
        "## Held-out ID, early → late",
        "",
        "| Model | Reflection effort | Checkpoint 0 | Early | Late | Change | z | p |",
        "|---|---|---|---|---|---|---|---|",
    ]
    late, summaries = {}, {}
    for (model, effort), names in CELLS.items():
        games = [g for n in names for g in id_games(n)]
        for n in names:
            summaries[n] = summarize(n)
        c0 = rate([g for g in games if g[0] == 0])
        e, l_ = rate([g for g in games if g[0] < EARLY]), rate([g for g in games if g[0] >= EARLY])
        z, p = z_test(*e, *l_)
        late[(model, effort)] = l_
        lines.append(f"| {model} | {effort} | {pct(*c0)} | {pct(*e)} | {pct(*l_)} | "
                     f"{100 * (l_[0] / l_[1] - e[0] / e[1]):+.0f} pp | {z:.2f} | {p:.2g} |")

    lines += ["", "## High against medium, late checkpoints", "",
              "| Model | Medium late | High late | z | p |", "|---|---|---|---|---|"]
    for model in ("Sonnet 5.5", "Haiku 5.5"):
        m, h = late[(model, "medium")], late[(model, "high")]
        z, p = z_test(*m, *h)
        lines.append(f"| {model} | {pct(*m)} | {pct(*h)} | {z:.2f} | {p:.2g} |")

    lines += ["", "## Per lineage", "",
              "| Lineage | Reflection effort | Held-out ID per checkpoint (%) | Fit rise (pp) | p | P_sat | "
              "Reflection calls | Code revisions | Games calling a saved tool | Billed |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for (model, effort), names in CELLS.items():
        for n in names:
            r = summaries[n]
            rise = "–" if r["rise"] is None else f"{r['rise']:.1f}"
            pv = "–" if r["p"] is None else f"{r['p']:.2g}"
            psat = "–" if r["psat"] is None else f"{r['psat']:.0f} ({r['kind']})"
            lines.append(f"| `{n}` | {effort} | {', '.join(f'{x:.0f}' for x in r['ids'])} | {rise} | {pv} | {psat} | "
                         f"{r['reflect_calls']:.1f} | {r['code_revisions']} | {100 * r['tool_called_share']:.0f} % | "
                         f"${r['billed']:.2f} |")

    lines += ["", "## Behaviour under constraints, effort medium", "",
              "All splits, both lineages pooled per checkpoint; columns as in report 15 (high effort is there).", "",
              "| Model | Checkpoint | Games | Calls per game | Near budget | Lost to limits | Illegal submissions | "
              "Moves per call |", "|---|---|---|---|---|---|---|---|"]
    for model in ("Sonnet 5.5", "Haiku 5.5"):
        per = [behaviour(n) for n in CELLS[(model, "medium")]]
        for t in range(max(len(p) for p in per)):
            rows = [p[t] for p in per if len(p) > t]
            g = sum(r["games"] for r in rows)

            def w(key):
                return sum(r[key] * r["games"] for r in rows) / g

            lines.append(f"| {model} | {t} | {g} | {w('calls'):.1f} | {100 * w('near'):.0f} % | "
                         f"{sum(r['lost_to_limits'] for r in rows)} | {sum(r['invalid'] for r in rows)} | "
                         f"{w('moves_per_call'):.2f} |")
    lines += READING
    lines.append("")
    REPORT.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
