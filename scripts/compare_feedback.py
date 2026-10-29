"""Limitation test 5: reflection with and without game records. Writes reports/18_experience_vs_compute.md.

Same model, efforts, opening bank, game counts and reflection budget (50 calls); the
no-feedback lineages got only a note in place of the training game records.

    uv run python scripts/compare_feedback.py
"""

import json
import sys
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ablate_inventory import summary as ablation_summary  # noqa: E402
from compare_models import EARLY, id_games, pct, rate, z_test  # noqa: E402
from compare_runs import summarize  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "18_experience_vs_compute.md"
ARMS = {
    "game records": ["sonnet_reflect_high", "sonnet_reflect_high_rep2"],
    "no game records": ["sonnet_nofeedback_high", "sonnet_nofeedback_high_rep2"],
}


def inventory_files(name: str) -> list[int]:
    """Functional files (outside tracking/) per checkpoint inventory."""
    d = ROOT / "runs" / name / "inventories"
    return [sum(1 for p in inv.rglob("*") if p.is_file() and "tracking" not in p.relative_to(inv).parts)
            for inv in sorted(d.glob("checkpoint_*"))]


def id_scores(name: str) -> dict[tuple[int, str], float]:
    """(checkpoint, game file) -> score; all four lineages play the same ID openings per checkpoint."""
    d = ROOT / "runs" / name / "games"
    return {(int(f.parent.parent.name[-3:]), f.name): json.loads(f.read_text())["result"]["score"]
            for f in d.glob("checkpoint_*/id/*.json")}


def sign_test(wins: int, losses: int) -> float:
    """Two-sided exact binomial p for discordant pairs."""
    n = wins + losses
    k = min(wins, losses)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n) if n else float("nan")


def thinking_turns(name: str) -> tuple[int, int]:
    """(assistant turns with a thinking summary, all assistant turns) over the run's reflections."""
    with_thinking = total = 0
    for f in (ROOT / "runs" / name / "reflect").glob("checkpoint_*/attempt_*/attempt_*.json"):
        for m in json.loads(f.read_text())["messages"]:
            if m["role"] == "assistant":
                total += 1
                with_thinking += bool((m.get("thinking") or "").strip())
    return with_thinking, total


