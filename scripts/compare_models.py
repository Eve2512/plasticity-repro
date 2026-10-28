"""Sonnet 5.5 vs Haiku 5.5 on Hex and Go, reflection effort high. Writes reports/15_model_game_comparison.md.

Two lineages per cell; held-out ID per colour. The split was fixed before the
plan A results were seen: "early" = checkpoints 0-2, "late" = checkpoint 3 and
after (all completed ones), so runs stopped early by their cap still count.

    uv run python scripts/compare_models.py
"""

import json
import sys
from math import erf, sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare_runs import summarize  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "15_model_game_comparison.md"
EARLY = 3  # checkpoints 0..EARLY-1 are early
CELLS = {
    ("Hex", "Sonnet 5.5"): ["sonnet_reflect_high", "sonnet_reflect_high_rep2"],
    ("Hex", "Haiku 5.5"): ["hex_haiku_reflect_high", "hex_haiku_reflect_high_rep2"],
    ("Go", "Sonnet 5.5"): ["go_sonnet_reflect_high", "go_sonnet_reflect_high_rep2"],
    ("Go", "Haiku 5.5"): ["go_haiku_reflect_high", "go_haiku_reflect_high_rep2"],
}
COLOURS = {"X": "first player", "O": "second player"}  # Hex red / Go Black, Hex blue / Go White


def id_games(name: str) -> list[tuple[int, str, float]]:
    """(checkpoint, actor, score) for every held-out ID game of completed checkpoints."""
    d = ROOT / "runs" / name
    done = len(json.loads((d / "results.json").read_text())["checkpoints"])
    out = []
    for t in range(done):
        for f in sorted((d / "games" / f"checkpoint_{t:03d}" / "id").glob("*.json")):
            r = json.loads(f.read_text())["result"]
            out.append((t, r["actor"], r["score"]))
    return out


def rate(games) -> tuple[float, int]:
    return sum(s for *_, s in games), len(games)


def z_test(a, n, b, m) -> tuple[float, float]:
    """Two-proportion z (b/m minus a/n) and its two-sided p."""
    if not n or not m:
        return float("nan"), float("nan")
    p = (a + b) / (n + m)
    se = sqrt(p * (1 - p) * (1 / n + 1 / m)) if 0 < p < 1 else 0
    if not se:
        return float("nan"), float("nan")
    z = (b / m - a / n) / se
    return z, 2 * (1 - 0.5 * (1 + erf(abs(z) / sqrt(2))))


def pct(a, n) -> str:
    return f"{a:g}/{n} = {100 * a / n:.0f} %" if n else "–"


BUDGET = 32  # actor model calls per game
NEAR = 28  # "near the budget": 28 or more of 32 calls


def behaviour(name: str) -> list[dict]:
    """Per completed checkpoint: how the actor and reflector worked within their limits (all splits)."""
    d = ROOT / "runs" / name
    res = json.loads((d / "results.json").read_text())
    rows = []
    for c in res["checkpoints"]:
        results = [json.loads(f.read_text())["result"] for f in (d / "games" / f"checkpoint_{c['t']:03d}").glob("*/*.json")]
        n = len(results)
        calls = [r["model_calls"] for r in results]
        moves = sum(len(r["moves"]) for r in results)
        refl = c.get("reflection") or {}
        rows.append({
            "t": c["t"], "games": n,
            "calls": sum(calls) / n,
            "near": sum(x >= NEAR for x in calls) / n,
            "lost_to_limits": sum(r["end_reason"] != "finished" for r in results),
            "invalid": sum(r["invalid_submissions"] for r in results),
            "moves_per_call": moves / max(1, sum(calls)),
            "reflect_calls": sum(a["calls"] for a in refl.get("attempts", [])) if refl else None,
            "rejected": sum(1 for a in refl.get("attempts", []) if a["error"]) if refl else None,
        })
    return rows