def main():
    lines = [
        "# 18 Experience vs compute (limitation test 5)",
        "",
        "Hex 6×6, Sonnet 5.5, actor effort medium, reflection effort high, 8 / 12 / 4 games per checkpoint,",
        "checkpoints 0–7, same opening bank. The no-feedback lineages played and paid for the same training",
        "games, but reflection found only a note saying no records were available, with the same 50-call",
        "budget, its inventory and the protocol files (`--no-feedback`).",
        "",
        "## Per lineage",
        "",
        "| Lineage | Reflection saw | Held-out ID per checkpoint (%) | Fit rise (pp) | p | Reflection calls (of 50) | "
        "Functional inventory files per checkpoint | Games calling a saved tool | Billed |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for arm, names in ARMS.items():
        for n in names:
            r = summarize(n)
            rise = "–" if r["rise"] is None else f"{r['rise']:.1f}"
            pv = "–" if r["p"] is None else f"{r['p']:.2g}"
            lines.append(f"| `{n}` | {arm} | {', '.join(f'{x:.0f}' for x in r['ids'])} | {rise} | {pv} | "
                         f"{r['reflect_calls']:.1f} | {', '.join(map(str, inventory_files(n)))} | "
                         f"{100 * r['tool_called_share']:.0f} % | ${r['billed']:.2f} |")

    lines += ["", f"## Held-out ID pooled, early (checkpoints 0–{EARLY - 1}) → late ({EARLY} onward)", "",
              "| Reflection saw | Early | Late | z | p |", "|---|---|---|---|---|"]
    late = {}
    for arm, names in ARMS.items():
        games = [g for n in names for g in id_games(n)]
        e, l_ = rate([g for g in games if g[0] < EARLY]), rate([g for g in games if g[0] >= EARLY])
        late[arm] = l_
        z, p = z_test(*e, *l_)
        lines.append(f"| {arm} | {pct(*e)} | {pct(*l_)} | {z:.2f} | {p:.2g} |")
    z, p = z_test(*late["no game records"], *late["game records"])
    lines += ["", f"Late, game records vs none: z = {z:.2f}, p = {p:.2g}."]

    fb = [id_scores(n) for n in ARMS["game records"]]
    nf = [id_scores(n) for n in ARMS["no game records"]]
    lines += ["", "## Same openings, checkpoint by checkpoint", "",
              "All four lineages play the same 12 held-out ID openings, against the same deterministic opponents,",
              "at every checkpoint, so the arms can be compared game by game. Lineage 1 is paired with lineage 1,",
              "rep2 with rep2.", "",
              "| Checkpoint | Game records (wins of 24) | No game records (wins of 24) | Difference |",
              "|---|---|---|---|"]
    for t in range(8):
        a = sum(s for f in fb for (c, _), s in f.items() if c == t)
        b = sum(s for f in nf for (c, _), s in f.items() if c == t)
        lines.append(f"| {t} | {a:g} | {b:g} | {a - b:+g} |")
    for label, keep in (("early", lambda t: t < EARLY), ("late", lambda t: t >= EARLY)):
        only_fb = only_nf = 0
        for f, g in zip(fb, nf):
            for k, s in f.items():
                if keep(k[0]) and k in g:
                    only_fb += s > g[k]
                    only_nf += g[k] > s
        lines.append(f"\n{label.capitalize()}: {only_fb} games won only with game records, {only_nf} only without; "
                     f"sign test p = {sign_test(only_fb, only_nf):.2g}.")

    no_tools = rate([g for n in ARMS["no game records"] for g in id_games(n)])
    empty = [ablation_summary(ROOT / "runs" / n, 7, "empty") for n in ARMS["game records"]]
    empty_rate = (sum(s["wins"] for s in empty), sum(s["games"] for s in empty))
    z, p = z_test(*no_tools, *empty_rate)
    lines += [
        "", "## Baselines without tools", "",
        "| Source | Held-out ID |", "|---|---|",
        f"| No-feedback lineages, all checkpoints (inventory always empty) | {pct(*no_tools)} |",
        f"| Report 17, `empty` arm (feedback lineages' final checkpoint, inventory removed) | {pct(*empty_rate)} |",
        "", f"Difference: z = {z:.2f}, p = {p:.2g} (different openings: report 17 drew 24 from checkpoint 7's bank).",
    ]

    lines += ["", "## Thinking summaries in reflection", "", "| Lineage | Reflection turns with a summary |", "|---|---|"]
    for names in ARMS.values():
        for n in names:
            t, total = thinking_turns(n)
            lines.append(f"| `{n}` | {t}/{total} |" if total else f"| `{n}` | – (not recorded) |")

    lines += READING
    lines.append("")
    REPORT.write_text("\n".join(lines))
    print("\n".join(lines))


READING = [
    "", "## Reading",
    "",
    "- Without game records the reflector built nothing. In all 14 reflections it used 4 of its 50 calls,",
    "  read the note and its empty inventory, ran the validator and stopped. Its thinking summaries say why:",
    "  the protocol asks every functional file to address an observed failure mode, and with nothing observed",
    "  any tool would be a guess. The extra compute was offered but not used.",
    "- So this test does not separate experience from compute the way it was planned. It shows that, under",
    "  the paper's reflection prompt, game records are what makes the agent build anything at all. A",
    "  stricter control would require the reflector to spend its budget (e.g. build a general Hex player from",
    "  the rules alone) and compare that with the feedback arm.",
    "- The no-feedback lineages are an untrained control on the same openings. Before tools mattered",
    "  (checkpoints 0–2) the arms are level (sign test p = 0.81); from checkpoint 3 the feedback arm wins",
    "  38 games the control loses and loses 5 the control wins (p = 2.5e-07). This paired test is much",
    "  stronger than either feedback lineage's own flat-curve test (p = 0.12–0.13, report 15).",
    "- The control's held-out ID falls from 72 % to 56 % (p = 0.024 if games are treated as independent)",
    "  although nothing changed: same empty inventory, same 12 openings at every checkpoint, deterministic",
    "  opponents. The drop is spread over six openings. The only varying part is the actor's sampling, plus",
    "  any drift in the served model during the ~3 hours of the run. A single lineage's curve can move this",
    "  much without any learning, and repeated openings make games far from independent.",
    "- The control ran three days after the feedback lineages (2026-10-28/29 vs 2026-10-25), so the paired",
    "  test controls for openings and opponents, not for time. At checkpoint 0 the arms are level (15 vs 15",
    "  wins), and the feedback lineages' late rate (83 %) is above the control's best stretch (72 %) too.",
    "- The control's pooled rate (62 %) and report 17's `empty` arm (52 %) do not differ significantly",
    "  (p = 0.21); both put the no-tool actor at roughly 50–60 %.",
    "- These are the first lineages with thinking recorded during the run (report 16 covers replayed",
    "  thinking for the older runs).",
]


if __name__ == "__main__":
    main()