def constraint_section() -> list[str]:
    lines = [
        "", "## Behaviour under constraints",
        "",
        f"Limits: {BUDGET} model calls per game (a game not finished within them is lost), 240 s per tool call",
        "(a second timeout forfeits), 50 reflection calls and 3 attempts per round. Adapting to these limits is",
        "part of what experience can change: e.g. handing play to a saved tool (more moves per model call),",
        "staying clear of the call budget, fewer illegal submissions. All splits; per checkpoint, both lineages",
        f"pooled. \"Near budget\" = {NEAR}+ of {BUDGET} calls.",
        "",
        "| Game | Model | Checkpoint | Games | Calls per game | Near budget | Lost to limits | Illegal submissions | "
        "Moves per call | Reflection calls (of 50) | Rejected attempts |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for (game, model), names in CELLS.items():
        per = [behaviour(n) for n in names]
        for t in range(max(len(p) for p in per)):
            rows = [p[t] for p in per if len(p) > t]
            g = sum(r["games"] for r in rows)

            def w(key):
                return sum(r[key] * r["games"] for r in rows) / g

            rc = [r["reflect_calls"] for r in rows if r["reflect_calls"] is not None]
            rj = [r["rejected"] for r in rows if r["rejected"] is not None]
            lines.append(
                f"| {game} | {model} | {t} | {g} | {w('calls'):.1f} | {100 * w('near'):.0f} % | "
                f"{sum(r['lost_to_limits'] for r in rows)} | {sum(r['invalid'] for r in rows)} | {w('moves_per_call'):.2f} | "
                f"{' / '.join(str(x) for x in rc) or '–'} | {sum(rj) if rj else '–'} |")
    return lines


READING = [
    "", "## Reading",
    "",
    "- Sonnet improves with experience on both games; Haiku does not. Pooled early → late held-out ID: Sonnet",
    "  +14 pp (Hex) and +15 pp (Go), Haiku −5 pp and −7 pp. Late Sonnet beats late Haiku by 44 pp (Hex) and",
    "  23 pp (Go). The pooled z-tests treat games as independent and ignore lineage; they are a summary, not",
    "  the gate. Haiku at reflection effort high stays flat, so the earlier Haiku result was not an effort artefact.",
    "- Per lineage, only `go_sonnet_reflect_high_rep2` passes the p < 0.05 rise gate (75 → 90 %, p = 0.04). The",
    "  two Hex Sonnet lineages rise by 21–27 pp but have p ≈ 0.12–0.13 with 12 ID games per checkpoint.",
    "- The two Go Sonnet lineages diverge. Rep2's saved tool was in use in every game from checkpoint 2 and ID held",
    "  at 85–90 %. Run 1 called its tool from checkpoint 1 but stayed at 30–35 % until checkpoint 5 (60 %), and",
    "  cost almost twice as much per checkpoint (25 reflection calls per round vs 14). It hit its $13 cap after 6",
    "  completed checkpoints.",
    "- Behaviour under constraints (table above). After the first reflection, Go Sonnet roughly doubled its model",
    "  calls per game (10 → 20), 31 % of games came near the 32-call budget and 6 were lost to it. At the next",
    "  checkpoint it moved play into its saved tool: 1.3 moves per model call, none near the budget, none lost.",
    "  Haiku went the other way on both games: calls per game rose (Hex 10 → 17, Go 11 → 16) and moves per call",
    "  fell, while it kept submitting illegal Go moves (1–10 per checkpoint vs Sonnet's 0–1 after checkpoint 2).",
    "- Not in the tables: run 1's checkpoint 6 finished all 32 games before the cap stopped it, so it is not",
    "  counted. In it the actor called its tool with a much larger search budget (e.g. `budget=2500000`), the",
    "  call ran past the 240 s tool limit and 9 of 32 games were forfeited (ID 7/20 = 35 %, 5 ID games lost this",
    "  way). Rep2 never did this. An adaptation that relaxes one limit (model calls) can break another (time).",
    "- OOD (GNU Go level 10) does not move for any cell; on 5×5 it plays almost like levels 5–9 (report 13), so",
    "  OOD here tests openings more than opponent strength.",
]


def main():
    lines = [
        "# 15 Sonnet 5.5 vs Haiku 5.5 on Hex and Go (reflection effort high)",
        "",
        "Actor effort medium, reflection effort high, two lineages per cell. Hex: 6×6, pooled openings,",
        "8 / 12 / 4 games per checkpoint (train / ID / OOD), opponents 3k–100k nodes. Go: 5×5, pooled openings,",
        "8 / 20 / 4, GNU Go levels 5–9 (ID) and 10 (OOD), training openings redrawn every checkpoint (report 13).",
        f"Early = checkpoints 0–{EARLY - 1} (checkpoint 0 is before any reflection); late = checkpoint {EARLY} onward.",
        "",
        "## Held-out ID, early → late",
        "",
        "| Game | Model | Lineages (checkpoints done) | Early | Late | Change | z | p |",
        "|---|---|---|---|---|---|---|---|",
    ]
    late_by_cell, games_by_cell, summaries = {}, {}, {}
    for (game, model), names in CELLS.items():
        games = [g for n in names for g in id_games(n)]
        for n in names:
            summaries[n] = summarize(n)
        early, late = rate([g for g in games if g[0] < EARLY]), rate([g for g in games if g[0] >= EARLY])
        z, p = z_test(*early, *late)
        late_by_cell[(game, model)] = late
        games_by_cell[(game, model)] = games
        done = ", ".join(f"`{n}` ({summaries[n]['checkpoints']})" for n in names)
        change = f"{100 * (late[0] / late[1] - early[0] / early[1]):+.0f} pp" if late[1] and early[1] else "–"
        lines.append(f"| {game} | {model} | {done} | {pct(*early)} | {pct(*late)} | {change} | {z:.2f} | {p:.2g} |")

    lines += ["", "## Sonnet vs Haiku, late checkpoints", "", "| Game | Sonnet late | Haiku late | z | p |", "|---|---|---|---|---|"]
    for game in ("Hex", "Go"):
        s, h = late_by_cell[(game, "Sonnet 5.5")], late_by_cell[(game, "Haiku 5.5")]
        z, p = z_test(*h, *s)
        lines.append(f"| {game} | {pct(*s)} | {pct(*h)} | {z:.2f} | {p:.2g} |")

    lines += ["", "## Per colour (first player: Hex red, Go Black; second: Hex blue, Go White)", "",
              "| Game | Model | Colour | Early | Late |", "|---|---|---|---|---|"]
    for (game, model), games in games_by_cell.items():
        for actor, label in COLOURS.items():
            g = [x for x in games if x[1] == actor]
            lines.append(f"| {game} | {model} | {label} | {pct(*rate([x for x in g if x[0] < EARLY]))} | "
                         f"{pct(*rate([x for x in g if x[0] >= EARLY]))} |")

    lines += ["", "## Per lineage", "",
              "| Lineage | Held-out ID per checkpoint (%) | Fit rise (pp) | p | P_sat | Reflection calls | "
              "Code revisions | Games calling a saved tool | Billed | Stopped |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for names in CELLS.values():
        for n in names:
            r = summaries[n]
            rise = "–" if r["rise"] is None else f"{r['rise']:.1f}"
            pv = "–" if r["p"] is None else f"{r['p']:.2g}"
            psat = "–" if r["psat"] is None else f"{r['psat']:.0f} ({r['kind']})"
            stopped = "cap" if r["stopped"] else "–"
            lines.append(f"| `{n}` | {', '.join(f'{x:.0f}' for x in r['ids'])} | {rise} | {pv} | {psat} | "
                         f"{r['reflect_calls']:.1f} | {r['code_revisions']} | {100 * r['tool_called_share']:.0f} % | "
                         f"${r['billed']:.2f} | {stopped} |")
    lines += constraint_section()
    lines += READING
    lines.append("")
    REPORT.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
